"""
VERA — Verificação Emergética de Recursos Ambientais
Sistema de cálculo de emergia baseado em Inventários do Ciclo de Vida (LCI)

Implementa o modelo de Odum (1996) para análise emergética:
E = (I − A)⁻¹ · R

Onde:
- E: Vetor de emergia (sej)
- I: Matriz identidade
- A: Matriz de tecnologia (coeficientes de consumo entre processos)
- R: Vetor de entradas de recursos externos
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
import json
import csv
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProjectConfig:
    """Configuração de um projeto de análise emergética"""
    name: str
    n: int  # Número de processos
    process_names: List[str]
    A: np.ndarray  # Matriz de tecnologia (n×n)
    R: np.ndarray  # Vetor de recursos (n×1)
    uevs: np.ndarray  # Transformidades/UEVs (n×1)
    types: List[str]  # Tipo de cada processo: 'Renovável', 'Não-Renovável', 'Produto', etc.


@dataclass
class CalculationResults:
    """Resultados do cálculo de emergia"""
    E_phys: np.ndarray  # Vetor de emergia física (fluxos resolvidos)
    E_solar: np.ndarray  # Vetor de emergia solar (com UEVs aplicadas)
    total_emergia: float  # Emergia total do sistema
    renewable_emergia: float  # Emergia renovável
    non_renewable_emergia: float  # Emergia não-renovável
    EYR: float  # Emergy Yield Ratio (rendimento emergético)
    ELR: float  # Environmental Loading Ratio (carga ambiental)
    ESI: float  # Emergy Sustainability Index (índice de sustentabilidade)
    EDE: float  # Emergy Density (densidade emergética)
    inv_matrix: np.ndarray  # Matriz inversa de (I-A)
    project_config: ProjectConfig  # Configuração do projeto


class MatrixOperations:
    """Operações matriciais básicas para cálculos de emergia"""
    
    @staticmethod
    def identity_matrix(n: int) -> np.ndarray:
        """Cria uma matriz identidade n×n"""
        return np.eye(n)
    
    @staticmethod
    def subtract_matrices(A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Subtrai matriz B de A"""
        return A - B
    
    @staticmethod
    def matrix_vector_multiply(M: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Multiplica matriz M por vetor v"""
        return M @ v
    
    @staticmethod
    def invert_matrix(M: np.ndarray) -> Optional[np.ndarray]:
        """
        Inverte uma matriz usando eliminação de Gauss-Jordan
        Retorna None se a matriz é singular
        """
        try:
            # Usa o método de Gauss-Jordan com pivotamento parcial
            n = M.shape[0]
            # Cria matriz aumentada [M | I]
            aug = np.hstack([M.copy(), np.eye(n)])
            
            # Eliminação progressiva
            for col in range(n):
                # Encontra pivô
                max_row = col + np.argmax(np.abs(aug[col:, col]))
                if np.abs(aug[max_row, col]) < 1e-12:
                    return None  # Matriz singular
                
                # Troca linhas
                aug[[col, max_row]] = aug[[max_row, col]]
                
                # Normaliza linha
                piv = aug[col, col]
                aug[col] = aug[col] / piv
                
                # Eliminação nas outras linhas
                for r in range(n):
                    if r != col:
                        f = aug[r, col]
                        aug[r] = aug[r] - f * aug[col]
            
            # Retorna a parte direita (inversa)
            return aug[:, n:]
        
        except (np.linalg.LinAlgError, ValueError):
            return None


class EmergyCalculator:
    """Calculador principal de emergia"""
    
    def __init__(self, project: ProjectConfig):
        """Inicializa o calculador com configuração de projeto"""
        self.project = project
        self.results: Optional[CalculationResults] = None
    
    def calculate(self) -> CalculationResults:
        """
        Calcula a emergia do sistema resolvendo E = (I − A)⁻¹ · R
        
        Retorna:
            CalculationResults: Objeto com todos os resultados do cálculo
        
        Lança:
            ValueError: Se a matriz (I-A) for singular
        """
        n = self.project.n
        A = self.project.A
        R = self.project.R.reshape(-1, 1)  # Garante coluna
        
        # Calcula (I - A)
        I = MatrixOperations.identity_matrix(n)
        I_minus_A = MatrixOperations.subtract_matrices(I, A)
        
        # Inverte (I - A)
        inv_matrix = MatrixOperations.invert_matrix(I_minus_A)
        if inv_matrix is None:
            raise ValueError(
                "Erro: Matriz (I−A) é singular e não pode ser invertida. "
                "Verifique se há ciclos inválidos (A[i][i]≥1)."
            )
        
        # Calcula E_phys = (I - A)^(-1) * R
        E_phys = MatrixOperations.matrix_vector_multiply(inv_matrix, R.flatten())
        
        # Aplica UEVs: E_solar = E_phys * UEVs
        E_solar = E_phys * self.project.uevs
        
        # Calcula emergia total
        total_emergia = np.sum(np.abs(E_solar))
        
        # Separa emergia renovável e não-renovável
        renewable_emergia = sum(
            abs(E_solar[i]) 
            for i in range(n) 
            if self.project.types[i] == 'Renovável'
        )
        non_renewable_emergia = sum(
            abs(E_solar[i]) 
            for i in range(n) 
            if self.project.types[i] == 'Não-Renovável'
        )
        
        # Calcula indicadores
        # EYR: Rendimento Emergético (Total / Produto)
        prod_idx = None
        for i in range(n):
            if self.project.types[i] == 'Produto':
                prod_idx = i
                break
        
        yield_emergia = abs(E_solar[prod_idx]) if prod_idx is not None else total_emergia
        EYR = total_emergia / yield_emergia if yield_emergia > 0 else 0
        
        # ELR: Carga Ambiental (Não-renovável / Renovável)
        ELR = (non_renewable_emergia / renewable_emergia 
               if renewable_emergia > 0 else 0)
        
        # ESI: Índice de Sustentabilidade (EYR / ELR)
        ESI = EYR / ELR if ELR > 0 else 0
        
        # EDE: Densidade Emergética (Total / n)
        EDE = total_emergia / n if n > 0 else 0
        
        # Armazena e retorna resultados
        self.results = CalculationResults(
            E_phys=E_phys,
            E_solar=E_solar,
            total_emergia=total_emergia,
            renewable_emergia=renewable_emergia,
            non_renewable_emergia=non_renewable_emergia,
            EYR=EYR,
            ELR=ELR,
            ESI=ESI,
            EDE=EDE,
            inv_matrix=inv_matrix,
            project_config=self.project
        )
        
        return self.results


class ResultsFormatter:
    """Formatação e apresentação de resultados"""
    
    @staticmethod
    def format_scientific(value: float, decimals: int = 2) -> str:
        """Formata número em notação científica"""
        if value == 0:
            return "0"
        return f"{value:.{decimals}e}"
    
    @staticmethod
    def format_decimal(value: float, decimals: int = 2) -> str:
        """Formata número com casas decimais"""
        if not np.isfinite(value):
            return "—"
        return f"{value:.{decimals}f}"
    
    @staticmethod
    def print_results(results: CalculationResults) -> None:
        """Imprime resultados de forma legível"""
        r = results
        config = r.project_config
        
        print("\n" + "="*70)
        print(f"VERA — Verificação Emergética de Recursos Ambientais")
        print(f"Projeto: {config.name}")
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("="*70)
        
        print(f"\n{'ENTRADA DE DADOS':^70}")
        print("-"*70)
        print(f"{'Processo':<20} {'Tipo':<20} {'R[i]':>15}")
        for i in range(config.n):
            print(f"{config.process_names[i]:<20} {config.types[i]:<20} {r.E_phys[i]:>15.6e}")
        
        print(f"\n{'INDICADORES EMERGÉTICOS':^70}")
        print("-"*70)
        print(f"Emergia Total:              {ResultsFormatter.format_scientific(r.total_emergia)} sej")
        print(f"Emergia Renovável:          {ResultsFormatter.format_scientific(r.renewable_emergia)} sej")
        print(f"Emergia Não-Renovável:      {ResultsFormatter.format_scientific(r.non_renewable_emergia)} sej")
        
        print(f"\n{'ÍNDICES DE SUSTENTABILIDADE':^70}")
        print("-"*70)
        print(f"EYR (Rendimento Emergético): {ResultsFormatter.format_decimal(r.EYR)}")
        if r.EYR > 1.2:
            print("     [OK] Sistema produtivo (EYR > 1.2)")
        else:
            print("     [AVISO] Rendimento baixo (EYR <= 1.2)")
        
        print(f"ELR (Carga Ambiental):      {ResultsFormatter.format_decimal(r.ELR)}")
        if r.ELR < 3:
            print("     [OK] Carga aceitável (ELR < 3)")
        else:
            print("     [AVISO] Alta pressão ambiental (ELR >= 3)")
        
        print(f"ESI (Sustentabilidade):     {ResultsFormatter.format_decimal(r.ESI)}")
        if r.ESI > 1:
            print("     [OK] Sistema sustentável (ESI > 1)")
        else:
            print("     [AVISO] Baixa sustentabilidade (ESI <= 1)")
        
        print(f"EDE (Densidade Emergética): {ResultsFormatter.format_decimal(r.EDE, 6)} sej")
        
        print(f"\n{'EMERGIA POR PROCESSO':^70}")
        print("-"*70)
        print(f"{'Processo':<20} {'E_phys (J)':>18} {'UEV':>15} {'E_solar (sej)':>18} {'% Total':>8}")
        for i in range(config.n):
            pct = (abs(r.E_solar[i]) / r.total_emergia * 100) if r.total_emergia > 0 else 0
            print(f"{config.process_names[i]:<20} {r.E_phys[i]:>18.6e} {config.uevs[i]:>15.6e} {r.E_solar[i]:>18.6e} {pct:>7.1f}%")
        
        print("\n" + "="*70)
    
    @staticmethod
    def export_csv(results: CalculationResults, filepath: str) -> None:
        """Exporta resultados para arquivo CSV"""
        r = results
        config = r.project_config
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Cabeçalho
            writer.writerow(['Processo', 'Tipo', 'R_entrada', 'E_fisico', 'UEV', 'Emergia_sej', 'Perc_Total'])
            
            # Dados
            for i in range(config.n):
                pct = (abs(r.E_solar[i]) / r.total_emergia * 100) if r.total_emergia > 0 else 0
                writer.writerow([
                    config.process_names[i],
                    config.types[i],
                    r.E_phys[i],
                    r.E_solar[i],
                    config.uevs[i],
                    r.E_solar[i],
                    f"{pct:.1f}%"
                ])
            
            # Resumo
            writer.writerow([])
            writer.writerow(['Emergia Total', '', '', '', '', r.total_emergia, ''])
            writer.writerow(['EYR', '', '', '', '', r.EYR, ''])
            writer.writerow(['ELR', '', '', '', '', r.ELR, ''])
            writer.writerow(['ESI', '', '', '', '', r.ESI, ''])
            writer.writerow(['EDE', '', '', '', '', r.EDE, ''])
    
    @staticmethod
    def export_json(results: CalculationResults, filepath: str) -> None:
        """Exporta resultados para arquivo JSON"""
        r = results
        config = r.project_config
        
        data = {
            "projeto": {
                "nome": config.name,
                "num_processos": config.n,
                "data_calculo": datetime.now().isoformat()
            },
            "processos": [
                {
                    "nome": config.process_names[i],
                    "tipo": config.types[i],
                    "E_fisico": float(r.E_phys[i]),
                    "E_solar": float(r.E_solar[i]),
                    "UEV": float(config.uevs[i]),
                    "percentual": float(abs(r.E_solar[i]) / r.total_emergia * 100) if r.total_emergia > 0 else 0
                }
                for i in range(config.n)
            ],
            "indicadores": {
                "emergia_total": float(r.total_emergia),
                "emergia_renovavel": float(r.renewable_emergia),
                "emergia_nao_renovavel": float(r.non_renewable_emergia),
                "EYR": float(r.EYR),
                "ELR": float(r.ELR),
                "ESI": float(r.ESI),
                "EDE": float(r.EDE)
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================
# EXEMPLO DE USO
# ============================================================
def create_demo_project() -> ProjectConfig:
    """Cria um projeto de demonstração"""
    return ProjectConfig(
        name="Projeto Demonstração",
        n=3,
        process_names=["Processo A", "Processo B", "Produto C"],
        A=np.array([
            [0.0, 0.1, 0.0],
            [0.2, 0.0, 0.1],
            [0.0, 0.3, 0.0]
        ]),
        R=np.array([10.0, 15.0, 5.0]),
        uevs=np.array([1.0e5, 1.5e5, 2.0e5]),
        types=["Renovável", "Não-Renovável", "Produto"]
    )


def main():
    """Executa exemplo de cálculo"""
    # Cria projeto
    project = create_demo_project()
    
    # Cria calculador
    calculator = EmergyCalculator(project)
    
    # Executa cálculo
    try:
        results = calculator.calculate()
        
        # Imprime resultados
        ResultsFormatter.print_results(results)
        
        # Exporta resultados
        csv_path = r"c:\Users\vitor\OneDrive\Documentos\Facul_Projetos\Emergia - Backup\resultado_emergia.csv"
        json_path = r"c:\Users\vitor\OneDrive\Documentos\Facul_Projetos\Emergia - Backup\resultado_emergia.json"
        
        ResultsFormatter.export_csv(results, csv_path)
        ResultsFormatter.export_json(results, json_path)
        
        print(f"\n[OK] Resultados exportados:")
        print(f"  - CSV: {csv_path}")
        print(f"  - JSON: {json_path}")
        
    except ValueError as e:
        print(f"Erro no cálculo: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
