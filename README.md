# 🔥 CBMAM · Dashboard TAF 2026

**Dashboard interativo de Análise do Teste de Aptidão Física (TAF)**  
Corpo de Bombeiros Militar do Amazonas · BM-6/EMG · 2026

🌐 **Deploy:** [tafcbmam.streamlit.app](https://tafcbmam.streamlit.app)

---

## 📋 Sobre o Projeto

Aplicação web desenvolvida em Streamlit para análise completa dos dados do TAF do CBMAM, edição 2026. O sistema processa dados de desempenho físico de **336 militares** em cinco disciplinas, oferecendo:

- Visualizações interativas com Plotly
- Rankings individuais e por posto/quadro
- Comparativos estatísticos por categoria
- Análise separada do TAF Adaptado
- Modos visual **Claro** e **Escuro** com CSS profissional

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.10+
- pip

### Instalação

```bash
# Clone o repositório
git clone https://github.com/AllanCardosoDev/TAFCBMAM.git
cd TAFCBMAM

# Instalar dependências
pip install -r requirements.txt

# Executar o dashboard
streamlit run taf.py
```

Acesse: `http://localhost:8501`

---

## 📊 Funcionalidades

### Páginas do Dashboard

| Página | Descrição |
|--------|-----------|
| 🏠 **Visão Geral** | KPIs gerais, ranking top/bottom, radar comparativo, mapa de calor, insights automáticos |
| 🪖 **Por Posto/Graduação** | Comparativo por posto, box plots, stacked bars, radar, taxa de ausência |
| 📋 **Por Quadro** | Análise por quadro funcional (QCOBM, QCPBM, QPBM, etc.) |
| 👤 **Ficha Individual** | Perfil detalhado de cada militar: gauge de média, ranking, pontos fortes/fracos |
| 📈 **Estatísticas** | Box plots, distribuições, correlações, percentis, top/bottom 10 por disciplina |
| ♿ **TAF Adaptado** | Militares na modalidade adaptada com análise própria |
| 📖 **Regras de Pontuação** | Tabelas completas de pontuação por disciplina, sexo e faixa etária |

### Filtros Globais (Sidebar)
- **Posto/Graduação**: MAJOR, CAP, 1° TEN, 2° TEN, ASP OF, ST, 1° SGT, 2° SGT, 3° SGT, CB, SD
- **Quadro**: QCOBM, QCPBM, QPBM, QOABM, QPEBM
- **Incluir ausentes**: Toggle para mostrar/ocultar militares sem avaliação
- **Tema**: Modo Escuro / Claro

---

## 📁 Estrutura do Projeto

```
TAFCBMAM/
├── taf.py                                        # App Streamlit principal (~2800 linhas)
├── TAF.csv                                       # Dados brutos do TAF
├── militaresALL.csv                              # Cadastro completo de militares (336)
├── logo.png                                      # Logo CBMAM
├── cbmam.html                                    # Arquivo auxiliar
├── requirements.txt                              # Dependências Python (versionadas)
├── README.md                                     # Documentação
└── data/
    ├── master_consolidado_100_completo_FINAL.csv # Dados consolidados com notas
    ├── master_consolidado_TODOS_militares.csv    # Todos os militares (inclui ausentes)
    └── master_taf_consolidado.csv                # TAF processado
```

---

## 📐 Sistema de Pontuação

As notas (0–10) são calculadas a partir dos valores brutos de desempenho físico:

### Masculino

| Disciplina | Métrica | Nota 10 | Nota 8 | Nota 6 |
|------------|---------|---------|--------|--------|
| Corrida 12min | Metros (↑ melhor) | ≥ 2800m | ≥ 2400m | ≥ 2000m |
| Abdominal | Repetições (↑ melhor) | ≥ 48 | ≥ 38 | ≥ 28 |
| Flexão | Repetições (↑ melhor) | ≥ 38 | ≥ 28 | ≥ 18 |
| Natação 50m | Segundos (↓ melhor) | ≤ 35s | ≤ 45s | ≤ 55s |
| Barra Dinâmica | Repetições (↑ melhor) | ≥ 14 | ≥ 10 | ≥ 6 |
| Barra Estática | Segundos (↑ melhor) | ≥ 70s | ≥ 50s | ≥ 30s |

### Classificação Final

| Classificação | Média Final |
|---------------|-------------|
| 🟢 Excelente | ≥ 9,0 |
| 🔵 Bom | ≥ 7,5 |
| 🟡 Regular | ≥ 6,0 |
| 🔴 Insuficiente | < 6,0 |

---

## 🛠️ Tecnologias

| Biblioteca | Versão | Uso |
|-----------|--------|-----|
| Streamlit | 1.39.0 | Interface web |
| Plotly | 5.24.0 | Gráficos interativos |
| Pandas | 2.2.3 | Processamento de dados |
| NumPy | 2.1.3 | Cálculos numéricos |
| Matplotlib | 3.9.2 | Gráficos auxiliares |
| Statsmodels | 0.14.2 | Análises estatísticas |
| OpenPyXL | 3.12.0 | Leitura de Excel |

---

## 📊 Dados

- **Efetivo total**: 336 militares
- **Presentes (TAF Regular)**: ~290 militares
- **TAF Adaptado**: ~46 militares
- **Disciplinas avaliadas**: Corrida 12min, Abdominal, Flexão, Natação 50m, Barra (Dinâmica/Estática)
- **Edição**: TAF BM-6/EMG 2026

---

## 🔒 Observações

- Os dados são de uso interno do CBMAM
- O sistema lê os arquivos CSV da pasta `data/` prioritariamente
- Compatível com Python 3.10+ e Python 3.14.3 (ambiente Streamlit Cloud)

---

**CBMAM · Corpo de Bombeiros Militar do Amazonas · 2026**
