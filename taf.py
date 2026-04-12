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
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }}
        [data-testid="stMetricLabel"] {{
            color: {theme['text_secondary']} !important;
            font-size: 0.9rem;
        }}
        [data-testid="stMetricValue"] {{
            color: {theme['text_primary']} !important;
            font-size: 1.8rem;
            font-weight: bold;
        }}
        [data-testid="stMetricDelta"] {{
            color: {theme['text_primary']} !important;
        }}

        /* Divisor */
        .st-emotion-cache-lnv1k {{ /* st.divider */
            border-top: 1px solid {theme['border_color']};
        }}

        /* Mensagens de alerta/info */
        .stAlert {{
            background-color: {theme['card_bg']};
            border: 1px solid {theme['card_border']};
            color: {theme['text_primary']};
        }}

        /* Estilos personalizados para títulos de seção */
        .section-title {{
            font-size: 1.3rem;
            font-weight: 600;
            color: {theme['text_primary']};
            margin-top: 20px;
            margin-bottom: 15px;
            border-bottom: 2px solid {theme['accent']};
            padding-bottom: 5px;
        }}

        /* Badges de classificação */
        .badge-Excelente {{
            background-color: {theme['badge_bg_good']};
            color: {theme['badge_text_good']};
            border: 1px solid {theme['badge_border_good']};
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .badge-Bom {{
            background-color: {theme['badge_bg_neutral']};
            color: {theme['badge_text_neutral']};
            border: 1px solid {theme['badge_border_neutral']};
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .badge-Regular {{
            background-color: {theme['badge_bg_avg']};
            color: {theme['badge_text_avg']};
            border: 1px solid {theme['badge_border_avg']};
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .badge-Insuficiente {{
            background-color: {theme['badge_bg_bad']};
            color: {theme['badge_text_bad']};
            border: 1px solid {theme['badge_border_bad']};
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .badge-Ausente {{
            background-color: {theme['bg_tertiary']};
            color: {theme['text_secondary']};
            border: 1px solid {theme['border_color']};
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# VARIÁVEIS GLOBAIS E CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

# Cores para gráficos Plotly (serão ajustadas pelo tema)
COR_MAP = {
    "Excelente": "#22c55e",
    "Bom":       "#3b82f6",
    "Regular":   "#f59e0b",
    "Insuficiente": "#ef4444",
    "Ausente":   "#64748b",
}

ORDEM_POSTO = {
    "CEL": 1, "TC": 2, "MAJOR": 3, "CAP": 4,
    "1° TEN": 5, "2° TEN": 6, "ASP OF": 7,
    "ST": 8, "1° SGT": 9, "2° SGT": 10, "3° SGT": 11,
    "CB": 12, "SD": 13,
}

# ══════════════════════════════════════════════════════════════════════════════
# REGRAS DE PONTUAÇÃO - MASCULINO (10 FAIXAS ETÁRIAS)
# ══════════════════════════════════════════════════════════════════════════════
REGRAS_MASCULINO = {
    '18-21': {'Corrida': {3200: 10, 3100: 9.5, 3000: 9.0, 2900: 8.5, 2800: 8.0, 2700: 7.5, 2600: 7.0, 2500: 6.5, 2400: 6.0, 2300: 5.5, 2200: 5.0, 2100: 4.5, 2000: 4.0, 1900: 3.5, 1800: 3.0, 1700: 2.5, 1600: 2.0, 1500: 1.5, 0: 0}, 'Flexão': {38: 10, 37: 9.5, 36: 9.0, 35: 8.5, 34: 8.0, 33: 7.5, 32: 7.0, 31: 6.5, 30: 6.0, 29: 5.5, 28: 5.0, 27: 4.5, 26: 4.0, 25: 3.5, 24: 3.0, 23: 2.5, 22: 2.0, 21: 1.5, 0: 0}, 'Abdominal': {48: 10, 47: 9.5, 46: 9.0, 45: 8.5, 44: 8.0, 43: 7.5, 42: 7.0, 41: 6.5, 40: 6.0, 39: 5.5, 38: 5.0, 37: 4.5, 36: 4.0, 35: 3.5, 34: 3.0, 33: 2.5, 32: 2.0, 31: 1.5, 0: 0}, 'Barra Dinâmica': {13: 10, 12: 9.5, 11: 9.0, 10: 8.5, 9: 8.0, 8: 7.5, 7: 7.0, 6: 6.5, 5: 6.0, 4: 5.5, 3: 5.0, 2: 4.5, 1: 4.0, 0: 0}, 'Barra Estática': {60: 10, 57: 9.5, 55: 9.0, 53: 8.5, 51: 8.0, 49: 7.5, 47: 7.0, 45: 6.5, 43: 6.0, 41: 5.5, 39: 5.0, 37: 4.5, 35: 4.0, 33: 3.5, 31: 3.0, 29: 2.5, 27: 2.0, 25: 1.5, 0: 0}, 'Natação': {40: 10, 44: 9.5, 48: 9.0, 52: 8.5, 56: 8.0, 60: 7.5, 64: 7.0, 68: 6.5, 72: 6.0, 76: 5.5, 80: 5.0, 84: 4.5, 88: 4.0, 92: 3.5, 96: 3.0, 100: 2.5, 104: 2.0, 108: 1.5, 999: 0}},
    '22-25': {'Corrida': {3200: 10, 3100: 9.5, 3000: 9.0, 2900: 8.5, 2800: 8.0, 2700: 7.5, 2600: 7.0, 2500: 6.5, 2400: 6.0, 2300: 5.5, 2200: 5.0, 2100: 4.5, 2000: 4.0, 1900: 3.5, 1800: 3.0, 1700: 2.5, 1600: 2.0, 1500: 1.5, 0: 0}, 'Flexão': {37: 10, 36: 9.5, 35: 9.0, 34: 8.5, 33: 8.0, 32: 7.5, 31: 7.0, 30: 6.5, 29: 6.0, 28: 5.5, 27: 5.0, 26: 4.5, 25: 4.0, 24: 3.5, 23: 3.0, 22: 2.5, 21: 2.0, 20: 1.5, 0: 0}, 'Abdominal': {47: 10, 46: 9.5, 45: 9.0, 44: 8.5, 43: 8.0, 42: 7.5, 41: 7.0, 40: 6.5, 39: 6.0, 38: 5.5, 37: 5.0, 36: 4.5, 35: 4.0, 34: 3.5, 33: 3.0, 32: 2.5, 31: 2.0, 30: 1.5, 0: 0}, 'Barra Dinâmica': {12: 10, 11: 9.5, 10: 9.0, 9: 8.5, 8: 8.0, 7: 7.5, 6: 7.0, 5: 6.5, 4: 6.0, 3: 5.5, 2: 5.0, 1: 4.5, 0: 0}, 'Barra Estática': {57: 10, 55: 9.5, 53: 9.0, 51: 8.5, 49: 8.0, 47: 7.5, 45: 7.0, 43: 6.5, 41: 6.0, 39: 5.5, 37: 5.0, 35: 4.5, 33: 4.0, 31: 3.5, 29: 3.0, 27: 2.5, 25: 2.0, 23: 1.5, 0: 0}, 'Natação': {44: 10, 48: 9.5, 52: 9.0, 56: 8.5, 60: 8.0, 64: 7.5, 68: 7.0, 72: 6.5, 76: 6.0, 80: 5.5, 84: 5.0, 88: 4.5, 92: 4.0, 96: 3.5, 100: 3.0, 104: 2.5, 108: 2.0, 112: 1.5, 999: 0}},
    '26-29': {'Corrida': {3000: 10, 2900: 9.5, 2800: 9.0, 2700: 8.5, 2600: 8.0, 2500: 7.5, 2400: 7.0, 2300: 6.5, 2200: 6.0, 2100: 5.5, 2000: 5.0, 1900: 4.5, 1800: 4.0, 1700: 3.5, 1600: 3.0, 1500: 2.5, 1400: 2.0, 1300: 1.5, 0: 0}, 'Flexão': {36: 10, 35: 9.5, 34: 9.0, 33: 8.5, 32: 8.0, 31: 7.5, 30: 7.0, 29: 6.5, 28: 6.0, 27: 5.5, 26: 5.0, 25: 4.5, 24: 4.0, 23: 3.5, 22: 3.0, 21: 2.5, 20: 2.0, 19: 1.5, 0: 0}, 'Abdominal': {46: 10, 45: 9.5, 44: 9.0, 43: 8.5, 42: 8.0, 41: 7.5, 40: 7.0, 39: 6.5, 38: 6.0, 37: 5.5, 36: 5.0, 35: 4.5, 34: 4.0, 33: 3.5, 32: 3.0, 31: 2.5, 30: 2.0, 29: 1.5, 0: 0}, 'Barra Dinâmica': {11: 10, 10: 9.5, 9: 9.0, 8: 8.5, 7: 8.0, 6: 7.5, 5: 7.0, 4: 6.5, 3: 6.0, 2: 5.5, 1: 5.0, 0: 0}, 'Barra Estática': {55: 10, 53: 9.5, 51: 9.0, 49: 8.5, 47: 8.0, 45: 7.5, 43: 7.0, 41: 6.5, 39: 6.0, 37: 5.5, 35: 5.0, 33: 4.5, 31: 4.0, 29: 3.5, 27: 3.0, 25: 2.5, 23: 2.0, 21: 1.5, 0: 0}, 'Natação': {48: 10, 52: 9.5, 56: 9.0, 60: 8.5, 64: 8.0, 68: 7.5, 72: 7.0, 76: 6.5, 80: 6.0, 84: 5.5, 88: 5.0, 92: 4.5, 96: 4.0, 100: 3.5, 104: 3.0, 108: 2.5, 112: 2.0, 116: 1.5, 999: 0}},
    '30-34': {'Corrida': {2800: 10, 2700: 9.5, 2600: 9.0, 2500: 8.5, 2400: 8.0, 2300: 7.5, 2200: 7.0, 2100: 6.5, 2000: 6.0, 1900: 5.5, 1800: 5.0, 1700: 4.5, 1600: 4.0, 1500: 3.5, 1400: 3.0, 1300: 2.5, 1200: 2.0, 1100: 1.5, 0: 0}, 'Flexão': {35: 10, 34: 9.5, 33: 9.0, 32: 8.5, 31: 8.0, 30: 7.5, 29: 7.0, 28: 6.5, 27: 6.0, 26: 5.5, 25: 5.0, 24: 4.5, 23: 4.0, 22: 3.5, 21: 3.0, 20: 2.5, 19: 2.0, 18: 1.5, 0: 0}, 'Abdominal': {45: 10, 44: 9.5, 43: 9.0, 42: 8.5, 41: 8.0, 40: 7.5, 39: 7.0, 38: 6.5, 37: 6.0, 36: 5.5, 35: 5.0, 34: 4.5, 33: 4.0, 32: 3.5, 31: 3.0, 30: 2.5, 29: 2.0, 28: 1.5, 0: 0}, 'Barra Dinâmica': {10: 10, 9: 9.5, 8: 9.0, 7: 8.5, 6: 8.0, 5: 7.5, 4: 7.0, 3: 6.5, 2: 6.0, 1: 5.5, 0: 0}, 'Barra Estática': {53: 10, 51: 9.5, 49: 9.0, 47: 8.5, 45: 8.0, 43: 7.5, 41: 7.0, 39: 6.5, 37: 6.0, 35: 5.5, 33: 5.0, 31: 4.5, 29: 4.0, 27: 3.5, 25: 3.0, 23: 2.5, 21: 2.0, 19: 1.5, 0: 0}, 'Natação': {52: 10, 56: 9.5, 60: 9.0, 64: 8.5, 68: 8.0, 72: 7.5, 76: 7.0, 80: 6.5, 84: 6.0, 88: 5.5, 92: 5.0, 96: 4.5, 100: 4.0, 104: 3.5, 108: 3.0, 112: 2.5, 116: 2.0, 120: 1.5, 999: 0}},
    '35-39': {'Corrida': {2600: 10, 2500: 9.5, 2400: 9.0, 2300: 8.5, 2200: 8.0, 2100: 7.5, 2000: 7.0, 1900: 6.5, 1800: 6.0, 1700: 5.5, 1600: 5.0, 1500: 4.5, 1400: 4.0, 1300: 3.5, 1200: 3.0, 1100: 2.5, 1000: 2.0, 900: 1.5, 0: 0}, 'Flexão': {34: 10, 33: 9.5, 32: 9.0, 31: 8.5, 30: 8.0, 29: 7.5, 28: 7.0, 27: 6.5, 26: 6.0, 25: 5.5, 24: 5.0, 23: 4.5, 22: 4.0, 21: 3.5, 20: 3.0, 19: 2.5, 18: 2.0, 17: 1.5, 0: 0}, 'Abdominal': {43: 10, 42: 9.5, 41: 9.0, 40: 8.5, 39: 8.0, 38: 7.5, 37: 7.0, 36: 6.5, 35: 6.0, 34: 5.5, 33: 5.0, 32: 4.5, 31: 4.0, 30: 3.5, 29: 3.0, 28: 2.5, 27: 2.0, 26: 1.5, 0: 0}, 'Barra Dinâmica': {9: 10, 8: 9.5, 7: 9.0, 6: 8.5, 5: 8.0, 4: 7.5, 3: 7.0, 2: 6.5, 1: 6.0, 0: 0}, 'Barra Estática': {51: 10, 49: 9.5, 47: 9.0, 45: 8.5, 43: 8.0, 41: 7.5, 39: 7.0, 37: 6.5, 35: 6.0, 33: 5.5, 31: 5.0, 29: 4.5, 27: 4.0, 25: 3.5, 23: 3.0, 21: 2.5, 19: 2.0, 17: 1.5, 0: 0}, 'Natação': {56: 10, 60: 9.5, 64: 9.0, 68: 8.5, 72: 8.0, 76: 7.5, 80: 7.0, 84: 6.5, 88: 6.0, 92: 5.5, 96: 5.0, 100: 4.5, 104: 4.0, 108: 3.5, 112: 3.0, 116: 2.5, 120: 2.0, 124: 1.5, 999: 0}},
    '40-44': {'Corrida': {2400: 10, 2300: 9.5, 2200: 9.0, 2100: 8.5, 2000: 8.0, 1900: 7.5, 1800: 7.0, 1700: 6.5, 1600: 6.0, 1500: 5.5, 1400: 5.0, 1300: 4.5, 1200: 4.0, 1100: 3.5, 1000: 3.0, 900: 2.5, 800: 2.0, 700: 1.5, 0: 0}, 'Flexão': {32: 10, 31: 9.5, 30: 9.0, 29: 8.5, 28: 8.0, 27: 7.5, 26: 7.0, 25: 6.5, 24: 6.0, 23: 5.5, 22: 5.0, 21: 4.5, 20: 4.0, 19: 3.5, 18: 3.0, 17: 2.5, 16: 2.0, 15: 1.5, 0: 0}, 'Abdominal': {41: 10, 40: 9.5, 39: 9.0, 38: 8.5, 37: 8.0, 36: 7.5, 35: 7.0, 34: 6.5, 33: 6.0, 32: 5.5, 31: 5.0, 30: 4.5, 29: 4.0, 28: 3.5, 27: 3.0, 26: 2.5, 25: 2.0, 24: 1.5, 0: 0}, 'Barra Dinâmica': {8: 10, 7: 9.5, 6: 9.0, 5: 8.5, 4: 8.0, 3: 7.5, 2: 7.0, 1: 6.5, 0: 0}, 'Barra Estática': {49: 10, 47: 9.5, 45: 9.0, 43: 8.5, 41: 8.0, 39: 7.5, 37: 7.0, 35: 6.5, 33: 6.0, 31: 5.5, 29: 5.0, 27: 4.5, 25: 4.0, 23: 3.5, 21: 3.0, 19: 2.5, 17: 2.0, 15: 1.5, 0: 0}, 'Natação': {60: 10, 64: 9.5, 68: 9.0, 72: 8.5, 76: 8.0, 80: 7.5, 84: 7.0, 88: 6.5, 92: 6.0, 96: 5.5, 100: 5.0, 104: 4.5, 108: 4.0, 112: 3.5, 116: 3.0, 120: 2.5, 124: 2.0, 128: 1.5, 999: 0}},
    '45-49': {'Corrida': {2200: 10, 2100: 9.5, 2000: 9.0, 1900: 8.5, 1800: 8.0, 1700: 7.5, 1600: 7.0, 1500: 6.5, 1400: 6.0, 1300: 5.5, 1200: 5.0, 1100: 4.5, 1000: 4.0, 900: 3.5, 800: 3.0, 700: 2.5, 600: 2.0, 500: 1.5, 0: 0}, 'Flexão': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5, 22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5, 14: 2.0, 13: 1.5, 0: 0}, 'Abdominal': {39: 10, 38: 9.5, 37: 9.0, 36: 8.5, 35: 8.0, 34: 7.5, 33: 7.0, 32: 6.5, 31: 6.0, 30: 5.5, 29: 5.0, 28: 4.5, 27: 4.0, 26: 3.5, 25: 3.0, 24: 2.5, 23: 2.0, 22: 1.5, 0: 0}, 'Barra Dinâmica': {7: 10, 6: 9.5, 5: 9.0, 4: 8.5, 3: 8.0, 2: 7.5, 1: 7.0, 0: 0}, 'Barra Estática': {47: 10, 45: 9.5, 43: 9.0, 41: 8.5, 39: 8.0, 37: 7.5, 35: 7.0, 33: 6.5, 31: 6.0, 29: 5.5, 27: 5.0, 25: 4.5, 23: 4.0, 21: 3.5, 19: 3.0, 17: 2.5, 15: 2.0, 13: 1.5, 0: 0}, 'Natação': {64: 10, 68: 9.5, 72: 9.0, 76: 8.5, 80: 8.0, 84: 7.5, 88: 7.0, 92: 6.5, 96: 6.0, 100: 5.5, 104: 5.0, 108: 4.5, 112: 4.0, 116: 3.5, 120: 3.0, 124: 2.5, 128: 2.0, 132: 1.5, 999: 0}},
    '50-54': {'Corrida': {2000: 10, 1900: 9.5, 1800: 9.0, 1700: 8.5, 1600: 8.0, 1500: 7.5, 1400: 7.0, 1300: 6.5, 1200: 6.0, 1100: 5.5, 1000: 5.0, 900: 4.5, 800: 4.0, 700: 3.5, 600: 3.0, 500: 2.5, 400: 2.0, 300: 1.5, 0: 0}, 'Flexão': {28: 10, 27: 9.5, 26: 9.0, 25: 8.5, 24: 8.0, 23: 7.5, 22: 7.0, 21: 6.5, 20: 6.0, 19: 5.5, 18: 5.0, 17: 4.5, 16: 4.0, 15: 3.5, 14: 3.0, 13: 2.5, 12: 2.0, 11: 1.5, 0: 0}, 'Abdominal': {37: 10, 36: 9.5, 35: 9.0, 34: 8.5, 33: 8.0, 32: 7.5, 31: 7.0, 30: 6.5, 29: 6.0, 28: 5.5, 27: 5.0, 26: 4.5, 25: 4.0, 24: 3.5, 23: 3.0, 22: 2.5, 21: 2.0, 20: 1.5, 0: 0}, 'Barra Dinâmica': {6: 10, 5: 9.5, 4: 9.0, 3: 8.5, 2: 8.0, 1: 7.5, 0: 0}, 'Barra Estática': {45: 10, 43: 9.5, 41: 9.0, 39: 8.5, 37: 8.0, 35: 7.5, 33: 7.0, 31: 6.5, 29: 6.0, 27: 5.5, 25: 5.0, 23: 4.5, 21: 4.0, 19: 3.5, 17: 3.0, 15: 2.5, 13: 2.0, 11: 1.5, 0: 0}, 'Natação': {68: 10, 72: 9.5, 76: 9.0, 80: 8.5, 84: 8.0, 88: 7.5, 92: 7.0, 96: 6.5, 100: 6.0, 104: 5.5, 108: 5.0, 112: 4.5, 116: 4.0, 120: 3.5, 124: 3.0, 128: 2.5, 132: 2.0, 136: 1.5, 999: 0}},
    '55-59': {'Corrida': {1800: 10, 1700: 9.5, 1600: 9.0, 1500: 8.5, 1400: 8.0, 1300: 7.5, 1200: 7.0, 1100: 6.5, 1000: 6.0, 900: 5.5, 800: 5.0, 700: 4.5, 600: 4.0, 500: 3.5, 400: 3.0, 300: 2.5, 200: 2.0, 100: 1.5, 0: 0}, 'Flexão': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0}, 'Abdominal': {35: 10, 34: 9.5, 33: 9.0, 32: 8.5, 31: 8.0, 30: 7.5, 29: 7.0, 28: 6.5, 27: 6.0, 26: 5.5, 25: 5.0, 24: 4.5, 23: 4.0, 22: 3.5, 21: 3.0, 20: 2.5, 19: 2.0, 18: 1.5, 0: 0}, 'Barra Dinâmica': {5: 10, 4: 9.5, 3: 9.0, 2: 8.5, 1: 8.0, 0: 0}, 'Barra Estática': {43: 10, 41: 9.5, 39: 9.0, 37: 8.5, 35: 8.0, 33: 7.5, 31: 7.0, 29: 6.5, 27: 6.0, 25: 5.5, 23: 5.0, 21: 4.5, 19: 4.0, 17: 3.5, 15: 3.0, 13: 2.5, 11: 2.0, 9: 1.5, 0: 0}, 'Natação': {72: 10, 76: 9.5, 80: 9.0, 84: 8.5, 88: 8.0, 92: 7.5, 96: 7.0, 100: 6.5, 104: 6.0, 108: 5.5, 112: 5.0, 116: 4.5, 120: 4.0, 124: 3.5, 128: 3.0, 132: 2.5, 136: 2.0, 140: 1.5, 999: 0}},
    '60+': {'Corrida': {1600: 10, 1500: 9.5, 1400: 9.0, 1300: 8.5, 1200: 8.0, 1100: 7.5, 1000: 7.0, 900: 6.5, 800: 6.0, 700: 5.5, 600: 5.0, 500: 4.5, 400: 4.0, 300: 3.5, 200: 3.0, 100: 2.5, 0: 0}, 'Flexão': {24: 10, 23: 9.5, 22: 9.0, 21: 8.5, 20: 8.0, 19: 7.5, 18: 7.0, 17: 6.5, 16: 6.0, 15: 5.5, 14: 5.0, 13: 4.5, 12: 4.0, 11: 3.5, 10: 3.0, 9: 2.5, 8: 2.0, 7: 1.5, 0: 0}, 'Abdominal': {33: 10, 32: 9.5, 31: 9.0, 30: 8.5, 29: 8.0, 28: 7.5, 27: 7.0, 26: 6.5, 25: 6.0, 24: 5.5, 23: 5.0, 22: 4.5, 21: 4.0, 20: 3.5, 19: 3.0, 18: 2.5, 17: 2.0, 16: 1.5, 0: 0}, 'Barra Dinâmica': {4: 10, 3: 9.5, 2: 9.0, 1: 8.5, 0: 0}, 'Barra Estática': {41: 10, 39: 9.5, 37: 9.0, 35: 8.5, 33: 8.0, 31: 7.5, 29: 7.0, 27: 6.5, 25: 6.0, 23: 5.5, 21: 5.0, 19: 4.5, 17: 4.0, 15: 3.5, 13: 3.0, 11: 2.5, 9: 2.0, 7: 1.5, 0: 0}, 'Natação': {76: 10, 80: 9.5, 84: 9.0, 88: 8.5, 92: 8.0, 96: 7.5, 100: 7.0, 104: 6.5, 108: 6.0, 112: 5.5, 116: 5.0, 120: 4.5, 124: 4.0, 128: 3.5, 132: 3.0, 136: 2.5, 140: 2.0, 144: 1.5, 999: 0}},
}

# ══════════════════════════════════════════════════════════════════════════════
# REGRAS DE PONTUAÇÃO - FEMININO (10 FAIXAS ETÁRIAS)
# ══════════════════════════════════════════════════════════════════════════════
REGRAS_FEMININO = {
    '18-21': {'Corrida': {2800: 10, 2700: 9.5, 2600: 9.0, 2500: 8.5, 2400: 8.0, 2300: 7.5, 2200: 7.0, 2100: 6.5, 2000: 6.0, 1900: 5.5, 1800: 5.0, 1700: 4.5, 1600: 4.0, 1500: 3.5, 1400: 3.0, 1300: 2.5, 1200: 2.0, 1100: 1.5, 0: 0}, 'Flexão': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5, 22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5, 14: 2.0, 13: 1.5, 0: 0}, 'Abdominal': {40: 10, 39: 9.5, 38: 9.0, 37: 8.5, 36: 8.0, 35: 7.5, 34: 7.0, 33: 6.5, 32: 6.0, 31: 5.5, 30: 5.0, 29: 4.5, 28: 4.0, 27: 3.5, 26: 3.0, 25: 2.5, 24: 2.0, 23: 1.5, 0: 0}, 'Barra Dinâmica': {8: 10, 7: 9.5, 6: 9.0, 5: 8.5, 4: 8.0, 3: 7.5, 2: 7.0, 1: 6.5, 0: 0}, 'Barra Estática': {40: 10, 38: 9.5, 36: 9.0, 34: 8.5, 32: 8.0, 30: 7.5, 28: 7.0, 26: 6.5, 24: 6.0, 22: 5.5, 20: 5.0, 18: 4.5, 16: 4.0, 14: 3.5, 12: 3.0, 10: 2.5, 8: 2.0, 6: 1.5, 0: 0}, 'Natação': {45: 10, 49: 9.5, 53: 9.0, 57: 8.5, 61: 8.0, 65: 7.5, 69: 7.0, 73: 6.5, 77: 6.0, 81: 5.5, 85: 5.0, 89: 4.5, 93: 4.0, 97: 3.5, 101: 3.0, 105: 2.5, 109: 2.0, 113: 1.5, 999: 0}},
    '22-25': {'Corrida': {2700: 10, 2600: 9.5, 2500: 9.0, 2400: 8.5, 2300: 8.0, 2200: 7.5, 2100: 7.0, 2000: 6.5, 1900: 6.0, 1800: 5.5, 1700: 5.0, 1600: 4.5, 1500: 4.0, 1400: 3.5, 1300: 3.0, 1200: 2.5, 1100: 2.0, 1000: 1.5, 0: 0}, 'Flexão': {29: 10, 28: 9.5, 27: 9.0, 26: 8.5, 25: 8.0, 24: 7.5, 23: 7.0, 22: 6.5, 21: 6.0, 20: 5.5, 19: 5.0, 18: 4.5, 17: 4.0, 16: 3.5, 15: 3.0, 14: 2.5, 13: 2.0, 12: 1.5, 0: 0}, 'Abdominal': {39: 10, 38: 9.5, 37: 9.0, 36: 8.5, 35: 8.0, 34: 7.5, 33: 7.0, 32: 6.5, 31: 6.0, 30: 5.5, 29: 5.0, 28: 4.5, 27: 4.0, 26: 3.5, 25: 3.0, 24: 2.5, 23: 2.0, 22: 1.5, 0: 0}, 'Barra Dinâmica': {7: 10, 6: 9.5, 5: 9.0, 4: 8.5, 3: 8.0, 2: 7.5, 1: 7.0, 0: 0}, 'Barra Estática': {38: 10, 36: 9.5, 34: 9.0, 32: 8.5, 30: 8.0, 28: 7.5, 26: 7.0, 24: 6.5, 22: 6.0, 20: 5.5, 18: 5.0, 16: 4.5, 14: 4.0, 12: 3.5, 10: 3.0, 8: 2.5, 6: 2.0, 4: 1.5, 0: 0}, 'Natação': {49: 10, 53: 9.5, 57: 9.0, 61: 8.5, 65: 8.0, 69: 7.5, 73: 7.0, 77: 6.5, 81: 6.0, 85: 5.5, 89: 5.0, 93: 4.5, 97: 4.0, 101: 3.5, 105: 3.0, 109: 2.5, 113: 2.0, 117: 1.5, 999: 0}},
    '26-29': {'Corrida': {2600: 10, 2500: 9.5, 2400: 9.0, 2300: 8.5, 2200: 8.0, 2100: 7.5, 2000: 7.0, 1900: 6.5, 1800: 6.0, 1700: 5.5, 1600: 5.0, 1500: 4.5, 1400: 4.0, 1300: 3.5, 1200: 3.0, 1100: 2.5, 1000: 2.0, 900: 1.5, 0: 0}, 'Flexão': {28: 10, 27: 9.5, 26: 9.0, 25: 8.5, 24: 8.0, 23: 7.5, 22: 7.0, 21: 6.5, 20: 6.0, 19: 5.5, 18: 5.0, 17: 4.5, 16: 4.0, 15: 3.5, 14: 3.0, 13: 2.5, 12: 2.0, 11: 1.5, 0: 0}, 'Abdominal': {38: 10, 37: 9.5, 36: 9.0, 35: 8.5, 34: 8.0, 33: 7.5, 32: 7.0, 31: 6.5, 30: 6.0, 29: 5.5, 28: 5.0, 27: 4.5, 26: 4.0, 25: 3.5, 24: 3.0, 23: 2.5, 22: 2.0, 21: 1.5, 0: 0}, 'Barra Dinâmica': {6: 10, 5: 9.5, 4: 9.0, 3: 8.5, 2: 8.0, 1: 7.5, 0: 0}, 'Barra Estática': {36: 10, 34: 9.5, 32: 9.0, 30: 8.5, 28: 8.0, 26: 7.5, 24: 7.0, 22: 6.5, 20: 6.0, 18: 5.5, 16: 5.0, 14: 4.5, 12: 4.0, 10: 3.5, 8: 3.0, 6: 2.5, 4: 2.0, 2: 1.5, 0: 0}, 'Natação': {53: 10, 57: 9.5, 61: 9.0, 65: 8.5, 69: 8.0, 73: 7.5, 77: 7.0, 81: 6.5, 85: 6.0, 89: 5.5, 93: 5.0, 97: 4.5, 101: 4.0, 105: 3.5, 109: 3.0, 113: 2.5, 117: 2.0, 121: 1.5, 999: 0}},
    '30-34': {'Corrida': {2500: 10, 2400: 9.5, 2300: 9.0, 2200: 8.5, 2100: 8.0, 2000: 7.5, 1900: 7.0, 1800: 6.5, 1700: 6.0, 1600: 5.5, 1500: 5.0, 1400: 4.5, 1300: 4.0, 1200: 3.5, 1100: 3.0, 1000: 2.5, 900: 2.0, 800: 1.5, 0: 0}, 'Flexão': {27: 10, 26: 9.5, 25: 9.0, 24: 8.5, 23: 8.0, 22: 7.5, 21: 7.0, 20: 6.5, 19: 6.0, 18: 5.5, 17: 5.0, 16: 4.5, 15: 4.0, 14: 3.5, 13: 3.0, 12: 2.5, 11: 2.0, 10: 1.5, 0: 0}, 'Abdominal': {37: 10, 36: 9.5, 35: 9.0, 34: 8.5, 33: 8.0, 32: 7.5, 31: 7.0, 30: 6.5, 29: 6.0, 28: 5.5, 27: 5.0, 26: 4.5, 25: 4.0, 24: 3.5, 23: 3.0, 22: 2.5, 21: 2.0, 20: 1.5, 0: 0}, 'Barra Dinâmica': {5: 10, 4: 9.5, 3: 9.0, 2: 8.5, 1: 8.0, 0: 0}, 'Barra Estática': {34: 10, 32: 9.5, 30: 9.0, 28: 8.5, 26: 8.0, 24: 7.5, 22: 7.0, 20: 6.5, 18: 6.0, 16: 5.5, 14: 5.0, 12: 4.5, 10: 4.0, 8: 3.5, 6: 3.0, 4: 2.5, 2: 2.0, 0: 0}, 'Natação': {57: 10, 61: 9.5, 65: 9.0, 69: 8.5, 73: 8.0, 77: 7.5, 81: 7.0, 85: 6.5, 89: 6.0, 93: 5.5, 97: 5.0, 101: 4.5, 105: 4.0, 109: 3.5, 113: 3.0, 117: 2.5, 121: 2.0, 125: 1.5, 999: 0}},
    '35-39': {'Corrida': {2400: 10, 2300: 9.5, 2200: 9.0, 2100: 8.5, 2000: 8.0, 1900: 7.5, 1800: 7.0, 1700: 6.5, 1600: 6.0, 1500: 5.5, 1400: 5.0, 1300: 4.5, 1200: 4.0, 1100: 3.5, 1000: 3.0, 900: 2.5, 800: 2.0, 700: 1.5, 0: 0}, 'Flexão': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0}, 'Abdominal': {36: 10, 35: 9.5, 34: 9.0, 33: 8.5, 32: 8.0, 31: 7.5, 30: 7.0, 29: 6.5, 28: 6.0, 27: 5.5, 26: 5.0, 25: 4.5, 24: 4.0, 23: 3.5, 22: 3.0, 21: 2.5, 20: 2.0, 19: 1.5, 0: 0}, 'Barra Dinâmica': {4: 10, 3: 9.5, 2: 9.0, 1: 8.5, 0: 0}, 'Barra Estática': {32: 10, 30: 9.5, 28: 9.0, 26: 8.5, 24: 8.0, 22: 7.5, 20: 7.0, 18: 6.5, 16: 6.0, 14: 5.5, 12: 5.0, 10: 4.5, 8: 4.0, 6: 3.5, 4: 3.0, 2: 2.5, 0: 0}, 'Natação': {61: 10, 65: 9.5, 69: 9.0, 73: 8.5, 77: 8.0, 81: 7.5, 85: 7.0, 89: 6.5, 93: 6.0, 97: 5.5, 101: 5.0, 105: 4.5, 109: 4.0, 113: 3.5, 117: 3.0, 121: 2.5, 125: 2.0, 129: 1.5, 999: 0}},
    '40-44': {'Corrida': {2300: 10, 2200: 9.5, 2100: 9.0, 2000: 8.5, 1900: 8.0, 1800: 7.5, 1700: 7.0, 1600: 6.5, 1500: 6.0, 1400: 5.5, 1300: 5.0, 1200: 4.5, 1100: 4.0, 1000: 3.5, 900: 3.0, 800: 2.5, 700: 2.0, 600: 1.5, 0: 0}, 'Flexão': {25: 10, 24: 9.5, 23: 9.0, 22: 8.5, 21: 8.0, 20: 7.5, 19: 7.0, 18: 6.5, 17: 6.0, 16: 5.5, 15: 5.0, 14: 4.5, 13: 4.0, 12: 3.5, 11: 3.0, 10: 2.5, 9: 2.0, 8: 1.5, 0: 0}, 'Abdominal': {35: 10, 34: 9.5, 33: 9.0, 32: 8.5, 31: 8.0, 30: 7.5, 29: 7.0, 28: 6.5, 27: 6.0, 26: 5.5, 25: 5.0, 24: 4.5, 23: 4.0, 22: 3.5, 21: 3.0, 20: 2.5, 19: 2.0, 18: 1.5, 0: 0}, 'Barra Dinâmica': {3: 10, 2: 9.5, 1: 9.0, 0: 0}, 'Barra Estática': {30: 10, 28: 9.5, 26: 9.0, 24: 8.5, 22: 8.0, 20: 7.5, 18: 7.0, 16: 6.5, 14: 6.0, 12: 5.5, 10: 5.0, 8: 4.5, 6: 4.0, 4: 3.5, 2: 3.0, 0: 0}, 'Natação': {65: 10, 69: 9.5, 73: 9.0, 77: 8.5, 81: 8.0, 85: 7.5, 89: 7.0, 93: 6.5, 97: 6.0, 101: 5.5, 105: 5.0, 109: 4.5, 113: 4.0, 117: 3.5, 121: 3.0, 125: 2.5, 129: 2.0, 133: 1.5, 999: 0}},
    '45-49': {'Corrida': {2200: 10, 2100: 9.5, 2000: 9.0, 1900: 8.5, 1800: 8.0, 1700: 7.5, 1600: 7.0, 1500: 6.5, 1400: 6.0, 1300: 5.5, 1200: 5.0, 1100: 4.5, 1000: 4.0, 900: 3.5, 800: 3.0, 700: 2.5, 600: 2.0, 500: 1.5, 0: 0}, 'Flexão': {24: 10, 23: 9.5, 22: 9.0, 21: 8.5, 20: 8.0, 19: 7.5, 18: 7.0, 17: 6.5, 16: 6.0, 15: 5.5, 14: 5.0, 13: 4.5, 12: 4.0, 11: 3.5, 10: 3.0, 9: 2.5, 8: 2.0, 7: 1.5, 0: 0}, 'Abdominal': {34: 10, 33: 9.5, 32: 9.0, 31: 8.5, 30: 8.0, 29: 7.5, 28: 7.0, 27: 6.5, 26: 6.0, 25: 5.5, 24: 5.0, 23: 4.5, 22: 4.0, 21: 3.5, 20: 3.0, 19: 2.5, 18: 2.0, 17: 1.5, 0: 0}, 'Barra Dinâmica': {2: 10, 1: 9.5, 0: 0}, 'Barra Estática': {28: 10, 26: 9.5, 24: 9.0, 22: 8.5, 20: 8.0, 18: 7.5, 16: 7.0, 14: 6.5, 12: 6.0, 10: 5.5, 8: 5.0, 6: 4.5, 4: 4.0, 2: 3.5, 0: 0}, 'Natação': {69: 10, 73: 9.5, 77: 9.0, 81: 8.5, 85: 8.0, 89: 7.5, 93: 7.0, 97: 6.5, 101: 6.0, 105: 5.5, 109: 5.0, 113: 4.5, 117: 4.0, 121: 3.5, 125: 3.0, 129: 2.5, 133: 2.0, 137: 1.5, 999: 0}},
    '50-54': {'Corrida': {2000: 10, 1900: 9.5, 1800: 9.0, 1700: 8.5, 1600: 8.0, 1500: 7.5, 1400: 7.0, 1300: 6.5, 1200: 6.0, 1100: 5.5, 1000: 5.0, 900: 4.5, 800: 4.0, 700: 3.5, 600: 3.0, 500: 2.5, 400: 2.0, 300: 1.5, 0: 0}, 'Flexão': {23: 10, 22: 9.5, 21: 9.0, 20: 8.5, 19: 8.0, 18: 7.5, 17: 7.0, 16: 6.5, 15: 6.0, 14: 5.5, 13: 5.0, 12: 4.5, 11: 4.0, 10: 3.5, 9: 3.0, 8: 2.5, 7: 2.0, 6: 1.5, 0: 0}, 'Abdominal': {33: 10, 32: 9.5, 31: 9.0, 30: 8.5, 29: 8.0, 28: 7.5, 27: 7.0, 26: 6.5, 25: 6.0, 24: 5.5, 23: 5.0, 22: 4.5, 21: 4.0, 20: 3.5, 19: 3.0, 18: 2.5, 17: 2.0, 16: 1.5, 0: 0}, 'Barra Dinâmica': {1: 10, 0: 0}, 'Barra Estática': {26: 10, 24: 9.5, 22: 9.0, 20: 8.5, 18: 8.0, 16: 7.5, 14: 7.0, 12: 6.5, 10: 6.0, 8: 5.5, 6: 5.0, 4: 4.5, 2: 4.0, 0: 0}, 'Natação': {73: 10, 77: 9.5, 81: 9.0, 85: 8.5, 89: 8.0, 93: 7.5, 97: 7.0, 101: 6.5, 105: 6.0, 109: 5.5, 113: 5.0, 117: 4.5, 121: 4.0, 125: 3.5, 129: 3.0, 133: 2.5, 137: 2.0, 141: 1.5, 999: 0}},
    '55-59': {'Corrida': {1800: 10, 1700: 9.5, 1600: 9.0, 1500: 8.5, 1400: 8.0, 1300: 7.5, 1200: 7.0, 1100: 6.5, 1000: 6.0, 900: 5.5, 800: 5.0, 700: 4.5, 600: 4.0, 500: 3.5, 400: 3.0, 300: 2.5, 200: 2.0, 100: 1.5, 0: 0}, 'Flexão': {22: 10, 21: 9.5, 20: 9.0, 19: 8.5, 18: 8.0, 17: 7.5, 16: 7.0, 15: 6.5, 14: 6.0, 13: 5.5, 12: 5.0, 11: 4.5, 10: 4.0, 9: 3.5, 8: 3.0, 7: 2.5, 6: 2.0, 5: 1.5, 0: 0}, 'Abdominal': {32: 10, 31: 9.5, 30: 9.0, 29: 8.5, 28: 8.0, 27: 7.5, 26: 7.0, 25: 6.5, 24: 6.0, 23: 5.5, 22: 5.0, 21: 4.5, 20: 4.0, 19: 3.5, 18: 3.0, 17: 2.5, 16: 2.0, 15: 1.5, 0: 0}, 'Barra Dinâmica': {0: 0}, 'Barra Estática': {24: 10, 22: 9.5, 20: 9.0, 18: 8.5, 16: 8.0, 14: 7.5, 12: 7.0, 10: 6.5, 8: 6.0, 6: 5.5, 4: 5.0, 2: 4.5, 0: 0}, 'Natação': {77: 10, 81: 9.5, 85: 9.0, 89: 8.5, 93: 8.0, 97: 7.5, 101: 7.0, 105: 6.5, 109: 6.0, 113: 5.5, 117: 5.0, 121: 4.5, 125: 4.0, 129: 3.5, 133: 3.0, 137: 2.5, 141: 2.0, 145: 1.5, 999: 0}},
    '60+': {'Corrida': {1600: 10, 1500: 9.5, 1400: 9.0, 1300: 8.5, 1200: 8.0, 1100: 7.5, 1000: 7.0, 900: 6.5, 800: 6.0, 700: 5.5, 600: 5.0, 500: 4.5, 400: 4.0, 300: 3.5, 200: 3.0, 100: 2.5, 0: 0}, 'Flexão': {21: 10, 20: 9.5, 19: 9.0, 18: 8.5, 17: 8.0, 16: 7.5, 15: 7.0, 14: 6.5, 13: 6.0, 12: 5.5, 11: 5.0, 10: 4.5, 9: 4.0, 8: 3.5, 7: 3.0, 6: 2.5, 5: 2.0, 4: 1.5, 0: 0}, 'Abdominal': {31: 10, 30: 9.5, 29: 9.0, 28: 8.5, 27: 8.0, 26: 7.5, 25: 7.0, 24: 6.5, 23: 6.0, 22: 5.5, 21: 5.0, 20: 4.5, 19: 4.0, 18: 3.5, 17: 3.0, 16: 2.5, 15: 2.0, 14: 1.5, 0: 0}, 'Barra Dinâmica': {0: 0}, 'Barra Estática': {22: 10, 20: 9.5, 18: 9.0, 16: 8.5, 14: 8.0, 12: 7.5, 10: 7.0, 8: 6.5, 6: 6.0, 4: 5.5, 2: 5.0, 0: 0}, 'Natação': {81: 10, 85: 9.5, 89: 9.0, 93: 8.5, 97: 8.0, 101: 7.5, 105: 7.0, 109: 6.5, 113: 6.0, 117: 5.5, 121: 5.0, 125: 4.5, 129: 4.0, 133: 3.5, 137: 3.0, 141: 2.5, 145: 2.0, 149: 1.5, 999: 0}},
}

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════

def limpar_nome(nome):
    """Remove acentos e caracteres especiais de uma string."""
    if pd.isna(nome):
        return nome
    nome = str(nome).upper()
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode('utf-8')
    nome = re.sub(r'[^A-Z0-9\s]', '', nome)
    return nome.strip()

def calcular_idade(data_nascimento):
    """Calcula a idade a partir da data de nascimento."""
    if pd.isna(data_nascimento):
        return np.nan
    today = datetime.today()
    return today.year - data_nascimento.year - ((today.month, today.day) < (data_nascimento.month, data_nascimento.day))

def get_faixa_etaria(idade):
    """Retorna a faixa etária com base na idade."""
    if pd.isna(idade):
        return "Não Informado"
    idade = int(idade)
    if 18 <= idade <= 21: return '18-21'
    if 22 <= idade <= 25: return '22-25'
    if 26 <= idade <= 29: return '26-29'
    if 30 <= idade <= 34: return '30-34'
    if 35 <= idade <= 39: return '35-39'
    if 40 <= idade <= 44: return '40-44'
    if 45 <= idade <= 49: return '45-49'
    if 50 <= idade <= 54: return '50-54'
    if 55 <= idade <= 59: return '55-59'
    if idade >= 60: return '60+'
    return "Não Classificado"

def parse_time_to_seconds(time_str):
    """Converte string de tempo (MM'SS" ou SS.0) para segundos."""
    if pd.isna(time_str) or not isinstance(time_str, str):
        return np.nan
    time_str = time_str.strip().replace('"', '').replace("'", ":") # Padroniza para MM:SS ou SS.0

    if re.fullmatch(r'\d+\.\d+', time_str): # Formato SS.0
        try:
            return float(time_str)
        except ValueError:
            return np.nan
    elif re.fullmatch(r'\d{1,2}:\d{2}', time_str): # Formato MM:SS
        try:
            minutes, seconds = map(int, time_str.split(':'))
            return minutes * 60 + seconds
        except ValueError:
            return np.nan
    elif re.fullmatch(r'\d{1,3}', time_str): # Formato SS (apenas segundos)
        try:
            return float(time_str)
        except ValueError:
            return np.nan
    return np.nan

def calcular_pontuacao(exercicio, resultado, sexo, faixa_etaria):
    """Calcula a pontuação de um exercício com base nas regras."""
    if pd.isna(resultado) or resultado == "NÃO COMPARECEU" or resultado == "NÃO" or resultado == "APTO":
        return np.nan

    regras = REGRAS_MASCULINO if sexo == 'Masculino' else REGRAS_FEMININO

    if faixa_etaria not in regras:
        return np.nan # Faixa etária não encontrada nas regras

    regras_exercicio = regras[faixa_etaria].get(exercicio)
    if not regras_exercicio:
        return np.nan # Exercício não encontrado para a faixa etária

    # Para Corrida, Flexão, Abdominal, Barra Dinâmica/Estática (maior valor = melhor)
    if exercicio in ['Corrida', 'Flexão', 'Abdominal', 'Barra Dinâmica', 'Barra Estática']:
        for limite, pontuacao in sorted(regras_exercicio.items(), reverse=True):
            if resultado >= limite:
                return pontuacao
    # Para Natação (menor valor = melhor)
    elif exercicio == 'Natação':
        for limite, pontuacao in sorted(regras_exercicio.items(), key=lambda item: item[0]):
            if resultado <= limite:
                return pontuacao
    return 0 # Se não atingiu nenhum limite, pontuação 0

def classificar_desempenho(media_final):
    """Classifica o desempenho com base na média final."""
    if pd.isna(media_final):
        return "Ausente"
    if media_final >= 8.0:
        return "Excelente"
    elif media_final >= 6.0:
        return "Bom"
    elif media_final >= 5.0:
        return "Regular"
    else:
        return "Insuficiente"

def ordem_posto(posto):
    """Retorna a ordem numérica de um posto para ordenação."""
    return ORDEM_POSTO.get(posto.upper().replace('°', ''), 99) # 99 para postos não mapeados

# ══════════════════════════════════════════════════════════════════════════════
# CARREGAMENTO E PRÉ-PROCESSAMENTO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    """Carrega e pré-processa os dados do TAF."""
    df = pd.read_csv("master_taf_consolidado.csv", sep="|", skipinitialspace=True)

    # Limpar espaços em branco dos nomes das colunas
    df.columns = df.columns.str.strip()

    # Renomear colunas para padronização
    df = df.rename(columns={
        "Posto": "POSTO_GRAD",
        "Nome": "NOME",
        "DataNascimento": "DATA_NASCIMENTO", # CORRIGIDO AQUI
        "Idade": "IDADE_CSV", # Manter a idade do CSV para comparação/referência
        "Raça/Cor": "RACA_COR",
    })

    # Remover a coluna 'ORD' se existir
    if 'ORD' in df.columns:
        df = df.drop(columns=['ORD'])

    # Limpar e padronizar dados
    df["NOME"] = df["NOME"].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df["NOME_COMPLETO"] = df["NOME"] # Manter nome original para ficha individual
    df["NOME_LIMPO"] = df["NOME"].apply(limpar_nome)
    df["POSTO_GRAD"] = df["POSTO_GRAD"].str.upper().str.strip()
    df["QUADRO"] = df["QUADRO"].str.upper().str.strip()
    df["SEXO"] = df["SEXO"].replace({"M": "Masculino", "F": "Feminino"}).fillna("Não Informado")
    df["SEXO"] = df["SEXO"].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # Tratamento da Data de Nascimento
    # Preencher NaNs na DataNascimento antes de converter para datetime
    df["DATA_NASCIMENTO"] = df["DATA_NASCIMENTO"].fillna("01/01/1900") # Data placeholder para NaNs
    df["DATA_NASCIMENTO"] = pd.to_datetime(df["DATA_NASCIMENTO"], format="%d/%m/%Y", errors='coerce')

    # Recalcular idade com base na DATA_NASCIMENTO
    df["IDADE"] = df["DATA_NASCIMENTO"].apply(calcular_idade)
    df["FAIXA_ETARIA"] = df["IDADE"].apply(get_faixa_etaria)

    # Identificar militares em TAF Adaptado ou com dados incompletos
    # Um militar é considerado "adaptado" se tiver "APTO" na corrida ou se tiver muitos NaNs nos exercícios principais
    # Ou se a idade ou sexo não puderem ser determinados para pontuação

    # Preencher valores "NÃO COMPARECEU", "NÃO", "APTO" e vazios com NaN para cálculo numérico
    exercicios_cols = ["Corrida", "Abdominal", "Flexao", "Natacao", "Barra"]
    for col in exercicios_cols:
        df[col] = df[col].replace(["NÃO COMPARECEU", "NÃO", "APTO", ""], np.nan)

    # Converter Corrida para numérico (metros)
    # Alguns valores de corrida estão como 'MM'SS"', 'MM'SS' ou 'MM'SS.0'
    # E outros como '24'51"' ou '21'13"' (tempo, não distância)
    # Precisamos identificar e tratar esses casos.

    # Identificar se a corrida é tempo (contém ' ou ") ou distância (apenas números)
    df['CORRIDA_IS_TEMPO'] = df['Corrida'].astype(str).str.contains(r"['\"]", na=False)

    # Para valores que parecem tempo, vamos ignorar para a pontuação de distância
    df.loc[df['CORRIDA_IS_TEMPO'], 'Corrida'] = np.nan
    df['Corrida'] = pd.to_numeric(df['Corrida'], errors='coerce')

    # Converter Natação para segundos
    df["Natacao"] = df["Natacao"].apply(parse_time_to_seconds)
    df = df.rename(columns={"Natacao": "NATACAO_SEG"})

    # Converter Barra para segundos (estática) ou repetições (dinâmica)
    # O CSV tem "01'01"", "51"", "15" (reps), "NÃO"
    df["Barra_Original"] = df["Barra"] # Manter original para referência
    df["Barra"] = df["Barra"].astype(str).str.strip().str.upper()

    # Identificar se é barra estática (tempo) ou dinâmica (repetições)
    # Se contém ' ou ", é tempo (estática). Se é apenas número, é repetições (dinâmica).
    df['BARRA_IS_TEMPO'] = df['Barra'].str.contains(r"['\"]", na=False)

    df['BARRA_ESTATICA_SEG'] = df.apply(
        lambda row: parse_time_to_seconds(row['Barra_Original']) if row['BARRA_IS_TEMPO'] else np.nan,
        axis=1
    )
    df['BARRA_DINAMICA_REPS'] = df.apply(
        lambda row: pd.to_numeric(row['Barra_Original'], errors='coerce') if not row['BARRA_IS_TEMPO'] else np.nan,
        axis=1
    )

    # Definir qual coluna de barra usar para pontuação (priorizar dinâmica se houver)
    # Se BARRA_DINAMICA_REPS não for NaN, usa ela. Senão, usa BARRA_ESTATICA_SEG.
    # Se ambos forem NaN, a pontuação será NaN.
    df['BARRA_VALOR'] = df['BARRA_DINAMICA_REPS'].fillna(df['BARRA_ESTATICA_SEG'])
    df['TIPO_BARRA'] = np.select(
        [df['BARRA_DINAMICA_REPS'].notna(), df['BARRA_ESTATICA_SEG'].notna()],
        ['Barra Dinâmica', 'Barra Estática'],
        default=np.nan
    )

    # Aplicar funções de pontuação
    df["PONTUACAO_CORRIDA"] = df.apply(
        lambda row: calcular_pontuacao("Corrida", row["Corrida"], row["SEXO"], row["FAIXA_ETARIA"]),
        axis=1
    )
    df["PONTUACAO_ABDOMINAL"] = df.apply(
        lambda row: calcular_pontuacao("Abdominal", row["Abdominal"], row["SEXO"], row["FAIXA_ETARIA"]),
        axis=1
    )
    df["PONTUACAO_FLEXAO"] = df.apply(
        lambda row: calcular_pontuacao("Flexão", row["Flexao"], row["SEXO"], row["FAIXA_ETARIA"]),
        axis=1
    )
    df["PONTUACAO_NATACAO"] = df.apply(
        lambda row: calcular_pontuacao("Natação", row["NATACAO_SEG"], row["SEXO"], row["FAIXA_ETARIA"]),
        axis=1
    )
    df["PONTUACAO_BARRA"] = df.apply(
        lambda row: calcular_pontuacao(row["TIPO_BARRA"], row["BARRA_VALOR"], row["SEXO"], row["FAIXA_ETARIA"]),
        axis=1
    )

    # Calcular Média Final
    pontuacoes_cols = [f"PONTUACAO_{ex}" for ex in ["CORRIDA", "ABDOMINAL", "FLEXAO", "NATACAO", "BARRA"]]
    df["MEDIA_FINAL"] = df[pontuacoes_cols].mean(axis=1)
    df["CLASSIFICACAO"] = df["MEDIA_FINAL"].apply(classificar_desempenho)

    # Identificar "PRESENTE" (se tem alguma pontuação válida)
    df["PRESENTE"] = df[pontuacoes_cols].notna().any(axis=1)

    # Separar TAF Adaptado
    # Considerar adaptado quem tem "APTO" na corrida original ou quem não tem pontuação em exercícios principais
    # mas tem algum valor em colunas que podem ser de TAF adaptado (ex: PRANCHA, CAMINHADA, etc.)
    # Por enquanto, vamos considerar "adaptado" quem não tem pontuação válida nos 5 exercícios principais
    # mas não está marcado como "NÃO COMPARECEU" na corrida.

    # Criar uma lista de colunas que podem indicar TAF adaptado (além dos 5 principais)
    # Estas colunas não estão no CSV fornecido, mas podem existir em outros dados ou serem adicionadas
    # Por enquanto, vamos usar a lógica de "não presente" nos 5 principais.

    # df_adaptado = df[~df["PRESENTE"]].copy() # Esta linha pode pegar quem simplesmente faltou

    # Uma abordagem mais robusta para TAF Adaptado:
    # 1. Militar que tem "APTO" na coluna original de Corrida (antes da conversão)
    # 2. Militar que não tem pontuação nos 5 exercícios principais, mas tem dados em outras colunas
    #    que indicam exercícios adaptados (se essas colunas existirem no CSV real).
    #    Como o CSV fornecido não tem essas colunas, vamos focar no "APTO" e na ausência de pontuação.

    df_adaptado = df[
        (df["Corrida_Original"].astype(str).str.upper() == "APTO") |
        (~df["PRESENTE"] & (df["Corrida_Original"].astype(str).str.upper() != "NÃO COMPARECEU"))
    ].copy()

    # Remover duplicatas baseadas em NOME e DATA_NASCIMENTO (ou CPF se for mais confiável)
    # O CSV tem algumas linhas duplicadas (ex: ORD 14 e 15, 18 e 19)
    df = df.drop_duplicates(subset=["NOME_COMPLETO", "DATA_NASCIMENTO"], keep='first')
    df_adaptado = df_adaptado.drop_duplicates(subset=["NOME_COMPLETO", "DATA_NASCIMENTO"], keep='first')

    return df, df_adaptado

# ══════════════════════════════════════════════════════════════════════════════
# GERAÇÃO DE PDF
# ══════════════════════════════════════════════════════════════════════════════

def generate_pdf_report(df_filtered, theme):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0, 0, 0) # Preto para o PDF, independente do tema do app
    c.drawString(50, height - 50, "Relatório TAF CBMAM")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, f"Data do Relatório: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.drawString(50, height - 90, f"Total de Militares Analisados: {len(df_filtered)}")

    y_position = height - 120

    # Resumo Geral
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_position, "Resumo Geral")
    y_position -= 20

    total_militares = len(df_filtered)
    presentes = df_filtered["PRESENTE"].sum()
    ausentes = total_militares - presentes
    media_geral = df_filtered["MEDIA_FINAL"].mean()

    c.setFont("Helvetica", 12)
    c.drawString(70, y_position, f"Total de Militares: {total_militares}")
    y_position -= 15
    c.drawString(70, y_position, f"Presentes: {presentes}")
    y_position -= 15
    c.drawString(70, y_position, f"Ausentes: {ausentes}")
    y_position -= 15
    c.drawString(70, y_position, f"Média Geral de Pontuação: {media_geral:.2f}")
    y_position -= 30

    # Gráfico de Classificação Geral
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_position, "Classificação Geral")
    y_position -= 20

    classificacao_counts = df_filtered["CLASSIFICACAO"].value_counts(normalize=True).reset_index()
    classificacao_counts.columns = ["Classificação", "Percentual"]

    fig_classificacao = px.pie(
        classificacao_counts,
        values="Percentual",
        names="Classificação",
        color="Classificação",
        color_discrete_map=COR_MAP,
        title="Distribuição de Classificação Geral"
    )
    fig_classificacao.update_layout(
        paper_bgcolor="white", plot_bgcolor="white", font_color="black",
        title_font_color="black", legend_font_color="black"
    )

    img_bytes = fig_classificacao.to_image(format="png", width=600, height=400, scale=2)
    img = ImageReader(io.BytesIO(img_bytes))
    c.drawImage(img, 50, y_position - 400, width=500, height=350)
    y_position -= 420

    # Adicionar nova página se necessário
    if y_position < 100:
        c.showPage()
        y_position = height - 50

    # Resumo por Quadro
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_position, "Resumo por Quadro")
    y_position -= 20

    resumo_q = df_filtered[df_filtered["PRESENTE"]].groupby("QUADRO").agg(
        Efetivo=("NOME", "count"),
        Média=("MEDIA_FINAL", "mean"),
    ).reset_index().round(2)

    # Converter DataFrame para string formatada para o PDF
    table_str = resumo_q.to_string(index=False)

    # Quebrar em linhas e desenhar
    c.setFont("Helvetica", 10)
    for line in table_str.split('\n'):
        c.drawString(50, y_position, line)
        y_position -= 14
        if y_position < 50: # Nova página se estiver muito baixo
            c.showPage()
            y_position = height - 50
            c.setFont("Helvetica", 10) # Resetar fonte após nova página

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ══════════════════════════════════════════════════════════════════════════════
# APLICAÇÃO STREAMLIT
# ══════════════════════════════════════════════════════════════════════════════

# Carregar dados
df_all, df_adaptado = load_data()

# Aplicar CSS do tema
apply_theme_css()

# Obter configuração de tema atual
theme = get_theme_config()
DARK = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=theme['text_primary'])
GRID = dict(gridcolor=theme['border_color'])

# Sidebar
with st.sidebar:
    st.image(_LOCAL_LOGO_PATH or _get_cbmam_image_url(), width=150)
    st.title("Dashboard TAF CBMAM")

    st.markdown("---")

    pagina = st.radio(
        "Navegação",
        ["🏠 Visão Geral", "📊 Análise Detalhada", "👤 Ficha Individual", "📈 Estatísticas", "♿ TAF Adaptado"],
        index=0,
        key="main_nav"
    )

    st.markdown("---")

    # Filtros globais
    st.subheader("Filtros")

    # Filtro de Quadro
    quadros_disponiveis = ["Todos"] + sorted(df_all["QUADRO"].dropna().unique().tolist())
    quadro_selecionado = st.selectbox("Filtrar por Quadro", quadros_disponiveis, key="filtro_quadro")

    # Filtro de Posto/Graduação
    postos_disponiveis = ["Todos"] + sorted(df_all["POSTO_GRAD"].dropna().unique().tolist(), key=ordem_posto)
    posto_selecionado = st.selectbox("Filtrar por Posto/Graduação", postos_disponiveis, key="filtro_posto")

    # Filtro de Sexo
    sexos_disponiveis = ["Todos"] + sorted(df_all["SEXO"].dropna().unique().tolist())
    sexo_selecionado = st.selectbox("Filtrar por Sexo", sexos_disponiveis, key="filtro_sexo")

    # Filtro de Faixa Etária
    faixas_disponiveis = ["Todas"] + sorted(df_all["FAIXA_ETARIA"].dropna().unique().tolist())
    faixa_selecionada = st.selectbox("Filtrar por Faixa Etária", faixas_disponiveis, key="filtro_faixa")

    st.markdown("---")

    # Botão de download de PDF
    if pagina in ["🏠 Visão Geral", "📊 Análise Detalhada"]: # Apenas para páginas com gráficos gerais
        st.subheader("Exportar Relatório")
        if st.button("Gerar PDF do Relatório"):
            with st.spinner("Gerando PDF..."):
                # Filtrar o DataFrame para o PDF com base nos filtros atuais
                df_filtered_for_pdf = df_all.copy()
                if quadro_selecionado != "Todos":
                    df_filtered_for_pdf = df_filtered_for_pdf[df_filtered_for_pdf["QUADRO"] == quadro_selecionado]
                if posto_selecionado != "Todos":
                    df_filtered_for_pdf = df_filtered_for_pdf[df_filtered_for_pdf["POSTO_GRAD"] == posto_selecionado]
                if sexo_selecionado != "Todos":
                    df_filtered_for_pdf = df_filtered_for_pdf[df_filtered_for_pdf["SEXO"] == sexo_selecionado]
                if faixa_selecionada != "Todas":
                    df_filtered_for_pdf = df_filtered_for_pdf[df_filtered_for_pdf["FAIXA_ETARIA"] == faixa_selecionada]

                pdf_buffer = generate_pdf_report(df_filtered_for_pdf, theme)
                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer,
                    file_name="relatorio_TAF_CBMAM.pdf",
                    mime="application/pdf"
                )

    st.markdown("---")

    # Toggle de tema
    if st.session_state.tema == "escuro":
        if st.button("Mudar para Tema Claro ☀️"):
            st.session_state.tema = "claro"
            st.rerun()
    else:
        if st.button("Mudar para Tema Escuro 🌙"):
            st.session_state.tema = "escuro"
            st.rerun()

# Aplicar filtros
df_filtered = df_all.copy()
if quadro_selecionado != "Todos":
    df_filtered = df_filtered[df_filtered["QUADRO"] == quadro_selecionado]
if posto_selecionado != "Todos":
    df_filtered = df_filtered[df_filtered["POSTO_GRAD"] == posto_selecionado]
if sexo_selecionado != "Todos":
    df_filtered = df_filtered[df_filtered["SEXO"] == sexo_selecionado]
if faixa_selecionada != "Todas":
    df_filtered = df_filtered[df_filtered["FAIXA_ETARIA"] == faixa_selecionada]

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: VISÃO GERAL
# ══════════════════════════════════════════════════════════════════════════════

if pagina == "🏠 Visão Geral":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">🏠 Visão Geral do TAF</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Resumo geral do desempenho dos militares no Teste de Aptidão Física
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    if len(df_filtered) == 0:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
    else:
        # KPIs
        total_militares = len(df_filtered)
        presentes = df_filtered["PRESENTE"].sum()
        ausentes = total_militares - presentes
        media_geral = df_filtered["MEDIA_FINAL"].mean()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Total Militares", total_militares)
        with col2:
            st.metric("✅ Presentes", presentes)
        with col3:
            st.metric("❌ Ausentes", ausentes)
        with col4:
            st.metric("⭐ Média Geral", f"{media_geral:.2f}")

        st.divider()

        # Gráfico de Classificação Geral
        st.markdown(f"<p class='section-title'>📈 Classificação Geral</p>", unsafe_allow_html=True)
        classificacao_counts = df_filtered["CLASSIFICACAO"].value_counts(normalize=True).reset_index()
        classificacao_counts.columns = ["Classificação", "Percentual"]

        fig_classificacao = px.pie(
            classificacao_counts,
            values="Percentual",
            names="Classificação",
            color="Classificação",
            color_discrete_map=COR_MAP,
            title="Distribuição de Classificação Geral"
        )
        fig_classificacao.update_layout(
            **DARK, height=400,
            legend=dict(font_color=theme['text_primary'])
        )
        st.plotly_chart(fig_classificacao, use_container_width=True)

        st.divider()

        # Desempenho por Quadro
        st.markdown(f"<p class='section-title'>🏢 Desempenho por Quadro</p>", unsafe_allow_html=True)
        resumo_quadro = df_filtered[df_filtered["PRESENTE"]].groupby("QUADRO")["MEDIA_FINAL"].mean().reset_index()
        fig_quadro = px.bar(
            resumo_quadro,
            x="QUADRO",
            y="MEDIA_FINAL",
            color="MEDIA_FINAL",
            color_continuous_scale=[theme['badge_bg_bad'], theme['badge_bg_avg'], theme['badge_bg_good']],
            labels={"MEDIA_FINAL": "Média de Pontuação"},
            title="Média de Pontuação por Quadro"
        )
        fig_quadro.update_layout(
            **DARK, height=400,
            xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID),
            coloraxis_colorbar=dict(title="Média")
        )
        st.plotly_chart(fig_quadro, use_container_width=True)

        st.divider()

        # Desempenho por Posto/Graduação
        st.markdown(f"<p class='section-title'>🎖️ Desempenho por Posto/Graduação</p>", unsafe_allow_html=True)
        resumo_posto = df_filtered[df_filtered["PRESENTE"]].groupby("POSTO_GRAD")["MEDIA_FINAL"].mean().reset_index()
        resumo_posto["_ordem"] = resumo_posto["POSTO_GRAD"].apply(ordem_posto)
        resumo_posto = resumo_posto.sort_values("_ordem").drop(columns=["_ordem"])

        fig_posto = px.bar(
            resumo_posto,
            x="POSTO_GRAD",
            y="MEDIA_FINAL",
            color="MEDIA_FINAL",
            color_continuous_scale=[theme['badge_bg_bad'], theme['badge_bg_avg'], theme['badge_bg_good']],
            labels={"MEDIA_FINAL": "Média de Pontuação"},
            title="Média de Pontuação por Posto/Graduação"
        )
        fig_posto.update_layout(
            **DARK, height=400,
            xaxis=dict(**GRID, tickangle=-45), yaxis=dict(range=[0, 11], **GRID),
            coloraxis_colorbar=dict(title="Média")
        )
        st.plotly_chart(fig_posto, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: ANÁLISE DETALHADA
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "📊 Análise Detalhada":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">📊 Análise Detalhada</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Aprofundamento nos resultados por exercício e comparações
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    if len(df_filtered[df_filtered["PRESENTE"]]) == 0:
        st.warning("Nenhum dado disponível para análise detalhada com os filtros selecionados.")
    else:
        df_presentes = df_filtered[df_filtered["PRESENTE"]].copy()

        notas_map = {
            "Corrida": "PONTUACAO_CORRIDA",
            "Abdominal": "PONTUACAO_ABDOMINAL",
            "Flexão": "PONTUACAO_FLEXAO",
            "Natação": "PONTUACAO_NATACAO",
            "Barra": "PONTUACAO_BARRA",
        }

        # Box plot de notas por atividade
        st.markdown(f"<p class='section-title'>📦 Distribuição de Notas por Atividade</p>", unsafe_allow_html=True)

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
        cores = [theme['badge_bg_bad'], theme['badge_bg_avg'], theme['badge_bg_neutral'], theme['badge_bg_good'], theme['accent']]
        for i, (label, col) in enumerate(notas_map.items()):
            vals = df_presentes[col].dropna()
            fig_hist_all.add_trace(go.Histogram(
                x=vals, name=label, opacity=0.6,
                marker_color=cores[i % len(cores)], nbinsx=12,
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

        df_corr = df_presentes[df_presentes["Corrida"].notna()].copy()
        fig_scatter = px.scatter(
            df_corr, x="Corrida", y="MEDIA_FINAL",
            color="CLASSIFICACAO", color_discrete_map=COR_MAP,
            size="MEDIA_FINAL", hover_name="NOME",
            trendline="ols", trendline_color_override=theme['text_primary'],
            labels={"Corrida": "Corrida 12min (metros)", "MEDIA_FINAL": "Média Final"},
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
                df_presentes["Corrida"].mean(),
                df_presentes["Abdominal"].mean(),
                df_presentes["Flexao"].mean(),
                df_presentes["NATACAO_SEG"].mean(),
                df_presentes["BARRA_VALOR"].mean(),
            ],
            "Mediana": [
                df_presentes["Corrida"].median(),
                df_presentes["Abdominal"].median(),
                df_presentes["Flexao"].median(),
                df_presentes["NATACAO_SEG"].median(),
                df_presentes["BARRA_VALOR"].median(),
            ],
            "Mínimo": [
                df_presentes["Corrida"].min(),
                df_presentes["Abdominal"].min(),
                df_presentes["Flexao"].min(),
                df_presentes["NATACAO_SEG"].min(),
                df_presentes["BARRA_VALOR"].min(),
            ],
            "Máximo": [
                df_presentes["Corrida"].max(),
                df_presentes["Abdominal"].max(),
                df_presentes["Flexao"].max(),
                df_presentes["NATACAO_SEG"].max(),
                df_presentes["BARRA_VALOR"].max(),
            ],
        }).round(1)
        st.dataframe(raw_stats, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: FICHA INDIVIDUAL
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "👤 Ficha Individual":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">👤 Ficha Individual</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Perfil detalhado de desempenho por militar
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    militares_nomes = ["Selecione um militar"] + sorted(df_filtered["NOME_COMPLETO"].unique().tolist())
    militar_selecionado = st.selectbox("Selecione o Militar", militares_nomes, key="ficha_militar_select")

    if militar_selecionado != "Selecione um militar":
        ficha = df_filtered[df_filtered["NOME_COMPLETO"] == militar_selecionado].iloc[0]

        st.markdown(f"""
        <div style="
            background-color: {theme['card_bg']};
            border: 1px solid {theme['card_border']};
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        ">
            <h3 style="margin-top:0; color:{theme['text_primary']};">{ficha['POSTO_GRAD']} {ficha['NOME_COMPLETO']}</h3>
            <p style="color:{theme['text_secondary']};">
                Quadro: <strong>{ficha['QUADRO']}</strong> |
                Sexo: <strong>{ficha['SEXO']}</strong> |
                Idade: <strong>{int(ficha['IDADE']) if pd.notna(ficha['IDADE']) else 'N/A'}</strong> |
                Faixa Etária: <strong>{ficha['FAIXA_ETARIA']}</strong>
            </p>
            <p style="font-size:1.2em; color:{theme['text_primary']};">
                Média Final: <strong>{ficha['MEDIA_FINAL']:.2f}</strong>
                <span class="badge-{ficha['CLASSIFICACAO']}">
                    {ficha['CLASSIFICACAO']}
                </span>
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<p class='section-title'>Detalhes do Desempenho</p>", unsafe_allow_html=True)

        if ficha["PRESENTE"]:
            col_corr, col_abd, col_flex, col_nat, col_barra = st.columns(5)

            with col_corr:
                st.metric("Corrida (m)", f"{ficha['Corrida']:.0f}" if pd.notna(ficha['Corrida']) else "N/A",
                          delta=f"{ficha['PONTUACAO_CORRIDA']:.1f} pts" if pd.notna(ficha['PONTUACAO_CORRIDA']) else None)
            with col_abd:
                st.metric("Abdominal (reps)", f"{ficha['Abdominal']:.0f}" if pd.notna(ficha['Abdominal']) else "N/A",
                          delta=f"{ficha['PONTUACAO_ABDOMINAL']:.1f} pts" if pd.notna(ficha['PONTUACAO_ABDOMINAL']) else None)
            with col_flex:
                st.metric("Flexão (reps)", f"{ficha['Flexao']:.0f}" if pd.notna(ficha['Flexao']) else "N/A",
                          delta=f"{ficha['PONTUACAO_FLEXAO']:.1f} pts" if pd.notna(ficha['PONTUACAO_FLEXAO']) else None)
            with col_nat:
                st.metric("Natação (seg)", f"{ficha['NATACAO_SEG']:.1f}" if pd.notna(ficha['NATACAO_SEG']) else "N/A",
                          delta=f"{ficha['PONTUACAO_NATACAO']:.1f} pts" if pd.notna(ficha['PONTUACAO_NATACAO']) else None)
            with col_barra:
                barra_val = f"{ficha['BARRA_VALOR']:.0f}" if pd.notna(ficha['BARRA_VALOR']) else "N/A"
                barra_tipo = ficha['TIPO_BARRA'] if pd.notna(ficha['TIPO_BARRA']) else "Barra"
                st.metric(f"{barra_tipo}", barra_val,
                          delta=f"{ficha['PONTUACAO_BARRA']:.1f} pts" if pd.notna(ficha['PONTUACAO_BARRA']) else None)

            st.markdown(f"<p class='section-title'>Gráfico de Pontuação por Exercício</p>", unsafe_allow_html=True)
            pontuacoes_display = {
                "Corrida": "PONTUACAO_CORRIDA",
                "Abdominal": "PONTUACAO_ABDOMINAL",
                "Flexão": "PONTUACAO_FLEXAO",
                "Natação": "PONTUACAO_NATACAO",
                "Barra": "PONTUACAO_BARRA",
            }
            pontuacoes_df = pd.DataFrame({
                "Exercício": pontuacoes_display.keys(),
                "Pontuação": [ficha[p] for p in pontuacoes_display.values()]
            })
            pontuacoes_df = pontuacoes_df.dropna(subset=["Pontuação"])

            if not pontuacoes_df.empty:
                fig_individual = px.bar(
                    pontuacoes_df,
                    x="Exercício",
                    y="Pontuação",
                    color="Pontuação",
                    color_continuous_scale=["#ef4444", "#f59e0b", "#3b82f6", "#22c55e"],
                    range_y=[0, 10],
                    labels={"Pontuação": "Pontuação"},
                    title=f"Desempenho de {militar_selecionado} por Exercício"
                )
                fig_individual.update_layout(**DARK, height=400, coloraxis_showscale=False, xaxis=dict(**GRID), yaxis=dict(**GRID))
                st.plotly_chart(fig_individual, use_container_width=True)
            else:
                st.info("Não há dados de pontuação para este militar.")
        else:
            st.info("Este militar não compareceu ou não possui dados de TAF válidos para pontuação.")

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: ESTATÍSTICAS
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "📈 Estatísticas":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">📈 Estatísticas Detalhadas</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Análise aprofundada de desempenho por faixa etária, sexo e exercício
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    if len(df_filtered[df_filtered["PRESENTE"]]) == 0:
        st.warning("Nenhum dado disponível para estatísticas com os filtros selecionados.")
    else:
        df_stats = df_filtered[df_filtered["PRESENTE"]].copy()

        st.markdown(f"<p class='section-title'>Média de Pontuação por Faixa Etária e Sexo</p>", unsafe_allow_html=True)
        media_idade_sexo = df_stats.groupby(["FAIXA_ETARIA", "SEXO"])["MEDIA_FINAL"].mean().reset_index()
        fig_media_idade_sexo = px.bar(
            media_idade_sexo,
            x="FAIXA_ETARIA",
            y="MEDIA_FINAL",
            color="SEXO",
            barmode="group",
            labels={"MEDIA_FINAL": "Média de Pontuação", "FAIXA_ETARIA": "Faixa Etária"},
            title="Média de Pontuação por Faixa Etária e Sexo"
        )
        fig_media_idade_sexo.update_layout(**DARK, height=450, xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID),
                                          legend=dict(font_color=theme['text_primary']))
        st.plotly_chart(fig_media_idade_sexo, use_container_width=True)

        st.markdown(f"<p class='section-title'>Distribuição de Pontuações por Exercício</p>", unsafe_allow_html=True)
        exercicio_selecionado = st.selectbox(
            "Selecione o Exercício para Análise",
            options=["Corrida", "Abdominal", "Flexão", "Natação", "Barra"],
            key="exercicio_stats"
        )
        coluna_pontuacao = f"PONTUACAO_{exercicio_selecionado.upper()}"

        if coluna_pontuacao in df_stats.columns:
            fig_dist_exercicio = px.histogram(
                df_stats,
                x=coluna_pontuacao,
                color="SEXO",
                barmode="overlay",
                nbins=20,
                labels={coluna_pontuacao: f"Pontuação {exercicio_selecionado}", "count": "Número de Militares"},
                title=f"Distribuição de Pontuações para {exercicio_selecionado}"
            )
            fig_dist_exercicio.update_layout(**DARK, height=450, xaxis=dict(**GRID), yaxis=dict(**GRID),
                                            legend=dict(font_color=theme['text_primary']))
            st.plotly_chart(fig_dist_exercicio, use_container_width=True)
        else:
            st.warning(f"Coluna de pontuação '{coluna_pontuacao}' não encontrada.")

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

        display_cols = [c for c in df_adaptado.columns if c not in ["PRESENTE", "_ordem", "NOME_COMPLETO", "Corrida_Original", "Barra_Original", "CORRIDA_IS_TEMPO", "BARRA_IS_TEMPO"]]
        df_adapt_display = df_adaptado[display_cols].copy()
        df_adapt_display = df_adapt_display.fillna("—")

        # Limpar valores "nan"
        for col in df_adapt_display.columns:
            df_adapt_display[col] = df_adapt_display[col].astype(str).replace("nan", "—")

        st.dataframe(df_adapt_display, height=500)

        # Exercícios realizados
        st.markdown(f"<p class='section-title'>📊 Exercícios Realizados</p>", unsafe_allow_html=True)

        # Estes exercícios devem ser as colunas que você espera no TAF adaptado
        # Adicionei algumas colunas que podem ser relevantes para TAF adaptado,
        # mas que não estão no CSV fornecido. Você pode ajustar esta lista.
        exercicios_adapt_cols = [
            "Corrida", "Abdominal", "Flexao", "NATACAO_SEG", "BARRA_VALOR", # Os 5 principais, mas para adaptados
            # Adicione aqui outras colunas que representariam exercícios adaptados no seu CSV
            # Ex: "CAMINHADA", "PRANCHA", "PUXADOR_FRONTAL", "FLUTUACAO", "SUPINO", "COOPER"
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
