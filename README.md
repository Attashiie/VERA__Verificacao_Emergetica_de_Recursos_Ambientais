<div align="center">

# 🌿 VERA
### Verificação Emergética de Recursos Ambientais

**Simulador de cálculos emergéticos baseado em Inventários do Ciclo de Vida (LCI)**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![HTML5](https://img.shields.io/badge/HTML5-standalone-E34F26?style=flat-square&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![License](https://img.shields.io/badge/Licença-Acadêmica-green?style=flat-square)](LICENSE)

---

> Projeto acadêmico desenvolvido para a disciplina de **Engenharia de Software** — UNIP (Universidade Paulista).  
> Inspirado na arquitetura do software **SCALE** *(Software for CALculating Emergy based on Life Cycle Inventories)*.

</div>

---

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [Instalação e Execução](#-instalação-e-execução)
- [Como Usar](#-como-usar)
- [Base Matemática](#-base-matemática)
- [Banco de UEVs](#-banco-de-uevs)
- [API REST — Endpoints](#-api-rest--endpoints)
- [Tecnologias](#-tecnologias)
- [Referências Científicas](#-referências-científicas)

---

## 🌱 Sobre o Projeto

O **VERA** é um simulador computacional voltado à **análise emergética** de sistemas produtivos e ecológicos. Baseado no modelo matemático de Odum (1996), o sistema resolve o sistema linear:

$$E = (I - A)^{-1} \cdot R$$

onde a emergia de cada processo é calculada a partir de dados de Inventário do Ciclo de Vida (LCI), convertendo fluxos heterogêneos de matéria, energia e serviços em uma unidade comum — o **solar emjoule (sej)**.

O projeto foi desenvolvido com ênfase na aplicação prática de conceitos de Engenharia de Software: arquitetura em camadas, padrões de projeto (Strategy, Repository, Facade, DTO), rastreabilidade de requisitos e qualidade conforme **ISO/IEC 25010**.

---

## ✨ Funcionalidades

| Funcionalidade | Front-end (HTML) | Back-end (Python/Flask) |
|---|:---:|:---:|
| Criação e gerenciamento de projetos LCI | ✅ | ✅ |
| Editor interativo da Matriz A e Vetor R | ✅ | — |
| Cálculo emergético (Gauss-Jordan) | ✅ | ✅ |
| Indicadores EYR, ELR, ESI, EDE | ✅ | ✅ |
| Gráficos interativos (Chart.js) | ✅ | — |
| Banco de UEVs (28 recursos, Odum 1996) | ✅ | ✅ |
| Importação de dados via CSV | ✅ | — |
| Exportação de resultados (CSV / JSON) | — | ✅ |
| Salvamento local de projetos | ✅ | — |
| API REST para integração externa | — | ✅ |
| Tutorial interativo passo a passo | ✅ | — |
| Modo offline (sem servidor) | ✅ | — |

---

## 🏗 Arquitetura

O sistema adota uma **arquitetura em três camadas** com comunicação via API REST:

```
┌─────────────────────────────────────────────┐
│           CAMADA DE APRESENTAÇÃO            │
│   HTML5 + CSS3 + JavaScript (ES6)           │
│   Chart.js · Sora Font · JetBrains Mono     │
│   VERA___Verificação_Emergética.html        │
│   vera-api-client.js                        │
└───────────────────┬─────────────────────────┘
                    │  HTTP/JSON (REST)
                    │  (modo offline: cálculo local)
┌───────────────────▼─────────────────────────┐
│            CAMADA DE INTEGRAÇÃO             │
│   Flask REST API · Flask-CORS               │
│   app.py                                    │
└───────────────────┬─────────────────────────┘
                    │
┌───────────────────▼─────────────────────────┐
│          CAMADA DE NEGÓCIO / DADOS          │
│   vera_calculator.py   → álgebra emergética │
│   vera_project_manager.py → CRUD projetos   │
│   uev_database.py      → banco de UEVs     │
└─────────────────────────────────────────────┘
```

**Padrões de projeto aplicados:**

- **Strategy** — `EmergyCalculator` encapsula o algoritmo de inversão matricial de forma intercambiável
- **Repository** — `UEVDatabase` abstrai o acesso ao banco de transformidades
- **DTO** — `ProjectConfig` e `CalculationResults` transferem dados entre camadas sem acoplamento
- **Facade** — `app.py` centraliza e simplifica o acesso ao back-end pelo cliente JS

---

## 📁 Estrutura de Arquivos

```
VERA/
│
├── 📄 VERA___Verificação_Emergética_de_Recursos_Ambientais.html
│       Interface principal — funciona standalone sem servidor
│
├── 🐍 app.py
│       Servidor Flask — API REST com 9 endpoints
│
├── 🐍 vera_calculator.py
│       Núcleo matemático — classes ProjectConfig, EmergyCalculator,
│       MatrixOperations, CalculationResults, ResultsFormatter
│
├── 🐍 vera_project_manager.py
│       Gerenciamento de projetos — CRUD, importação/exportação JSON e CSV
│       CLI interativa (InteractiveCLI)
│
├── 🐍 uev_database.py
│       Banco de dados de transformidades (UEVs) — 28 recursos
│       baseados em Odum (1996), com busca por nome e categoria
│
├── 📜 vera-api-client.js
│       Cliente JS para comunicação com a API Flask
│       Gerencia fallback automático para modo offline
│
└── 📖 README.md
```

---

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.8+
- pip

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/vera.git
cd vera
```

### 2. Instale as dependências Python

```bash
pip install flask flask-cors numpy
```

### 3. Inicie o servidor Flask

```bash
python app.py
```

O servidor sobe em `http://localhost:5000`.

### 4. Abra a interface

Abra o arquivo `VERA___Verificação_Emergética_de_Recursos_Ambientais.html` no navegador.

> **Modo offline:** A interface funciona sem o servidor Flask. Nesse caso, os cálculos são executados diretamente em JavaScript no navegador, com as mesmas fórmulas do back-end Python.

---

### Uso via linha de comando (CLI)

```bash
# Interface interativa
python vera_project_manager.py

# Executar exemplo de demonstração
python vera_project_manager.py example

# Executar cálculo isolado
python vera_calculator.py
```

---

## 📖 Como Usar

### Fluxo básico na interface web

```
1. Abrir o HTML no navegador
        ↓
2. Dashboard → "Novo Projeto" ou "Carregar Demonstração"
        ↓
3. Editor LCI
   • Definir número de processos (n)
   • Preencher a Matriz A (coeficientes tecnológicos)
   • Preencher o Vetor R (entradas externas)
   • Definir UEVs e tipos (Renovável / Não-Renovável / Produto)
        ↓
4. Clicar em "▶ Calcular Emergia"
        ↓
5. Resultados
   • Indicadores EYR, ELR, ESI, EDE com interpretação automática
   • Gráficos de emergia por processo
   • Rede de fluxos visual
   • Exportar CSV
```

### Importação via CSV

No painel do Editor LCI, cole dados no formato:

```
a11,a12,...,a1n,R1
a21,a22,...,a2n,R2
...
an1,an2,...,ann,Rn
```

---

## 📐 Base Matemática

### Modelo matricial de Odum (1996)

O VERA implementa a álgebra emergética baseada no modelo insumo-produto de Leontief, adaptado por Odum para sistemas ecológicos:

$$E = (I - A)^{-1} \cdot R$$

| Símbolo | Descrição | Dimensão |
|---|---|---|
| `E` | Vetor de emergia física por processo | n × 1 |
| `I` | Matriz identidade | n × n |
| `A` | Matriz de tecnologia (coeficientes de consumo) | n × n |
| `R` | Vetor de entradas externas de recursos | n × 1 |

A inversão de `(I − A)` é realizada via **eliminação de Gauss-Jordan com pivotamento parcial**, implementada em `MatrixOperations.invert_matrix()`.

A emergia solar de cada processo é então:

$$E_{\text{solar},i} = E_i \times \text{UEV}_i \quad [\text{sej}]$$

### Indicadores de sustentabilidade

| Índice | Fórmula | Interpretação |
|---|---|---|
| **EYR** | `Y / F` | > 1.2 → sistema produtivo |
| **ELR** | `(N + F) / R` | < 3 → carga ambiental aceitável |
| **ESI** | `EYR / ELR` | > 1 → sistema sustentável |
| **EDE** | `E_total / n` | Intensidade emergética média |

---

## 🗄 Banco de UEVs

O sistema inclui **28 transformidades** organizadas em 4 categorias, baseadas em Odum (1996):

| Categoria | Exemplos | Unidade |
|---|---|---|
| **Renovável** | Luz solar (1,00), Vento (1,50×10³), Chuva geopotencial (2,79×10⁴) | sej/J |
| **Não-Renovável** | Petróleo (5,40×10⁴), Gás natural (4,80×10⁴), Carvão (3,98×10⁴) | sej/J |
| **Importado** | Eletricidade (1,60×10⁵), Aço (1,13×10⁹), Cimento (3,05×10⁸) | sej/J ou sej/g |
| **Serviço** | Trabalho humano (2,50×10⁶) | sej/J metabólico |

Valores regionalizados para o Brasil também estão incluídos (matriz hidrotérmica, bacias úmidas).

---

## 🔌 API REST — Endpoints

Base URL: `http://localhost:5000`

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/` | Status e lista de endpoints |
| `GET` | `/api/status` | Status detalhado da API |
| `POST` | `/api/calcular` | **Calcula emergia** (payload JSON) |
| `GET` | `/api/uevs` | Lista todas as UEVs por categoria |
| `POST` | `/api/uevs/buscar` | Busca UEV por nome de recurso |
| `POST` | `/api/salvar` | Salva projeto em arquivo JSON |
| `GET` | `/api/projetos` | Lista projetos em memória |
| `GET` | `/api/projeto/<nome>` | Carrega projeto pelo nome |
| `POST` | `/api/validar-matriz` | Valida matriz A (dimensões, diagonal, negativos) |

### Exemplo — POST `/api/calcular`

```json
{
  "name": "Meu Projeto",
  "n": 3,
  "process_names": ["Solar", "Biomassa", "Produto"],
  "A": [[0, 0.1, 0], [0.2, 0, 0.1], [0, 0.3, 0]],
  "R": [5000, 200, 80],
  "uevs": [1.0, 3.49e4, 5.4e4],
  "types": ["Renovável", "Renovável", "Produto"]
}
```

---

## 🛠 Tecnologias

| Camada | Tecnologia | Finalidade |
|---|---|---|
| Front-end | HTML5, CSS3, JavaScript ES6 | Interface e cálculo offline |
| Visualização | Chart.js 4.4.1 | Gráficos interativos |
| Tipografia | Sora, JetBrains Mono | Interface |
| Back-end | Python 3.8+ | Lógica e cálculo |
| Álgebra linear | NumPy | Arrays e matrizes |
| API | Flask + Flask-CORS | REST API |
| Serialização | JSON | Persistência e comunicação |

---

## 📚 Referências Científicas

- **ODUM, H. T.** *Systems Ecology: An Introduction.* New York: Wiley-Interscience, 1983.
- **ODUM, H. T.** *Environmental Accounting: Emergy and Environmental Decision Making.* New York: John Wiley & Sons, 1996.
- **BROWN, M. T.; ULGIATI, S.** Emergy-based indices and ratios to evaluate sustainability. *Ecological Engineering,* v. 9, p. 51–69, 1997.
- **REEH, D. et al.** SCALE: A software framework for calculating emergy based on life cycle inventory data. *Resources, Conservation and Recycling,* v. 168, p. 105307, 2021.
- **GAMMA, E. et al.** *Design Patterns: Elements of Reusable Object-Oriented Software.* Reading: Addison-Wesley, 1994.
- **ISO/IEC 25010:2011** — Systems and Software Quality Requirements and Evaluation (SQuaRE).
- **ABNT NBR ISO 14044:2009** — Avaliação do ciclo de vida — Requisitos e orientações.

---

<div align="center">

Desenvolvido como projeto acadêmico — Engenharia de Software · UNIP

</div>
