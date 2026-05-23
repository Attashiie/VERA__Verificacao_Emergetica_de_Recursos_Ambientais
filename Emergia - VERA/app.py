"""
VERA — API Flask para conectar HTML com Python
Servidor que recebe cálculos do HTML e retorna resultados
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import json
from datetime import datetime

from vera_calculator import ProjectConfig, EmergyCalculator, ResultsFormatter
from vera_project_manager import ProjectManager
from uev_database import UEVDatabase


app = Flask(__name__)
CORS(app)  # Permite requisições do HTML

# Instâncias globais
manager = ProjectManager()
uev_db = UEVDatabase()


@app.route('/')
def index():
    """Rota raiz"""
    return jsonify({
        "nome": "VERA API",
        "versao": "1.0",
        "status": "rodando",
        "endpoints": {
            "POST /api/calcular": "Calcula emergia",
            "GET /api/uevs": "Retorna banco de UEVs",
            "POST /api/salvar": "Salva projeto",
            "GET /api/projetos": "Lista projetos salvos",
            "GET /api/projeto/<nome>": "Carrega projeto"
        }
    })


@app.route('/api/calcular', methods=['POST'])
def calcular():
    """
    Calcula emergia baseado em dados do projeto
    
    Esperado JSON:
    {
        "name": "Meu Projeto",
        "n": 3,
        "process_names": ["A", "B", "C"],
        "A": [[0, 0.1, 0], [0.2, 0, 0.1], [0, 0.3, 0]],
        "R": [100, 50, 30],
        "uevs": [1e5, 1.5e5, 2e5],
        "types": ["Renovável", "Não-Renovável", "Produto"]
    }
    """
    try:
        data = request.json
        
        # Validação básica
        if not all(k in data for k in ['name', 'n', 'A', 'R', 'uevs', 'types', 'process_names']):
            return jsonify({"erro": "Faltam campos obrigatórios"}), 400
        
        # Converte para numpy arrays
        A = np.array(data['A'])
        R = np.array(data['R'])
        uevs = np.array(data['uevs'])
        
        # Cria projeto
        project = ProjectConfig(
            name=data['name'],
            n=data['n'],
            process_names=data['process_names'],
            A=A,
            R=R,
            uevs=uevs,
            types=data['types']
        )
        
        # Calcula
        calculator = EmergyCalculator(project)
        results = calculator.calculate()
        
        # Prepara resposta
        response = {
            "sucesso": True,
            "projeto": data['name'],
            "data_calculo": datetime.now().isoformat(),
            "indicadores": {
                "emergia_total": float(results.total_emergia),
                "emergia_renovavel": float(results.renewable_emergia),
                "emergia_nao_renovavel": float(results.non_renewable_emergia),
                "EYR": float(results.EYR),
                "ELR": float(results.ELR),
                "ESI": float(results.ESI),
                "EDE": float(results.EDE)
            },
            "processos": [
                {
                    "nome": project.process_names[i],
                    "tipo": project.types[i],
                    "E_fisico": float(results.E_phys[i]),
                    "E_solar": float(results.E_solar[i]),
                    "UEV": float(project.uevs[i]),
                    "percentual": float(abs(results.E_solar[i]) / results.total_emergia * 100) if results.total_emergia > 0 else 0
                }
                for i in range(project.n)
            ],
            "mensagem_sucesso": f"Cálculo concluído — Emergia total: {ResultsFormatter.format_scientific(results.total_emergia)} sej"
        }
        
        # Salva projeto em memória
        manager.projects[data['name']] = project
        
        return jsonify(response), 200
    
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": f"Erro no servidor: {str(e)}"}), 500


@app.route('/api/uevs', methods=['GET'])
def get_uevs():
    """Retorna banco de dados de UEVs"""
    try:
        # Agrupa por categoria
        grouped = {}
        for record in uev_db.data:
            cat = record['category']
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append({
                "resource": record['resource'],
                "uev": record['uev'],
                "unit": record['unit'],
                "source": record['source']
            })
        
        return jsonify({
            "sucesso": True,
            "total": len(uev_db.data),
            "categorias": grouped
        }), 200
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/uevs/buscar', methods=['POST'])
def buscar_uev():
    """Busca UEV de um recurso específico"""
    try:
        data = request.json
        recurso = data.get('recurso', '')
        
        uev = uev_db.get_uev(recurso)
        
        if uev:
            return jsonify({
                "sucesso": True,
                "recurso": recurso,
                "uev": float(uev)
            }), 200
        else:
            # Tenta busca parcial
            resultados = uev_db.search_by_name(recurso)
            if resultados:
                return jsonify({
                    "sucesso": True,
                    "mensagem": "Busca parcial",
                    "resultados": [
                        {"recurso": r['resource'], "uev": r['uev'], "unit": r['unit']}
                        for r in resultados
                    ]
                }), 200
            else:
                return jsonify({
                    "sucesso": False,
                    "erro": f"UEV não encontrado para '{recurso}'"
                }), 404
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/salvar', methods=['POST'])
def salvar_projeto():
    """Salva projeto em arquivo JSON"""
    try:
        data = request.json
        nome_arquivo = data.get('nome_arquivo', 'projeto.json')
        
        if not data.get('name'):
            return jsonify({"erro": "Nome do projeto obrigatório"}), 400
        
        # Converte para numpy arrays
        A = np.array(data['A'])
        R = np.array(data['R'])
        uevs = np.array(data['uevs'])
        
        project = ProjectConfig(
            name=data['name'],
            n=data['n'],
            process_names=data['process_names'],
            A=A,
            R=R,
            uevs=uevs,
            types=data['types']
        )
        
        # Salva
        filepath = f"projetos_{nome_arquivo}"
        manager.save_project_to_json(project, filepath)
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"Projeto '{data['name']}' salvo em {filepath}"
        }), 200
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/projetos', methods=['GET'])
def listar_projetos():
    """Lista todos os projetos salvos em memória"""
    try:
        projetos = []
        for nome, proj in manager.projects.items():
            projetos.append({
                "nome": nome,
                "n_processos": proj.n,
                "processos": proj.process_names
            })
        
        return jsonify({
            "sucesso": True,
            "total": len(projetos),
            "projetos": projetos
        }), 200
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/projeto/<nome>', methods=['GET'])
def carregar_projeto(nome):
    """Carrega um projeto específico"""
    try:
        projeto = manager.get_project(nome)
        
        if projeto:
            return jsonify({
                "sucesso": True,
                "name": projeto.name,
                "n": projeto.n,
                "process_names": projeto.process_names,
                "A": projeto.A.tolist(),
                "R": projeto.R.tolist(),
                "uevs": projeto.uevs.tolist(),
                "types": projeto.types
            }), 200
        else:
            return jsonify({"erro": f"Projeto '{nome}' não encontrado"}), 404
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/validar-matriz', methods=['POST'])
def validar_matriz():
    """Valida se a matriz está em formato correto"""
    try:
        data = request.json
        
        A = np.array(data.get('A', []))
        n = data.get('n', 0)
        
        errors = []
        
        # Verifica dimensões
        if A.shape != (n, n):
            errors.append(f"Matriz A deve ser {n}×{n}, mas é {A.shape[0]}×{A.shape[1]}")
        
        # Verifica diagonal
        for i in range(n):
            if A[i, i] >= 1:
                errors.append(f"Erro: A[{i}][{i}] = {A[i, i]} >= 1 (não pode consumir 100% de si)")
        
        # Verifica valores
        if np.any(A < 0):
            errors.append("Erro: Matriz contém valores negativos")
        
        if errors:
            return jsonify({
                "valido": False,
                "erros": errors
            }), 400
        else:
            return jsonify({
                "valido": True,
                "mensagem": "Matriz está válida"
            }), 200
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Status da API"""
    return jsonify({
        "status": "online",
        "versao": "1.0",
        "projetos_em_memoria": len(manager.projects),
        "uvs_disponibles": len(uev_db.data),
        "timestamp": datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def nao_encontrado(e):
    """Erro 404"""
    return jsonify({"erro": "Endpoint não encontrado"}), 404


@app.errorhandler(500)
def erro_servidor(e):
    """Erro 500"""
    return jsonify({"erro": "Erro interno do servidor"}), 500


if __name__ == '__main__':
    print("""
    ================================================================================
    VERA API — Servidor Flask iniciado
    ================================================================================
    
    Acesse em: http://localhost:5000
    
    Endpoints disponíveis:
    - GET  /                      Status da API
    - GET  /api/status            Status detalhado
    - POST /api/calcular          Calcula emergia
    - GET  /api/uevs              Lista todas as UEVs
    - POST /api/uevs/buscar       Busca UEV específica
    - POST /api/salvar            Salva projeto
    - GET  /api/projetos          Lista projetos em memória
    - GET  /api/projeto/<nome>    Carrega projeto específico
    - POST /api/validar-matriz    Valida matriz A
    
    Para parar: Ctrl+C
    ================================================================================
    """)
    
    # Modo debug ativado para desenvolvimento
    app.run(debug=True, host='0.0.0.0', port=5000)
