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

def apply_dynamic_css(theme):
    css = f"""
    <style>
      /* Cores de fundo e texto globais */
      body, p, span, div, label, h1, h2, h3, h4, h5, h6, text, tspan {{
        color: {theme['text_primary']} !important;
        fill: {theme['text_primary']} !important;
      }}
      [data-testid="stAppViewContainer"] {{
        background: {theme['bg_primary']};
      }}
      [data-testid="stSidebar"] {{
        background: {theme['bg_secondary']};
        border-right: 1px solid {theme['border_color']};
      }}

      /* Inputs e campos de texto */
      input, 
      input[type="text"],
      input[type="search"],
      input[type="password"],
      input[type="email"],
      input[type="number"],
      input[type="date"],
      textarea,
      .stTextInput > div > div > input,
      .stNumberInput > div > div > input {{
        color: {theme['text_primary']} !important;
        background-color: {theme['input_bg']} !important;
        border: 1px solid {theme['input_border']} !important;
        border-radius: 6px !important;
      }}

      input::placeholder {{
        color: {theme['text_secondary']} !important;
        opacity: 0.8 !important;
      }}

      /* Selectbox específico do Streamlit */
      .stSelectbox > div > div > input,
      [data-testid="stSelectbox"] input {{
        color: {theme['text_primary']} !important;
        background-color: {theme['input_bg']} !important;
        border: 1px solid {theme['input_border']} !important;
        padding: 10px 12px !important;
        border-radius: 6px !important;
      }}

      .stSelectbox > div > div > input:focus {{
        outline: none !important;
        border-color: {theme['accent']} !important;
        box-shadow: 0 0 0 3px {theme['accent']}40 !important; /* 40 é opacidade */
      }}

      /* Melhoria para selectbox dropdown */
      div[data-baseweb="select"] {{
        background-color: {theme['input_bg']} !important;
        border: 1px solid {theme['input_border']} !important;
        border-radius: 6px !important;
      }}

      /* Opções do dropdown */
      div[data-baseweb="menu"] {{
        background-color: {theme['bg_secondary']} !important;
        border: 1px solid {theme['border_color']} !important;
        border-radius: 6px !important;
      }}

      li[data-baseweb="option"] {{
        color: {theme['text_primary']} !important;
        background-color: {theme['bg_secondary']} !important;
        padding: 12px 16px !important;
      }}

      li[data-baseweb="option"]:hover {{
        background-color: {theme['accent']}30 !important; /* 30 é opacidade */
        color: {theme['text_primary']} !important;
      }}

      /* Botões */
      button {{
        color: {theme['text_primary']} !important;
        background-color: {theme['bg_tertiary']} !important;
        border: 1px solid {theme['border_color']} !important;
        border-radius: 6px !important;
      }}
      button:hover {{
        background-color: {theme['accent']} !important;
        color: white !important;
        border-color: {theme['accent']} !important;
      }}

      /* Links */
      a {{
        color: {theme['accent']} !important;
      }}

      /* Expander */
      .streamlit-expanderHeader {{
        background-color: {theme['bg_secondary']} !important;
        color: {theme['text_primary']} !important;
        border: 1px solid {theme['border_color']} !important;
        border-radius: 6px !important;
      }}
      .streamlit-expanderContent {{
        background-color: {theme['bg_tertiary']} !important;
        border: 1px solid {theme['border_color']} !important;
        border-top: none !important;
        border-bottom-left-radius: 6px !important;
        border-bottom-right-radius: 6px !important;
      }}

      /* Dataframe */
      .stDataFrame {{
        color: {theme['text_primary']} !important;
      }}
      .stDataFrame .header {{
        background-color: {theme['bg_secondary']} !important;
        color: {theme['text_primary']} !important;
      }}
      .stDataFrame .row-even {{
        background-color: {theme['bg_tertiary']} !important;
      }}
      .stDataFrame .row-odd {{
        background-color: {theme['bg_primary']} !important;
      }}
      .stDataFrame .dataframe-column-header {{
        color: {theme['text_primary']} !important;
      }}

      /* Metric */
      [data-testid="stMetric"] > div > div:first-child {{
        color: {theme['text_secondary']} !important;
      }}
      [data-testid="stMetric"] > div > div:nth-child(2) {{
        color: {theme['text_primary']} !important;
      }}

      /* Badges (para classificação) */
      .badge-excelente {{
          background-color: {theme['badge_bg_good']};
          color: {theme['badge_text_good']};
          border: 1px solid {theme['badge_border_good']};
      }}
      .badge-bom {{
          background-color: {theme['badge_bg_avg']};
          color: {theme['badge_text_avg']};
          border: 1px solid {theme['badge_border_avg']};
      }}
      .badge-regular {{
          background-color: {theme['badge_bg_avg']};
          color: {theme['badge_text_avg']};
          border: 1px solid {theme['badge_border_avg']};
      }}
      .badge-insuficiente {{
          background-color: {theme['badge_bg_bad']};
          color: {theme['badge_text_bad']};
          border: 1px solid {theme['badge_border_bad']};
      }}
      .badge-ausente {{
          background-color: {theme['badge_bg_neutral']};
          color: {theme['badge_text_neutral']};
          border: 1px solid {theme['badge_border_neutral']};
      }}
      .badge {{
          display: inline-block;
          padding: 0.25em 0.6em;
          font-size: 0.75em;
          font-weight: 700;
          line-height: 1;
          text-align: center;
          white-space: nowrap;
          vertical-align: baseline;
          border-radius: 0.375rem;
      }}

      /* Títulos de seção */
      .section-title {{
          font-size: 1.25rem;
          font-weight: 600;
          color: {theme['text_primary']};
          margin-top: 1.5rem;
          margin-bottom: 0.75rem;
      }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DO PLOTLY
# ══════════════════════════════════════════════════════════════════════════════

# Cores para o tema escuro
DARK_PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e7eefc"),
    xaxis=dict(gridcolor="rgba(255,255,255,.06)", zerolinecolor="rgba(255,255,255,.06)"),
    yaxis=dict(gridcolor="rgba(255,255,255,.06)", zerolinecolor="rgba(255,255,255,.06)"),
    legend=dict(font=dict(color="#e7eefc")),
    colorway=px.colors.qualitative.Plotly # Garante cores distintas
)

# Cores para o tema claro
LIGHT_PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#1a1a1a"),
    xaxis=dict(gridcolor="rgba(0,0,0,.1)", zerolinecolor="rgba(0,0,0,.1)"),
    yaxis=dict(gridcolor="rgba(0,0,0,.1)", zerolinecolor="rgba(0,0,0,.1)"),
    legend=dict(font=dict(color="#1a1a1a")),
    colorway=px.colors.qualitative.Plotly # Garante cores distintas
)

# ══════════════════════════════════════════════════════════════════════════════
# MAPAS DE CORES E ORDENAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

COR_MAP = {
    "Excelente": "#22c55e",
    "Bom":       "#3b82f6",
    "Regular":   "#f59e0b",
    "Insuficiente": "#ef4444",
    "Ausente":   "#64748b",
    "Não Compareceu": "#64748b", # Adicionado para consistência
}

ORDEM_POSTO = {
    "CEL": 1, "TC": 2, "MAJOR": 3, "CAP": 4,
    "1° TEN": 5, "2° TEN": 6, "ASP OF": 7,
    "ST": 8, "1° SGT": 9, "2° SGT": 10, "3° SGT": 11,
    "CB": 12, "SD": 13,
}

def ordem_posto(posto):
    return ORDEM_POSTO.get(posto, 99) # Retorna 99 para postos não mapeados, colocando-os no final

# ══════════════════════════════════════════════════════════════════════════════
# REGRAS DE PONTUAÇÃO - MASCULINO (10 FAIXAS ETÁRIAS)
# ══════════════════════════════════════════════════════════════════════════════
REGRAS_MASCULINO = {
    '18-21': {'Corrida': {3200: 10, 3100: 9.5, 3000: 9.0, 2900: 8.5, 2800: 8.0, 2700: 7.5, 2600: 7.0, 2500: 6.5, 2400: 6.0, 2300: 5.5, 2200: 5.0, 2100: 4.5, 2000: 4.0, 1900: 3.5, 1800: 3.0, 1700: 2.5, 1600: 2.0, 1500: 1.5, 0: 0}, 'Flexao': {38: 10, 37: 9.5, 36: 9.0, 35: 8.5, 34: 8.0, 33: 7.5, 32: 7.0, 31: 6.5, 30: 6.0, 29: 5.5, 28: 5.0, 27: 4.5, 26: 4.0, 25: 3.5, 24: 3.0, 23: 2.5, 22: 2.0, 21: 1.5, 0: 0}, 'Abdominal': {48: 10, 47: 9.5, 46: 9.0, 45: 8.5, 44: 8.0, 43: 7.5, 42: 7.0, 41: 6.5, 40: 6.0, 39: 5.5, 38: 5.0, 37: 4.5, 36: 4.0, 35: 3.5, 34: 3.0, 33: 2.5, 32: 2.0, 31: 1.5, 0: 0}, 'Barra': {13: 10, 12: 9.5, 11: 9.0, 10: 8.5, 9: 8.0, 8: 7.5, 7: 7.0, 6: 6.5, 5: 6.0, 4: 5.5, 3: 5.0, 2: 4.5, 1: 4.0, 0: 0}, 'Natação': {40: 10, 44: 9.5, 48: 9.0, 52: 8.5, 56: 8.0, 60: 7.5, 64: 7.0, 68: 6.5, 72: 6.0, 76: 5.5, 80: 5.0, 84: 4.5, 88: 4.0, 92: 3.5, 96: 3.0, 100: 2.5, 104: 2.0, 108: 1.5, 112: 1.0, 116: 0.5, 120: 0}},
    '22-25': {'Corrida': {3000: 10, 2900: 9.5, 2800: 9.0, 2700: 8.5, 2600: 8.0, 2500: 7.5, 2400: 7.0, 2300: 6.5, 2200: 6.0, 2100: 5.5, 2000: 5.0, 1900: 4.5, 1800: 4.0, 1700: 3.5, 1600: 3.0, 1500: 2.5, 1400: 2.0, 1300: 1.5, 0: 0}, 'Flexao': {36: 10, 35: 9.5, 34: 9.0, 33: 8.5, 32: 8.0, 31: 7.5, 30: 7.0, 29: 6.5, 28: 6.0, 27: 5.5, 26: 5.0, 25: 4.5, 24: 4.0, 23: 3.5, 22: 3.0, 21: 2.5, 20: 2.0, 19: 1.5, 0: 0}, 'Abdominal': {46: 10, 45: 9.5, 44: 9.0, 43: 8.5, 42: 8.0, 41: 7.5, 40: 7.0, 39: 6.5, 38: 6.0, 37: 5.5, 36: 5.0, 35: 4.5, 34: 4.0, 33: 3.5, 32: 3.0, 31: 2.5, 30: 2.0, 29: 1.5, 0: 0}, 'Barra': {12: 10, 11: 9.5, 10: 9.0, 9: 8.5, 8: 8.0, 7: 7.5, 6: 7.0, 5: 6.5, 4: 6.0, 3: 5.5, 2: 5.0, 1: 4.5, 0: 0}, 'Natação': {42: 10, 46: 9.5, 50: 9.0, 54: 8.5, 58: 8.0, 62: 7.5, 66: 7.0, 70: 6.5, 74: 6.0, 78: 5.5, 82: 5.0, 86: 4.5, 90: 4.0, 94: 3.5, 98: 3.0, 102: 2.5, 106: 2.0, 110: 1.5, 114: 1.0, 118: 0.5, 122: 0}},
    '26-29': {'Corrida': {2800: 10, 2700: 9.5, 2600: 9.0, 2500: 8.5, 2400: 8.0, 2300: 7.5, 2200: 7.0, 2100: 6.5, 2000: 6.0, 1900: 5.5, 1800: 5.0, 1700: 4.5, 1600: 4.0, 1500: 3.5, 1400: 3.0, 1300: 2.5, 1200: 2.0, 1100: 1.5, 0: 0}, 'Flexao': {34: 10, 33: 9.5, 32: 9.0, 31: 8.5, 30: 8.0, 29: 7.5, 28: 7.0, 27: 6.5, 26: 6.0, 25: 5.5, 24: 5.0, 23: 4.5, 22: 4.0, 21: 3.5, 20: 3.0, 19: 2.5, 18: 2.0, 17: 1.5, 0: 0}, 'Abdominal': {44: 10, 43: 9.5, 42: 9.0, 41: 8.5, 40: 8.0, 39: 7.5, 38: 7.0, 37: 6.5, 36: 6.0, 35: 5.5, 34: 5.0, 33: 4.5, 32: 4.0, 31: 3.5, 30: 3.0, 29: 2.5, 28: 2.0, 27: 1.5, 0: 0}, 'Barra': {11: 10, 10: 9.5, 9: 9.0, 8: 8.5, 7: 8.0, 6: 7.5, 5: 7.0, 4: 6.5, 3: 6.0, 2: 5.5, 1: 5.0, 0: 0}, 'Natação': {44: 10, 48: 9.5, 52: 9.0, 56: 8.5, 60: 8.0, 64: 7.5, 68: 7.0, 72: 6.5, 76: 6.0, 80: 5.5, 84: 5.0, 88: 4.5, 92: 4.0, 96: 3.5, 100: 3.0, 104: 2.5, 108: 2.0, 112: 1.5, 116: 1.0, 120: 0.5, 124: 0}},
    '30-33': {'Corrida': {2600: 10, 2500: 9.5, 2400: 9.0, 2300: 8.5, 2200: 8.0, 2100: 7.5, 2000: 7.0, 1900: 6.5, 1800: 6.0, 1700: 5.5, 1600: 5.0, 1500: 4.5, 1400: 4.0, 1300: 3.5, 1200: 3.0, 1100: 2.5, 1000: 2.0, 900: 1.5, 0: 0}, 'Flexao': {32: 10, 31: 9.5, 30: 9.0, 29: 8.5, 28: 8.0, 27: 7.5, 26: 7.0, 25: 6.5, 24: 6.0, 23: 5.5, 22: 5.0, 21: 4.5, 20: 4.0, 19: 3.5, 18: 3.0, 17: 2.5, 16: 2.0, 15: 1.5, 0: 0}, 'Abdominal': {42: 10, 41: 9.5, 40: 9.0, 39: 8.5, 38: 8.0, 37: 7.5, 36: 7.0, 35: 6.5, 34: 6.0, 33: 5.5, 32: 5.0, 31: 4.5, 30: 4.0, 29: 3.5, 28: 3.0, 27: 2.5, 26: 2.0, 25: 1.5, 0: 0}, 'Barra': {10: 10, 9: 9.5, 8: 9.0, 7: 8.5, 6: 8.0, 5: 7.5, 4: 7.0, 3: 6.5, 2: 6.0, 1: 5.5, 0: 0}, 'Natação': {46: 10, 50: 9.5, 54: 9.0, 58: 8.5, 62: 8.0, 66: 7.5, 70: 7.0, 74: 6.5, 78: 6.0, 82: 5.5, 86: 5.0, 90: 4.5, 94: 4.0, 98: 3.5, 102: 3.0, 106: 2.5, 110: 2.0, 114: 1.5, 118: 1.0, 122: 0.5, 126: 0}},
    '34-37': {'Corrida': {2400: 10, 2300: 9.5, 2200: 9.0, 2100: 8.5, 2000: 8.0, 1900: 7.5, 1800: 7.0, 1700: 6.5, 1600: 6.0, 1500: 5.5, 1400: 5.0, 1300: 4.5, 1200: 4.0, 1100: 3.5, 1000: 3.0, 900: 2.5, 800: 2.0, 700: 1.5, 0: 0}, 'Flexao': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5, 22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5, 14: 2.0, 13: 1.5, 0: 0}, 'Abdominal': {40: 10, 39: 9.5, 38: 9.0, 37: 8.5, 36: 8.0, 35: 7.5, 34: 7.0, 33: 6.5, 32: 6.0, 31: 5.5, 30: 5.0, 29: 4.5, 28: 4.0, 27: 3.5, 26: 3.0, 25: 2.5, 24: 2.0, 23: 1.5, 0: 0}, 'Barra': {9: 10, 8: 9.5, 7: 9.0, 6: 8.5, 5: 8.0, 4: 7.5, 3: 7.0, 2: 6.5, 1: 6.0, 0: 0}, 'Natação': {48: 10, 52: 9.5, 56: 9.0, 60: 8.5, 64: 8.0, 68: 7.5, 72: 7.0, 76: 6.5, 80: 6.0, 84: 5.5, 88: 5.0, 92: 4.5, 96: 4.0, 100: 3.5, 104: 3.0, 108: 2.5, 112: 2.0, 116: 1.5, 120: 1.0, 124: 0.5, 128: 0}},
    '38-41': {'Corrida': {2200: 10, 2100: 9.5, 2000: 9.0, 1900: 8.5, 1800: 8.0, 1700: 7.5, 1600: 7.0, 1500: 6.5, 1400: 6.0, 1300: 5.5, 1200: 5.0, 1100: 4.5, 1000: 4.0, 900: 3.5, 800: 3.0, 700: 2.5, 600: 2.0, 500: 1.5, 0: 0}, 'Flexao': {28: 10, 27: 9.5, 26: 9.0, 25: 8.5, 24: 8.0, 23: 7.5, 22: 7.0, 21: 6.5, 20: 6.0, 19: 5.5, 18: 5.0, 17: 4.5, 16: 4.0, 15: 3.5, 14: 3.0, 13: 2.5, 12: 2.0, 11: 1.5, 0: 0}, 'Abdominal': {38: 10, 37: 9.5, 36: 9.0, 35: 8.5, 34: 8.0, 33: 7.5, 32: 7.0, 31: 6.5, 30: 6.0, 29: 5.5, 28: 5.0, 27: 4.5, 26: 4.0, 25: 3.5, 24: 3.0, 23: 2.5, 22: 2.0, 21: 1.5, 0: 0}, 'Barra': {8: 10, 7: 9.5, 6: 9.0, 5: 8.5, 4: 8.0, 3: 7.5, 2: 7.0, 1: 6.5, 0: 0}, 'Natação': {50: 10, 54: 9.5, 58: 9.0, 62: 8.5, 66: 8.0, 70: 7.5, 74: 7.0, 78: 6.5, 82: 6.0, 86: 5.5, 90: 5.0, 94: 4.5, 98: 4.0, 102: 3.5, 106: 3.0, 110: 2.5, 114: 2.0, 118: 1.5, 122: 1.0, 126: 0.5, 130: 0}},
    '42-45': {'Corrida': {2000: 10, 1900: 9.5, 1800: 9.0, 1700: 8.5, 1600: 8.0, 1500: 7.5, 1400: 7.0, 1300: 6.5, 1200: 6.0, 1100: 5.5, 1000: 5.0, 900: 4.5, 800: 4.0, 700: 3.5, 600: 3.0, 500: 2.5, 400: 2.0, 300: 1.5, 0: 0}, 'Flexao': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0}, 'Abdominal': {36: 10, 35: 9.5, 34: 9.0, 33: 8.5, 32: 8.0, 31: 7.5, 30: 7.0, 29: 6.5, 28: 6.0, 27: 5.5, 26: 5.0, 25: 4.5, 24: 4.0, 23: 3.5, 22: 3.0, 21: 2.5, 20: 2.0, 19: 1.5, 0: 0}, 'Barra': {7: 10, 6: 9.5, 5: 9.0, 4: 8.5, 3: 8.0, 2: 7.5, 1: 7.0, 0: 0}, 'Natação': {52: 10, 56: 9.5, 60: 9.0, 64: 8.5, 68: 8.0, 72: 7.5, 76: 7.0, 80: 6.5, 84: 6.0, 88: 5.5, 92: 5.0, 96: 4.5, 100: 4.0, 104: 3.5, 108: 3.0, 112: 2.5, 116: 2.0, 120: 1.5, 124: 1.0, 128: 0.5, 132: 0}},
    '46-49': {'Corrida': {1800: 10, 1700: 9.5, 1600: 9.0, 1500: 8.5, 1400: 8.0, 1300: 7.5, 1200: 7.0, 1100: 6.5, 1000: 6.0, 900: 5.5, 800: 5.0, 700: 4.5, 600: 4.0, 500: 3.5, 400: 3.0, 300: 2.5, 200: 2.0, 100: 1.5, 0: 0}, 'Flexao': {24: 10, 23: 9.5, 22: 9.0, 21: 8.5, 20: 8.0, 19: 7.5, 18: 7.0, 17: 6.5, 16: 6.0, 15: 5.5, 14: 5.0, 13: 4.5, 12: 4.0, 11: 3.5, 10: 3.0, 9: 2.5, 8: 2.0, 7: 1.5, 0: 0}, 'Abdominal': {34: 10, 33: 9.5, 32: 9.0, 31: 8.5, 30: 8.0, 29: 7.5, 28: 7.0, 27: 6.5, 26: 6.0, 25: 5.5, 24: 5.0, 23: 4.5, 22: 4.0, 21: 3.5, 20: 3.0, 19: 2.5, 18: 2.0, 17: 1.5, 0: 0}, 'Barra': {6: 10, 5: 9.5, 4: 9.0, 3: 8.5, 2: 8.0, 1: 7.5, 0: 0}, 'Natação': {54: 10, 58: 9.5, 62: 9.0, 66: 8.5, 70: 8.0, 74: 7.5, 78: 7.0, 82: 6.5, 86: 6.0, 90: 5.5, 94: 5.0, 98: 4.5, 102: 4.0, 106: 3.5, 110: 3.0, 114: 2.5, 118: 2.0, 122: 1.5, 126: 1.0, 130: 0.5, 134: 0}},
    '50-53': {'Corrida': {1600: 10, 1500: 9.5, 1400: 9.0, 1300: 8.5, 1200: 8.0, 1100: 7.5, 1000: 7.0, 900: 6.5, 800: 6.0, 700: 5.5, 600: 5.0, 500: 4.5, 400: 4.0, 300: 3.5, 200: 3.0, 100: 2.5, 0: 0}, 'Flexao': {22: 10, 21: 9.5, 20: 9.0, 19: 8.5, 18: 8.0, 17: 7.5, 16: 7.0, 15: 6.5, 14: 6.0, 13: 5.5, 12: 5.0, 11: 4.5, 10: 4.0, 9: 3.5, 8: 3.0, 7: 2.5, 6: 2.0, 5: 1.5, 0: 0}, 'Abdominal': {32: 10, 31: 9.5, 30: 9.0, 29: 8.5, 28: 8.0, 27: 7.5, 26: 7.0, 25: 6.5, 24: 6.0, 23: 5.5, 22: 5.0, 21: 4.5, 20: 4.0, 19: 3.5, 18: 3.0, 17: 2.5, 16: 2.0, 15: 1.5, 0: 0}, 'Barra': {5: 10, 4: 9.5, 3: 9.0, 2: 8.5, 1: 8.0, 0: 0}, 'Natação': {56: 10, 60: 9.5, 64: 9.0, 68: 8.5, 72: 8.0, 76: 7.5, 80: 7.0, 84: 6.5, 88: 6.0, 92: 5.5, 96: 5.0, 100: 4.5, 104: 4.0, 108: 3.5, 112: 3.0, 116: 2.5, 120: 2.0, 124: 1.5, 128: 1.0, 132: 0.5, 136: 0}},
    '54-57': {'Corrida': {1400: 10, 1300: 9.5, 1200: 9.0, 1100: 8.5, 1000: 8.0, 900: 7.5, 800: 7.0, 700: 6.5, 600: 6.0, 500: 5.5, 400: 5.0, 300: 4.5, 200: 4.0, 100: 3.5, 0: 0}, 'Flexao': {20: 10, 19: 9.5, 18: 9.0, 17: 8.5, 16: 8.0, 15: 7.5, 14: 7.0, 13: 6.5, 12: 6.0, 11: 5.5, 10: 5.0, 9: 4.5, 8: 4.0, 7: 3.5, 6: 3.0, 5: 2.5, 4: 2.0, 3: 1.5, 0: 0}, 'Abdominal': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5, 22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5, 14: 2.0, 13: 1.5, 0: 0}, 'Barra': {4: 10, 3: 9.5, 2: 9.0, 1: 8.5, 0: 0}, 'Natação': {58: 10, 62: 9.5, 66: 9.0, 70: 8.5, 74: 8.0, 78: 7.5, 82: 7.0, 86: 6.5, 90: 6.0, 94: 5.5, 98: 5.0, 102: 4.5, 106: 4.0, 110: 3.5, 114: 3.0, 118: 2.5, 122: 2.0, 126: 1.5, 130: 1.0, 134: 0.5, 138: 0}},
    '58-61': {'Corrida': {1200: 10, 1100: 9.5, 1000: 9.0, 900: 8.5, 800: 8.0, 700: 7.5, 600: 7.0, 500: 6.5, 400: 6.0, 300: 5.5, 200: 5.0, 100: 4.5, 0: 0}, 'Flexao': {18: 10, 17: 9.5, 16: 9.0, 15: 8.5, 14: 8.0, 13: 7.5, 12: 7.0, 11: 6.5, 10: 6.0, 9: 5.5, 8: 5.0, 7: 4.5, 6: 4.0, 5: 3.5, 4: 3.0, 3: 2.5, 2: 2.0, 1: 1.5, 0: 0}, 'Abdominal': {28: 10, 27: 9.5, 26: 9.0, 25: 8.5, 24: 8.0, 23: 7.5, 22: 7.0, 21: 6.5, 20: 6.0, 19: 5.5, 18: 5.0, 17: 4.5, 16: 4.0, 15: 3.5, 14: 3.0, 13: 2.5, 12: 2.0, 11: 1.5, 0: 0}, 'Barra': {3: 10, 2: 9.5, 1: 9.0, 0: 0}, 'Natação': {60: 10, 64: 9.5, 68: 9.0, 72: 8.5, 76: 8.0, 80: 7.5, 84: 7.0, 88: 6.5, 92: 6.0, 96: 5.5, 100: 5.0, 104: 4.5, 108: 4.0, 112: 3.5, 116: 3.0, 120: 2.5, 124: 2.0, 128: 1.5, 132: 1.0, 136: 0.5, 140: 0}},
    '62+': {'Corrida': {1000: 10, 900: 9.5, 800: 9.0, 700: 8.5, 600: 8.0, 500: 7.5, 400: 7.0, 300: 6.5, 200: 6.0, 100: 5.5, 0: 0}, 'Flexao': {16: 10, 15: 9.5, 14: 9.0, 13: 8.5, 12: 8.0, 11: 7.5, 10: 7.0, 9: 6.5, 8: 6.0, 7: 5.5, 6: 5.0, 5: 4.5, 4: 4.0, 3: 3.5, 2: 3.0, 1: 2.5, 0: 0}, 'Abdominal': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0}, 'Barra': {2: 10, 1: 9.5, 0: 0}, 'Natação': {62: 10, 66: 9.5, 70: 9.0, 74: 8.5, 78: 8.0, 82: 7.5, 86: 7.0, 90: 6.5, 94: 6.0, 98: 5.5, 102: 5.0, 106: 4.5, 110: 4.0, 114: 3.5, 118: 3.0, 122: 2.5, 126: 2.0, 130: 1.5, 134: 1.0, 138: 0.5, 142: 0}},
}

# ══════════════════════════════════════════════════════════════════════════════
# REGRAS DE PONTUAÇÃO - FEMININO (10 FAIXAS ETÁRIAS)
# ══════════════════════════════════════════════════════════════════════════════
REGRAS_FEMININO = {
    '18-21': {'Corrida': {1800: 10, 1700: 9.5, 1600: 9.0, 1500: 8.5, 1400: 8.0, 1300: 7.5, 1200: 7.0, 1100: 6.5, 1000: 6.0, 900: 5.5, 800: 5.0, 700: 4.5, 600: 4.0, 500: 3.5, 400: 3.0, 300: 2.5, 200: 2.0, 100: 1.5, 0: 0}, 'Flexao': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0}, 'Abdominal': {40: 10, 39: 9.5, 38: 9.0, 37: 8.5, 36: 8.0, 35: 7.5, 34: 7.0, 33: 6.5, 32: 6.0, 31: 5.5, 30: 5.0, 29: 4.5, 28: 4.0, 27: 3.5, 26: 3.0, 25: 2.5, 24: 2.0, 23: 1.5, 0: 0}, 'Barra': {60: 10, 63: 9.5, 66: 9.0, 69: 8.5, 72: 8.0, 75: 7.5, 78: 7.0, 81: 6.5, 84: 6.0, 87: 5.5, 90: 5.0, 93: 4.5, 96: 4.0, 99: 3.5, 102: 3.0, 105: 2.5, 108: 2.0, 111: 1.5, 114: 1.0, 117: 0.5, 120: 0}, 'Natação': {45: 10, 49: 9.5, 53: 9.0, 57: 8.5, 61: 8.0, 65: 7.5, 69: 7.0, 73: 6.5, 77: 6.0, 81: 5.5, 85: 5.0, 89: 4.5, 93: 4.0, 97: 3.5, 101: 3.0, 105: 2.5, 109: 2.0, 113: 1.5, 117: 1.0, 121: 0.5, 125: 0}},
    '22-25': {'Corrida': {1700: 10, 1600: 9.5, 1500: 9.0, 1400: 8.5, 1300: 8.0, 1200: 7.5, 1100: 7.0, 1000: 6.5, 900: 6.0, 800: 5.5, 700: 5.0, 600: 4.5, 500: 4.0, 400: 3.5, 300: 3.0, 200: 2.5, 100: 2.0, 0: 0}, 'Flexao': {24: 10, 23: 9.5, 22: 9.0, 21: 8.5, 20: 8.0, 19: 7.5, 18: 7.0, 17: 6.5, 16: 6.0, 15: 5.5, 14: 5.0, 13: 4.5, 12: 4.0, 11: 3.5, 10: 3.0, 9: 2.5, 8: 2.0, 7: 1.5, 0: 0}, 'Abdominal': {38: 10, 37: 9.5, 36: 9.0, 35: 8.5, 34: 8.0, 33: 7.5, 32: 7.0, 31: 6.5, 30: 6.0, 29: 5.5, 28: 5.0, 27: 4.5, 26: 4.0, 25: 3.5, 24: 3.0, 23: 2.5, 22: 2.0, 21: 1.5, 0: 0}, 'Barra': {62: 10, 65: 9.5, 68: 9.0, 71: 8.5, 74: 8.0, 77: 7.5, 80: 7.0, 83: 6.5, 86: 6.0, 89: 5.5, 92: 5.0, 95: 4.5, 98: 4.0, 101: 3.5, 104: 3.0, 107: 2.5, 110: 2.0, 113: 1.5, 116: 1.0, 119: 0.5, 122: 0}, 'Natação': {47: 10, 51: 9.5, 55: 9.0, 59: 8.5, 63: 8.0, 67: 7.5, 71: 7.0, 75: 6.5, 79: 6.0, 83: 5.5, 87: 5.0, 91: 4.5, 95: 4.0, 99: 3.5, 103: 3.0, 107: 2.5, 111: 2.0, 115: 1.5, 119: 1.0, 123: 0.5, 127: 0}},
    '26-29': {'Corrida': {1600: 10, 1500: 9.5, 1400: 9.0, 1300: 8.5, 1200: 8.0, 1100: 7.5, 1000: 7.0, 900: 6.5, 800: 6.0, 700: 5.5, 600: 5.0, 500: 4.5, 400: 4.0, 300: 3.5, 200: 3.0, 100: 2.5, 0: 0}, 'Flexao': {22: 10, 21: 9.5, 20: 9.0, 19: 8.5, 18: 8.0, 17: 7.5, 16: 7.0, 15: 6.5, 14: 6.0, 13: 5.5, 12: 5.0, 11: 4.5, 10: 4.0, 9: 3.5, 8: 3.0, 7: 2.5, 6: 2.0, 5: 1.5, 0: 0}, 'Abdominal': {36: 10, 35: 9.5, 34: 9.0, 33: 8.5, 32: 8.0, 31: 7.5, 30: 7.0, 29: 6.5, 28: 6.0, 27: 5.5, 26: 5.0, 25: 4.5, 24: 4.0, 23: 3.5, 22: 3.0, 21: 2.5, 20: 2.0, 19: 1.5, 0: 0}, 'Barra': {64: 10, 67: 9.5, 70: 9.0, 73: 8.5, 76: 8.0, 79: 7.5, 82: 7.0, 85: 6.5, 88: 6.0, 91: 5.5, 94: 5.0, 97: 4.5, 100: 4.0, 103: 3.5, 106: 3.0, 109: 2.5, 112: 2.0, 115: 1.5, 118: 1.0, 121: 0.5, 124: 0}, 'Natação': {49: 10, 53: 9.5, 57: 9.0, 61: 8.5, 65: 8.0, 69: 7.5, 73: 7.0, 77: 6.5, 81: 6.0, 85: 5.5, 89: 5.0, 93: 4.5, 97: 4.0, 101: 3.5, 105: 3.0, 109: 2.5, 113: 2.0, 117: 1.5, 121: 1.0, 125: 0.5, 129: 0}},
    '30-33': {'Corrida': {1500: 10, 1400: 9.5, 1300: 9.0, 1200: 8.5, 1100: 8.0, 1000: 7.5, 900: 7.0, 800: 6.5, 700: 6.0, 600: 5.5, 500: 5.0, 400: 4.5, 300: 4.0, 200: 3.5, 100: 3.0, 0: 0}, 'Flexao': {20: 10, 19: 9.5, 18: 9.0, 17: 8.5, 16: 8.0, 15: 7.5, 14: 7.0, 13: 6.5, 12: 6.0, 11: 5.5, 10: 5.0, 9: 4.5, 8: 4.0, 7: 3.5, 6: 3.0, 5: 2.5, 4: 2.0, 3: 1.5, 0: 0}, 'Abdominal': {34: 10, 33: 9.5, 32: 9.0, 31: 8.5, 30: 8.0, 29: 7.5, 28: 7.0, 27: 6.5, 26: 6.0, 25: 5.5, 24: 5.0, 23: 4.5, 22: 4.0, 21: 3.5, 20: 3.0, 19: 2.5, 18: 2.0, 17: 1.5, 0: 0}, 'Barra': {66: 10, 69: 9.5, 72: 9.0, 75: 8.5, 78: 8.0, 81: 7.5, 84: 7.0, 87: 6.5, 90: 6.0, 93: 5.5, 96: 5.0, 99: 4.5, 102: 4.0, 105: 3.5, 108: 3.0, 111: 2.5, 114: 2.0, 117: 1.5, 120: 1.0, 123: 0.5, 126: 0}, 'Natação': {51: 10, 55: 9.5, 59: 9.0, 63: 8.5, 67: 8.0, 71: 7.5, 75: 7.0, 79: 6.5, 83: 6.0, 87: 5.5, 91: 5.0, 95: 4.5, 99: 4.0, 103: 3.5, 107: 3.0, 111: 2.5, 115: 2.0, 119: 1.5, 123: 1.0, 127: 0.5, 131: 0}},
    '34-37': {'Corrida': {1400: 10, 1300: 9.5, 1200: 9.0, 1100: 8.5, 1000: 8.0, 900: 7.5, 800: 7.0, 700: 6.5, 600: 6.0, 500: 5.5, 400: 5.0, 300: 4.5, 200: 4.0, 100: 3.5, 0: 0}, 'Flexao': {18: 10, 17: 9.5, 16: 9.0, 15: 8.5, 14: 8.0, 13: 7.5, 12: 7.0, 11: 6.5, 10: 6.0, 9: 5.5, 8: 5.0, 7: 4.5, 6: 4.0, 5: 3.5, 4: 3.0, 3: 1.5, 0: 0}, 'Abdominal': {32: 10, 31: 9.5, 30: 9.0, 29: 8.5, 28: 8.0, 27: 7.5, 26: 7.0, 25: 6.5, 24: 6.0, 23: 5.5, 22: 5.0, 21: 4.5, 20: 4.0, 19: 3.5, 18: 3.0, 17: 2.5, 16: 2.0, 15: 1.5, 0: 0}, 'Barra': {68: 10, 71: 9.5, 74: 9.0, 77: 8.5, 80: 8.0, 83: 7.5, 86: 7.0, 89: 6.5, 92: 6.0, 95: 5.5, 98: 5.0, 101: 4.5, 104: 4.0, 107: 3.5, 110: 3.0, 113: 2.5, 116: 2.0, 119: 1.5, 122: 1.0, 125: 0.5, 128: 0}, 'Natação': {53: 10, 57: 9.5, 61: 9.0, 65: 8.5, 69: 8.0, 73: 7.5, 77: 7.0, 81: 6.5, 85: 6.0, 89: 5.5, 93: 5.0, 97: 4.5, 101: 4.0, 105: 3.5, 109: 3.0, 113: 2.5, 117: 2.0, 121: 1.5, 125: 1.0, 129: 0.5, 133: 0}},
    '38-41': {'Corrida': {1300: 10, 1200: 9.5, 1100: 9.0, 1000: 8.5, 900: 8.0, 800: 7.5, 700: 7.0, 600: 6.5, 500: 6.0, 400: 5.5, 300: 5.0, 200: 4.5, 100: 4.0, 0: 0}, 'Flexao': {16: 10, 15: 9.5, 14: 9.0, 13: 8.5, 12: 8.0, 11: 7.5, 10: 7.0, 9: 6.5, 8: 6.0, 7: 5.5, 6: 5.0, 5: 4.5, 4: 4.0, 3: 3.5, 2: 1.5, 0: 0}, 'Abdominal': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5, 22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5, 14: 2.0, 13: 1.5, 0: 0}, 'Barra': {70: 10, 73: 9.5, 76: 9.0, 79: 8.5, 82: 8.0, 85: 7.5, 88: 7.0, 91: 6.5, 94: 6.0, 97: 5.5, 100: 5.0, 103: 4.5, 106: 4.0, 109: 3.5, 112: 3.0, 115: 2.5, 118: 2.0, 121: 1.5, 124: 1.0, 127: 0.5, 130: 0}, 'Natação': {55: 10, 59: 9.5, 63: 9.0, 67: 8.5, 71: 8.0, 75: 7.5, 79: 7.0, 83: 6.5, 87: 6.0, 91: 5.5, 95: 5.0, 99: 4.5, 103: 4.0, 107: 3.5, 111: 3.0, 115: 2.5, 119: 2.0, 123: 1.5, 127: 1.0, 131: 0.5, 135: 0}},
    '42-45': {'Corrida': {1200: 10, 1100: 9.5, 1000: 9.0, 900: 8.5, 800: 8.0, 700: 7.5, 600: 7.0, 500: 6.5, 400: 6.0, 300: 5.5, 200: 5.0, 100: 4.5, 0: 0}, 'Flexao': {14: 10, 13: 9.5, 12: 9.0, 11: 8.5, 10: 8.0, 9: 7.5, 8: 7.0, 7: 6.5, 6: 6.0, 5: 5.5, 4: 5.0, 3: 4.5, 2: 3.0, 1: 1.5, 0: 0}, 'Abdominal': {28: 10, 27: 9.5, 26: 9.0, 25: 8.5, 24: 8.0, 23: 7.5, 22: 7.0, 21: 6.5, 20: 6.0, 19: 5.5, 18: 5.0, 17: 4.5, 16: 4.0, 15: 3.5, 14: 3.0, 13: 2.5, 12: 2.0, 11: 1.5, 0: 0}, 'Barra': {72: 10, 75: 9.5, 78: 9.0, 81: 8.5, 84: 8.0, 87: 7.5, 90: 7.0, 93: 6.5, 96: 6.0, 99: 5.5, 102: 5.0, 105: 4.5, 108: 4.0, 111: 3.5, 114: 3.0, 117: 2.5, 120: 2.0, 123: 1.5, 126: 1.0, 129: 0.5, 132: 0}, 'Natação': {57: 10, 61: 9.5, 65: 9.0, 69: 8.5, 73: 8.0, 77: 7.5, 81: 7.0, 85: 6.5, 89: 6.0, 93: 5.5, 97: 5.0, 101: 4.5, 105: 4.0, 109: 3.5, 113: 3.0, 117: 2.5, 121: 2.0, 125: 1.5, 129: 1.0, 133: 0.5, 137: 0}},
    '46-49': {'Corrida': {1100: 10, 1000: 9.5, 900: 9.0, 800: 8.5, 700: 8.0, 600: 7.5, 500: 7.0, 400: 6.5, 300: 6.0, 200: 5.5, 100: 5.0, 0: 0}, 'Flexao': {12: 10, 11: 9.5, 10: 9.0, 9: 8.5, 8: 8.0, 7: 7.5, 6: 7.0, 5: 6.5, 4: 6.0, 3: 5.5, 2: 4.0, 1: 2.5, 0: 0}, 'Abdominal': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0}, 'Barra': {74: 10, 77: 9.5, 80: 9.0, 83: 8.5, 86: 8.0, 89: 7.5, 92: 7.0, 95: 6.5, 98: 6.0, 101: 5.5, 104: 5.0, 107: 4.5, 110: 4.0, 113: 3.5, 116: 3.0, 119: 2.5, 122: 2.0, 125: 1.5, 128: 1.0, 131: 0.5, 134: 0}, 'Natação': {59: 10, 63: 9.5, 67: 9.0, 71: 8.5, 75: 8.0, 79: 7.5, 83: 7.0, 87: 6.5, 91: 6.0, 95: 5.5, 99: 5.0, 103: 4.5, 107: 4.0, 111: 3.5, 115: 3.0, 119: 2.5, 123: 2.0, 127: 1.5, 131: 1.0, 135: 0.5, 139: 0}},
    '50-53': {'Corrida': {1000: 10, 900: 9.5, 800: 9.0, 700: 8.5, 600: 8.0, 500: 7.5, 400: 7.0, 300: 6.5, 200: 6.0, 100: 5.5, 0: 0}, 'Flexao': {10: 10, 9: 9.5, 8: 9.0, 7: 8.5, 6: 8.0, 5: 7.5, 4: 7.0, 3: 6.5, 2: 5.0, 1: 3.5, 0: 0}, 'Abdominal': {24: 10, 23: 9.5, 22: 9.0, 21: 8.5, 20: 8.0, 19: 7.5, 18: 7.0, 17: 6.5, 16: 6.0, 15: 5.5, 14: 5.0, 13: 4.5, 12: 4.0, 11: 3.5, 10: 3.0, 9: 2.5, 8: 2.0, 7: 1.5, 0: 0}, 'Barra': {76: 10, 79: 9.5, 82: 9.0, 85: 8.5, 88: 8.0, 91: 7.5, 94: 7.0, 97: 6.5, 100: 6.0, 103: 5.5, 106: 5.0, 109: 4.5, 112: 4.0, 115: 3.5, 118: 3.0, 121: 2.5, 124: 2.0, 127: 1.5, 130: 1.0, 133: 0.5, 136: 0}, 'Natação': {61: 10, 65: 9.5, 69: 9.0, 73: 8.5, 77: 8.0, 81: 7.5, 85: 7.0, 89: 6.5, 93: 6.0, 97: 5.5, 101: 5.0, 105: 4.5, 109: 4.0, 113: 3.5, 117: 3.0, 121: 2.5, 125: 2.0, 129: 1.5, 133: 1.0, 137: 0.5, 141: 0}},
    '54-57': {'Corrida': {900: 10, 800: 9.5, 700: 9.0, 600: 8.5, 500: 8.0, 400: 7.5, 300: 7.0, 200: 6.5, 100: 6.0, 0: 0}, 'Flexao': {8: 10, 7: 9.5, 6: 9.0, 5: 8.5, 4: 8.0, 3: 7.0, 2: 5.5, 1: 4.0, 0: 0}, 'Abdominal': {22: 10, 21: 9.5, 20: 9.0, 19: 8.5, 18: 8.0, 17: 7.5, 16: 7.0, 15: 6.5, 14: 6.0, 13: 5.5, 12: 5.0, 11: 4.5, 10: 4.0, 9: 3.5, 8: 3.0, 7: 2.5, 6: 2.0, 5: 1.5, 0: 0}, 'Barra': {78: 10, 81: 9.5, 84: 9.0, 87: 8.5, 90: 8.0, 93: 7.5, 96: 7.0, 99: 6.5, 102: 6.0, 105: 5.5, 108: 5.0, 111: 4.5, 114: 4.0, 117: 3.5, 120: 3.0, 123: 2.5, 126: 2.0, 129: 1.5, 132: 1.0, 135: 0.5, 138: 0}, 'Natação': {63: 10, 67: 9.5, 71: 9.0, 75: 8.5, 79: 8.0, 83: 7.5, 87: 7.0, 91: 6.5, 95: 6.0, 99: 5.5, 103: 5.0, 107: 4.5, 111: 4.0, 115: 3.5, 119: 3.0, 123: 2.5, 127: 2.0, 131: 1.5, 135: 1.0, 139: 0.5, 143: 0}},
    '58-61': {'Corrida': {800: 10, 700: 9.5, 600: 9.0, 500: 8.5, 400: 8.0, 300: 7.5, 200: 7.0, 100: 6.5, 0: 0}, 'Flexao': {6: 10, 5: 9.5, 4: 9.0, 3: 8.0, 2: 6.5, 1: 5.0, 0: 0}, 'Abdominal': {20: 10, 19: 9.5, 18: 9.0, 17: 8.5, 16: 8.0, 15: 7.5, 14: 7.0, 13: 6.5, 12: 6.0, 11: 5.5, 10: 5.0, 9: 4.5, 8: 4.0, 7: 3.5, 6: 3.0, 5: 2.5, 4: 2.0, 3: 1.5, 0: 0}, 'Barra': {80: 10, 83: 9.5, 86: 9.0, 89: 8.5, 92: 8.0, 95: 7.5, 98: 7.0, 101: 6.5, 104: 6.0, 107: 5.5, 110: 5.0, 113: 4.5, 116: 4.0, 119: 3.5, 122: 3.0, 125: 2.5, 128: 2.0, 131: 1.5, 134: 1.0, 137: 0.5, 140: 0}, 'Natação': {65: 10, 69: 9.5, 73: 9.0, 77: 8.5, 81: 8.0, 85: 7.5, 89: 7.0, 93: 6.5, 97: 6.0, 101: 5.5, 105: 5.0, 109: 4.5, 113: 4.0, 117: 3.5, 121: 3.0, 125: 2.5, 129: 2.0, 133: 1.5, 137: 1.0, 141: 0.5, 145: 0}},
    '62+': {'Corrida': {700: 10, 600: 9.5, 500: 9.0, 400: 8.5, 300: 8.0, 200: 7.5, 100: 7.0, 0: 0}, 'Flexao': {4: 10, 3: 9.0, 2: 7.5, 1: 6.0, 0: 0}, 'Abdominal': {18: 10, 17: 9.5, 16: 9.0, 15: 8.5, 14: 8.0, 13: 7.5, 12: 7.0, 11: 6.5, 10: 6.0, 9: 5.5, 8: 5.0, 7: 4.5, 6: 4.0, 5: 3.5, 4: 3.0, 3: 2.5, 2: 2.0, 1: 1.5, 0: 0}, 'Barra': {82: 10, 85: 9.5, 88: 9.0, 91: 8.5, 94: 8.0, 97: 7.5, 100: 7.0, 103: 6.5, 106: 6.0, 109: 5.5, 112: 5.0, 115: 4.5, 118: 4.0, 121: 3.5, 124: 3.0, 127: 2.5, 130: 2.0, 133: 1.5, 136: 1.0, 139: 0.5, 142: 0}, 'Natação': {67: 10, 71: 9.5, 75: 9.0, 79: 8.5, 83: 8.0, 87: 7.5, 91: 7.0, 95: 6.5, 99: 6.0, 103: 5.5, 107: 5.0, 111: 4.5, 115: 4.0, 119: 3.5, 123: 3.0, 127: 2.5, 131: 2.0, 135: 1.5, 139: 1.0, 143: 0.5, 147: 0}},
}

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE PROCESSAMENTO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

def calcular_idade(data_nascimento: datetime) -> int:
    """Calcula a idade a partir da data de nascimento."""
    today = datetime.today()
    return today.year - data_nascimento.year - ((today.month, today.day) < (data_nascimento.month, data_nascimento.day))

def get_faixa_etaria(idade: int) -> str:
    """Determina a faixa etária com base na idade."""
    if 18 <= idade <= 21: return '18-21'
    elif 22 <= idade <= 25: return '22-25'
    elif 26 <= idade <= 29: return '26-29'
    elif 30 <= idade <= 33: return '30-33'
    elif 34 <= idade <= 37: return '34-37'
    elif 38 <= idade <= 41: return '38-41'
    elif 42 <= idade <= 45: return '42-45'
    elif 46 <= idade <= 49: return '46-49'
    elif 50 <= idade <= 53: return '50-53'
    elif 54 <= idade <= 57: return '54-57'
    elif 58 <= idade <= 61: return '58-61'
    elif idade >= 62: return '62+'
    return 'Não Informado'

def parse_tempo_to_seconds(tempo_str: str) -> float:
    """Converte string de tempo (MM'SS" ou SS") para segundos."""
    if pd.isna(tempo_str) or not isinstance(tempo_str, str):
        return np.nan

    tempo_str = tempo_str.strip().replace(" ", "").replace(",", ".").upper()

    # Remove qualquer texto adicional como "P" ou "ESTÁT"
    tempo_str = re.sub(r'[A-Z]+', '', tempo_str)

    match_min_sec = re.match(r"(\d+)'(\d+)\"?", tempo_str) # MM'SS"
    match_sec = re.match(r"(\d+)\"?", tempo_str) # SS"

    if match_min_sec:
        minutes = int(match_min_sec.group(1))
        seconds = int(match_min_sec.group(2))
        return minutes * 60 + seconds
    elif match_sec:
        return int(match_sec.group(1))
    return np.nan

def parse_corrida_value(value):
    """
    Tenta interpretar o valor da corrida como distância (int) ou tempo (segundos).
    Retorna (distancia_m, tempo_seg, is_tempo_format)
    """
    if pd.isna(value) or value == "" or str(value).strip().upper() in ["NÃO COMPARECEU", "NÃO", "NC"]:
        return np.nan, np.nan, False

    s_value = str(value).strip().replace(",", ".")

    # Tentar como tempo (MM'SS" ou SS")
    tempo_seg = parse_tempo_to_seconds(s_value)
    if not pd.isna(tempo_seg):
        return np.nan, tempo_seg, True # É um tempo

    # Tentar como distância (número)
    try:
        distancia = float(s_value)
        return distancia, np.nan, False # É uma distância
    except ValueError:
        pass # Não é um número simples

    return np.nan, np.nan, False # Não conseguiu interpretar

def parse_barra_value(value, sexo):
    """
    Tenta interpretar o valor da barra como repetições (int) ou tempo (segundos).
    Retorna (repeticoes, tempo_seg, is_tempo_format)
    """
    if pd.isna(value) or value == "" or str(value).strip().upper() in ["NÃO COMPARECEU", "NÃO", "NC"]:
        return np.nan, np.nan, False

    s_value = str(value).strip().replace(",", ".")

    # Tentar como tempo (MM'SS" ou SS")
    tempo_seg = parse_tempo_to_seconds(s_value)
    if not pd.isna(tempo_seg):
        return np.nan, tempo_seg, True # É um tempo

    # Tentar como repetições (número)
    try:
        repeticoes = float(s_value)
        return repeticoes, np.nan, False # É uma repetição
    except ValueError:
        pass # Não é um número simples

    return np.nan, np.nan, False # Não conseguiu interpretar

def calcular_pontuacao(valor, exercicio, faixa_etaria, sexo):
    """Calcula a pontuação para um dado exercício, faixa etária e sexo."""
    regras = REGRAS_MASCULINO if sexo == 'Masculino' else REGRAS_FEMININO

    if faixa_etaria not in regras or exercicio not in regras[faixa_etaria]:
        return np.nan # Regra não encontrada

    regras_exercicio = regras[faixa_etaria][exercicio]

    # Para corrida (distância) e exercícios de repetição (abdominal, flexão, barra masculina)
    # a pontuação é maior para valores maiores.
    # Para natação e barra feminina (tempo), a pontuação é maior para valores menores (tempos mais rápidos).

    if exercicio == 'Natação' or (exercicio == 'Barra' and sexo == 'Feminino'):
        # Para tempo, queremos o menor valor que ainda dá a pontuação
        # As chaves das regras são os limites MÁXIMOS para aquela pontuação
        pontuacao = 0
        for limite, score in sorted(regras_exercicio.items(), key=lambda item: item[0], reverse=False):
            if valor <= limite:
                pontuacao = score
                break
        return pontuacao
    else: # Corrida (distância), Abdominal, Flexão, Barra (masculina - repetições)
        # Para distância/repetições, queremos o maior valor que ainda dá a pontuação
        # As chaves das regras são os limites MÍNIMOS para aquela pontuação
        pontuacao = 0
        for limite, score in sorted(regras_exercicio.items(), key=lambda item: item[0], reverse=True):
            if valor >= limite:
                pontuacao = score
                break
        return pontuacao

    return np.nan # Caso não encontre pontuação (deve ser coberto pelos loops)


def classificar_desempenho(media_final):
    """Classifica o desempenho geral com base na média final."""
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

@st.cache_data
def load_data():
    """Carrega e pré-processa os dados do TAF."""
    df = pd.read_csv("master_taf_consolidado.csv")

    # 1. Padronizar nomes de colunas
    df.columns = [col.strip().replace(" ", "").replace("/", "").upper() for col in df.columns]

    # Renomear colunas específicas para o padrão esperado
    df = df.rename(columns={
        "NOME": "NOME", # Já está NOME
        "DATANASCIMENTO": "DATA_NASCIMENTO",
        "POSTO": "POSTO_GRAD", # Renomear para POSTO_GRAD
        "RACA/COR": "RACA_COR",
    })

    # 2. Limpeza e conversão de tipos
    df["NOME"] = df["NOME"].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df["SEXO"] = df["SEXO"].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df["POSTO_GRAD"] = df["POSTO_GRAD"].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df["QUADRO"] = df["QUADRO"].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # Converter DataNascimento para datetime e calcular idade
    df["DATA_NASCIMENTO"] = pd.to_datetime(df["DATA_NASCIMENTO"], format="%d/%m/%Y", errors="coerce")
    df["IDADE"] = df["DATA_NASCIMENTO"].apply(lambda x: calcular_idade(x) if pd.notna(x) else np.nan)
    df["FAIXA_ETARIA"] = df["IDADE"].apply(lambda x: get_faixa_etaria(int(x)) if pd.notna(x) else "Não Informado")

    # 3. Processar colunas de exercícios
    # Manter as colunas originais para o TAF Adaptado
    df["Corrida_Original"] = df["CORRIDA"]
    df["Abdominal_Original"] = df["ABDOMINAL"]
    df["Flexao_Original"] = df["FLEXAO"]
    df["Natacao_Original"] = df["NATACAO"]
    df["Barra_Original"] = df["BARRA"]

    # Inicializar colunas processadas
    df["CORRIDA_DISTANCIA_M"] = np.nan
    df["CORRIDA_TEMPO_SEG"] = np.nan
    df["BARRA_REPETICOES"] = np.nan
    df["BARRA_TEMPO_SEG"] = np.nan

    # Aplicar parsing para Corrida
    for idx, row in df.iterrows():
        dist, tempo, is_tempo = parse_corrida_value(row["CORRIDA_Original"])
        df.loc[idx, "CORRIDA_DISTANCIA_M"] = dist
        df.loc[idx, "CORRIDA_TEMPO_SEG"] = tempo
        # Marcar se o valor original da corrida era um tempo
        df.loc[idx, "CORRIDA_IS_TEMPO"] = is_tempo

    # Aplicar parsing para Barra
    for idx, row in df.iterrows():
        reps, tempo, is_tempo = parse_barra_value(row["BARRA_Original"], row["SEXO"])
        df.loc[idx, "BARRA_REPETICOES"] = reps
        df.loc[idx, "BARRA_TEMPO_SEG"] = tempo
        # Marcar se o valor original da barra era um tempo
        df.loc[idx, "BARRA_IS_TEMPO"] = is_tempo

    # Limpar e converter Abdominal e Flexao
    for col in ["ABDOMINAL", "FLEXAO"]:
        df[col] = df[col].astype(str).str.replace(" rep", "", regex=False).str.strip()
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Limpar e converter Natacao
    df["NATACAO"] = df["NATACAO"].astype(str).str.strip().replace({"NÃO": np.nan, "": np.nan})
    df["NATACAO_SEG"] = pd.to_numeric(df["NATACAO"], errors="coerce") # Coluna para pontuação

    # 4. Determinar TAF Adaptado
    # Um militar é TAF Adaptado se:
    # - Não compareceu a NENHUM exercício regular (Corrida, Abdominal, Flexao, Natacao, Barra)
    # - OU, se o valor da Corrida foi interpretado como tempo (e não distância)
    # - OU, se o valor da Barra foi interpretado como tempo para Masculino (ou repetições para Feminino)
    #   (Ou seja, fez a prova de barra de forma "invertida" ou adaptada)

    # Inicializa a coluna 'TAF_ADAPTADO' como False
    df['TAF_ADAPTADO'] = False

    # Condição 1: Não compareceu a nenhum exercício regular
    # Consideramos "não compareceu" se todas as colunas de exercício (processadas) são NaN
    exercicios_regulares_cols = ["CORRIDA_DISTANCIA_M", "ABDOMINAL", "FLEXAO", "NATACAO_SEG", "BARRA_REPETICOES", "BARRA_TEMPO_SEG"]
    df['TODOS_AUSENTES'] = df[exercicios_regulares_cols].isna().all(axis=1)
    df.loc[df['TODOS_AUSENTES'], 'TAF_ADAPTADO'] = True

    # Condição 2: Corrida foi tempo (e não distância)
    df.loc[df["CORRIDA_IS_TEMPO"] == True, 'TAF_ADAPTADO'] = True

    # Condição 3: Barra foi tempo para Masculino ou repetições para Feminino
    df.loc[(df["SEXO"] == "Masculino") & (df["BARRA_IS_TEMPO"] == True), 'TAF_ADAPTADO'] = True
    df.loc[(df["SEXO"] == "Feminino") & (df["BARRA_IS_TEMPO"] == False) & (df["BARRA_REPETICOES"].notna()), 'TAF_ADAPTADO'] = True

    # 5. Criar colunas de exercícios para pontuação (CORRIDA e BARRA)
    # CORRIDA: Para pontuação, usamos a distância em metros. Se for tempo, será NaN aqui.
    df["CORRIDA"] = df["CORRIDA_DISTANCIA_M"]

    # BARRA: Para pontuação, usamos repetições para Masculino e tempo em segundos para Feminino.
    df["BARRA"] = np.nan
    df.loc[df["SEXO"] == "Masculino", "BARRA"] = df["BARRA_REPETICOES"]
    df.loc[df["SEXO"] == "Feminino", "BARRA"] = df["BARRA_TEMPO_SEG"]

    # 6. Calcular pontuações
    exercicios = ["Corrida", "Abdominal", "Flexao", "Barra", "Natação"] # Natação usa NATACAO_SEG
    for ex in exercicios:
        col_valor = "NATACAO_SEG" if ex == "Natação" else ex
        df[f"PONTUACAO_{ex.upper()}"] = df.apply(
            lambda row: calcular_pontuacao(
                row[col_valor], ex, row["FAIXA_ETARIA"], row["SEXO"]
            ) if pd.notna(row[col_valor]) and row["FAIXA_ETARIA"] != "Não Informado" else np.nan,
            axis=1
        )

    # 7. Calcular Média Final e Classificação
    pontuacoes_cols = [f"PONTUACAO_{ex.upper()}" for ex in exercicios]

    # A média final só é calculada para quem não é TAF Adaptado e tem pelo menos uma pontuação válida
    df["MEDIA_FINAL"] = np.nan
    df["CLASSIFICACAO"] = "Ausente"

    df_nao_adaptado = df[~df['TAF_ADAPTADO']].copy()

    # Calcula a média apenas para as pontuações válidas (não NaN)
    df_nao_adaptado["MEDIA_FINAL"] = df_nao_adaptado[pontuacoes_cols].mean(axis=1, skipna=True)

    # Se a média for NaN (todos os exercícios foram NaN), então a classificação é "Ausente"
    df_nao_adaptado.loc[df_nao_adaptado["MEDIA_FINAL"].isna(), "CLASSIFICACAO"] = "Ausente"
    # Caso contrário, classifica com base na média
    df_nao_adaptado.loc[df_nao_adaptado["MEDIA_FINAL"].notna(), "CLASSIFICACAO"] = df_nao_adaptado["MEDIA_FINAL"].apply(classificar_desempenho)

    # Atualiza o DataFrame original com os resultados
    df.update(df_nao_adaptado[["MEDIA_FINAL", "CLASSIFICACAO"]])

    # Separar TAF Adaptado
    df_adaptado = df[df["TAF_ADAPTADO"]].copy()
    df_regular = df[~df["TAF_ADAPTADO"]].copy()

    return df_regular, df_adaptado

# ══════════════════════════════════════════════════════════════════════════════
# GERAÇÃO DE PDF
# ══════════════════════════════════════════════════════════════════════════════

def create_pdf_report(df_militar, theme):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Cores para o PDF (simplificadas)
    text_color = "black" if theme['tema'] == "claro" else "white"
    bg_color = "white" if theme['tema'] == "claro" else "#1a1a1a"
    accent_color = theme['accent']

    # Definir fundo
    c.setFillColor(bg_color)
    c.rect(0, 0, width, height, fill=1)

    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "Ficha Individual de Desempenho TAF")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Nome: {df_militar['NOME'].iloc[0]}")
    c.drawString(50, height - 95, f"Posto/Grad: {df_militar['POSTO_GRAD'].iloc[0]}")
    c.drawString(50, height - 110, f"Quadro: {df_militar['QUADRO'].iloc[0]}")
    c.drawString(50, height - 125, f"Sexo: {df_militar['SEXO'].iloc[0]}")
    c.drawString(50, height - 140, f"Idade: {int(df_militar['IDADE'].iloc[0])} ({df_militar['FAIXA_ETARIA'].iloc[0]})")
    c.drawString(50, height - 155, f"Data de Nascimento: {df_militar['DATA_NASCIMENTO'].iloc[0].strftime('%d/%m/%Y')}")

    # Resumo do Desempenho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 190, "Resumo do Desempenho")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 210, f"Média Final: {df_militar['MEDIA_FINAL'].iloc[0]:.2f}")
    c.drawString(50, height - 225, f"Classificação: {df_militar['CLASSIFICACAO'].iloc[0]}")

    # Detalhes dos Exercícios
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 260, "Detalhes dos Exercícios")
    c.setFont("Helvetica", 12)

    y_pos = height - 280
    exercicios_display = {
        "Corrida": "Corrida (m)",
        "Abdominal": "Abdominal (reps)",
        "Flexao": "Flexão (reps)",
        "Natação": "Natação (seg)",
        "Barra": "Barra (reps/seg)",
    }

    for ex_key, ex_label in exercicios_display.items():
        valor_col = ex_key
        if ex_key == "Natação":
            valor_col = "NATACAO_SEG"
        elif ex_key == "Barra":
            if df_militar['SEXO'].iloc[0] == 'Masculino':
                valor_col = "BARRA_REPETICOES"
            else:
                valor_col = "BARRA_TEMPO_SEG"

        valor = df_militar[valor_col].iloc[0]
        pontuacao = df_militar[f"PONTUACAO_{ex_key.upper()}"].iloc[0]

        valor_str = f"{valor:.1f}" if pd.notna(valor) else "N/A"
        pontuacao_str = f"{pontuacao:.1f}" if pd.notna(pontuacao) else "N/A"

        c.drawString(50, y_pos, f"{ex_label}: {valor_str} - Pontuação: {pontuacao_str}")
        y_pos -= 15

    # Adicionar gráficos
    y_chart_start = y_pos - 30 # Espaço antes dos gráficos

    # Gráfico de Radar
    fig_radar = create_radar_chart(df_militar, theme)
    img_radar = io.BytesIO()
    fig_radar.write_image(img_radar, format="png", width=500, height=300, scale=2)
    img_radar.seek(0)
    c.drawImage(ImageReader(img_radar), 50, y_chart_start - 300, width=250, height=150) # Ajustar tamanho e posição

    # Gráfico de Barras de Pontuação
    fig_bar = create_bar_chart_pontuacoes(df_militar, theme)
    img_bar = io.BytesIO()
    fig_bar.write_image(img_bar, format="png", width=500, height=300, scale=2)
    img_bar.seek(0)
    c.drawImage(ImageReader(img_bar), width / 2 + 20, y_chart_start - 300, width=250, height=150) # Ajustar tamanho e posição

    c.save()
    buffer.seek(0)
    return buffer

def create_radar_chart(df_militar, theme):
    exercicios = ["Corrida", "Abdominal", "Flexao", "Barra", "Natação"]
    pontuacoes = [df_militar[f"PONTUACAO_{ex.upper()}"].iloc[0] for ex in exercicios]

    # Substituir NaN por 0 para o gráfico de radar
    pontuacoes = [p if pd.notna(p) else 0 for p in pontuacoes]

    fig = go.Figure(data=go.Scatterpolar(
        r=pontuacoes,
        theta=exercicios,
        fill='toself',
        name=df_militar['NOME'].iloc[0],
        marker_color=theme['accent']
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                gridcolor=theme['border_color'],
                linecolor=theme['border_color'],
                tickfont_color=theme['text_secondary']
            ),
            angularaxis=dict(
                linecolor=theme['border_color'],
                tickfont_color=theme['text_secondary']
            )
        ),
        showlegend=False,
        title=f"Pontuação por Exercício - {df_militar['NOME'].iloc[0]}",
        title_font_color=theme['text_primary'],
        ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME)
    )
    return fig

def create_bar_chart_pontuacoes(df_militar, theme):
    exercicios = ["Corrida", "Abdominal", "Flexao", "Barra", "Natação"]
    pontuacoes = [df_militar[f"PONTUACAO_{ex.upper()}"].iloc[0] for ex in exercicios]

    # Substituir NaN por 0 para o gráfico de barras
    pontuacoes = [p if pd.notna(p) else 0 for p in pontuacoes]

    df_plot = pd.DataFrame({"Exercício": exercicios, "Pontuação": pontuacoes})

    fig = px.bar(
        df_plot,
        x="Exercício",
        y="Pontuação",
        title=f"Pontuações Detalhadas - {df_militar['NOME'].iloc[0]}",
        color="Pontuação",
        color_continuous_scale=px.colors.sequential.Viridis,
        range_y=[0, 10]
    )
    fig.update_layout(
        ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
        title_font_color=theme['text_primary'],
        xaxis_title_font_color=theme['text_secondary'],
        yaxis_title_font_color=theme['text_secondary'],
        coloraxis_colorbar_tickfont_color=theme['text_secondary']
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# CARREGAR DADOS
# ══════════════════════════════════════════════════════════════════════════════

df_regular, df_adaptado = load_data()

# ══════════════════════════════════════════════════════════════════════════════
# APLICAR CSS
# ══════════════════════════════════════════════════════════════════════════════

theme = get_theme_config()
apply_dynamic_css(theme)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    if _LOCAL_LOGO_PATH:
        st.image(str(_LOCAL_LOGO_PATH), use_column_width="always")
    else:
        st.image(_get_cbmam_image_url(), use_column_width="always")

    st.markdown(f"<h2 style='color:{theme['text_primary']};'>Navegação</h2>", unsafe_allow_html=True)
    pagina = st.radio(
        "Selecione a página:",
        ["📊 Dashboard Geral", "👤 Ficha Individual", "♿ TAF Adaptado"],
        key="main_nav",
        format_func=lambda x: x.split(" ")[1] if " " in x else x # Remove o ícone para o radio button
    )

    st.markdown(f"<h2 style='color:{theme['text_primary']};'>Configurações</h2>", unsafe_allow_html=True)
    if st.button(f"Mudar para Tema {'Claro' if st.session_state.tema == 'escuro' else 'Escuro'}"):
        st.session_state.tema = "claro" if st.session_state.tema == "escuro" else "escuro"
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: DASHBOARD GERAL
# ══════════════════════════════════════════════════════════════════════════════

if pagina == "📊 Dashboard Geral":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">📊 Dashboard Geral</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Visão geral do desempenho dos militares no TAF.
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    # Filtros
    st.markdown(f"<p class='section-title'>Filtros</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        postos_selecionados = st.multiselect(
            "Posto/Graduação",
            options=df_regular["POSTO_GRAD"].unique(),
            default=df_regular["POSTO_GRAD"].unique(),
            key="filtro_posto"
        )
    with col2:
        quadros_selecionados = st.multiselect(
            "Quadro",
            options=df_regular["QUADRO"].unique(),
            default=df_regular["QUADRO"].unique(),
            key="filtro_quadro"
        )
    with col3:
        sexos_selecionados = st.multiselect(
            "Sexo",
            options=df_regular["SEXO"].unique(),
            default=df_regular["SEXO"].unique(),
            key="filtro_sexo"
        )

    df_filtrado = df_regular[
        df_regular["POSTO_GRAD"].isin(postos_selecionados) &
        df_regular["QUADRO"].isin(quadros_selecionados) &
        df_regular["SEXO"].isin(sexos_selecionados)
    ]

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        # KPIs
        st.markdown(f"<p class='section-title'>Indicadores Chave</p>", unsafe_allow_html=True)
        total_militares = len(df_filtrado)
        total_presentes = df_filtrado["CLASSIFICACAO"].apply(lambda x: x != "Ausente").sum()
        total_ausentes = total_militares - total_presentes
        media_geral = df_filtrado["MEDIA_FINAL"].mean()

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric("👥 Total Militares", total_militares)
        with kpi2:
            st.metric("✅ Presentes", total_presentes)
        with kpi3:
            st.metric("❌ Ausentes", total_ausentes)
        with kpi4:
            st.metric("⭐ Média Geral", f"{media_geral:.2f}")

        st.divider()

        # Distribuição por Classificação
        st.markdown(f"<p class='section-title'>Distribuição por Classificação</p>", unsafe_allow_html=True)
        classificacao_counts = df_filtrado["CLASSIFICACAO"].value_counts().reset_index()
        classificacao_counts.columns = ["Classificação", "Quantidade"]

        # Ordenar as classificações
        ordem_classificacao = ["Excelente", "Bom", "Regular", "Insuficiente", "Ausente"]
        classificacao_counts["Classificação"] = pd.Categorical(
            classificacao_counts["Classificação"], categories=ordem_classificacao, ordered=True
        )
        classificacao_counts = classificacao_counts.sort_values("Classificação")

        fig_classificacao = px.bar(
            classificacao_counts,
            x="Classificação",
            y="Quantidade",
            color="Classificação",
            color_discrete_map=COR_MAP,
            text="Quantidade",
            title="Distribuição de Militares por Classificação",
        )
        fig_classificacao.update_traces(textposition="outside")
        fig_classificacao.update_layout(
            ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
            height=400,
            xaxis=dict(title="Classificação", **(DARK_PLOTLY_THEME['xaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['xaxis'])),
            yaxis=dict(title="Número de Militares", **(DARK_PLOTLY_THEME['yaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['yaxis'])),
            legend=dict(font_color=theme['text_primary'])
        )
        st.plotly_chart(fig_classificacao, use_container_width=True)

        st.divider()

        # Média de Pontuação por Exercício e Sexo
        st.markdown(f"<p class='section-title'>Média de Pontuação por Exercício e Sexo</p>", unsafe_allow_html=True)
        exercicios_pontuacao = ["PONTUACAO_CORRIDA", "PONTUACAO_ABDOMINAL", "PONTUACAO_FLEXAO", "PONTUACAO_NATACAO", "PONTUACAO_BARRA"]
        df_medias = df_filtrado.groupby("SEXO")[exercicios_pontuacao].mean().reset_index()
        df_medias = df_medias.melt(id_vars="SEXO", var_name="Exercício", value_name="Média de Pontuação")
        df_medias["Exercício"] = df_medias["Exercício"].str.replace("PONTUACAO_", "").str.replace("_", " ").str.title()

        fig_medias_exercicio = px.bar(
            df_medias,
            x="Exercício",
            y="Média de Pontuação",
            color="SEXO",
            barmode="group",
            title="Média de Pontuação por Exercício e Sexo",
            range_y=[0, 10]
        )
        fig_medias_exercicio.update_layout(
            ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
            height=450,
            xaxis=dict(title="Exercício", **(DARK_PLOTLY_THEME['xaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['xaxis'])),
            yaxis=dict(title="Média de Pontuação", **(DARK_PLOTLY_THEME['yaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['yaxis'])),
            legend=dict(font_color=theme['text_primary'])
        )
        st.plotly_chart(fig_medias_exercicio, use_container_width=True)

        st.divider()

        # Média de Pontuação por Faixa Etária e Sexo
        st.markdown(f"<p class='section-title'>Média de Pontuação por Faixa Etária e Sexo</p>", unsafe_allow_html=True)
        df_medias_idade_sexo = df_filtrado.groupby(["FAIXA_ETARIA", "SEXO"])["MEDIA_FINAL"].mean().reset_index()

        # Ordenar faixas etárias
        ordem_faixa_etaria = ['18-21', '22-25', '26-29', '30-33', '34-37', '38-41', '42-45', '46-49', '50-53', '54-57', '58-61', '62+', 'Não Informado']
        df_medias_idade_sexo["FAIXA_ETARIA"] = pd.Categorical(
            df_medias_idade_sexo["FAIXA_ETARIA"], categories=ordem_faixa_etaria, ordered=True
        )
        df_medias_idade_sexo = df_medias_idade_sexo.sort_values("FAIXA_ETARIA")

        fig_media_idade_sexo = px.line(
            df_medias_idade_sexo,
            x="FAIXA_ETARIA",
            y="MEDIA_FINAL",
            color="SEXO",
            markers=True,
            title="Média de Pontuação Final por Faixa Etária e Sexo",
            range_y=[0, 10]
        )
        fig_media_idade_sexo.update_layout(
            ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
            height=450,
            xaxis=dict(title="Faixa Etária", **(DARK_PLOTLY_THEME['xaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['xaxis'])),
            yaxis=dict(title="Média Final", **(DARK_PLOTLY_THEME['yaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['yaxis'])),
            legend=dict(font_color=theme['text_primary'])
        )
        st.plotly_chart(fig_media_idade_sexo, use_container_width=True)

        st.divider()

        # Distribuição de Pontuações por Exercício
        st.markdown(f"<p class='section-title'>Distribuição de Pontuações por Exercício</p>", unsafe_allow_html=True)
        exercicio_selecionado = st.selectbox(
            "Selecione o Exercício para Análise",
            options=["Corrida", "Abdominal", "Flexao", "Natação", "Barra"],
            key="exercicio_stats"
        )
        coluna_pontuacao = f"PONTUACAO_{exercicio_selecionado.upper()}"

        if coluna_pontuacao in df_filtrado.columns:
            fig_dist_exercicio = px.histogram(
                df_filtrado.dropna(subset=[coluna_pontuacao]), # Remover NaNs para o histograma
                x=coluna_pontuacao,
                color="SEXO",
                barmode="overlay",
                nbins=20,
                labels={coluna_pontuacao: f"Pontuação {exercicio_selecionado}", "count": "Número de Militares"},
                title=f"Distribuição de Pontuações para {exercicio_selecionado}"
            )
            fig_dist_exercicio.update_layout(
                ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
                height=450,
                xaxis=dict(title=f"Pontuação {exercicio_selecionado}", **(DARK_PLOTLY_THEME['xaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['xaxis'])),
                yaxis=dict(title="Número de Militares", **(DARK_PLOTLY_THEME['yaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['yaxis'])),
                legend=dict(font_color=theme['text_primary'])
            )
            st.plotly_chart(fig_dist_exercicio, use_container_width=True)
        else:
            st.warning(f"Coluna de pontuação '{coluna_pontuacao}' não encontrada ou sem dados.")

        st.divider()

        # Tabela de percentis
        st.markdown(f"<p class='section-title'>📊 Tabela de Percentis</p>", unsafe_allow_html=True)

        notas_map = {
            "Corrida": "PONTUACAO_CORRIDA",
            "Abdominal": "PONTUACAO_ABDOMINAL",
            "Flexão": "PONTUACAO_FLEXAO",
            "Natação": "PONTUACAO_NATACAO",
            "Barra": "PONTUACAO_BARRA",
        }

        percentis = [10, 25, 50, 75, 90]
        perc_data = {"Percentil": [f"P{p}" for p in percentis]}
        for label, col in notas_map.items():
            vals = df_filtrado[col].dropna()
            perc_data[label] = [round(np.percentile(vals, p), 2) if len(vals) > 0 else 0
                                for p in percentis]

        # Adicionar Média Final aos percentis
        media_final_vals = df_filtrado["MEDIA_FINAL"].dropna()
        perc_data["Média Final"] = [
            round(np.percentile(media_final_vals, p), 2) if len(media_final_vals) > 0 else 0
            for p in percentis
        ]
        st.dataframe(pd.DataFrame(perc_data), hide_index=True)

        # Estatísticas descritivas
        st.markdown(f"<p class='section-title'>📋 Estatísticas Descritivas</p>", unsafe_allow_html=True)

        desc_cols = list(notas_map.values()) + ["MEDIA_FINAL"]
        desc_labels = list(notas_map.keys()) + ["Média Final"]
        desc = df_filtrado[desc_cols].describe().T
        desc.index = desc_labels
        desc = desc[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
        desc.columns = ["N", "Média", "Desvio", "Mín", "P25", "Mediana", "P75", "Máx"]
        desc = desc.round(2)
        st.dataframe(desc)

        st.divider()

        # Top 10 e Bottom 10
        st.markdown(f"<p class='section-title'>🏆 Top 10 e Bottom 10</p>", unsafe_allow_html=True)

        col_t, col_bt = st.columns(2)
        with col_t:
            st.markdown("**🥇 Top 10 — Maiores Médias**")
            top10 = df_filtrado.nlargest(10, "MEDIA_FINAL")[
                ["NOME", "POSTO_GRAD", "QUADRO", "MEDIA_FINAL", "CLASSIFICACAO"]
            ].reset_index(drop=True)
            top10.index += 1
            st.dataframe(top10)

        with col_bt:
            st.markdown("**⚠️ Bottom 10 — Menores Médias**")
            # Filtrar militares que realmente compareceram (não "Ausente") para o bottom 10
            bot10_compareceu = df_filtrado[df_filtrado["CLASSIFICACAO"] != "Ausente"].nsmallest(10, "MEDIA_FINAL")[
                ["NOME", "POSTO_GRAD", "QUADRO", "MEDIA_FINAL", "CLASSIFICACAO"]
            ].reset_index(drop=True)
            bot10_compareceu.index += 1
            st.dataframe(bot10_compareceu)

        st.divider()

        # Valores brutos — desempenho real
        st.markdown(f"<p class='section-title'>🔢 Desempenho Bruto (Valores Reais)</p>", unsafe_allow_html=True)

        raw_stats = pd.DataFrame({
            "Exercício": ["Corrida (m)", "Abdominal (reps)", "Flexão (reps)",
                        "Natação (seg)", "Barra (reps/seg)"],
            "Média": [
                df_filtrado["CORRIDA_DISTANCIA_M"].mean(),
                df_filtrado["ABDOMINAL"].mean(),
                df_filtrado["FLEXAO"].mean(),
                df_filtrado["NATACAO_SEG"].mean(),
                df_filtrado["BARRA"].mean(), # Usa a coluna BARRA que já está padronizada
            ],
            "Mediana": [
                df_filtrado["CORRIDA_DISTANCIA_M"].median(),
                df_filtrado["ABDOMINAL"].median(),
                df_filtrado["FLEXAO"].median(),
                df_filtrado["NATACAO_SEG"].median(),
                df_filtrado["BARRA"].median(),
            ],
            "Mínimo": [
                df_filtrado["CORRIDA_DISTANCIA_M"].min(),
                df_filtrado["ABDOMINAL"].min(),
                df_filtrado["FLEXAO"].min(),
                df_filtrado["NATACAO_SEG"].min(),
                df_filtrado["BARRA"].min(),
            ],
            "Máximo": [
                df_filtrado["CORRIDA_DISTANCIA_M"].max(),
                df_filtrado["ABDOMINAL"].max(),
                df_filtrado["FLEXAO"].max(),
                df_filtrado["NATACAO_SEG"].max(),
                df_filtrado["BARRA"].max(),
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
    Perfil detalhado de desempenho de um militar específico.
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    # Combinar df_regular e df_adaptado para a seleção
    df_todos_militares = pd.concat([df_regular, df_adaptado]).sort_values("NOME").reset_index(drop=True)

    nomes_militares = df_todos_militares["NOME"].unique()
    militar_selecionado = st.selectbox(
        "Selecione o Militar",
        options=nomes_militares,
        key="militar_ficha_individual"
    )

    if militar_selecionado:
        df_militar = df_todos_militares[df_todos_militares["NOME"] == militar_selecionado].iloc[0]

        st.markdown(f"<p class='section-title'>Dados Pessoais</p>", unsafe_allow_html=True)
        col_dp1, col_dp2, col_dp3 = st.columns(3)
        with col_dp1:
            st.markdown(f"**Nome:** {df_militar['NOME']}")
            st.markdown(f"**Posto/Grad:** {df_militar['POSTO_GRAD']}")
            st.markdown(f"**Quadro:** {df_militar['QUADRO']}")
        with col_dp2:
            st.markdown(f"**Sexo:** {df_militar['SEXO']}")
            st.markdown(f"**Idade:** {int(df_militar['IDADE'])} anos")
            st.markdown(f"**Faixa Etária:** {df_militar['FAIXA_ETARIA']}")
        with col_dp3:
            st.markdown(f"**Data Nasc.:** {df_militar['DATA_NASCIMENTO'].strftime('%d/%m/%Y')}")
            st.markdown(f"**CPF:** {df_militar['CPF']}")
            st.markdown(f"**Raça/Cor:** {df_militar['RACA_COR']}")

        st.divider()

        if df_militar['TAF_ADAPTADO']:
            st.warning(f"Este militar ({militar_selecionado}) foi classificado para TAF Adaptado. Os resultados abaixo refletem os dados brutos, e a pontuação/classificação regular pode não ser aplicável.")
            st.markdown(f"<p class='section-title'>Resultados (TAF Adaptado)</p>", unsafe_allow_html=True)

            col_adapt1, col_adapt2 = st.columns(2)
            with col_adapt1:
                st.markdown(f"**Corrida:** {df_militar['Corrida_Original'] if pd.notna(df_militar['Corrida_Original']) else 'N/A'}")
                st.markdown(f"**Abdominal:** {df_militar['Abdominal_Original'] if pd.notna(df_militar['Abdominal_Original']) else 'N/A'}")
                st.markdown(f"**Flexão:** {df_militar['Flexao_Original'] if pd.notna(df_militar['Flexao_Original']) else 'N/A'}")
            with col_adapt2:
                st.markdown(f"**Natação:** {df_militar['Natacao_Original'] if pd.notna(df_militar['Natacao_Original']) else 'N/A'}")
                st.markdown(f"**Barra:** {df_militar['Barra_Original'] if pd.notna(df_militar['Barra_Original']) else 'N/A'}")

            st.info("Para militares em TAF Adaptado, a avaliação é individualizada e não segue as tabelas de pontuação padrão.")

        else:
            st.markdown(f"<p class='section-title'>Resultados TAF</p>", unsafe_allow_html=True)
            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.markdown(f"**Média Final:** {df_militar['MEDIA_FINAL']:.2f}")
            with col_res2:
                classificacao_badge = f"<span class='badge badge-{df_militar['CLASSIFICACAO'].lower().replace(' ', '-')}'>{df_militar['CLASSIFICACAO']}</span>"
                st.markdown(f"**Classificação:** {classificacao_badge}", unsafe_allow_html=True)
            with col_res3:
                st.markdown(f"**Situação:** {'Apto' if df_militar['MEDIA_FINAL'] >= 5.0 else 'Inapto'}")

            st.divider()

            st.markdown(f"<p class='section-title'>Pontuações por Exercício</p>", unsafe_allow_html=True)
            col_ex1, col_ex2, col_ex3 = st.columns(3)
            exercicios_display = {
                "Corrida": "Corrida (m)",
                "Abdominal": "Abdominal (reps)",
                "Flexao": "Flexão (reps)",
                "Natação": "Natação (seg)",
                "Barra": "Barra (reps/seg)",
            }

            # Para exibir os valores brutos corretos
            valor_corrida_display = f"{df_militar['CORRIDA_DISTANCIA_M']:.0f} m" if pd.notna(df_militar['CORRIDA_DISTANCIA_M']) else "N/A"
            valor_natacao_display = f"{df_militar['NATACAO_SEG']:.1f} seg" if pd.notna(df_militar['NATACAO_SEG']) else "N/A"

            valor_barra_display = "N/A"
            if df_militar['SEXO'] == 'Masculino' and pd.notna(df_militar['BARRA_REPETICOES']):
                valor_barra_display = f"{df_militar['BARRA_REPETICOES']:.0f} reps"
            elif df_militar['SEXO'] == 'Feminino' and pd.notna(df_militar['BARRA_TEMPO_SEG']):
                valor_barra_display = f"{df_militar['BARRA_TEMPO_SEG']:.1f} seg"

            with col_ex1:
                st.markdown(f"**Corrida:** {valor_corrida_display} (Pontuação: {df_militar['PONTUACAO_CORRIDA']:.1f} pts)")
                st.markdown(f"**Abdominal:** {df_militar['ABDOMINAL']:.0f} reps (Pontuação: {df_militar['PONTUACAO_ABDOMINAL']:.1f} pts)")
            with col_ex2:
                st.markdown(f"**Flexão:** {df_militar['FLEXAO']:.0f} reps (Pontuação: {df_militar['PONTUACAO_FLEXAO']:.1f} pts)")
                st.markdown(f"**Natação:** {valor_natacao_display} (Pontuação: {df_militar['PONTUACAO_NATACAO']:.1f} pts)")
            with col_ex3:
                st.markdown(f"**Barra:** {valor_barra_display} (Pontuação: {df_militar['PONTUACAO_BARRA']:.1f} pts)")

            st.divider()

            # Gráficos
            st.markdown(f"<p class='section-title'>Visualização de Desempenho</p>", unsafe_allow_html=True)
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_radar = create_radar_chart(pd.DataFrame([df_militar]), theme)
                st.plotly_chart(fig_radar, use_container_width=True)
            with col_g2:
                fig_bar = create_bar_chart_pontuacoes(pd.DataFrame([df_militar]), theme)
                st.plotly_chart(fig_bar, use_container_width=True)

            st.divider()

            # Botão para gerar PDF
            if st.button("Gerar PDF da Ficha Individual"):
                with st.spinner("Gerando PDF..."):
                    pdf_buffer = create_pdf_report(pd.DataFrame([df_militar]), theme)
                    st.download_button(
                        label="Download PDF",
                        data=pdf_buffer,
                        file_name=f"ficha_individual_{militar_selecionado.replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("PDF gerado com sucesso!")

    else:
        st.info("Selecione um militar para visualizar sua ficha individual.")

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

        # Um militar está "presente" no TAF Adaptado se tiver algum valor não-NaN e não "NÃO COMPARECEU"
        # em qualquer uma das colunas originais de exercício.
        exercicios_originais_cols_check = ["Corrida_Original", "Abdominal_Original", "Flexao_Original", "Natacao_Original", "Barra_Original"]

        df_adaptado_presente_check = df_adaptado[exercicios_originais_cols_check].apply(
            lambda row: any(pd.notna(val) and str(val).strip().upper() not in ["NÃO COMPARECEU", "NÃO", "NAN", ""] for val in row),
            axis=1
        )

        presentes_adapt = df_adaptado_presente_check.sum()
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
            ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
            height=350,
            xaxis=dict(title="Posto/Graduação", **(DARK_PLOTLY_THEME['xaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['xaxis']), tickangle=-45),
            yaxis=dict(title="Quantidade", **(DARK_PLOTLY_THEME['yaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['yaxis'])),
            margin=dict(t=50, b=20),
            legend=dict(font_color=theme['text_primary'])
        )
        st.plotly_chart(fig_adapt, use_container_width=True)

        # Tabela de dados
        st.markdown(f"<p class='section-title'>📋 Dados Completos — TAF Adaptado</p>", unsafe_allow_html=True)

        # Exibir as colunas originais de Corrida e Barra para TAF Adaptado
        display_cols_adapt = [
            "NOME", "POSTO_GRAD", "QUADRO", "SEXO", "IDADE", "FAIXA_ETARIA",
            "Corrida_Original", "Abdominal_Original", "Flexao_Original",
            "Natacao_Original", "Barra_Original"
        ]
        # Filtrar apenas as colunas que realmente existem no df_adaptado
        display_cols_adapt_existentes = [col for col in display_cols_adapt if col in df_adaptado.columns]

        df_adapt_display = df_adaptado[display_cols_adapt_existentes].copy()
        df_adapt_display = df_adapt_display.fillna("—")

        # Limpar valores "nan"
        for col in df_adapt_display.columns:
            df_adapt_display[col] = df_adapt_display[col].astype(str).replace("nan", "—")

        st.dataframe(df_adapt_display, height=500)

        # Exercícios realizados (contagem de valores não-NaN nas colunas originais)
        st.markdown(f"<p class='section-title'>📊 Exercícios Realizados</p>", unsafe_allow_html=True)

        # Usar as colunas originais para contar, pois no adaptado não há pontuação padronizada
        exercicios_originais_para_contar = {
            "Corrida": "Corrida_Original",
            "Abdominal": "Abdominal_Original",
            "Flexão": "Flexao_Original",
            "Natação": "Natacao_Original",
            "Barra": "Barra_Original",
        }

        ex_count = {}
        for display_name, col_name in exercicios_originais_para_contar.items():
            if col_name in df_adaptado.columns:
                count = df_adaptado[col_name].dropna().apply(
                    lambda x: str(x).strip().upper() not in ("", "NAN", "NÃO COMPARECEU", "NÃO", "NC")
                ).sum()
                ex_count[display_name] = count

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
                ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
                height=400,
                xaxis=dict(title="Exercício", **(DARK_PLOTLY_THEME['xaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['xaxis']), tickangle=-45),
                yaxis=dict(title="Realizaram", **(DARK_PLOTLY_THEME['yaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['yaxis'])),
                margin=dict(t=50, b=20),
                legend=dict(font_color=theme['text_primary'])
            )
            st.plotly_chart(fig_ex, use_container_width=True)
        else:
            st.info("Nenhum exercício adaptado com dados válidos encontrado.")

        st.info(
            f"ℹ️ O TAF Adaptado avalia militares com necessidades especiais ou "
            f"restrições médicas, utilizando exercícios alternativos conforme "
            f"aptidão individual. Cada militar realiza um conjunto diferente de provas."
        )
