import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ══════════════════════════════════════════════════════════════════════════════
# TEMA (CLARO/ESCURO)
# ══════════════════════════════════════════════════════════════════════════════

def get_theme_config():
    """Retorna configuração de cores baseada no tema selecionado"""
    if st.session_state.get("tema", "escuro") == "claro":
        return {
            "bg_primary": "#ffffff",
            "bg_secondary": "#f8f9fa",
            "bg_tertiary": "#e9ecef",
            "text_primary": "#1a1a1a",
            "text_secondary": "#495057",
            "border_color": "rgba(0,0,0,0.1)",
            "input_bg": "#ffffff",
            "input_border": "rgba(0,0,0,0.2)",
            "accent": "#0066cc",
            "card_bg": "rgba(240,242,246,0.9)",
            "card_border": "rgba(0,0,0,0.15)",
            "badge_bg_good": "#d1fae5", "badge_text_good": "#065f46", "badge_border_good": "rgba(16,185,129,0.3)",
            "badge_bg_avg": "#fef3c7", "badge_text_avg": "#92400e", "badge_border_avg": "rgba(251,191,36,0.3)",
            "badge_bg_bad": "#fee2e2", "badge_text_bad": "#991b1b", "badge_border_bad": "rgba(239,68,68,0.3)",
            "badge_bg_neutral": "#e0e7ff", "badge_text_neutral": "#3730a3", "badge_border_neutral": "rgba(99,102,241,0.3)",
        }
    else:
        return {
            "bg_primary": "#0b1220",
            "bg_secondary": "#111b2e",
            "bg_tertiary": "#1a2847",
            "text_primary": "#ffffff",
            "text_secondary": "#94a3b8",
            "border_color": "rgba(255,255,255,0.08)",
            "input_bg": "rgba(6,10,16,0.96)",
            "input_border": "rgba(255,255,255,0.08)",
            "accent": "#3b82f6",
            "card_bg": "rgba(17,27,46,0.95)",
            "card_border": "rgba(59,130,246,0.4)",
            "badge_bg_good": "#166534", "badge_text_good": "#bbf7d0", "badge_border_good": "rgba(34,197,94,0.3)",
            "badge_bg_avg": "#92400e", "badge_text_avg": "#fef3c7", "badge_border_avg": "rgba(251,191,36,0.3)",
            "badge_bg_bad": "#991b1b", "badge_text_bad": "#fee2e2", "badge_border_bad": "rgba(239,68,68,0.3)",
            "badge_bg_neutral": "#3730a3", "badge_text_neutral": "#e0e7ff", "badge_border_neutral": "rgba(99,102,241,0.3)",
        }

# ══════════════════════════════════════════════════════════════════════════════
# IMAGEM CBMAM
# ══════════════════════════════════════════════════════════════════════════════

def _get_cbmam_image_url() -> str:
    """Retorna URL oficial do brasão do CBMAM"""
    return "https://i.imgur.com/8QfQ2vF.png"

def _find_local_logo():
    """Procura por logo local em assets/"""
    base = Path(__file__).resolve().parent
    search_folders = [base, base / "assets", base.parent / "assets", base.parent]
    exts = ["png", "jpg", "jpeg", "svg", "webp", "gif"]

    for folder in search_folders:
        try:
            if not folder.exists():
                continue
            for ext in exts:
                p = folder / f"logo.{ext}"
                if p.exists():
                    return p
            for f in folder.iterdir():
                if f.is_file() and f.name.lower().startswith("logo."):
                    return f
        except Exception:
            continue
    return None

_LOCAL_LOGO_PATH = _find_local_logo()

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO INICIAL
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="CBMAM · Dashboard TAF",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar session state
if "tema" not in st.session_state:
    st.session_state.tema = "escuro"

# ══════════════════════════════════════════════════════════════════════════════
# CSS DINÂMICO BASEADO NO TEMA
# ══════════════════════════════════════════════════════════════════════════════

def apply_theme_css():
    """Aplica CSS dinâmico baseado no tema"""
    theme = get_theme_config()

    css = f"""
    <style>
        /* Reset de cores para elementos específicos que o Streamlit sobrescreve */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {{
            color: {theme['text_primary']};
        }}

        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(135deg, {theme['bg_primary']} 0%, {theme['bg_secondary']} 100%);
        }}

        [data-testid="stSidebar"] {{
            background: {theme['bg_secondary']};
            border-right: 1px solid {theme['border_color']};
        }}

        /* Títulos */
        h1, h2, h3, h4, h5, h6 {{
            color: {theme['text_primary']};
        }}

        /* Parágrafos e texto geral */
        p, label, .stMarkdown, .stText {{
            color: {theme['text_primary']};
        }}

        /* Inputs */
        input, textarea, select {{
            color: {theme['text_primary']} !important;
            background-color: {theme['input_bg']} !important;
            border: 1px solid {theme['input_border']} !important;
            border-radius: 6px !important;
        }}

        input::placeholder {{
            color: {theme['text_secondary']} !important;
            opacity: 0.8 !important;
        }}

        /* Selectbox */
        [data-testid="stSelectbox"] div[data-baseweb="select"] {{
            background-color: {theme['input_bg']} !important;
            border: 1px solid {theme['input_border']} !important;
            border-radius: 6px !important;
        }}
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child {{
            color: {theme['text_primary']} !important;
        }}
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child:hover {{
            border-color: {theme['accent']} !important;
        }}
        .st-emotion-cache-16idsd6 p {{ /* Selectbox options */
            color: {theme['text_primary']} !important;
        }}
        .st-emotion-cache-16idsd6 .st-emotion-cache-1wivf87 {{ /* Selectbox dropdown */
            background-color: {theme['input_bg']} !important;
            border: 1px solid {theme['input_border']} !important;
        }}
        .st-emotion-cache-16idsd6 .st-emotion-cache-1wivf87 div[role="option"] {{
            color: {theme['text_primary']} !important;
        }}
        .st-emotion-cache-16idsd6 .st-emotion-cache-1wivf87 div[role="option"]:hover {{
            background-color: {theme['bg_tertiary']} !important;
        }}

        /* Botões */
        .stButton > button {{
            background-color: {theme['accent']};
            color: {theme['text_primary']};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .stButton > button:hover {{
            background-color: {theme['accent']}D0; /* Um pouco mais escuro */
            color: {theme['text_primary']};
        }}
        .stButton > button:focus {{
            box-shadow: 0 0 0 2px {theme['accent']}80;
        }}

        /* Dataframe */
        .stDataFrame {{
            color: {theme['text_primary']};
        }}
        .stDataFrame .dataframe {{
            background-color: {theme['card_bg']};
            color: {theme['text_primary']};
            border: 1px solid {theme['card_border']};
            border-radius: 8px;
        }}
        .stDataFrame .dataframe th {{
            background-color: {theme['bg_tertiary']};
            color: {theme['text_primary']};
            border-bottom: 1px solid {theme['border_color']};
        }}
        .stDataFrame .dataframe td {{
            color: {theme['text_primary']};
            border-bottom: 1px solid {theme['border_color']};
        }}

        /* Metrics */
        [data-testid="stMetric"] {{
            background-color: {theme['card_bg']};
            border: 1px solid {theme['card_border']};
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,.1);
        }}
        [data-testid="stMetric"] label {{
            color: {theme['text_secondary']};
            font-size: 0.9rem;
        }}
        [data-testid="stMetric"] div[data-testid="stMetricValue"] {{
            color: {theme['text_primary']};
            font-size: 2.2rem;
            font-weight: 700;
        }}
        [data-testid="stMetric"] div[data-testid="stMetricDelta"] {{
            color: {theme['text_primary']};
            font-size: 1rem;
        }}

        /* Dividers */
        .st-emotion-cache-10q0tfy {{ /* Divider line */
            background-color: {theme['border_color']};
        }}

        /* Custom section titles */
        .section-title {{
            font-size: 1.3rem;
            font-weight: 600;
            color: {theme['text_primary']};
            margin-top: 20px;
            margin-bottom: 15px;
            border-bottom: 2px solid {theme['accent']};
            padding-bottom: 5px;
        }}

        /* Custom card for individual ficha */
        .ficha-header-card {{
            background: linear-gradient(135deg, {theme['card_bg']} 0%, {theme['bg_tertiary']} 100%);
            border: 1px solid {theme['card_border']};
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 20px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }}
        .ficha-header-card .title {{
            font-size: 1.8rem;
            font-weight: 800;
            color: {theme['text_primary']};
        }}
        .ficha-header-card .subtitle {{
            color: {theme['text_secondary']};
            margin-top: 4px;
        }}
        .ficha-header-card .badge-container {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .ficha-header-card .badge {{
            border-radius: 12px;
            padding: 10px 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .ficha-header-card .badge .label {{
            font-size: .75rem;
            color: {theme['text_secondary']};
        }}
        .ficha-header-card .badge .value {{
            font-size: 1.3rem;
            font-weight: 800;
            color: {theme['text_primary']}; /* Default, overridden by specific badge colors */
        }}

        /* Raw data cards */
        .raw-data-card {{
            background: {theme['card_bg']};
            border: 2px solid {theme['card_border']};
            border-radius: 14px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,.3);
        }}
        .raw-data-card .label {{
            font-size: .7rem;
            color: {theme['text_secondary']};
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .raw-data-card .value {{
            font-size: 1.8rem;
            font-weight: 900;
            color: {theme['accent']};
            margin: 6px 0;
        }}
        .raw-data-card .unit {{
            font-size: .65rem;
            color: {theme['text_secondary']};
            font-weight: 500;
        }}

        /* Detailed activity cards */
        .activity-card {{
            background: {theme['card_bg']};
            border: 1px solid {theme['card_border']};
            border-radius: 14px;
            padding: 16px;
            text-align: center;
        }}
        .activity-card .label {{
            font-size: .8rem;
            color: {theme['text_secondary']};
            margin-bottom: 8px;
        }}
        .activity-card .value {{
            font-size: 2rem;
            font-weight: 800;
            color: {theme['text_primary']};
        }}
        .activity-card .delta {{
            font-size: .8rem;
            margin-top: 4px;
        }}
        .activity-card .progress-bar {{
            background: rgba(255,255,255,.06);
            border-radius: 6px;
            margin-top: 10px;
            height: 6px;
            overflow: hidden;
        }}
        .activity-card .progress-fill {{
            height: 100%;
            border-radius: 6px;
        }}

        /* Summary card */
        .summary-card {{
            background: {theme['card_bg']};
            border: 1px solid {theme['card_border']};
            border-radius: 14px;
            padding: 20px;
            margin-top: 10px;
            line-height: 2;
            color: {theme['text_primary']};
        }}
        .summary-card b {{
            color: {theme['text_primary']};
        }}
        .summary-card span {{
            font-weight: 700;
        }}

        /* Info boxes */
        .stAlert {{
            background-color: {theme['bg_tertiary']} !important;
            color: {theme['text_primary']} !important;
            border-color: {theme['border_color']} !important;
        }}
        .stAlert > div > div > div > p {{
            color: {theme['text_primary']} !important;
        }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Aplica o CSS dinâmico
apply_theme_css()

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DE PLOTLY
# ══════════════════════════════════════════════════════════════════════════════

theme = get_theme_config()

DARK = {
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "font_color": theme['text_primary'],
    "xaxis": {"gridcolor": theme['border_color'], "zerolinecolor": theme['border_color']},
    "yaxis": {"gridcolor": theme['border_color'], "zerolinecolor": theme['border_color']},
    "legend": {"font_color": theme['text_primary']},
}

GRID = {
    "showgrid": True,
    "gridwidth": 1,
    "gridcolor": theme['border_color'],
    "zeroline": True,
    "zerolinewidth": 1,
    "zerolinecolor": theme['border_color'],
}

COR_MAP = {
    "Excelente": "#22c55e",
    "Bom": "#3b82f6",
    "Regular": "#f59e0b",
    "Insuficiente": "#ef4444",
}

# ══════════════════════════════════════════════════════════════════════════════
# REGRAS DE PONTUAÇÃO (ADAPTADAS PARA O SEU CSV)
# ══════════════════════════════════════════════════════════════════════════════

# As regras de pontuação devem ser definidas aqui, com base na idade e sexo.
# Exemplo de estrutura (ajuste conforme as regras reais do CBMAM):
# {
#     "Corrida": {
#         "Masculino": {
#             (18, 24): [(1800, 0), (2000, 2), (2200, 4), (2400, 6), (2600, 8), (2800, 10)],
#             (25, 29): [(1700, 0), (1900, 2), (2100, 4), (2300, 6), (2500, 8), (2700, 10)],
#             ...
#         },
#         "Feminino": { ... }
#     },
#     "Abdominal": { ... },
#     ...
# }

# Para simplificar, vou usar um conjunto de regras genéricas e você pode ajustá-las.
# A estrutura deve ser: (limite_inferior, pontuacao)
# Para corrida, é distância (m). Para abdominal/flexão, é repetições. Para natação, é tempo (s). Para barra, é repetições ou tempo (s).

REGRAS_MASCULINO = {
    "Corrida": {
        (18, 24): [(1800, 0), (2000, 2), (2200, 4), (2400, 6), (2600, 8), (2800, 10)],
        (25, 29): [(1700, 0), (1900, 2), (2100, 4), (2300, 6), (2500, 8), (2700, 10)],
        (30, 34): [(1600, 0), (1800, 2), (2000, 4), (2200, 6), (2400, 8), (2600, 10)],
        (35, 39): [(1500, 0), (1700, 2), (1900, 4), (2100, 6), (2300, 8), (2500, 10)],
        (40, 44): [(1400, 0), (1600, 2), (1800, 4), (2000, 6), (2200, 8), (2400, 10)],
        (45, 49): [(1300, 0), (1500, 2), (1700, 4), (1900, 6), (2100, 8), (2300, 10)],
        (50, 54): [(1200, 0), (1400, 2), (1600, 4), (1800, 6), (2000, 8), (2200, 10)],
        (55, 99): [(1100, 0), (1300, 2), (1500, 4), (1700, 6), (1900, 8), (2100, 10)],
    },
    "Abdominal": {
        (18, 24): [(25, 0), (30, 2), (35, 4), (40, 6), (45, 8), (50, 10)],
        (25, 29): [(23, 0), (28, 2), (33, 4), (38, 6), (43, 8), (48, 10)],
        (30, 34): [(21, 0), (26, 2), (31, 4), (36, 6), (41, 8), (46, 10)],
        (35, 39): [(19, 0), (24, 2), (29, 4), (34, 6), (39, 8), (44, 10)],
        (40, 44): [(17, 0), (22, 2), (27, 4), (32, 6), (37, 8), (42, 10)],
        (45, 49): [(15, 0), (20, 2), (25, 4), (30, 6), (35, 8), (40, 10)],
        (50, 54): [(13, 0), (18, 2), (23, 4), (28, 6), (33, 8), (38, 10)],
        (55, 99): [(11, 0), (16, 2), (21, 4), (26, 6), (31, 8), (36, 10)],
    },
    "Flexao": {
        (18, 24): [(15, 0), (20, 2), (25, 4), (30, 6), (35, 8), (40, 10)],
        (25, 29): [(13, 0), (18, 2), (23, 4), (28, 6), (33, 8), (38, 10)],
        (30, 34): [(11, 0), (16, 2), (21, 4), (26, 6), (31, 8), (36, 10)],
        (35, 39): [(9, 0), (14, 2), (19, 4), (24, 6), (29, 8), (34, 10)],
        (40, 44): [(7, 0), (12, 2), (17, 4), (22, 6), (27, 8), (32, 10)],
        (45, 49): [(5, 0), (10, 2), (15, 4), (20, 6), (25, 8), (30, 10)],
        (50, 54): [(3, 0), (8, 2), (13, 4), (18, 6), (23, 8), (28, 10)],
        (55, 99): [(1, 0), (6, 2), (11, 4), (16, 6), (21, 8), (26, 10)],
    },
    "Natacao": { # Tempo em segundos (menor tempo = melhor)
        (18, 24): [(60, 0), (55, 2), (50, 4), (45, 6), (40, 8), (35, 10)],
        (25, 29): [(65, 0), (60, 2), (55, 4), (50, 6), (45, 8), (40, 10)],
        (30, 34): [(70, 0), (65, 2), (60, 4), (55, 6), (50, 8), (45, 10)],
        (35, 39): [(75, 0), (70, 2), (65, 4), (60, 6), (55, 8), (50, 10)],
        (40, 44): [(80, 0), (75, 2), (70, 4), (65, 6), (60, 8), (55, 10)],
        (45, 49): [(85, 0), (80, 2), (75, 4), (70, 6), (65, 8), (60, 10)],
        (50, 54): [(90, 0), (85, 2), (80, 4), (75, 6), (70, 8), (65, 10)],
        (55, 99): [(95, 0), (90, 2), (85, 4), (80, 6), (75, 8), (70, 10)],
    },
    "Barra": { # Repetições ou tempo em segundos (maior = melhor)
        (18, 24): [(1, 0), (3, 2), (5, 4), (7, 6), (9, 8), (11, 10)], # Repetições
        (25, 29): [(1, 0), (2, 2), (4, 4), (6, 6), (8, 8), (10, 10)],
        (30, 34): [(0, 0), (1, 2), (3, 4), (5, 6), (7, 8), (9, 10)],
        (35, 39): [(0, 0), (1, 2), (2, 4), (4, 6), (6, 8), (8, 10)],
        (40, 44): [(0, 0), (0, 2), (1, 4), (3, 6), (5, 8), (7, 10)],
        (45, 49): [(0, 0), (0, 2), (0, 4), (2, 6), (4, 8), (6, 10)],
        (50, 54): [(0, 0), (0, 2), (0, 4), (1, 6), (3, 8), (5, 10)],
        (55, 99): [(0, 0), (0, 2), (0, 4), (0, 6), (2, 8), (4, 10)],
    },
}

REGRAS_FEMININO = {
    "Corrida": {
        (18, 24): [(1600, 0), (1800, 2), (2000, 4), (2200, 6), (2400, 8), (2600, 10)],
        (25, 29): [(1500, 0), (1700, 2), (1900, 4), (2100, 6), (2300, 8), (2500, 10)],
        (30, 34): [(1400, 0), (1600, 2), (1800, 4), (2000, 6), (2200, 8), (2400, 10)],
        (35, 39): [(1300, 0), (1500, 2), (1700, 4), (1900, 6), (2100, 8), (2300, 10)],
        (40, 44): [(1200, 0), (1400, 2), (1600, 4), (1800, 6), (2000, 8), (2200, 10)],
        (45, 49): [(1100, 0), (1300, 2), (1500, 4), (1700, 6), (1900, 8), (2100, 10)],
        (50, 54): [(1000, 0), (1200, 2), (1400, 4), (1600, 6), (1800, 8), (2000, 10)],
        (55, 99): [(900, 0), (1100, 2), (1300, 4), (1500, 6), (1700, 8), (1900, 10)],
    },
    "Abdominal": {
        (18, 24): [(20, 0), (25, 2), (30, 4), (35, 6), (40, 8), (45, 10)],
        (25, 29): [(18, 0), (23, 2), (28, 4), (33, 6), (38, 8), (43, 10)],
        (30, 34): [(16, 0), (21, 2), (26, 4), (31, 6), (36, 8), (41, 10)],
        (35, 39): [(14, 0), (19, 2), (24, 4), (29, 6), (34, 8), (39, 10)],
        (40, 44): [(12, 0), (17, 2), (22, 4), (27, 6), (32, 8), (37, 10)],
        (45, 49): [(10, 0), (15, 2), (20, 4), (25, 6), (30, 8), (35, 10)],
        (50, 54): [(8, 0), (13, 2), (18, 4), (23, 6), (28, 8), (33, 10)],
        (55, 99): [(6, 0), (11, 2), (16, 4), (21, 6), (26, 8), (31, 10)],
    },
    "Flexao": { # Flexão de joelhos para feminino
        (18, 24): [(10, 0), (15, 2), (20, 4), (25, 6), (30, 8), (35, 10)],
        (25, 29): [(8, 0), (13, 2), (18, 4), (23, 6), (28, 8), (33, 10)],
        (30, 34): [(6, 0), (11, 2), (16, 4), (21, 6), (26, 8), (31, 10)],
        (35, 39): [(4, 0), (9, 2), (14, 4), (19, 6), (24, 8), (29, 10)],
        (40, 44): [(2, 0), (7, 2), (12, 4), (17, 6), (22, 8), (27, 10)],
        (45, 49): [(0, 0), (5, 2), (10, 4), (15, 6), (20, 8), (25, 10)],
        (50, 54): [(0, 0), (3, 2), (8, 4), (13, 6), (18, 8), (23, 10)],
        (55, 99): [(0, 0), (1, 2), (6, 4), (11, 6), (16, 8), (21, 10)],
    },
    "Natacao": { # Tempo em segundos (menor tempo = melhor)
        (18, 24): [(70, 0), (65, 2), (60, 4), (55, 6), (50, 8), (45, 10)],
        (25, 29): [(75, 0), (70, 2), (65, 4), (60, 6), (55, 8), (50, 10)],
        (30, 34): [(80, 0), (75, 2), (70, 4), (65, 6), (60, 8), (55, 10)],
        (35, 39): [(85, 0), (80, 2), (75, 4), (70, 6), (65, 8), (60, 10)],
        (40, 44): [(90, 0), (85, 2), (80, 4), (75, 6), (70, 8), (65, 10)],
        (45, 49): [(95, 0), (90, 2), (85, 4), (80, 6), (75, 8), (70, 10)],
        (50, 54): [(100, 0), (95, 2), (90, 4), (85, 6), (80, 8), (75, 10)],
        (55, 99): [(105, 0), (100, 2), (95, 4), (90, 6), (85, 8), (80, 10)],
    },
    "Barra": { # Barra estática (tempo em segundos) ou dinâmica (repetições)
        (18, 24): [(5, 0), (10, 2), (15, 4), (20, 6), (25, 8), (30, 10)], # Tempo em segundos
        (25, 29): [(4, 0), (8, 2), (12, 4), (16, 6), (20, 8), (24, 10)],
        (30, 34): [(3, 0), (6, 2), (9, 4), (12, 6), (15, 8), (18, 10)],
        (35, 39): [(2, 0), (4, 2), (6, 4), (8, 6), (10, 8), (12, 10)],
        (40, 44): [(1, 0), (2, 2), (3, 4), (4, 6), (5, 8), (6, 10)],
        (45, 49): [(0, 0), (1, 2), (2, 4), (3, 6), (4, 8), (5, 10)],
        (50, 54): [(0, 0), (0, 2), (1, 4), (2, 6), (3, 8), (4, 10)],
        (55, 99): [(0, 0), (0, 2), (0, 4), (1, 6), (2, 8), (3, 10)],
    },
}

def calcular_idade(data_nascimento):
    """Calcula a idade a partir da data de nascimento."""
    if pd.isna(data_nascimento):
        return np.nan
    today = datetime.today()
    return today.year - data_nascimento.year - ((today.month, today.day) < (data_nascimento.month, data_nascimento.day))

def get_faixa_etaria(idade):
    """Retorna a faixa etária para uma dada idade."""
    if pd.isna(idade):
        return "Não Informado"
    if idade < 25: return "18-24"
    elif idade < 30: return "25-29"
    elif idade < 35: return "30-34"
    elif idade < 40: return "35-39"
    elif idade < 45: return "40-44"
    elif idade < 50: return "45-49"
    elif idade < 55: return "50-54"
    else: return "55+"

def calcular_pontuacao(exercicio, valor, sexo, idade):
    """Calcula a pontuação para um exercício, sexo e idade."""
    if pd.isna(valor) or pd.isna(sexo) or pd.isna(idade):
        return np.nan

    regras = REGRAS_MASCULINO if sexo == "Masculino" else REGRAS_FEMININO
    regras_exercicio = regras.get(exercicio)

    if not regras_exercicio:
        return np.nan

    for faixa, pontos_faixa in regras_exercicio.items():
        if faixa[0] <= idade <= faixa[1]:
            # Para natação, menor tempo é melhor, então invertemos a lógica de busca
            if exercicio == "Natacao":
                pontos_faixa = sorted(pontos_faixa, key=lambda x: x[0], reverse=True)
                for limite, pontuacao in pontos_faixa:
                    if valor <= limite:
                        return pontuacao
                return 0 # Se for pior que o pior limite, pontuação 0
            else: # Para corrida, abdominal, flexão, barra (maior é melhor)
                pontos_faixa = sorted(pontos_faixa, key=lambda x: x[0])
                for limite, pontuacao in pontos_faixa:
                    if valor >= limite:
                        return pontuacao
                return 0 # Se for pior que o pior limite, pontuação 0
    return np.nan

def classificar_desempenho(media_final):
    """Classifica o desempenho com base na média final."""
    if pd.isna(media_final):
        return "Não Avaliado"
    if media_final >= 9.0:
        return "Excelente"
    elif media_final >= 7.5:
        return "Bom"
    elif media_final >= 6.0:
        return "Regular"
    else:
        return "Insuficiente"

def identificar_ponto_fraco(row, exercicios):
    """Identifica o ponto fraco do militar (menor pontuação)."""
    pontuacoes = {ex: row[f"PONTUACAO_{ex.upper()}"] for ex in exercicios if pd.notna(row[f"PONTUACAO_{ex.upper()}"])}
    if not pontuacoes:
        return "N/A"
    return min(pontuacoes, key=pontuacoes.get)

def parse_barra_value(value):
    """Converte o valor da barra para segundos (estática) ou repetições (dinâmica)."""
    if pd.isna(value) or not isinstance(value, str):
        return np.nan
    value = value.strip().lower()
    if "não" in value or "nc" in value:
        return np.nan

    # Repetições
    if re.match(r"^\d+$", value):
        return float(value)

    # Tempo em segundos (xx" ou 01'01")
    match_min_sec = re.match(r"(\d+)'(\d+)\"", value)
    match_sec = re.match(r"(\d+)\"", value)

    if match_min_sec:
        minutes = int(match_min_sec.group(1))
        seconds = int(match_min_sec.group(2))
        return float(minutes * 60 + seconds)
    elif match_sec:
        return float(match_sec.group(1))

    return np.nan

def parse_corrida_value(value):
    """Converte o valor da corrida para metros."""
    if pd.isna(value) or not isinstance(value, str):
        return np.nan
    value = value.strip().lower()
    if "não" in value or "nc" in value:
        return np.nan

    # Metros
    if re.match(r"^\d+$", value):
        return float(value)

    # Tempo em minutos e segundos (ex: 24'51") - converter para metros (aproximação)
    # Assumindo que o valor é o tempo em minutos e segundos, e precisamos de metros.
    # Se "24'51"" significa 24 minutos e 51 segundos, e o exercício é corrida de 12 minutos,
    # então este valor é o tempo total para uma distância X, não a distância.
    # O CSV parece ter "24'51"" na coluna Corrida para um militar, mas outros têm "2000".
    # Vamos assumir que se for tempo, é um erro de entrada e o valor esperado é metros.
    # Para o caso "24'51"", vou retornar NaN, pois não é uma distância em metros.
    match_min_sec = re.match(r"(\d+)'(\d+)\"", value)
    if match_min_sec:
        return np.nan # Não é uma distância em metros

    return np.nan # Caso não seja número ou formato de tempo reconhecido

def parse_natacao_value(value):
    """Converte o valor da natação para segundos."""
    if pd.isna(value) or not isinstance(value, str):
        return np.nan
    value = value.strip().lower()
    if "não" in value or "nc" in value:
        return np.nan

    # Segundos
    if re.match(r"^\d+(\.\d+)?$", value):
        return float(value)

    return np.nan

def parse_abdominal_flexao_value(value):
    """Converte o valor de abdominal/flexão para repetições."""
    if pd.isna(value) or not isinstance(value, str):
        return np.nan
    value = value.strip().lower()
    if "não" in value or "nc" in value:
        return np.nan

    # Repetições
    match_reps = re.match(r"(\d+)\s*rep", value)
    if match_reps:
        return float(match_reps.group(1))
    elif re.match(r"^\d+$", value):
        return float(value)

    return np.nan

# ══════════════════════════════════════════════════════════════════════════════
# CARREGAMENTO E PRÉ-PROCESSAMENTO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    df = pd.read_csv("master_taf_consolidado.csv")

    # Renomear colunas para facilitar o acesso
    df.columns = [col.strip().replace(" ", "_").replace("/", "_").upper() for col in df.columns]

    # Preencher valores ausentes para CPF e DataNascimento para evitar erros
    df["CPF"] = df["CPF"].fillna("Não Informado")
    df["DATA_NASCIMENTO"] = df["DATA_NASCIMENTO"].fillna("01/01/1900") # Data placeholder

    # Converter DataNascimento para datetime
    df["DATA_NASCIMENTO"] = pd.to_datetime(df["DATA_NASCIMENTO"], format="%d/%m/%Y", errors="coerce")

    # Calcular idade e faixa etária
    df["IDADE"] = df["DATA_NASCIMENTO"].apply(calcular_idade)
    df["FAIXA_ETARIA"] = df["IDADE"].apply(get_faixa_etaria)

    # Padronizar Sexo
    df["SEXO"] = df["SEXO"].replace({"M": "Masculino", "F": "Feminino"}).fillna("Não Informado")

    # Limpeza e conversão dos resultados dos exercícios
    exercicios_cols = ["CORRIDA", "ABDOMINAL", "FLEXAO", "NATACAO", "BARRA"]

    # Identificar militares que não compareceram ou não fizeram nenhum exercício
    df["PRESENTE"] = True
    for col in exercicios_cols:
        df[col] = df[col].astype(str).str.strip().str.upper()
        df.loc[df[col].isin(["NÃO COMPARECEU", "NÃO", "NÃO CONSTA NENHUM EXERCICIO", "NC", "NAO"]), "PRESENTE"] = False

    # Marcar como ausente se todos os exercícios forem NaN após a limpeza inicial
    df.loc[df[exercicios_cols].isnull().all(axis=1), "PRESENTE"] = False

    # Aplicar funções de parse para cada exercício
    df["CORRIDA"] = df["CORRIDA"].apply(parse_corrida_value)
    df["ABDOMINAL"] = df["ABDOMINAL"].apply(parse_abdominal_flexao_value)
    df["FLEXAO"] = df["FLEXAO"].apply(parse_abdominal_flexao_value)
    df["NATACAO_SEG"] = df["NATACAO"].apply(parse_natacao_value) # Renomear para evitar conflito
    df["BARRA_VALOR"] = df["BARRA"].apply(parse_barra_value) # Renomear para evitar conflito

    # Calcular pontuações
    df["PONTUACAO_CORRIDA"] = df.apply(lambda row: calcular_pontuacao("Corrida", row["CORRIDA"], row["SEXO"], row["IDADE"]), axis=1)
    df["PONTUACAO_ABDOMINAL"] = df.apply(lambda row: calcular_pontuacao("Abdominal", row["ABDOMINAL"], row["SEXO"], row["IDADE"]), axis=1)
    df["PONTUACAO_FLEXAO"] = df.apply(lambda row: calcular_pontuacao("Flexao", row["FLEXAO"], row["SEXO"], row["IDADE"]), axis=1)
    df["PONTUACAO_NATACAO"] = df.apply(lambda row: calcular_pontuacao("Natacao", row["NATACAO_SEG"], row["SEXO"], row["IDADE"]), axis=1)
    df["PONTUACAO_BARRA"] = df.apply(lambda row: calcular_pontuacao("Barra", row["BARRA_VALOR"], row["SEXO"], row["IDADE"]), axis=1)

    # Calcular Média Final (apenas para quem compareceu e tem pontuações válidas)
    pontuacao_cols = ["PONTUACAO_CORRIDA", "PONTUACAO_ABDOMINAL", "PONTUACAO_FLEXAO", "PONTUACAO_NATACAO", "PONTUACAO_BARRA"]

    # Apenas considerar pontuações válidas para a média
    df["MEDIA_FINAL"] = df[pontuacao_cols].mean(axis=1)

    # Classificar desempenho
    df["CLASSIFICACAO"] = df["MEDIA_FINAL"].apply(classificar_desempenho)

    # Identificar ponto fraco
    df["PONTO_FRACO"] = df.apply(lambda row: identificar_ponto_fraco(row, ["Corrida", "Abdominal", "Flexao", "Natacao", "Barra"]), axis=1)

    # Separar TAF Adaptado (exemplo: se o quadro for "QPEBM" ou "QOABM" e tiver valores "NÃO" em exercícios principais)
    # Ou, mais robusto, se houver uma coluna explícita para TAF Adaptado.
    # Por enquanto, vou usar uma heurística: se o militar tem alguma pontuação NaN mas está presente, pode ser adaptado.
    # Ou se a coluna "Corrida" ou "Flexao" tem valores como "NÃO CONSTA NENHUM EXERCICIO" mas não foi marcado como ausente.

    # Para o seu CSV, a coluna "QUADRO" parece ser um bom indicador.
    # Vamos considerar "QPEBM" e "QOABM" como quadros que podem ter TAF Adaptado.
    # E também militares que foram marcados como presentes mas têm muitos NaNs nos exercícios padrão.

    df_adaptado = df[
        ((df["QUADRO"].isin(["QPEBM", "QOABM"])) & (df["PRESENTE"])) |
        ((df["PRESENTE"]) & (df[pontuacao_cols].isnull().sum(axis=1) > 2)) # Mais de 2 exercícios padrão sem pontuação
    ].copy()

    # Remover militares do TAF Adaptado do dataframe principal de TAF normal
    df_normal = df[~df.index.isin(df_adaptado.index)].copy()

    # Adicionar coluna NOME_COMPLETO para busca
    df_normal["NOME_COMPLETO"] = df_normal["NOME"].apply(lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode("utf-8").upper())
    df_adaptado["NOME_COMPLETO"] = df_adaptado["NOME"].apply(lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode("utf-8").upper())

    return df_normal, df_adaptado

df_all, df_adaptado = load_data()

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════

def ordem_posto(posto):
    """Define uma ordem para os postos/graduações para ordenação."""
    ordem = {
        "MAJOR": 1, "CAP": 2, "1º TEN": 3, "1° TEN": 3, "2º TEN": 4, "2° TEN": 4,
        "ASP OF": 5, "ST": 6, "1º SGT": 7, "1° SGT": 7, "2º SGT": 8, "2° SGT": 8,
        "3º SGT": 9, "3° SGT": 9, "CB": 10, "SD": 11
    }
    return ordem.get(posto.upper().strip(), 99)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Logo
    if _LOCAL_LOGO_PATH:
        st.image(str(_LOCAL_LOGO_PATH), use_column_width=True)
    else:
        st.image(_get_cbmam_image_url(), use_column_width=True)

    st.markdown("---")

    # Seleção de página
    pagina = st.radio(
        "Navegação",
        ["🏠 Dashboard Geral", "👤 Ficha Individual", "📈 Estatísticas", "♿ TAF Adaptado"],
        index=0,
        key="pagina_selecao",
    )

    st.markdown("---")

    # Filtros globais (aplicados a todas as páginas, exceto TAF Adaptado)
    st.markdown("### ⚙️ Filtros")
    todos_postos = ["Todos"] + sorted(df_all["POSTO_GRAD"].unique(), key=ordem_posto)
    posto_filtro = st.selectbox("Posto/Graduação", todos_postos, key="posto_filtro")

    todos_quadros = ["Todos"] + sorted(df_all["QUADRO"].unique())
    quadro_filtro = st.selectbox("Quadro", todos_quadros, key="quadro_filtro")

    todas_faixas = ["Todas"] + sorted(df_all["FAIXA_ETARIA"].unique())
    faixa_etaria_filtro = st.selectbox("Faixa Etária", todas_faixas, key="faixa_etaria_filtro")

    todos_sexos = ["Ambos"] + sorted(df_all["SEXO"].unique())
    sexo_filtro = st.selectbox("Sexo", todos_sexos, key="sexo_filtro")

    # Aplicar filtros
    df_filtered = df_all.copy()
    if posto_filtro != "Todos":
        df_filtered = df_filtered[df_filtered["POSTO_GRAD"] == posto_filtro]
    if quadro_filtro != "Todos":
        df_filtered = df_filtered[df_filtered["QUADRO"] == quadro_filtro]
    if faixa_etaria_filtro != "Todas":
        df_filtered = df_filtered[df_filtered["FAIXA_ETARIA"] == faixa_etaria_filtro]
    if sexo_filtro != "Ambos":
        df_filtered = df_filtered[df_filtered["SEXO"] == sexo_filtro]

    st.markdown("---")

    # Opções de tema
    st.markdown("### 🎨 Tema")
    if st.button("☀️ Tema Claro", use_container_width=True):
        st.session_state.tema = "claro"
        st.rerun()
    if st.button("🌙 Tema Escuro", use_container_width=True):
        st.session_state.tema = "escuro"
        st.rerun()

    st.markdown("---")

    # Botão para gerar PDF (apenas na página de Ficha Individual ou Dashboard Geral)
    if pagina == "👤 Ficha Individual" or pagina == "🏠 Dashboard Geral":
        st.markdown("### 📄 Exportar para PDF")
        if st.button("Gerar Relatório PDF", use_container_width=True):
            st.session_state["gerar_pdf"] = True
        else:
            st.session_state["gerar_pdf"] = False

# ══════════════════════════════════════════════════════════════════════════════
# GERAÇÃO DE PDF
# ══════════════════════════════════════════════════════════════════════════════

def generate_pdf_report(page_title, charts_to_save, militar_data=None):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0.1, 0.1, 0.1) # Cor escura para o texto no PDF
    c.drawString(30, height - 50, f"Relatório TAF - {page_title}")
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 70, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.line(30, height - 80, width - 30, height - 80)

    y_position = height - 120

    if militar_data:
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, y_position, f"Militar: {militar_data['NOME']}")
        y_position -= 20
        c.setFont("Helvetica", 12)
        c.drawString(30, y_position, f"Posto: {militar_data['POSTO_GRAD']} | Quadro: {militar_data['QUADRO']}")
        y_position -= 15
        c.drawString(30, y_position, f"Média Final: {militar_data['MEDIA_FINAL']:.2f} | Classificação: {militar_data['CLASSIFICACAO']}")
        y_position -= 30

    for title, fig in charts_to_save:
        if y_position < 200: # Nova página se não houver espaço suficiente
            c.showPage()
            y_position = height - 50
            c.setFont("Helvetica-Bold", 16)
            c.drawString(30, y_position, f"Relatório TAF - {page_title} (continuação)")
            c.line(30, y_position - 10, width - 30, y_position - 10)
            y_position -= 40

        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y_position, title)
        y_position -= 15

        img_buffer = io.BytesIO()
        fig.write_image(img_buffer, format="png", width=800, height=450, scale=2) # Aumentar escala para melhor qualidade
        img_buffer.seek(0)
        img = ImageReader(img_buffer)

        # Calculate aspect ratio to fit image
        img_width, img_height = 500, 280 # Approximate size for charts
        aspect_ratio = img.width / img.height

        if img_width / aspect_ratio > (height - y_position - 20): # If image is too tall
            img_height = height - y_position - 20
            img_width = img_height * aspect_ratio

        if img_width > (width - 60): # If image is too wide
            img_width = width - 60
            img_height = img_width / aspect_ratio

        c.drawImage(img, 30, y_position - img_height, width=img_width, height=img_height)
        y_position -= (img_height + 30)

    c.save()
    buffer.seek(0)
    return buffer

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: DASHBOARD GERAL
# ══════════════════════════════════════════════════════════════════════════════

if pagina == "🏠 Dashboard Geral":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">🏠 Dashboard Geral</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Visão geral do desempenho do TAF do CBMAM
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    df_presentes = df_filtered[df_filtered["PRESENTE"]].copy()

    if len(df_presentes) == 0:
        st.warning("Nenhum dado disponível com os filtros selecionados.")
        st.stop()

    # KPIs
    total_militares = len(df_filtered)
    militares_presentes = len(df_presentes)
    militares_ausentes = total_militares - militares_presentes
    media_geral = df_presentes["MEDIA_FINAL"].mean() if militares_presentes > 0 else 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("👥 Total Militares", total_militares)
    with kpi2:
        st.metric("✅ Presentes", militares_presentes)
    with kpi3:
        st.metric("❌ Ausentes", militares_ausentes)
    with kpi4:
        st.metric("📊 Média Geral", f"{media_geral:.2f}")

    st.divider()

    charts_for_pdf = []

    # Distribuição de Média Final
    st.markdown(f"<p class='section-title'>📈 Distribuição da Média Final</p>", unsafe_allow_html=True)
    fig_dist = px.histogram(
        df_presentes,
        x="MEDIA_FINAL",
        nbins=20,
        title="Distribuição das Médias Finais",
        labels={"MEDIA_FINAL": "Média Final", "count": "Número de Militares"},
        color_discrete_sequence=[theme['accent']]
    )
    fig_dist.update_layout(**DARK, height=400, xaxis=dict(**GRID), yaxis=dict(**GRID))
    st.plotly_chart(fig_dist, use_container_width=True)
    charts_for_pdf.append(("Distribuição da Média Final", fig_dist))

    # Média por Sexo e Faixa Etária
    st.markdown(f"<p class='section-title'>📊 Média por Sexo e Faixa Etária</p>", unsafe_allow_html=True)
    media_sexo_idade = df_presentes.groupby(["SEXO", "FAIXA_ETARIA"])["MEDIA_FINAL"].mean().reset_index()
    fig_sexo_idade = px.bar(
        media_sexo_idade,
        x="FAIXA_ETARIA",
        y="MEDIA_FINAL",
        color="SEXO",
        barmode="group",
        title="Média Final por Sexo e Faixa Etária",
        labels={"MEDIA_FINAL": "Média Final", "FAIXA_ETARIA": "Faixa Etária"},
        color_discrete_map={"Masculino": theme['accent'], "Feminino": "#e76f51"}
    )
    fig_sexo_idade.update_layout(**DARK, height=400, xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID))
    st.plotly_chart(fig_sexo_idade, use_container_width=True)
    charts_for_pdf.append(("Média por Sexo e Faixa Etária", fig_sexo_idade))

    # Classificação Geral
    st.markdown(f"<p class='section-title'>🏆 Classificação Geral</p>", unsafe_allow_html=True)
    classificacao_counts = df_presentes["CLASSIFICACAO"].value_counts().reset_index()
    classificacao_counts.columns = ["Classificação", "Quantidade"]
    fig_class = px.pie(
        classificacao_counts,
        values="Quantidade",
        names="Classificação",
        title="Distribuição das Classificações",
        color="Classificação",
        color_discrete_map=COR_MAP
    )
    fig_class.update_layout(**DARK, height=400, showlegend=True)
    st.plotly_chart(fig_class, use_container_width=True)
    charts_for_pdf.append(("Classificação Geral", fig_class))

    # Média por Quadro
    st.markdown(f"<p class='section-title'>🏢 Média por Quadro</p>", unsafe_allow_html=True)
    df_q_media = df_presentes.groupby("QUADRO")["MEDIA_FINAL"].mean().reset_index()
    df_q_media["_ordem"] = df_q_media["QUADRO"].apply(lambda x: df_presentes[df_presentes["QUADRO"] == x]["POSTO_GRAD"].apply(ordem_posto).mean())
    df_q_media = df_q_media.sort_values("_ordem").drop(columns=["_ordem"])

    fig_q = px.bar(
        df_q_media, x="QUADRO", y="MEDIA_FINAL",
        color="MEDIA_FINAL",
        color_continuous_scale=["#ef4444", "#f59e0b", "#3b82f6", "#22c55e"],
        text="MEDIA_FINAL",
        labels={"QUADRO": "Quadro", "MEDIA_FINAL": "Média Final"},
        title="Média final por quadro",
    )
    fig_q.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_q.update_layout(
        **DARK, height=400, coloraxis_showscale=False,
        xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID),
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig_q, use_container_width=True)
    charts_for_pdf.append(("Média por Quadro", fig_q))

    # Box plot por quadro
    st.markdown(f"<p class='section-title'>📦 Distribuição por Quadro</p>", unsafe_allow_html=True)

    fig_box_q = px.box(
        df_presentes, x="QUADRO", y="MEDIA_FINAL",
        color="QUADRO",
        labels={"QUADRO": "Quadro", "MEDIA_FINAL": "Média Final"},
        title="Distribuição da média final por quadro",
    )
    fig_box_q.update_layout(
        **DARK, height=450, showlegend=False,
        xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID),
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig_box_q, use_container_width=True)
    charts_for_pdf.append(("Distribuição por Quadro", fig_box_q))

    # Classificação por quadro (stacked bar)
    st.markdown(f"<p class='section-title'>📊 Classificação por Quadro</p>", unsafe_allow_html=True)

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
    charts_for_pdf.append(("Classificação por Quadro", fig_stack_q))

    # Radar por quadro
    st.markdown(f"<p class='section-title'>🕸️ Radar Comparativo por Quadro</p>", unsafe_allow_html=True)

    colunas_nota = ["PONTUACAO_CORRIDA", "PONTUACAO_ABDOMINAL", "PONTUACAO_FLEXAO", "PONTUACAO_NATACAO", "PONTUACAO_BARRA"]
    cats_radar = ["Corrida", "Abdominal", "Flexão", "Natação", "Barra"]

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
                            gridcolor=theme['border_color'],
                            tickfont_color=theme['text_secondary']),
            angularaxis=dict(gridcolor=theme['border_color']),
        ),
        **DARK, height=450,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        title="Perfil de desempenho por quadro",
    )
    st.plotly_chart(fig_radar_q, use_container_width=True)
    charts_for_pdf.append(("Radar Comparativo por Quadro", fig_radar_q))

    # Desempenho por atividade e quadro
    st.markdown(f"<p class='section-title'>💪 Notas por Atividade × Quadro</p>", unsafe_allow_html=True)

    notas_map = {
        "Corrida": "PONTUACAO_CORRIDA",
        "Abdominal": "PONTUACAO_ABDOMINAL",
        "Flexão": "PONTUACAO_FLEXAO",
        "Natação": "PONTUACAO_NATACAO",
        "Barra": "PONTUACAO_BARRA",
    }
    labels_nota = list(notas_map.keys())

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
    charts_for_pdf.append(("Notas por Atividade x Quadro", fig_disc_q))

    if st.session_state.get("gerar_pdf"):
        pdf_buffer = generate_pdf_report("Dashboard Geral", charts_for_pdf)
        st.download_button(
            label="Download PDF do Dashboard Geral",
            data=pdf_buffer,
            file_name="relatorio_dashboard_geral.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.session_state["gerar_pdf"] = False # Resetar para não gerar novamente

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: FICHA INDIVIDUAL
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "👤 Ficha Individual":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">👤 Ficha Individual</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Perfil detalhado de cada militar
    </p>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("#### 🔍 Selecionar Militar")
        busca = st.text_input("🔎 Buscar por nome", placeholder="Digite parte do nome...", key="busca_ficha")

        # Filtrar apenas militares com dados completos (presente + media final valida)
        df_busca = df_all[df_all["PRESENTE"] & df_all["MEDIA_FINAL"].notna()].copy()

        if len(df_busca) == 0:
            st.error("❌ Nenhum militar com dados completos disponível.")
            st.stop()

        st.markdown(f"<p style='font-size:0.85rem;color:{theme['text_secondary']};'>Total: {len(df_busca)} militares</p>", unsafe_allow_html=True)

        lista_nomes = df_busca["NOME"].tolist()
        if busca:
            lista_nomes = [n for n in lista_nomes if busca.upper() in unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode("utf-8").upper()]

        if not lista_nomes:
            st.warning(f"⚠️ Nenhum militar encontrado para '{busca}'")
            # Se não encontrou, mostra todos novamente para o selectbox não ficar vazio
            lista_nomes = df_busca["NOME"].tolist()
            if not lista_nomes: # Se mesmo assim estiver vazio, para o app
                st.stop()

        st.markdown(f"<span style='color:{theme['text_primary']};'>**Selecione um militar:**</span>", unsafe_allow_html=True)
        militar_sel = st.selectbox("militar", lista_nomes, index=0, label_visibility="collapsed")

    # Verificar se militar foi selecionado
    if militar_sel is None or militar_sel == "":
        st.info("Selecione um militar para visualizar seus dados.")
        st.stop()

    # Buscar dados do militar
    row_match = df_all[df_all["NOME"] == militar_sel]
    if len(row_match) == 0:
        st.error(f"Militar não encontrado: {militar_sel}")
        st.stop()

    row = row_match.iloc[0]
    vals_ind = [float(row[c]) if pd.notna(row[c]) else 0.0 for c in colunas_nota]
    nome_curto = " ".join(str(militar_sel).split()[:2])
    media_ind = float(row["MEDIA_FINAL"]) if pd.notna(row["MEDIA_FINAL"]) else 0.0
    class_ind = row["CLASSIFICACAO"]
    posto_ind = row["POSTO_GRAD"]
    quadro_ind = row["QUADRO"]

    # Comparacoes
    media_geral = df_all[df_all["PRESENTE"]]["MEDIA_FINAL"].mean()
    diff_geral = media_ind - media_geral

    # Media do mesmo posto
    media_posto = df_all[
        (df_all["PRESENTE"]) & (df_all["POSTO_GRAD"] == posto_ind)
    ]["MEDIA_FINAL"].mean()
    diff_posto = media_ind - media_posto

    # Ranking
    df_rank_calc = df_all[df_all["PRESENTE"] & df_all["MEDIA_FINAL"].notna()].copy()
    if len(df_rank_calc) > 0:
        rank_pos = df_rank_calc["MEDIA_FINAL"].rank(ascending=False, method="min")
        rank_idx = df_rank_calc[df_rank_calc["NOME"] == militar_sel].index
        if len(rank_idx) > 0:
            posicao = int(rank_pos[rank_idx[0]])
            total = len(df_rank_calc)
        else:
            posicao = 0
            total = len(df_rank_calc)
    else:
        posicao = 0
        total = 0

    pf_notas = {l: float(row[c]) for l, c in notas_map.items() if pd.notna(row[c])}
    pf_forte = max(pf_notas, key=lambda k: pf_notas[k]) if pf_notas else "—"
    pf_fraco = row["PONTO_FRACO"]

    badge_config = {
        "Excelente":    (theme['badge_bg_good'], theme['badge_text_good'], theme['badge_border_good']),
        "Bom":          (theme['badge_bg_neutral'], theme['badge_text_neutral'], theme['badge_border_neutral']),
        "Regular":      (theme['badge_bg_avg'], theme['badge_text_avg'], theme['badge_border_avg']),
        "Insuficiente": (theme['badge_bg_bad'], theme['badge_text_bad'], theme['badge_border_bad']),
    }.get(class_ind, (theme['card_bg'], theme['text_primary'], theme['card_border']))

    sinal_g = "+" if diff_geral >= 0 else ""
    cor_g = "#22c55e" if diff_geral >= 0 else "#ef4444"
    sinal_p = "+" if diff_posto >= 0 else ""
    cor_p = "#22c55e" if diff_posto >= 0 else "#ef4444"

    st.markdown(f"""
    <div class="ficha-header-card">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
        <div>
        <div class="title">🪖 {nome_curto}</div>
        <div class="subtitle">
            {posto_ind} · {quadro_ind} · CBMAM · 2026
        </div>
        </div>
        <div class="badge-container">
        <div class="badge" style="background:{badge_config[2]};border:1px solid {badge_config[2]};">
            <div class="label">CLASSIFICAÇÃO</div>
            <div class="value" style="color:{badge_config[1]};">{class_ind}</div>
        </div>
        <div class="badge" style="background:{theme['card_bg']};border:1px solid {theme['card_border']};">
            <div class="label">MÉDIA FINAL</div>
            <div class="value" style="color:{theme['text_primary']};">{media_ind:.1f}</div>
        </div>
        <div class="badge" style="background:{theme['card_bg']};border:1px solid {theme['card_border']};">
            <div class="label">RANKING</div>
            <div class="value" style="color:{theme['text_primary']};">{posicao}° / {total}</div>
        </div>
        <div class="badge" style="background:{theme['card_bg']};border:1px solid {theme['card_border']};">
            <div class="label">vs GERAL</div>
            <div class="value" style="color:{cor_g};">{sinal_g}{diff_geral:.2f}</div>
        </div>
        <div class="badge" style="background:{theme['card_bg']};border:1px solid {theme['card_border']};">
            <div class="label">vs {posto_ind}</div>
            <div class="value" style="color:{cor_p};">{sinal_p}{diff_posto:.2f}</div>
        </div>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    charts_for_pdf_individual = []

    # Dados brutos do militar
    st.markdown(f"<p class='section-title'>📝 Desempenho Bruto (Valores Realizados)</p>", unsafe_allow_html=True)
    raw_cols = st.columns(5)
    raw_data = [
        ("🏃 Corrida 12min", row["CORRIDA"], "metros"),
        ("💪 Abdominal", row["ABDOMINAL"], "reps"),
        ("🤸 Flexão", row["FLEXAO"], "reps"),
        ("🏊 Natação 50m", row["NATACAO_SEG"], "seg"),
        ("🔩 Barra", row["BARRA_VALOR"], "rep/seg"),
    ]
    for i, (label, val, unit) in enumerate(raw_data):
        with raw_cols[i]:
            display_val = str(int(val)) if pd.notna(val) and val != 0 else "—"
            st.markdown(f"""
            <div class="raw-data-card">
            <div class="label">{label}</div>
            <div class="value">{display_val}</div>
            <div class="unit">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    # Radar e barras
    col_r, col_b2 = st.columns(2)

    med_geral_vals = [df_all[df_all["PRESENTE"]][c].mean() for c in colunas_nota]
    med_posto_vals = [
        df_all[(df_all["PRESENTE"]) & (df_all["POSTO_GRAD"] == posto_ind)][c].mean()
        for c in colunas_nota
    ]

    with col_r:
        st.markdown(f"<p class='section-title'>🕸️ Radar de Atributos</p>", unsafe_allow_html=True)

        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=[10] * len(cats_radar), theta=cats_radar, fill="toself", name="Máximo",
            line_color=theme['border_color'], fillcolor=f"{theme['border_color']}30",
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
            line_color=theme['accent'], fillcolor=f"{theme['accent']}30",
        ))
        fig_r.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 10],
                                gridcolor=theme['border_color'],
                                tickfont_color=theme['text_secondary']),
                angularaxis=dict(gridcolor=theme['border_color']),
            ),
            **DARK,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, font_color=theme['text_primary']),
            height=440, margin=dict(t=30, b=70),
        )
        st.plotly_chart(fig_r, use_column_width=True)
        charts_for_pdf_individual.append((f"Radar de Atributos - {nome_curto}", fig_r))

    with col_b2:
        st.markdown(f"<p class='section-title'>📊 Notas vs Referências</p>", unsafe_allow_html=True)

        fig_b = go.Figure()
        fig_b.add_trace(go.Bar(
            name="Média Geral", x=labels_nota, y=med_geral_vals,
            marker_color=f"{theme['accent']}50",
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
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, font_color=theme['text_primary']),
            height=440, margin=dict(t=30, b=70),
        )
        st.plotly_chart(fig_b, use_column_width=True)
        charts_for_pdf_individual.append((f"Notas vs Referências - {nome_curto}", fig_b))

    # Cards de notas
    st.markdown(f"<p class='section-title'>🎯 Detalhamento por Atividade</p>", unsafe_allow_html=True)

    cols_disc = st.columns(5)
    for i, (label, col_n) in enumerate(zip(labels_nota, colunas_nota)):
        nota_v = float(row[col_n]) if pd.notna(row[col_n]) else 0.0
        med_v = df_all[df_all["PRESENTE"]][col_n].mean()
        delta_v = nota_v - med_v
        s = "+" if delta_v >= 0 else ""
        c_delta = "#22c55e" if delta_v >= 0 else "#ef4444"
        icone = "🟢" if nota_v >= med_v else "🔴"

        progress_color = ""
        if nota_v >= 9.0: progress_color = "#22c55e"
        elif nota_v >= 7.5: progress_color = "#3b82f6"
        elif nota_v >= 6.0: progress_color = "#f59e0b"
        else: progress_color = "#ef4444"

        with cols_disc[i]:
            st.markdown(f"""
            <div class="activity-card">
            <div class="label">{label}</div>
            <div class="value">{nota_v:.1f}</div>
            <div class="delta" style="color:{c_delta};">
                {icone} {s}{delta_v:.2f} vs geral
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width:{nota_v * 10}%;background:{progress_color};"></div>
            </div>
            </div>
            """, unsafe_allow_html=True)

    # Gauge
    st.markdown(f"<p class='section-title'>🏁 Indicador de Média Final</p>", unsafe_allow_html=True)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=media_ind,
        delta={"reference": media_geral, "valueformat": ".2f",
            "increasing": {"color": "#22c55e"},
            "decreasing": {"color": "#ef4444"}},
        title={"text": f"Média Final · {nome_curto}<br>"
            f"<span style='font-size:.8rem;color:{theme['text_secondary']}'>Ref: média geral ({media_geral:.2f})</span>"},
        gauge={
            "axis": {"range": [0, 10], "tickcolor": theme['text_secondary']},
            "bar": {"color": COR_MAP.get(class_ind, theme['accent'])},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": theme['border_color'],
            "steps": [
                {"range": [0, 6.0], "color": f"{theme['badge_border_bad']}30"},
                {"range": [6.0, 7.5], "color": f"{theme['badge_border_avg']}30"},
                {"range": [7.5, 9.0], "color": f"{theme['badge_border_neutral']}30"},
                {"range": [9.0, 10], "color": f"{theme['badge_border_good']}30"},
            ],
            "threshold": {
                "line": {"color": "#f59e0b", "width": 3},
                "thickness": 0.8,
                "value": media_geral,
            },
        },
        number={"font": {"color": theme['text_primary'], "size": 56}},
    ))
    fig_gauge.update_layout(
        **DARK, height=320, margin=dict(t=60, b=20, l=40, r=40),
    )
    st.plotly_chart(fig_gauge, use_column_width=True)
    charts_for_pdf_individual.append((f"Indicador de Média Final - {nome_curto}", fig_gauge))

    # Resumo
    st.markdown(f"""
    <div class="summary-card">
    <b>🪖 Posto/Graduação:</b> {posto_ind} · {quadro_ind}<br>
    <b>🟢 Ponto forte:</b> {pf_forte} ({pf_notas.get(pf_forte, 0):.1f})<br>
    <b>🔴 Ponto fraco:</b> {pf_fraco} ({pf_notas.get(pf_fraco, 0):.1f})<br>
    <b>📍 Ranking:</b> {posicao}° de {total} avaliados<br>
    <b>📈 vs Média geral ({media_geral:.2f}):</b>
    <span style="color:{cor_g};">{sinal_g}{diff_geral:.2f}</span><br>
    <b>📈 vs Média {posto_ind} ({media_posto:.2f}):</b>
    <span style="color:{cor_p};">{sinal_p}{diff_posto:.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("gerar_pdf"):
        pdf_buffer = generate_pdf_report(f"Ficha Individual - {nome_curto}", charts_for_pdf_individual, militar_data=row)
        st.download_button(
            label=f"Download PDF da Ficha de {nome_curto}",
            data=pdf_buffer,
            file_name=f"relatorio_ficha_individual_{nome_curto.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.session_state["gerar_pdf"] = False # Resetar para não gerar novamente

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: ESTATÍSTICAS
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📈 Estatísticas":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">📈 Análise Estatística</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Boxplots, distribuições, correlações e percentis do TAF
    </p>
    """, unsafe_allow_html=True)
    st.divider()

    df_presentes = df_filtered[df_filtered["PRESENTE"]].copy()

    if len(df_presentes) == 0:
        st.warning("Nenhum dado disponível com os filtros selecionados.")
        st.stop()

    # Box plots por atividade
    st.markdown(f"<p class='section-title'>📦 Box Plot — Notas por Atividade</p>", unsafe_allow_html=True)

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
    st.markdown(f"<p class='section-title'>📉 Distribuição de Notas por Atividade</p>", unsafe_allow_html=True)

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
        legend=dict(font_color=theme['text_primary'])
    )
    st.plotly_chart(fig_hist_all, use_container_width=True)

    # Correlação corrida x média
    st.markdown(f"<p class='section-title'>🏃 Correlação: Corrida × Média Final</p>", unsafe_allow_html=True)

    df_corr = df_presentes[df_presentes["CORRIDA"].notna()].copy()
    fig_scatter = px.scatter(
        df_corr, x="CORRIDA", y="MEDIA_FINAL",
        color="CLASSIFICACAO", color_discrete_map=COR_MAP,
        size="MEDIA_FINAL", hover_name="NOME",
        trendline="ols", trendline_color_override=theme['text_primary'],
        labels={"CORRIDA": "Corrida 12min (metros)", "MEDIA_FINAL": "Média Final"},
        title="Militares com maior distância na corrida têm média mais alta?",
    )
    fig_scatter.update_layout(
        **DARK, height=420,
        yaxis=dict(**GRID), xaxis=dict(**GRID),
        margin=dict(t=50, b=20),
        legend=dict(font_color=theme['text_primary'])
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Tabela de percentis
    st.markdown(f"<p class='section-title'>📊 Tabela de Percentis</p>", unsafe_allow_html=True)

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
    st.dataframe(pd.DataFrame(perc_data), hide_index=True)

    # Estatísticas descritivas
    st.markdown(f"<p class='section-title'>📋 Estatísticas Descritivas</p>", unsafe_allow_html=True)

    desc_cols = list(notas_map.values()) + ["MEDIA_FINAL"]
    desc_labels = list(notas_map.keys()) + ["Média Final"]
    desc = df_presentes[desc_cols].describe().T
    desc.index = desc_labels
    desc = desc[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
    desc.columns = ["N", "Média", "Desvio", "Mín", "P25", "Mediana", "P75", "Máx"]
    desc = desc.round(2)
    st.dataframe(desc)

    # Top 10 e Bottom 10
    st.markdown(f"<p class='section-title'>🏆 Top 10 e Bottom 10</p>", unsafe_allow_html=True)

    col_t, col_bt = st.columns(2)
    with col_t:
        st.markdown(f"<span style='color:{theme['text_primary']};'>**🥇 Top 10 — Maiores Médias**</span>", unsafe_allow_html=True)
        top10 = df_presentes.nlargest(10, "MEDIA_FINAL")[
            ["NOME", "POSTO_GRAD", "QUADRO", "MEDIA_FINAL", "CLASSIFICACAO"]
        ].reset_index(drop=True)
        top10.index += 1
        st.dataframe(top10)

    with col_bt:
        st.markdown(f"<span style='color:{theme['text_primary']};'>**⚠️ Bottom 10 — Menores Médias**</span>", unsafe_allow_html=True)
        bot10 = df_presentes.nsmallest(10, "MEDIA_FINAL")[
            ["NOME", "POSTO_GRAD", "QUADRO", "MEDIA_FINAL", "CLASSIFICACAO"]
        ].reset_index(drop=True)
        bot10.index += 1
        st.dataframe(bot10)

    # Valores brutos — desempenho real
    st.markdown(f"<p class='section-title'>🔢 Desempenho Bruto (Valores Reais)</p>", unsafe_allow_html=True)

    raw_stats = pd.DataFrame({
        "Exercício": ["Corrida 12min (m)", "Abdominal (reps)", "Flexão (reps)",
                    "Natação 50m (seg)", "Barra (valor)"],
        "Média": [
            df_presentes["CORRIDA"].mean(),
            df_presentes["ABDOMINAL"].mean(),
            df_presentes["FLEXAO"].mean(),
            df_presentes["NATACAO_SEG"].mean(),
            df_presentes["BARRA_VALOR"].mean(),
        ],
        "Mediana": [
            df_presentes["CORRIDA"].median(),
            df_presentes["ABDOMINAL"].median(),
            df_presentes["FLEXAO"].median(),
            df_presentes["NATACAO_SEG"].median(),
            df_presentes["BARRA_VALOR"].median(),
        ],
        "Mínimo": [
            df_presentes["CORRIDA"].min(),
            df_presentes["ABDOMINAL"].min(),
            df_presentes["FLEXAO"].min(),
            df_presentes["NATACAO_SEG"].min(),
            df_presentes["BARRA_VALOR"].min(),
        ],
        "Máximo": [
            df_presentes["CORRIDA"].max(),
            df_presentes["ABDOMINAL"].max(),
            df_presentes["FLEXAO"].max(),
            df_presentes["NATACAO_SEG"].max(),
            df_presentes["BARRA_VALOR"].max(),
        ],
    }).round(1)
    st.dataframe(raw_stats, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: TAF ADAPTADO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "♿ TAF Adaptado":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">♿ TAF Adaptado</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Dados dos militares que realizaram o TAF na modalidade adaptada
    </p>
    """, unsafe_allow_html=True)
    st.divider()

    if len(df_adaptado) == 0:
        st.info("Nenhum dado de TAF Adaptado encontrado.")
    else:
        # KPIs
        total_adapt = len(df_adaptado)
        presentes_adapt = int(df_adaptado["PRESENTE"].sum())
        ausentes_adapt = total_adapt - presentes_adapt

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("👥 Total", total_adapt)
        with k2:
            st.metric("✅ Presentes", presentes_adapt)
        with k3:
            st.metric("❌ Ausentes", ausentes_adapt)

        st.divider()

        # Por posto
        st.markdown(f"<p class='section-title'>🪖 Efetivo por Posto/Graduação</p>", unsafe_allow_html=True)

        adapt_posto = df_adaptado.groupby("POSTO_GRAD").size().reset_index(name="Quantidade")
        adapt_posto["_ordem"] = adapt_posto["POSTO_GRAD"].apply(ordem_posto)
        adapt_posto = adapt_posto.sort_values("_ordem").drop(columns=["_ordem"])

        fig_adapt = px.bar(
            adapt_posto, x="POSTO_GRAD", y="Quantidade",
            color="Quantidade",
            color_continuous_scale=[theme['accent'], "#22c55e"],
            text="Quantidade",
            labels={"POSTO_GRAD": "Posto/Graduação"},
            title="Militares no TAF Adaptado por posto",
        )
        fig_adapt.update_traces(textposition="outside")
        fig_adapt.update_layout(
            **DARK, height=350, coloraxis_showscale=False,
            xaxis=dict(**GRID, tickangle=-45),
            yaxis=dict(**GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_adapt, use_container_width=True)

        # Tabela de dados
        st.markdown(f"<p class='section-title'>📋 Dados Completos — TAF Adaptado</p>", unsafe_allow_html=True)

        display_cols = [c for c in df_adaptado.columns if c not in ["PRESENTE", "_ordem", "NOME_COMPLETO"]]
        df_adapt_display = df_adaptado[display_cols].copy()
        df_adapt_display = df_adapt_display.fillna("—")

        # Limpar valores "nan"
        for col in df_adapt_display.columns:
            df_adapt_display[col] = df_adapt_display[col].astype(str).replace("nan", "—")

        st.dataframe(df_adapt_display, height=500)

        # Exercícios realizados
        st.markdown(f"<p class='section-title'>📊 Exercícios Realizados</p>", unsafe_allow_html=True)

        # Estes exercícios devem ser as colunas que você espera no TAF Adaptado
        exercicios_adapt_cols = [
            "CAMINHADA", "ABDOMINAL", "FLEXAO", "PRANCHA", "NATACAO",
            "BARRA_EST", "BARRA_DIN", "CORRIDA", "PUXADOR_FRONTAL",
            "FLUTUACAO", "SUPINO", "COOPER"
        ]

        # Filtrar apenas as colunas que realmente existem no df_adaptado
        exercicios_adapt_cols_existentes = [col for col in exercicios_adapt_cols if col in df_adaptado.columns]

        ex_count = {}
        for ex in exercicios_adapt_cols_existentes:
            # Contar valores não nulos e que não são "NÃO" ou "NC"
            count = df_adaptado[ex].dropna().apply(
                lambda x: str(x).strip().upper() not in ("", "NAN", "NÃO COMPARECEU", "NÃO", "NC")
            ).sum()
            ex_count[ex] = count

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
        else:
            st.info("Nenhum exercício adaptado com dados válidos encontrado.")

        st.info(
            f"ℹ️ O TAF Adaptado avalia militares com necessidades especiais ou "
            f"restrições médicas, utilizando exercícios alternativos conforme "
            f"aptidão individual. Cada militar realiza um conjunto diferente de provas."
        )
