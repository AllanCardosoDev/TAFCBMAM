import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Dashboard TAF CBMAM",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# ESTILOS CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #e7eefc;
    }
    .stApp {
        background-color: #0d1117;
        background-image: url(data:image/png;base64,{bg_image_base64});
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }
    .sidebar .sidebar-content {
        background-color: #161b22;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #e7eefc;
        font-weight: 700;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #e7eefc;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(255,255,255,.1);
        padding-bottom: 0.5rem;
    }
    .stMetric {
        background-color: rgba(17,27,46,.8);
        border: 1px solid rgba(255,255,255,.1);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,.1);
    }
    .stMetric > div:first-child {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
    }
    .stMetric > div:nth-child(2) > div:first-child {
        font-size: 2.2rem;
        font-weight: 800;
        color: #e7eefc;
    }
    .stMetric > div:nth-child(2) > div:nth-child(2) {
        font-size: 0.9rem;
        color: #64748b;
    }
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #2563eb;
    }
    .stSelectbox > div > div {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #e7eefc;
    }
    .stMultiSelect > div > div {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #e7eefc;
    }
    .stTextInput > div > div > input {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #e7eefc;
    }
    .stAlert {
        border-radius: 8px;
    }
    .stDataFrame {
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,.1);
    }
    .stMarkdown p {
        color: #cbd5e1;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #e7eefc;
    }
    .css-1d391kg { /* Sidebar background */
        background-color: #161b22;
    }
    .css-1lcbmhc { /* Main content padding */
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    .css-1lcbmhc .block-container {
        max-width: 1200px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES E DADOS ESTÁTICOS
# ══════════════════════════════════════════════════════════════════════════════

# Carregar imagem de fundo e converter para base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Substitua 'path/to/your/background_image.jpg' pelo caminho real da sua imagem
# bg_image_base64 = get_base64_image("assets/background.jpg") # Removido para evitar erro se a imagem não existir
bg_image_base64 = "" # Deixado vazio para não quebrar o código se a imagem não for fornecida

# Mapeamento de cores para classificações
COR_MAP = {
    "Excelente": "#22c55e",
    "Bom": "#3b82f6",
    "Regular": "#f59e0b",
    "Insuficiente": "#ef4444",
    "Não Compareceu": "#64748b",
}

# Configurações de tema para Plotly
DARK = {
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "font_color": "#e7eefc",
    "title_font_color": "#e7eefc",
    "legend_font_color": "#e7eefc",
    "hoverlabel_bgcolor": "#1e293b",
    "hoverlabel_font_color": "#e7eefc",
}
GRID = {
    "gridcolor": "rgba(255,255,255,.1)",
    "zerolinecolor": "rgba(255,255,255,.1)",
}

# Ordem dos postos para gráficos
ORDEM_POSTOS = [
    "CEL", "TC", "MAJ", "CAP", "1º TEN", "2º TEN",
    "ASP OF", "SUB TEN", "1º SGT", "2º SGT", "3º SGT",
    "CB", "SD"
]

def ordem_posto(posto):
    try:
        return ORDEM_POSTOS.index(posto)
    except ValueError:
        return len(ORDEM_POSTOS) # Coloca postos não listados no final

# Colunas de notas e seus rótulos
notas_map = {
    "Corrida": "NOTA_CORRIDA",
    "Abdominal": "NOTA_ABDOMINAL",
    "Flexão": "NOTA_FLEXAO",
    "Natação": "NOTA_NATACAO",
    "Barra": "NOTA_BARRA",
}
colunas_nota = list(notas_map.values())
labels_nota = list(notas_map.keys())
cats_radar = labels_nota + [labels_nota[0]] # Para fechar o gráfico de radar

# ══════════════════════════════════════════════════════════════════════════════
# DADOS DE PONTUAÇÃO TAF (MASCULINO E FEMININO)
# ══════════════════════════════════════════════════════════════════════════════

# Dados de pontuação TAF Masculino
TAF_MASCULINO = {
    "Corrida": {
        "faixas": [3200, 3100, 3000, 2900, 2800, 2700, 2600, 2500, 2400, 2300, 2200, 2100, 2000, 1900, 1800, 1700, 1600, 1500],
        "pontos": {
            (18, 21): [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5],
            (22, 25): [10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2],
            (26, 29): [10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5],
            (30, 34): [10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3],
            (35, 39): [10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5],
            (40, 44): [10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4],
            (45, 49): [10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5],
            (50, 53): [10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5],
            (54, 57): [10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5],
            (58, 150): [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6], # >58
        }
    },
    "Flexão": {
        "faixas": [38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21],
        "pontos": {
            (18, 21): [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5],
            (22, 25): [10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2],
            (26, 29): [10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5],
            (30, 34): [10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3],
            (35, 39): [10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5],
            (40, 44): [10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4],
            (45, 49): [10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5],
            (50, 53): [10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5],
            (54, 57): [10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5],
            (58, 150): [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6], # >58
        }
    },
    "Abdominal": {
        "faixas": [48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31],
        "pontos": {
            (18, 21): [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5],
            (22, 25): [10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2],
            (26, 29): [10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5],
            (30, 34): [10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3],
            (35, 39): [10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5],
            (40, 44): [10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4],
            (45, 49): [10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5],
            (50, 53): [10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5],
            (54, 57): [10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5],
            (58, 150): [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6], # >58
        }
    },
    "Barra": { # Barra Dinâmica
        "faixas": [13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        "pontos": {
            (18, 21): [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4],
            (22, 25): [10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5],
            (26, 29): [10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5],
            (30, 34): [10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5],
            (35, 39): [10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6],
            (40, 44): [10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5],
            (45, 49): [10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7],
            (50, 53): [10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5],
            (54, 57): [10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8],
            (58, 150): [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5], # >58
        }
    },
    "Barra_Est": { # Barra Estática (segundos)
        "faixas": [60, 57, 55, 53, 51, 49, 47, 45, 43, 41, 39, 37, 35, 33, 31, 29, 27, 25],
        "pontos": {
            (18, 21): [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5],
            (22, 25): [10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2],
            (26, 29): [10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5],
            (30, 34): [10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3],
            (35, 39): [10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5],
            (40, 44): [10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4],
            (45, 49): [10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5],
            (50, 53): [10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5],
            (54, 57): [10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5],
            (58, 150): [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6], # >58
        }
    },
    "Natacao": {
        "faixas": [40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108], # segundos
        "pontos": {
            (18, 21): [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5],
            (22, 25): [10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2],
            (26, 29): [10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5],
            (30, 34): [10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3],
            (35, 39): [10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5],
            (40, 44): [10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4],
            (45, 49): [10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5],
            (50, 53): [10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5],
            (54, 57): [10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5],
            (58, 150): [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6], # >58
        }
    },
}

# Dados de pontuação TAF Feminino
TAF_FEMININO = {
    "Corrida": {
        "faixas": [2700, 2600, 2500, 2400, 2300, 2200, 2100, 2000, 1900, 1800, 1700, 1600, 1500, 1400, 1300, 1200, 1100, 1000],
        "pontos": {
            (18, 21): [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5],
            (22, 25): [10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2],
            (26, 29): [10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5],
            (30, 34): [10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3],
            (35, 39): [10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5],
            (40, 44): [10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4],
            (45, 49): [10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5],
            (50, 53): [10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5],
            (54, 57): [10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5],
            (58, 150): [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6], # >58
        }
    },
    "Flexão": {
        "faixas": [30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13],
        "pontos": {
            (18, 21): [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5],
            (22, 25): [10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2],
            (26, 29): [10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5],
            (30, 34): [10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3],
            (35, 39): [10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5],
            (40, 44): [10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4],
            (45, 49): [10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5],
            (50, 53): [10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5],
            (54, 57): [10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5],
            (58, 150): [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6], # >58
        }
    },
    "Abdominal": {
        "faixas": [42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25],
        "pontos": {
            (18, 21): [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5],
            (22, 25): [10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2],
            (26, 29): [10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5],
            (30, 34): [10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3],
            (35, 39): [10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5],
            (40, 44): [10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4],
            (45, 49): [10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5],
            (50, 53): [10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5],
            (54, 57): [10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5],
            (58, 150): [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6], # >58
        }
    },
    "Barra": { # Barra Estática (segundos)
        "faixas": [50, 47, 45, 43, 41, 39, 37, 35, 33, 31, 29, 27, 25, 23, 21, 19, 17],
        "pontos": {
            (18, 21): [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2],
            (22, 25): [10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5],
            (26, 29): [10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3],
            (30, 34): [10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5],
            (35, 39): [10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4],
            (40, 44): [10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5],
            (45, 49): [10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5],
            (50, 53): [10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5],
            (54, 57): [10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6],
            (58, 150): [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6], # >58
        }
    },
    "Natacao": {
        "faixas": [58, 62, 66, 70, 74, 78, 82, 86, 90, 94, 98, 102, 106, 110, 114, 118, 122], # segundos
        "pontos": {
            (18, 21): [10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5, 2],
            (22, 25): [10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3, 2.5],
            (26, 29): [10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5, 3],
            (30, 34): [10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4, 3.5],
            (35, 39): [10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5, 4],
            (40, 44): [10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4.5],
            (45, 49): [10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5],
            (50, 53): [10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5],
            (54, 57): [10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6],
            (58, 150): [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9.5, 9, 8.5, 8, 7.5, 7, 6.5, 6], # >58
        }
    },
}

# Função para obter a nota baseada na idade, sexo e desempenho
def get_nota_taf(exercicio, desempenho, idade, sexo, barra_tipo=None):
    if pd.isna(desempenho) or pd.isna(idade) or pd.isna(sexo):
        return np.nan

    tabela_referencia = TAF_MASCULINO if sexo == "M" else TAF_FEMININO

    # Ajuste para Barra (Dinâmica vs Estática)
    if exercicio == "Barra":
        if sexo == "M": # Masculino usa Barra Dinâmica
            exercicio_key = "Barra"
        else: # Feminino usa Barra Estática
            exercicio_key = "Barra_Est"
    else:
        exercicio_key = exercicio

    if exercicio_key not in tabela_referencia:
        return np.nan # Exercício não encontrado na tabela de referência

    faixas_desempenho = tabela_referencia[exercicio_key]["faixas"]
    pontos_idade = tabela_referencia[exercicio_key]["pontos"]

    # Encontrar a faixa etária correta
    faixa_etaria_encontrada = None
    for faixa_min, faixa_max in pontos_idade.keys():
        if faixa_min <= idade <= faixa_max:
            faixa_etaria_encontrada = (faixa_min, faixa_max)
            break

    if faixa_etaria_encontrada is None:
        return np.nan # Idade fora das faixas definidas

    pontuacoes = pontos_idade[faixa_etaria_encontrada]

    # Encontrar a pontuação para o desempenho
    nota = 0.0
    for i, limite in enumerate(faixas_desempenho):
        if exercicio == "Natacao": # Natação é tempo, menor é melhor
            if desempenho <= limite:
                nota = pontuacoes[i]
                break
        else: # Outros exercícios, maior é melhor
            if desempenho >= limite:
                nota = pontuacoes[i]
                break
    else: # Se não atingiu nenhuma faixa, a nota é a menor possível ou 0
        nota = pontuacoes[-1] if pontuacoes else 0.0 # Garante que pega a menor nota se o desempenho for muito baixo
        # Se o desempenho for abaixo da menor faixa, a nota é 0.0 (insuficiente)
        if exercicio == "Natacao":
            if desempenho > faixas_desempenho[-1]: # Se o tempo for maior que o pior tempo da tabela
                nota = 0.0
        else:
            if desempenho < faixas_desempenho[-1]: # Se o desempenho for menor que o pior desempenho da tabela
                nota = 0.0

    return nota

# ══════════════════════════════════════════════════════════════════════════════
# CARREGAMENTO E PRÉ-PROCESSAMENTO DOS DADOS
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    # Dados fictícios para demonstração
    data = {
        "ORD": list(range(1, 51)),
        "NOME": [f"MILITAR {i}" for i in range(1, 51)],
        "POSTO_GRAD": np.random.choice(ORDEM_POSTOS, 50),
        "QUADRO": np.random.choice(["QCOBM", "QCPBM", "QPBM"], 50),
        "SEXO": np.random.choice(["M", "F"], 50),
        "IDADE": np.random.randint(20, 60, 50),
        "PRESENTE": np.random.choice([True, False], 50, p=[0.9, 0.1]),
        "CORRIDA_RAW": np.random.randint(1500, 3500, 50), # metros
        "ABDOMINAL_RAW": np.random.randint(20, 50, 50), # reps
        "FLEXAO_RAW": np.random.randint(15, 40, 50), # reps
        "NATACAO_RAW": np.random.randint(40, 120, 50), # segundos
        "BARRA_RAW": np.random.randint(0, 15, 50), # reps (dinâmica) ou segundos (estática)
        "BARRA_TIPO": np.random.choice(["Dinâmica", "Estática"], 50), # Tipo de barra para feminino
        "TAF_ADAPTADO": np.random.choice([True, False], 50, p=[0.05, 0.95]),
        "PONTO_FRACO": np.random.choice(labels_nota, 50),
    }
    df = pd.DataFrame(data)

    # Simular alguns ausentes e TAF adaptado
    df.loc[df["PRESENTE"] == False, ["CORRIDA_RAW", "ABDOMINAL_RAW", "FLEXAO_RAW", "NATACAO_RAW", "BARRA_RAW"]] = np.nan
    df.loc[df["TAF_ADAPTADO"] == True, ["CORRIDA_RAW", "ABDOMINAL_RAW", "FLEXAO_RAW", "NATACAO_RAW", "BARRA_RAW"]] = np.nan
    df.loc[df["TAF_ADAPTADO"] == True, "PONTO_FRACO"] = np.nan

    # Calcular notas baseadas nas regras de idade e sexo
    df["NOTA_CORRIDA"] = df.apply(lambda row: get_nota_taf("Corrida", row["CORRIDA_RAW"], row["IDADE"], row["SEXO"]), axis=1)
    df["NOTA_ABDOMINAL"] = df.apply(lambda row: get_nota_taf("Abdominal", row["ABDOMINAL_RAW"], row["IDADE"], row["SEXO"]), axis=1)
    df["NOTA_FLEXAO"] = df.apply(lambda row: get_nota_taf("Flexão", row["FLEXAO_RAW"], row["IDADE"], row["SEXO"]), axis=1)
    df["NOTA_NATACAO"] = df.apply(lambda row: get_nota_taf("Natacao", row["NATACAO_RAW"], row["IDADE"], row["SEXO"]), axis=1)

    # Lógica para Barra: Masculino usa Barra Dinâmica, Feminino usa Barra Estática
    df["NOTA_BARRA"] = df.apply(
        lambda row: get_nota_taf("Barra", row["BARRA_RAW"], row["IDADE"], row["SEXO"]) if row["SEXO"] == "M" else \
                    get_nota_taf("Barra_Est", row["BARRA_RAW"], row["IDADE"], row["SEXO"]), axis=1
    )

    # Média final e classificação
    df["MEDIA_FINAL"] = df[colunas_nota].mean(axis=1)

    def classificar(media):
        if pd.isna(media):
            return "Não Compareceu"
        if media >= 9.0:
            return "Excelente"
        elif media >= 7.5:
            return "Bom"
        elif media >= 6.0:
            return "Regular"
        else:
            return "Insuficiente"

    df["CLASSIFICACAO"] = df["MEDIA_FINAL"].apply(classificar)

    # Identificar o ponto fraco (menor nota)
    def find_ponto_fraco(row):
        if row["PRESENTE"] == False or row["TAF_ADAPTADO"] == True:
            return np.nan
        notas = {label: row[col] for label, col in notas_map.items()}
        min_nota = min(notas.values())
        if pd.isna(min_nota):
            return np.nan

        # Se a menor nota for 0, verificar se todas as notas são 0 ou NaN
        if min_nota == 0.0:
            if all(pd.isna(v) or v == 0.0 for v in notas.values()):
                return "Não avaliado/Todas insuficientes" # Ou outro rótulo apropriado

        # Se houver notas válidas, encontrar o exercício com a menor nota
        for label, nota in notas.items():
            if nota == min_nota:
                return label
        return np.nan

    df["PONTO_FRACO"] = df.apply(find_ponto_fraco, axis=1)


    return df

df_all = load_data()

# Filtros globais
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Bras%C3%A3o_do_Corpo_de_Bombeiros_Militar_do_Amazonas.svg/1200px-Bras%C3%A3o_do_Corpo_de_Bombeiros_Militar_do_Amazonas.svg.png", width=100)
    st.title("🔥 Dashboard TAF CBMAM")
    st.markdown("---")

    st.markdown("### ⚙️ Filtros")
    postos_selecionados = st.multiselect(
        "Posto/Graduação",
        options=df_all["POSTO_GRAD"].unique(),
        default=df_all["POSTO_GRAD"].unique(),
    )
    quadros_selecionados = st.multiselect(
        "Quadro",
        options=df_all["QUADRO"].unique(),
        default=df_all["QUADRO"].unique(),
    )
    sexo_selecionado = st.multiselect(
        "Sexo",
        options=df_all["SEXO"].unique(),
        default=df_all["SEXO"].unique(),
    )
    idade_min, idade_max = st.slider(
        "Faixa Etária",
        min_value=int(df_all["IDADE"].min()),
        max_value=int(df_all["IDADE"].max()),
        value=(int(df_all["IDADE"].min()), int(df_all["IDADE"].max())),
    )

    st.markdown("---")
    pagina = st.radio(
        "Navegação",
        [
            "🏠 Visão Geral",
            "🪖 Por Posto/Graduação",
            "📋 Por Quadro",
            "👤 Ficha Individual",
            "📈 Estatísticas",
            "♿ TAF Adaptado",
        ],
    )

# Aplicar filtros
df_filtered = df_all[
    (df_all["POSTO_GRAD"].isin(postos_selecionados)) &
    (df_all["QUADRO"].isin(quadros_selecionados)) &
    (df_all["SEXO"].isin(sexo_selecionado)) &
    (df_all["IDADE"] >= idade_min) &
    (df_all["IDADE"] <= idade_max)
]

df_presentes = df_filtered[df_filtered["PRESENTE"] & (df_filtered["TAF_ADAPTADO"] == False)].copy()
df_ausentes = df_filtered[df_filtered["PRESENTE"] == False].copy()
df_adaptado = df_filtered[df_filtered["TAF_ADAPTADO"] == True].copy()


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: VISÃO GERAL
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "🏠 Visão Geral":
    st.markdown(
        """
    <h1 style="margin:0;font-size:2rem;">🏠 Visão Geral do TAF 2026</h1>
    <p style="margin:6px 0 12px;color:#94a3b8;">
      Análise de desempenho do Teste de Aptidão Física do CBMAM
    </p>
    """,
        unsafe_allow_html=True,
    )
    st.divider()

    if len(df_presentes) > 0:
        # KPIs
        total_militares = len(df_filtered)
        presentes = len(df_presentes)
        ausentes = len(df_ausentes)
        adaptados = len(df_adaptado)
        media_geral = df_presentes["MEDIA_FINAL"].mean()
        taxa_aprovacao = (
            (df_presentes["CLASSIFICACAO"].isin(["Excelente", "Bom", "Regular"])).sum()
            / presentes
            * 100
        ) if presentes > 0 else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("👥 Total Militares", total_militares)
        c2.metric("✅ Presentes", presentes)
        c3.metric("❌ Ausentes", ausentes)
        c4.metric("♿ TAF Adaptado", adaptados)
        c5.metric("📈 Média Geral", f"{media_geral:.2f}")

        st.divider()

        # Distribuição de Classificação
        st.markdown(
            '<p class="section-title">📊 Distribuição de Classificação</p>',
            unsafe_allow_html=True,
        )
        classificacao_counts = (
            df_presentes["CLASSIFICACAO"].value_counts(normalize=True) * 100
        ).reset_index()
        classificacao_counts.columns = ["Classificação", "Percentual"]
        classificacao_counts["Classificação"] = pd.Categorical(
            classificacao_counts["Classificação"],
            categories=["Excelente", "Bom", "Regular", "Insuficiente"],
            ordered=True,
        )
        classificacao_counts = classificacao_counts.sort_values("Classificação")

        fig_class = px.bar(
            classificacao_counts,
            x="Classificação",
            y="Percentual",
            color="Classificação",
            color_discrete_map=COR_MAP,
            text="Percentual",
            title="Percentual de Militares por Classificação",
        )
        fig_class.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_class.update_layout(
            **DARK,
            height=400,
            xaxis=dict(**GRID),
            yaxis=dict(range=[0, 100], **GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_class, use_container_width=True)

        st.info(
            f"**✅ Taxa de Aprovação:** {taxa_aprovacao:.1f}% dos militares "
            "presentes atingiram a classificação Regular ou superior."
        )

        # Média por disciplina
        st.markdown(
            '<p class="section-title">💪 Média de Notas por Atividade</p>',
            unsafe_allow_html=True,
        )

        df_disc = (
            df_presentes[colunas_nota].mean().reset_index()
        )
        df_disc.columns = ["Atividade", "Média"]
        df_disc["Atividade"] = df_disc["Atividade"].map(
            {v: k for k, v in notas_map.items()}
        )
        df_disc = df_disc.sort_values("Média", ascending=True)

        fig_disc = px.bar(
            df_disc, x="Média", y="Atividade", orientation="h", text="Média",
            color_discrete_sequence=["#3b82f6"],
            title="Nota média por exercício",
        )
        fig_disc.update_traces(texttemplate="%{text:.2f}", textposition="outside",
                               showlegend=False)
        fig_disc.update_layout(
            **DARK, height=320,
            xaxis=dict(range=[0, 11], **GRID),
            yaxis=dict(**GRID),
            margin=dict(l=10, r=70, t=50, b=20),
        )
        st.plotly_chart(fig_disc, use_container_width=True)

        disc_pior = df_disc.iloc[0]
        disc_melhor = df_disc.iloc[-1]
        st.info(
            f"**📌 Insight:** A atividade com menor média é "
            f"**{disc_pior['Atividade']}** ({disc_pior['Média']:.2f}). "
            f"O ponto forte é **{disc_melhor['Atividade']}** ({disc_melhor['Média']:.2f})."
        )

        # Radar Top 5 vs Bottom 5
        st.markdown('<p class="section-title">🕸️ Radar — Top 5 vs Bottom 5</p>',
                    unsafe_allow_html=True)

        top5 = df_presentes.nlargest(5, "MEDIA_FINAL")[colunas_nota].mean().tolist()
        bottom5 = df_presentes.nsmallest(5, "MEDIA_FINAL")[colunas_nota].mean().tolist()

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=top5 + [top5[0]], theta=cats_radar, fill="toself", name="Top 5",
            line_color="#22c55e", fillcolor="rgba(34,197,94,.15)",
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=bottom5 + [bottom5[0]], theta=cats_radar, fill="toself", name="Bottom 5",
            line_color="#ef4444", fillcolor="rgba(239,68,68,.15)",
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 10],
                                gridcolor="rgba(255,255,255,.12)",
                                tickfont_color="#94a3b8"),
                angularaxis=dict(gridcolor="rgba(255,255,255,.12)"),
            ),
            **DARK,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15),
            height=420, title="Comparativo — Top 5 vs Bottom 5",
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Mapa de calor
        st.markdown('<p class="section-title">🌡️ Mapa de Calor — Notas</p>',
                    unsafe_allow_html=True)

        df_heat = df_presentes[["NOME", "POSTO_GRAD"] + colunas_nota].copy()
        df_heat["LABEL"] = df_heat.apply(
            lambda r: f"{r['POSTO_GRAD']} {' '.join(str(r['NOME']).split()[:2])}", axis=1
        )
        df_heat = df_heat.sort_values("MEDIA_FINAL", ascending=False) # Ordenar pelo MEDIA_FINAL

        z_vals = df_heat[colunas_nota].values.tolist()
        fig_heat = go.Figure(go.Heatmap(
            z=z_vals, x=labels_nota, y=df_heat["LABEL"].tolist(),
            colorscale=[[0, "#ef4444"], [0.5, "#f59e0b"], [0.75, "#3b82f6"], [1, "#22c55e"]],
            zmin=0, zmax=10,
            text=[[f"{v:.1f}" if pd.notna(v) else "—" for v in row] for row in z_vals],
            texttemplate="%{text}",
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}<extra></extra>",
            colorbar=dict(title="Nota", tickfont_color="#e7eefc",
                         title_font_color="#e7eefc"),
        ))
        fig_heat.update_layout(
            **DARK, height=max(500, len(df_heat) * 20),
            margin=dict(l=10, r=10, t=20, b=20),
            xaxis=dict(side="top"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        # Pontos fracos
        st.markdown('<p class="section-title">🔍 Atividades com Mais Pontos Fracos</p>',
                    unsafe_allow_html=True)

        pf_df = df_presentes["PONTO_FRACO"].value_counts().reset_index()
        pf_df.columns = ["Atividade", "Quantidade"]

        fig_pf = px.bar(
            pf_df, x="Atividade", y="Quantidade",
            color="Quantidade",
            color_continuous_scale=["#22c55e", "#f59e0b", "#ef4444"],
            text="Quantidade", title="Atividade com pior nota individual",
        )
        fig_pf.update_traces(textposition="outside")
        fig_pf.update_layout(
            **DARK, coloraxis_showscale=False,
            yaxis=dict(**GRID), xaxis=dict(**GRID),
            margin=dict(t=50, b=20), height=350,
        )
        st.plotly_chart(fig_pf, use_container_width=True)

        if len(pf_df) > 0:
            st.warning(
                f"⚠️ **{pf_df.iloc[0]['Quantidade']} militares** têm pior desempenho em "
                f"**{pf_df.iloc[0]['Atividade']}**. Recomenda-se treino focado."
            )

        # Tabela
        st.markdown('<p class="section-title">📋 Tabela Completa</p>',
                    unsafe_allow_html=True)

        df_display = df_presentes[[
            "ORD", "POSTO_GRAD", "QUADRO", "NOME", "SEXO", "IDADE",
            "NOTA_CORRIDA", "NOTA_ABDOMINAL", "NOTA_FLEXAO",
            "NOTA_NATACAO", "NOTA_BARRA", "MEDIA_FINAL",
            "CLASSIFICACAO", "PONTO_FRACO",
        ]].rename(columns={
            "ORD": "Nº", "POSTO_GRAD": "Posto", "QUADRO": "Quadro",
            "NOTA_CORRIDA": "Corrida", "NOTA_ABDOMINAL": "Abdominal",
            "NOTA_FLEXAO": "Flexão", "NOTA_NATACAO": "Natação",
            "NOTA_BARRA": "Barra", "MEDIA_FINAL": "Média",
            "CLASSIFICACAO": "Status", "PONTO_FRACO": "Ponto Fraco",
        })

        def colorir(val):
            try:
                v = float(val)
            except (ValueError, TypeError):
                return ""
            if v >= 9.0: return "background-color:rgba(34,197,94,.25);color:#bbf7d0"
            if v >= 7.5: return "background-color:rgba(59,130,246,.25);color:#bfdbfe"
            if v >= 6.0: return "background-color:rgba(245,158,11,.25);color:#fde68a"
            return "background-color:rgba(239,68,68,.25);color:#fecaca"

        st.dataframe(
            df_display.style.map(colorir, subset=["Média"]),
            use_container_width=True, height=420,
        )

        # Conclusões
        st.divider()
        st.markdown('<p class="section-title">💡 Conclusões e Recomendações</p>',
                    unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            #### 🎯 Treinamento direcionado
            Intensificar treinos na atividade com menor média coletiva.
            Um programa semanal específico pode elevar o desempenho
            geral em até 15% em 3 meses.
            """)
        with c2:
            st.markdown("""
            #### 📅 Monitoramento contínuo
            Aplicar o TAF a cada bimestre para acompanhar evolução
            individual e detectar regressões antes de nível crítico.
            """)
        with c3:
            st.markdown("""
            #### 🤝 Mentoria entre pares
            Militares *Excelente* podem apoiar os de *Insuficiente* em
            sessões conjuntas, fortalecendo o espírito de equipe.
            """)

    else:
        st.warning("Nenhum militar encontrado com os filtros atuais.")


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: POR POSTO/GRADUAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🪖 Por Posto/Graduação":
    st.markdown("""
    <h1 style="margin:0;font-size:2rem;">🪖 Análise por Posto/Graduação</h1>
    <p style="margin:6px 0 12px;color:#94a3b8;">
      Comparativo de desempenho entre os diferentes postos e graduações
    </p>
    """, unsafe_allow_html=True)
    st.divider()

    if len(df_presentes) == 0:
        st.warning("Nenhum dado disponível com os filtros atuais.")
    else:
        # Tabela resumo
        st.markdown('<p class="section-title">📊 Resumo por Posto/Graduação</p>',
                    unsafe_allow_html=True)

        resumo = df_presentes.groupby("POSTO_GRAD").agg(
            Efetivo=("NOME", "count"),
            Media=("MEDIA_FINAL", "mean"),
            Mediana=("MEDIA_FINAL", "median"),
            Minimo=("MEDIA_FINAL", "min"),
            Maximo=("MEDIA_FINAL", "max"),
            Desvio=("MEDIA_FINAL", "std"),
        ).reset_index()
        resumo["_ordem"] = resumo["POSTO_GRAD"].apply(ordem_posto)
        resumo = resumo.sort_values("_ordem").drop(columns=["_ordem"])
        resumo.columns = ["Posto/Grad", "Efetivo", "Média", "Mediana",
                          "Mínimo", "Máximo", "Desvio Padrão"]
        for c in ["Média", "Mediana", "Mínimo", "Máximo", "Desvio Padrão"]:
            resumo[c] = resumo[c].round(2)
        st.dataframe(resumo, use_container_width=True, hide_index=True)

        # Média por posto
        st.markdown('<p class="section-title">📈 Média por Posto/Graduação</p>',
                    unsafe_allow_html=True)

        df_posto_media = df_presentes.groupby("POSTO_GRAD")["MEDIA_FINAL"].mean().reset_index()
        df_posto_media["_ordem"] = df_posto_media["POSTO_GRAD"].apply(ordem_posto)
        df_posto_media = df_posto_media.sort_values("_ordem")

        fig_posto = px.bar(
            df_posto_media, x="POSTO_GRAD", y="MEDIA_FINAL",
            color="MEDIA_FINAL",
            color_continuous_scale=["#ef4444", "#f59e0b", "#3b82f6", "#22c55e"],
            text="MEDIA_FINAL",
            labels={"POSTO_GRAD": "Posto/Graduação", "MEDIA_FINAL": "Média"},
            title="Média final por posto/graduação",
        )
        fig_posto.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_posto.update_layout(
            **DARK, height=400, coloraxis_showscale=False,
            xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_posto, use_container_width=True)

        # Box plot
        st.markdown('<p class="section-title">📦 Distribuição por Posto/Graduação</p>',
                    unsafe_allow_html=True)

        df_box = df_presentes.copy()
        df_box["_ordem"] = df_box["POSTO_GRAD"].apply(ordem_posto)
        df_box = df_box.sort_values("_ordem")

        fig_box = px.box(
            df_box, x="POSTO_GRAD", y="MEDIA_FINAL",
            color="POSTO_GRAD",
            labels={"POSTO_GRAD": "Posto/Graduação", "MEDIA_FINAL": "Média Final"},
            title="Distribuição da média final por posto",
        )
        fig_box.update_layout(
            **DARK, height=450, showlegend=False,
            xaxis=dict(**GRID), yaxis=dict(**GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_box, use_container_width=True)

        # Classificação por posto (stacked bar)
        st.markdown('<p class="section-title">📊 Classificação por Posto</p>',
                    unsafe_allow_html=True)

        class_posto = df_presentes.groupby(
            ["POSTO_GRAD", "CLASSIFICACAO"]
        ).size().reset_index(name="Qtd")
        class_posto["_ordem"] = class_posto["POSTO_GRAD"].apply(ordem_posto)
        class_posto = class_posto.sort_values("_ordem")

        fig_stack = px.bar(
            class_posto, x="POSTO_GRAD", y="Qtd", color="CLASSIFICACAO",
            color_discrete_map=COR_MAP, barmode="stack",
            labels={"POSTO_GRAD": "Posto/Graduação", "Qtd": "Quantidade"},
            title="Distribuição de classificações por posto",
        )
        fig_stack.update_layout(
            **DARK, height=400,
            xaxis=dict(**GRID), yaxis=dict(**GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_stack, use_container_width=True)

        # Radar comparativo dos postos
        st.markdown('<p class="section-title">🕸️ Radar Comparativo por Posto</p>',
                    unsafe_allow_html=True)

        postos_top = df_posto_media["POSTO_GRAD"].tolist() # Todos os postos
        cores_radar = ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6", "#a855f7", "#ec4899", "#8b5cf6", "#10b981", "#f97316", "#6366f1", "#d946b1", "#06b6d4", "#f43f5e"]
        fig_radar_posto = go.Figure()
        for idx, posto in enumerate(postos_top):
            vals = df_presentes[df_presentes["POSTO_GRAD"] == posto][colunas_nota].mean().tolist()
            fig_radar_posto.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats_radar,
                name=posto, line_color=cores_radar[idx % len(cores_radar)],
            ))
        fig_radar_posto.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 10],
                                gridcolor="rgba(255,255,255,.12)",
                                tickfont_color="#94a3b8"),
                angularaxis=dict(gridcolor="rgba(255,255,255,.12)"),
            ),
            **DARK, height=450,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            title="Perfil de desempenho por posto",
        )
        st.plotly_chart(fig_radar_posto, use_container_width=True)

        # Taxa de ausência por posto
        st.markdown('<p class="section-title">📋 Taxa de Ausência por Posto</p>',
                    unsafe_allow_html=True)

        ausencia = df_all.groupby("POSTO_GRAD").agg(
            Total=("NOME", "count"),
            Ausentes=("PRESENTE", lambda x: (~x).sum()),
        ).reset_index()
        ausencia["Taxa (%)"] = (ausencia["Ausentes"] / ausencia["Total"] * 100).round(1)
        ausencia["_ordem"] = ausencia["POSTO_GRAD"].apply(ordem_posto)
        ausencia = ausencia.sort_values("_ordem").drop(columns=["_ordem"])

        fig_aus = px.bar(
            ausencia, x="POSTO_GRAD", y="Taxa (%)",
            color="Taxa (%)",
            color_continuous_scale=["#22c55e", "#f59e0b", "#ef4444"],
            text="Taxa (%)",
            labels={"POSTO_GRAD": "Posto/Graduação"},
            title="Percentual de ausência por posto",
        )
        fig_aus.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_aus.update_layout(
            **DARK, height=350, coloraxis_showscale=False,
            xaxis=dict(**GRID), yaxis=dict(**GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_aus, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: POR QUADRO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📋 Por Quadro":
    st.markdown("""
    <h1 style="margin:0;font-size:2rem;">📋 Análise por Quadro</h1>
    <p style="margin:6px 0 12px;color:#94a3b8;">
      Comparativo de desempenho entre os diferentes quadros (QCOBM, QCPBM, QPBM, etc.)
    </p>
    """, unsafe_allow_html=True)
    st.divider()

    if len(df_presentes) == 0:
        st.warning("Nenhum dado disponível com os filtros atuais.")
    else:
        # Resumo por quadro
        st.markdown('<p class="section-title">📊 Resumo por Quadro</p>',
                    unsafe_allow_html=True)

        resumo_q = df_presentes.groupby("QUADRO").agg(
            Efetivo=("NOME", "count"),
            Media=("MEDIA_FINAL", "mean"),
            Mediana=("MEDIA_FINAL", "median"),
            Minimo=("MEDIA_FINAL", "min"),
            Maximo=("MEDIA_FINAL", "max"),
        ).reset_index()
        resumo_q.columns = ["Quadro", "Efetivo", "Média", "Mediana", "Mínimo", "Máximo"]
        for c in ["Média", "Mediana", "Mínimo", "Máximo"]:
            resumo_q[c] = resumo_q[c].round(2)
        resumo_q = resumo_q.sort_values("Média", ascending=False)
        st.dataframe(resumo_q, use_container_width=True, hide_index=True)

        # Média por quadro
        st.markdown('<p class="section-title">📈 Média por Quadro</p>',
                    unsafe_allow_html=True)

        df_q_media = df_presentes.groupby("QUADRO")["MEDIA_FINAL"].mean().reset_index()
        df_q_media = df_q_media.sort_values("MEDIA_FINAL", ascending=False)

        fig_q = px.bar(
            df_q_media, x="QUADRO", y="MEDIA_FINAL",
            color="MEDIA_FINAL",
            color_continuous_scale=["#ef4444", "#f59e0b", "#3b82f6", "#22c55e"],
            text="MEDIA_FINAL",
            labels={"QUADRO": "Quadro", "MEDIA_FINAL": "Média"},
            title="Média final por quadro",
        )
        fig_q.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_q.update_layout(
            **DARK, height=400, coloraxis_showscale=False,
            xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_q, use_container_width=True)

        # Box plot por quadro
        st.markdown('<p class="section-title">📦 Distribuição por Quadro</p>',
                    unsafe_allow_html=True)

        fig_box_q = px.box(
            df_presentes, x="QUADRO", y="MEDIA_FINAL",
            color="QUADRO",
            labels={"QUADRO": "Quadro", "MEDIA_FINAL": "Média Final"},
            title="Distribuição da média final por quadro",
        )
        fig_box_q.update_layout(
            **DARK, height=450, showlegend=False,
            xaxis=dict(**GRID), yaxis=dict(**GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_box_q, use_container_width=True)

        # Classificação por quadro (stacked bar)
        st.markdown('<p class="section-title">📊 Classificação por Quadro</p>',
                    unsafe_allow_html=True)

        class_q = df_presentes.groupby(
            ["QUADRO", "CLASSIFICACAO"]
        ).size().reset_index(name="Qtd")

        fig_stack_q = px.bar(
            class_q, x="QUADRO", y="Qtd", color="CLASSIFICACAO",
            color_discrete_map=COR_MAP, barmode="stack",
            labels={"QUADRO": "Quadro", "Qtd": "Quantidade"},
            title="Classificações por quadro",
        )
        fig_stack_q.update_layout(
            **DARK, height=400,
            xaxis=dict(**GRID), yaxis=dict(**GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_stack_q, use_container_width=True)

        # Radar por quadro
        st.markdown('<p class="section-title">🕸️ Radar Comparativo por Quadro</p>',
                    unsafe_allow_html=True)

        cores_q = ["#ef4444", "#3b82f6", "#22c55e", "#f59e0b", "#a855f7"]
        fig_radar_q = go.Figure()
        for idx, quadro in enumerate(df_q_media["QUADRO"].tolist()):
            vals = df_presentes[df_presentes["QUADRO"] == quadro][colunas_nota].mean().tolist()
            fig_radar_q.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats_radar,
                name=quadro, line_color=cores_q[idx % len(cores_q)],
            ))
        fig_radar_q.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 10],
                                gridcolor="rgba(255,255,255,.12)",
                                tickfont_color="#94a3b8"),
                angularaxis=dict(gridcolor="rgba(255,255,255,.12)"),
            ),
            **DARK, height=450,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            title="Perfil de desempenho por quadro",
        )
        st.plotly_chart(fig_radar_q, use_container_width=True)

        # Desempenho por atividade e quadro
        st.markdown('<p class="section-title">💪 Notas por Atividade × Quadro</p>',
                    unsafe_allow_html=True)

        disc_data = []
        for q in df_presentes["QUADRO"].unique():
            for label, col in notas_map.items():
                media_val = df_presentes[df_presentes["QUADRO"] == q][col].mean()
                disc_data.append({"Quadro": q, "Atividade": label, "Média": media_val})
        df_disc_q = pd.DataFrame(disc_data)

        fig_disc_q = px.bar(
            df_disc_q, x="Atividade", y="Média", color="Quadro",
            barmode="group", text="Média",
            title="Média por atividade e quadro",
        )
        fig_disc_q.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_disc_q.update_layout(
            **DARK, height=420,
            xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_disc_q, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: FICHA INDIVIDUAL
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "👤 Ficha Individual":
    st.markdown("""
    <h1 style="margin:0;font-size:2rem;">👤 Ficha Individual</h1>
    <p style="margin:6px 0 12px;color:#94a3b8;">
      Perfil detalhado de cada militar
    </p>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("**🔎 Selecionar Militar**")
        busca = st.text_input("Buscar por nome", placeholder="Digite parte do nome...")

        df_busca = df_all[df_all["PRESENTE"] & (df_all["TAF_ADAPTADO"] == False)].copy()
        lista_nomes = df_busca["NOME"].tolist()
        if busca:
            lista_nomes = [n for n in lista_nomes if busca.upper() in n.upper()]

        if lista_nomes:
            militar_sel = st.selectbox("Militar", lista_nomes)
        else:
            st.warning("Nenhum militar encontrado.")
            militar_sel = df_busca["NOME"].iloc[0] if len(df_busca) > 0 else None

    if militar_sel is None:
        st.warning("Nenhum militar disponível.")
    else:
        row = df_all[df_all["NOME"] == militar_sel].iloc[0]
        vals_ind = [float(row[c]) if pd.notna(row[c]) else 0.0 for c in colunas_nota]
        nome_curto = " ".join(str(militar_sel).split()[:2])
        media_ind = float(row["MEDIA_FINAL"]) if pd.notna(row["MEDIA_FINAL"]) else 0.0
        class_ind = row["CLASSIFICACAO"]
        posto_ind = row["POSTO_GRAD"]
        quadro_ind = row["QUADRO"]
        idade_ind = int(row["IDADE"])
        sexo_ind = row["SEXO"]

        # Comparações
        media_geral = df_all[df_all["PRESENTE"] & (df_all["TAF_ADAPTADO"] == False)]["MEDIA_FINAL"].mean()
        diff_geral = media_ind - media_geral

        # Média do mesmo posto
        media_posto = df_all[
            (df_all["PRESENTE"]) & (df_all["TAF_ADAPTADO"] == False) & (df_all["POSTO_GRAD"] == posto_ind)
        ]["MEDIA_FINAL"].mean()
        diff_posto = media_ind - media_posto

        # Ranking
        df_rank_calc = df_all[df_all["PRESENTE"] & (df_all["TAF_ADAPTADO"] == False) & df_all["MEDIA_FINAL"].notna()].copy()
        rank_pos = df_rank_calc["MEDIA_FINAL"].rank(ascending=False, method="min")
        posicao = int(rank_pos[df_rank_calc["NOME"] == militar_sel].values[0])
        total = len(df_rank_calc)

        pf_notas = {l: float(row[c]) for l, c in notas_map.items() if pd.notna(row[c])}
        pf_forte = max(pf_notas, key=pf_notas.get) if pf_notas else "—"
        pf_fraco = row["PONTO_FRACO"]

        badge_cor = {
            "Excelente":    ("#bbf7d0", "#166534", "rgba(34,197,94,.3)"),
            "Bom":          ("#bfdbfe", "#1e3a5f", "rgba(59,130,246,.3)"),
            "Regular":      ("#fde68a", "#78350f", "rgba(245,158,11,.3)"),
            "Insuficiente": ("#fecaca", "#7f1d1d", "rgba(239,68,68,.3)"),
            "Não Compareceu": ("#cbd5e1", "#334155", "rgba(100,116,139,.3)"),
        }.get(class_ind, ("#e7eefc", "#1e293b", "rgba(255,255,255,.1)"))

        sinal_g = "+" if diff_geral >= 0 else ""
        cor_g = "#22c55e" if diff_geral >= 0 else "#ef4444"
        sinal_p = "+" if diff_posto >= 0 else ""
        cor_p = "#22c55e" if diff_posto >= 0 else "#ef4444"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(239,68,68,.15),rgba(59,130,246,.1));
                    border:1px solid rgba(239,68,68,.3);border-radius:16px;
                    padding:24px 28px;margin-bottom:20px;">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
            <div>
              <div style="font-size:1.8rem;font-weight:800;">🪖 {nome_curto}</div>
              <div style="color:#94a3b8;margin-top:4px;">
                {posto_ind} · {quadro_ind} · {sexo_ind} · {idade_ind} anos · CBMAM · 2026
              </div>
            </div>
            <div style="display:flex;gap:12px;flex-wrap:wrap;">
              <div style="background:{badge_cor[2]};border-radius:12px;padding:10px 20px;text-align:center;">
                <div style="font-size:.75rem;color:#94a3b8;">CLASSIFICAÇÃO</div>
                <div style="font-size:1.3rem;font-weight:800;color:{badge_cor[0]};">{class_ind}</div>
              </div>
              <div style="background:rgba(255,255,255,.05);border-radius:12px;padding:10px 20px;text-align:center;">
                <div style="font-size:.75rem;color:#94a3b8;">MÉDIA FINAL</div>
                <div style="font-size:1.3rem;font-weight:800;">{media_ind:.1f}</div>
              </div>
              <div style="background:rgba(255,255,255,.05);border-radius:12px;padding:10px 20px;text-align:center;">
                <div style="font-size:.75rem;color:#94a3b8;">RANKING</div>
                <div style="font-size:1.3rem;font-weight:800;">{posicao}° / {total}</div>
              </div>
              <div style="background:rgba(255,255,255,.05);border-radius:12px;padding:10px 20px;text-align:center;">
                <div style="font-size:.75rem;color:#94a3b8;">vs GERAL</div>
                <div style="font-size:1.3rem;font-weight:800;color:{cor_g};">{sinal_g}{diff_geral:.2f}</div>
              </div>
              <div style="background:rgba(255,255,255,.05);border-radius:12px;padding:10px 20px;text-align:center;">
                <div style="font-size:.75rem;color:#94a3b8;">vs {posto_ind}</div>
                <div style="font-size:1.3rem;font-weight:800;color:{cor_p};">{sinal_p}{diff_posto:.2f}</div>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Dados brutos do militar
        st.markdown('<p class="section-title">📝 Desempenho Bruto</p>',
                    unsafe_allow_html=True)
        raw_cols = st.columns(5)
        raw_data = [
            ("🏃 Corrida 12min", row["CORRIDA_RAW"], "metros"),
            ("💪 Abdominal", row["ABDOMINAL_RAW"], "reps"),
            ("🤸 Flexão", row["FLEXAO_RAW"], "reps"),
            ("🏊 Natação 50m", row["NATACAO_RAW"], "segundos"),
            ("🔩 Barra", row["BARRA_RAW"], f"({row['BARRA_TIPO']})" if pd.notna(row.get("BARRA_TIPO")) else ""),
        ]
        for i, (label, val, unit) in enumerate(raw_data):
            with raw_cols[i]:
                display_val = str(val) if pd.notna(val) and str(val).strip() not in ("nan", "") else "—"
                st.markdown(f"""
                <div style="background:rgba(17,27,46,.8);border:1px solid rgba(255,255,255,.1);
                            border-radius:14px;padding:12px;text-align:center;">
                  <div style="font-size:.75rem;color:#94a3b8;">{label}</div>
                  <div style="font-size:1.5rem;font-weight:800;margin:4px 0;">{display_val}</div>
                  <div style="font-size:.7rem;color:#64748b;">{unit}</div>
                </div>
                """, unsafe_allow_html=True)

        # Radar e barras
        col_r, col_b2 = st.columns(2)

        med_geral_vals = [df_all[df_all["PRESENTE"] & (df_all["TAF_ADAPTADO"] == False)][c].mean() for c in colunas_nota]
        med_posto_vals = [
            df_all[(df_all["PRESENTE"]) & (df_all["TAF_ADAPTADO"] == False) & (df_all["POSTO_GRAD"] == posto_ind)][c].mean()
            for c in colunas_nota
        ]

        with col_r:
            st.markdown('<p class="section-title">🕸️ Radar de Atributos</p>',
                        unsafe_allow_html=True)

            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(
                r=[10] * len(cats_radar), theta=cats_radar, fill="toself", name="Máximo",
                line_color="rgba(255,255,255,.1)", fillcolor="rgba(255,255,255,.03)",
            ))
            fig_r.add_trace(go.Scatterpolar(
                r=med_geral_vals + [med_geral_vals[0]], theta=cats_radar,
                fill="toself", name="Média Geral",
                line_color="#f59e0b", fillcolor="rgba(245,158,11,.1)", line_dash="dot",
            ))
            fig_r.add_trace(go.Scatterpolar(
                r=med_posto_vals + [med_posto_vals[0]], theta=cats_radar,
                fill="toself", name=f"Média {posto_ind}",
                line_color="#a855f7", fillcolor="rgba(168,85,247,.1)", line_dash="dot",
            ))
            fig_r.add_trace(go.Scatterpolar(
                r=vals_ind + [vals_ind[0]], theta=cats_radar,
                fill="toself", name=nome_curto,
                line_color="#3b82f6", fillcolor="rgba(59,130,246,.2)",
            ))
            fig_r.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 10],
                                    gridcolor="rgba(255,255,255,.12)",
                                    tickfont_color="#94a3b8"),
                    angularaxis=dict(gridcolor="rgba(255,255,255,.12)"),
                ),
                **DARK,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25),
                height=440, margin=dict(t=30, b=70),
            )
            st.plotly_chart(fig_r, use_container_width=True)

        with col_b2:
            st.markdown('<p class="section-title">📊 Notas vs Referências</p>',
                        unsafe_allow_html=True)

            fig_b = go.Figure()
            fig_b.add_trace(go.Bar(
                name="Média Geral", x=labels_nota, y=med_geral_vals,
                marker_color="rgba(245,158,11,.5)",
                text=[f"{v:.1f}" for v in med_geral_vals], textposition="outside",
            ))
            fig_b.add_trace(go.Bar(
                name=nome_curto, x=labels_nota, y=vals_ind,
                marker_color=[
                    "#22c55e" if n >= m else "#ef4444"
                    for n, m in zip(vals_ind, med_geral_vals)
                ],
                text=[f"{v:.1f}" for v in vals_ind], textposition="outside",
            ))
            fig_b.update_layout(
                barmode="group", **DARK,
                yaxis=dict(range=[0, 12], **GRID), xaxis=dict(**GRID),
                legend=dict(orientation="h", yanchor="bottom", y=-0.25),
                height=440, margin=dict(t=30, b=70),
            )
            st.plotly_chart(fig_b, use_container_width=True)

        # Cards de notas
        st.markdown('<p class="section-title">🎯 Detalhamento por Atividade</p>',
                    unsafe_allow_html=True)

        cols_disc = st.columns(5)
        for i, (label, col_n) in enumerate(zip(labels_nota, colunas_nota)):
            nota_v = float(row[col_n]) if pd.notna(row[col_n]) else 0.0
            med_v = df_all[df_all["PRESENTE"] & (df_all["TAF_ADAPTADO"] == False)][col_n].mean()
            delta_v = nota_v - med_v
            s = "+" if delta_v >= 0 else ""
            c_delta = "#22c55e" if delta_v >= 0 else "#ef4444"
            icone = "🟢" if nota_v >= med_v else "🔴"

            with cols_disc[i]:
                st.markdown(f"""
                <div style="background:rgba(17,27,46,.8);border:1px solid rgba(255,255,255,.1);
                            border-radius:14px;padding:16px;text-align:center;">
                  <div style="font-size:.8rem;color:#94a3b8;margin-bottom:8px;">{label}</div>
                  <div style="font-size:2rem;font-weight:800;">{nota_v:.1f}</div>
                  <div style="font-size:.8rem;color:{c_delta};margin-top:4px;">
                    {icone} {s}{delta_v:.2f} vs geral
                  </div>
                  <div style="background:rgba(255,255,255,.06);border-radius:6px;
                              margin-top:10px;height:6px;overflow:hidden;">
                    <div style="width:{nota_v * 10}%;height:100%;
                                background:{'#22c55e' if nota_v >= 9.0 else '#3b82f6' if nota_v >= 7.5 else '#f59e0b' if nota_v >= 6.0 else '#ef4444'};
                                border-radius:6px;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # Gauge
        st.markdown('<p class="section-title">🏁 Indicador de Média Final</p>',
                    unsafe_allow_html=True)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=media_ind,
            delta={"reference": media_geral, "valueformat": ".2f",
                   "increasing": {"color": "#22c55e"},
                   "decreasing": {"color": "#ef4444"}},
            title={"text": f"Média Final · {nome_curto}<br>"
                   f"<span style='font-size:.8rem;color:#94a3b8'>"
                   f"Ref: média geral ({media_geral:.2f})</span>"},
            gauge={
                "axis": {"range": [0, 10], "tickcolor": "#94a3b8"},
                "bar": {"color": COR_MAP.get(class_ind, "#3b82f6")},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(255,255,255,.1)",
                "steps": [
                    {"range": [0, 6.0], "color": "rgba(239,68,68,.15)"},
                    {"range": [6.0, 7.5], "color": "rgba(245,158,11,.15)"},
                    {"range": [7.5, 9.0], "color": "rgba(59,130,246,.15)"},
                    {"range": [9.0, 10], "color": "rgba(34,197,94,.15)"},
                ],
                "threshold": {
                    "line": {"color": "#f59e0b", "width": 3},
                    "thickness": 0.8,
                    "value": media_geral,
                },
            },
            number={"font": {"color": "#e7eefc", "size": 56}},
        ))
        fig_gauge.update_layout(
            **DARK, height=320, margin=dict(t=60, b=20, l=40, r=40),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Resumo
        st.markdown(f"""
        <div style="background:rgba(17,27,46,.8);border:1px solid rgba(255,255,255,.1);
                    border-radius:14px;padding:20px;margin-top:10px;line-height:2;">
          <b>🪖 Posto/Graduação:</b> {posto_ind} · {quadro_ind} ({sexo_ind}, {idade_ind} anos)<br>
          <b>🟢 Ponto forte:</b> {pf_forte} ({pf_notas.get(pf_forte, 0):.1f})<br>
          <b>🔴 Ponto fraco:</b> {pf_fraco} ({pf_notas.get(pf_fraco, 0):.1f})<br>
          <b>📍 Ranking:</b> {posicao}° de {total} avaliados<br>
          <b>📈 vs Média geral ({media_geral:.2f}):</b>
          <span style="color:{cor_g};font-weight:700;">{sinal_g}{diff_geral:.2f}</span><br>
          <b>📈 vs Média {posto_ind} ({media_posto:.2f}):</b>
          <span style="color:{cor_p};font-weight:700;">{sinal_p}{diff_posto:.2f}</span>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: ESTATÍSTICAS
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📈 Estatísticas":
    st.markdown("""
    <h1 style="margin:0;font-size:2rem;">📈 Análise Estatística</h1>
    <p style="margin:6px 0 12px;color:#94a3b8;">
      Boxplots, distribuições, correlações e percentis do TAF
    </p>
    """, unsafe_allow_html=True)
    st.divider()

    if len(df_presentes) == 0:
        st.warning("Nenhum dado disponível.")
    else:
        # Box plots por atividade
        st.markdown('<p class="section-title">📦 Box Plot — Notas por Atividade</p>',
                    unsafe_allow_html=True)

        box_data = []
        for label, col in notas_map.items():
            for val in df_presentes[col].dropna():
                box_data.append({"Atividade": label, "Nota": val})
        df_box = pd.DataFrame(box_data)

        fig_box = px.box(
            df_box, x="Atividade", y="Nota", color="Atividade",
            title="Distribuição de notas por atividade",
        )
        fig_box.update_layout(
            **DARK, height=450, showlegend=False,
            xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_box, use_container_width=True)

        # Histogramas sobrepostos
        st.markdown('<p class="section-title">📉 Distribuição de Notas por Atividade</p>',
                    unsafe_allow_html=True)

        fig_hist_all = go.Figure()
        cores = ["#ef4444", "#f59e0b", "#3b82f6", "#22c55e", "#a855f7"]
        for i, (label, col) in enumerate(notas_map.items()):
            vals = df_presentes[col].dropna()
            fig_hist_all.add_trace(go.Histogram(
                x=vals, name=label, opacity=0.6,
                marker_color=cores[i], nbinsx=12,
            ))
        fig_hist_all.update_layout(
            **DARK, height=400, barmode="overlay",
            xaxis=dict(title="Nota", **GRID),
            yaxis=dict(title="Frequência", **GRID),
            title="Sobreposição de distribuições",
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_hist_all, use_container_width=True)

        # Correlação corrida x média
        st.markdown('<p class="section-title">🏃 Correlação: Corrida × Média Final</p>',
                    unsafe_allow_html=True)

        df_corr = df_presentes[df_presentes["NOTA_CORRIDA"].notna()].copy()
        fig_scatter = px.scatter(
            df_corr, x="NOTA_CORRIDA", y="MEDIA_FINAL",
            color="CLASSIFICACAO", color_discrete_map=COR_MAP,
            size="MEDIA_FINAL", hover_name="NOME",
            trendline="ols", trendline_color_override="#ffffff",
            labels={"NOTA_CORRIDA": "Nota Corrida", "MEDIA_FINAL": "Média Final"},
            title="Militares com maior nota na corrida tendem a ter média mais alta?",
        )
        fig_scatter.update_layout(
            **DARK, height=420,
            yaxis=dict(**GRID), xaxis=dict(**GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Tabela de percentis
        st.markdown('<p class="section-title">📊 Tabela de Percentis</p>',
                    unsafe_allow_html=True)

        percentis = [10, 25, 50, 75, 90]
        perc_data = {"Percentil": [f"P{p}" for p in percentis]}
        for label, col in notas_map.items():
            vals = df_presentes[col].dropna()
            perc_data[label] = [round(np.percentile(vals, p), 2) if len(vals) > 0 else 0
                                for p in percentis]
        perc_data["Média Final"] = [
            round(np.percentile(df_presentes["MEDIA_FINAL"].dropna(), p), 2)
            for p in percentis
        ]
        st.dataframe(pd.DataFrame(perc_data), use_container_width=True, hide_index=True)

        # Estatísticas descritivas
        st.markdown('<p class="section-title">📋 Estatísticas Descritivas</p>',
                    unsafe_allow_html=True)

        desc_cols = list(notas_map.values()) + ["MEDIA_FINAL"]
        desc_labels = list(notas_map.keys()) + ["Média Final"]
        desc = df_presentes[desc_cols].describe().T
        desc.index = desc_labels
        desc = desc[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
        desc.columns = ["N", "Média", "Desvio", "Mín", "P25", "Mediana", "P75", "Máx"]
        desc = desc.round(2)
        st.dataframe(desc, use_container_width=True)

        # Top 10 e Bottom 10
        st.markdown('<p class="section-title">🏆 Top 10 e Bottom 10</p>',
                    unsafe_allow_html=True)

        col_t, col_bt = st.columns(2)
        with col_t:
            st.markdown("**🥇 Top 10 — Maiores Médias**")
            top10 = df_presentes.nlargest(10, "MEDIA_FINAL")[
                ["NOME", "POSTO_GRAD", "QUADRO", "MEDIA_FINAL", "CLASSIFICACAO"]
            ].reset_index(drop=True)
            top10.index += 1
            st.dataframe(top10, use_container_width=True)

        with col_bt:
            st.markdown("**⚠️ Bottom 10 — Menores Médias**")
            bot10 = df_presentes.nsmallest(10, "MEDIA_FINAL")[
                ["NOME", "POSTO_GRAD", "QUADRO", "MEDIA_FINAL", "CLASSIFICACAO"]
            ].reset_index(drop=True)
            bot10.index += 1
            st.dataframe(bot10, use_container_width=True)

        # Valores brutos — desempenho real
        st.markdown('<p class="section-title">🔢 Desempenho Bruto (Valores Reais)</p>',
                    unsafe_allow_html=True)

        raw_stats = pd.DataFrame({
            "Exercício": ["Corrida 12min (m)", "Abdominal (reps)", "Flexão (reps)",
                          "Natação 50m (seg)", "Barra (valor)"],
            "Média": [
                df_presentes["CORRIDA_RAW"].mean(),
                df_presentes["ABDOMINAL_RAW"].mean(),
                df_presentes["FLEXAO_RAW"].mean(),
                df_presentes["NATACAO_RAW"].mean(),
                df_presentes["BARRA_RAW"].mean(),
            ],
            "Mediana": [
                df_presentes["CORRIDA_RAW"].median(),
                df_presentes["ABDOMINAL_RAW"].median(),
                df_presentes["FLEXAO_RAW"].median(),
                df_presentes["NATACAO_RAW"].median(),
                df_presentes["BARRA_RAW"].median(),
            ],
            "Mínimo": [
                df_presentes["CORRIDA_RAW"].min(),
                df_presentes["ABDOMINAL_RAW"].min(),
                df_presentes["FLEXAO_RAW"].min(),
                df_presentes["NATACAO_RAW"].min(),
                df_presentes["BARRA_RAW"].min(),
            ],
            "Máximo": [
                df_presentes["CORRIDA_RAW"].max(),
                df_presentes["ABDOMINAL_RAW"].max(),
                df_presentes["FLEXAO_RAW"].max(),
                df_presentes["NATACAO_RAW"].max(),
                df_presentes["BARRA_RAW"].max(),
            ],
        }).round(1)
        st.dataframe(raw_stats, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: TAF ADAPTADO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "♿ TAF Adaptado":
    st.markdown("""
    <h1 style="margin:0;font-size:2rem;">♿ TAF Adaptado</h1>
    <p style="margin:6px 0 12px;color:#94a3b8;">
      Dados dos militares que realizaram o TAF na modalidade adaptada
    </p>
    """, unsafe_allow_html=True)
    st.divider()

    if len(df_adaptado) == 0:
        st.warning("Nenhum dado de TAF Adaptado encontrado.")
    else:
        # KPIs
        total_adapt = len(df_adaptado)
        presentes_adapt = int(df_adaptado["PRESENTE"].sum())
        ausentes_adapt = total_adapt - presentes_adapt

        k1, k2, k3 = st.columns(3)
        k1.metric("👥 Total", total_adapt)
        k2.metric("✅ Presentes", presentes_adapt)
        k3.metric("❌ Ausentes", ausentes_adapt)

        st.divider()

        # Por posto
        st.markdown('<p class="section-title">🪖 Efetivo por Posto/Graduação</p>',
                    unsafe_allow_html=True)

        adapt_posto = df_adaptado.groupby("POSTO_GRAD").size().reset_index(name="Quantidade")
        adapt_posto["_ordem"] = adapt_posto["POSTO_GRAD"].apply(ordem_posto)
        adapt_posto = adapt_posto.sort_values("_ordem").drop(columns=["_ordem"])

        fig_adapt = px.bar(
            adapt_posto, x="POSTO_GRAD", y="Quantidade",
            color="Quantidade",
            color_continuous_scale=["#3b82f6", "#22c55e"],
            text="Quantidade",
            labels={"POSTO_GRAD": "Posto/Graduação"},
            title="Militares no TAF Adaptado por posto",
        )
        fig_adapt.update_traces(textposition="outside")
        fig_adapt.update_layout(
            **DARK, height=350, coloraxis_showscale=False,
            xaxis=dict(**GRID), yaxis=dict(**GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_adapt, use_container_width=True)

        # Tabela de dados
        st.markdown('<p class="section-title">📋 Dados Completos — TAF Adaptado</p>',
                    unsafe_allow_html=True)

        display_cols = [c for c in df_adaptado.columns if c not in ["PRESENTE", "_ordem"]]
        df_adapt_display = df_adaptado[display_cols].copy()
        df_adapt_display = df_adapt_display.fillna("—")

        # Limpar valores "nan"
        for col in df_adapt_display.columns:
            df_adapt_display[col] = df_adapt_display[col].astype(str).replace("nan", "—")

        st.dataframe(df_adapt_display, use_container_width=True, height=500)

        # Exercícios realizados
        st.markdown('<p class="section-title">📊 Exercícios Realizados</p>',
                    unsafe_allow_html=True)

        exercicios_adapt = ["CAMINHADA", "ABDOMINAL", "FLEXAO", "PRANCHA", "NATACAO",
                            "BARRA_EST", "BARRA_DIN", "CORRIDA", "PUXADOR_FRONTAL",
                            "FLUTUACAO", "SUPINO", "COOPER"]
        ex_count = {}
        for ex in exercicios_adapt:
            # Verifica se a coluna existe no DataFrame antes de tentar acessá-la
            if ex in df_adaptado.columns:
                count = df_adaptado[ex].dropna().apply(
                    lambda x: str(x).strip() not in ("", "nan", "NÃO COMPARECEU", "NÃO")
                ).sum()
                ex_count[ex] = count
            else:
                # Se a coluna não existe, pode-se adicionar com 0 ou ignorar
                ex_count[ex] = 0 # Adiciona com 0 se a coluna não existir

        ex_df = pd.DataFrame({
            "Exercício": list(ex_count.keys()),
            "Realizaram": list(ex_count.values()),
        }).sort_values("Realizaram", ascending=False)
        ex_df = ex_df[ex_df["Realizaram"] > 0]

        if len(ex_df) > 0:
            fig_ex = px.bar(
                ex_df, x="Exercício", y="Realizaram",
                color="Realizaram",
                color_continuous_scale=["#f59e0b", "#22c55e"],
                text="Realizaram",
                title="Quantidade de militares por exercício (TAF Adaptado)",
            )
            fig_ex.update_traces(textposition="outside")
            fig_ex.update_layout(
                **DARK, height=400, coloraxis_showscale=False,
                xaxis=dict(**GRID, tickangle=-45),
                yaxis=dict(**GRID),
                margin=dict(t=50, b=20),
            )
            st.plotly_chart(fig_ex, use_container_width=True)

        st.info(
            "ℹ️ O TAF Adaptado avalia militares com necessidades especiais ou "
            "restrições médicas, utilizando exercícios alternativos conforme "
            "aptidão individual. Cada militar realiza um conjunto diferente de provas."
        )
