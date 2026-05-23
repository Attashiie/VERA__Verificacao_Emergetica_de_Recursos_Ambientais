"""
Gerenciador de projetos VERA — Interface de linha de comando
Permite criar, carregar, salvar e processar projetos de análise emergética
"""

import json
import os
from typing import List, Optional, Dict
import numpy as np
from vera_calculator import (
    ProjectConfig, 
    EmergyCalculator, 
    ResultsFormatter
)


class ProjectManager:
    """Gerencia projetos de análise emergética"""
    
    def __init__(self, storage_dir: str = "."):
        """Inicializa gerenciador de projetos"""
        self.storage_dir = storage_dir
        self.projects: Dict[str, ProjectConfig] = {}
    
    def create_project(
        self,
        name: str,
        n: int,
        process_names: Optional[List[str]] = None,
        A: Optional[np.ndarray] = None,
        R: Optional[np.ndarray] = None,
        uevs: Optional[np.ndarray] = None,
        types: Optional[List[str]] = None
    ) -> ProjectConfig:
        """Cria um novo projeto"""
        
        if process_names is None:
            process_names = [f"Processo {chr(65 + i)}" for i in range(n)]
        
        if A is None:
            A = np.zeros((n, n))
        
        if R is None:
            R = np.ones(n)
        
        if uevs is None:
            uevs = np.ones(n) * 1e5
        
        if types is None:
            types = ['Renovável'] * (n - 1) + ['Produto']
        
        project = ProjectConfig(
            name=name,
            n=n,
            process_names=process_names,
            A=A,
            R=R,
            uevs=uevs,
            types=types
        )
        
        self.projects[name] = project
        return project
    
    def load_project_from_json(self, filepath: str) -> ProjectConfig:
        """Carrega projeto de arquivo JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        project = ProjectConfig(
            name=data['name'],
            n=data['n'],
            process_names=data['process_names'],
            A=np.array(data['A']),
            R=np.array(data['R']),
            uevs=np.array(data['uevs']),
            types=data['types']
        )
        
        self.projects[project.name] = project
        return project
    
    def save_project_to_json(self, project: ProjectConfig, filepath: str) -> None:
        """Salva projeto em arquivo JSON"""
        data = {
            'name': project.name,
            'n': project.n,
            'process_names': project.process_names,
            'A': project.A.tolist(),
            'R': project.R.tolist(),
            'uevs': project.uevs.tolist(),
            'types': project.types
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_project_from_csv(self, filepath: str, name: str) -> ProjectConfig:
        """
        Carrega projeto de arquivo CSV
        Formato esperado: processo,tipo,R,UEV
        """
        import csv
        
        process_names = []
        types = []
        R = []
        uevs = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                process_names.append(row['processo'])
                types.append(row['tipo'])
                R.append(float(row['R']))
                uevs.append(float(row['UEV']))
        
        n = len(process_names)
        project = ProjectConfig(
            name=name,
            n=n,
            process_names=process_names,
            A=np.zeros((n, n)),
            R=np.array(R),
            uevs=np.array(uevs),
            types=types
        )
        
        self.projects[name] = project
        return project
    
    def get_project(self, name: str) -> Optional[ProjectConfig]:
        """Obtém projeto pelo nome"""
        return self.projects.get(name)
    
    def list_projects(self) -> List[str]:
        """Lista nomes de todos os projetos carregados"""
        return list(self.projects.keys())
    
    def calculate_and_export(
        self,
        project_name: str,
        output_dir: str = "."
    ) -> None:
        """Calcula e exporta resultados de um projeto"""
        project = self.get_project(project_name)
        if project is None:
            print(f"Erro: Projeto '{project_name}' não encontrado")
            return
        
        calculator = EmergyCalculator(project)
        
        try:
            results = calculator.calculate()
            
            # Cria nomes de arquivo
            safe_name = project_name.replace(' ', '_').replace('/', '_')
            csv_path = os.path.join(output_dir, f"{safe_name}_results.csv")
            json_path = os.path.join(output_dir, f"{safe_name}_results.json")
            
            # Exporta resultados
            ResultsFormatter.print_results(results)
            ResultsFormatter.export_csv(results, csv_path)
            ResultsFormatter.export_json(results, json_path)
            
            print(f"\n[OK] Resultados salvos:")
            print(f"  CSV:  {csv_path}")
            print(f"  JSON: {json_path}")
        
        except ValueError as e:
            print(f"Erro no cálculo: {e}")


class InteractiveCLI:
    """Interface de linha de comando interativa"""
    
    def __init__(self):
        """Inicializa CLI"""
        self.manager = ProjectManager()
    
    def show_menu(self):
        """Exibe menu principal"""
        print("\n" + "="*70)
        print("VERA — Verificação Emergética de Recursos Ambientais")
        print("="*70)
        print("\n1. Criar novo projeto")
        print("2. Carregar projeto de arquivo JSON")
        print("3. Carregar projeto de arquivo CSV")
        print("4. Listar projetos carregados")
        print("5. Calcular e exportar resultados")
        print("6. Sair")
        print("\nEscolha uma opção (1-6): ", end="")
    
    def run(self):
        """Executa a interface interativa"""
        while True:
            self.show_menu()
            choice = input().strip()
            
            if choice == "1":
                self.create_project_interactive()
            elif choice == "2":
                self.load_json_interactive()
            elif choice == "3":
                self.load_csv_interactive()
            elif choice == "4":
                self.list_projects_interactive()
            elif choice == "5":
                self.calculate_interactive()
            elif choice == "6":
                print("\nAté logo!")
                break
            else:
                print("Opção inválida!")
    
    def create_project_interactive(self):
        """Cria projeto interativamente"""
        print("\n--- Criar Novo Projeto ---")
        
        name = input("Nome do projeto: ").strip()
        if not name:
            name = "Novo Projeto"
        
        try:
            n = int(input("Número de processos: "))
            if n < 2:
                print("Erro: Número de processos deve ser ≥ 2")
                return
        except ValueError:
            print("Erro: Número inválido")
            return
        
        # Nomes dos processos
        process_names = []
        for i in range(n):
            pname = input(f"Nome do processo {i+1} [{chr(65+i)}]: ").strip()
            process_names.append(pname or chr(65 + i))
        
        # Tipos
        types = []
        for i in range(n):
            print(f"Tipo de {process_names[i]} (Renovável/Não-Renovável/Produto): ", end="")
            ptype = input().strip() or "Renovável"
            types.append(ptype)
        
        # Vetor R
        print("\nEntradas de recursos (R):")
        R = []
        for i in range(n):
            try:
                val = float(input(f"R[{process_names[i]}]: "))
                R.append(val)
            except ValueError:
                R.append(1.0)
        
        # UEVs
        print("\nTransformidades (UEVs):")
        uevs = []
        for i in range(n):
            try:
                val = float(input(f"UEV[{process_names[i]}] (ex: 1e5): "))
                uevs.append(val)
            except ValueError:
                uevs.append(1e5)
        
        # Cria projeto
        project = self.manager.create_project(
            name=name,
            n=n,
            process_names=process_names,
            A=np.zeros((n, n)),
            R=np.array(R),
            uevs=np.array(uevs),
            types=types
        )
        
        print(f"\n[OK] Projeto '{name}' criado com sucesso!")
    
    def load_json_interactive(self):
        """Carrega projeto de JSON"""
        print("\n--- Carregar Projeto JSON ---")
        filepath = input("Caminho do arquivo: ").strip()
        
        if not os.path.exists(filepath):
            print(f"Erro: Arquivo '{filepath}' não encontrado")
            return
        
        try:
            project = self.manager.load_project_from_json(filepath)
            print(f"[OK] Projeto '{project.name}' carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar: {e}")
    
    def load_csv_interactive(self):
        """Carrega projeto de CSV"""
        print("\n--- Carregar Projeto CSV ---")
        filepath = input("Caminho do arquivo: ").strip()
        name = input("Nome do projeto: ").strip() or "Projeto CSV"
        
        if not os.path.exists(filepath):
            print(f"Erro: Arquivo '{filepath}' não encontrado")
            return
        
        try:
            project = self.manager.load_project_from_csv(filepath, name)
            print(f"[OK] Projeto '{name}' carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar: {e}")
    
    def list_projects_interactive(self):
        """Lista projetos carregados"""
        projects = self.manager.list_projects()
        if not projects:
            print("\nNenhum projeto carregado.")
            return
        
        print("\n--- Projetos Carregados ---")
        for i, name in enumerate(projects, 1):
            proj = self.manager.get_project(name)
            print(f"{i}. {name} ({proj.n} processos)")
    
    def calculate_interactive(self):
        """Calcula resultados"""
        projects = self.manager.list_projects()
        if not projects:
            print("\nNenhum projeto carregado!")
            return
        
        print("\n--- Selecionar Projeto para Calcular ---")
        for i, name in enumerate(projects, 1):
            print(f"{i}. {name}")
        
        try:
            choice = int(input("Escolha um projeto: ")) - 1
            if 0 <= choice < len(projects):
                project_name = projects[choice]
                output_dir = input("Diretório de saída [.]: ").strip() or "."
                self.manager.calculate_and_export(project_name, output_dir)
            else:
                print("Opção inválida!")
        except ValueError:
            print("Erro: Número inválido")


# ============================================================
# EXEMPLO DE USO VIA SCRIPT
# ============================================================
def example_usage():
    """Exemplo de uso programático"""
    manager = ProjectManager()
    
    # Cria projeto de demonstração
    project = manager.create_project(
        name="Análise Agricultura Regenerativa",
        n=4,
        process_names=["Solo", "Biomassa", "Água", "Produto Agrícola"],
        A=np.array([
            [0.0, 0.1, 0.05, 0.0],
            [0.2, 0.0, 0.1, 0.15],
            [0.1, 0.05, 0.0, 0.08],
            [0.0, 0.0, 0.0, 0.0]
        ]),
        R=np.array([100.0, 150.0, 200.0, 50.0]),
        uevs=np.array([3.49e4, 6.8e4, 3.1e5, 1.0e6]),
        types=["Renovável", "Renovável", "Renovável", "Produto"]
    )
    
    # Calcula e exporta
    manager.calculate_and_export(
        "Análise Agricultura Regenerativa",
        output_dir=r"c:\Users\vitor\OneDrive\Documentos\Facul_Projetos\Emergia - Backup"
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "example":
        print("Executando exemplo de uso...")
        example_usage()
    else:
        # Executa interface interativa
        cli = InteractiveCLI()
        cli.run()
