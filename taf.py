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
      select {{
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
        background-color: {theme['card_bg']} !important;
        border: 2px solid {theme['card_border']} !important;
        padding: 10px 12px !important;
        border-radius: 8px !important;
      }}

      .stSelectbox > div > div > input:focus {{
        outline: none !important;
        border-color: {theme['accent']} !important;
        box-shadow: 0 0 0 3px {theme['accent']}40 !important; /* 40 é opacidade */
      }}

      /* Melhoria para selectbox dropdown */
      div[data-baseweb="select"] {{
        background-color: {theme['card_bg']} !important;
        border: 2px solid {theme['card_border']} !important;
        border-radius: 8px !important;
      }}

      /* Opções do dropdown */
      div[data-baseweb="menu"] {{
        background-color: {theme['card_bg']} !important;
      }}

      div[data-baseweb="menu"] > div {{
        background-color: {theme['card_bg']} !important;
      }}

      li[data-baseweb="option"] {{
        color: {theme['text_primary']} !important;
        background-color: {theme['card_bg']} !important;
        padding: 12px 16px !important;
      }}

      li[data-baseweb="option"]:hover {{
        background-color: {theme['accent']}50 !important; /* 50 é opacidade */
        color: {theme['text_primary']} !important;
      }}

      div[data-baseweb="popover"] {{
        background-color: {theme['card_bg']} !important;
      }}

      /* Botões */
      .stButton > button {{
        background-color: {theme['accent']} !important;
        color: {theme['text_primary']} !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        transition: background-color 0.2s ease !important;
      }}
      .stButton > button:hover {{
        background-color: {theme['accent']}cc !important; /* Cor mais escura no hover */
      }}

      /* Links */
      a {{
        color: {theme['accent']} !important;
      }}

      /* Divisores */
      .st-emotion-cache-10o4y0x {{ /* stDivider */
        background-color: {theme['border_color']} !important;
      }}

      /* Títulos de seção */
      .section-title {{
        font-size: 1.2rem;
        font-weight: bold;
        color: {theme['text_primary']} !important;
        margin-top: 20px;
        margin-bottom: 10px;
      }}

      /* Métricas */
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

      /* Badges */
      .badge-good {{
        background-color: {theme['badge_bg_good']};
        color: {theme['badge_text_good']};
        border: 1px solid {theme['badge_border_good']};
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
      }}
      .badge-avg {{
        background-color: {theme['badge_bg_avg']};
        color: {theme['badge_text_avg']};
        border: 1px solid {theme['badge_border_avg']};
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
      }}
      .badge-bad {{
        background-color: {theme['badge_bg_bad']};
        color: {theme['badge_text_bad']};
        border: 1px solid {theme['badge_border_bad']};
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
      }}
      .badge-neutral {{
        background-color: {theme['badge_bg_neutral']};
        color: {theme['badge_text_neutral']};
        border: 1px solid {theme['badge_border_neutral']};
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
      }}

      /* Dataframe */
      .stDataFrame {{
        color: {theme['text_primary']} !important;
      }}
      .stDataFrame table {{
        background-color: {theme['card_bg']} !important;
        border: 1px solid {theme['card_border']} !important;
      }}
      .stDataFrame th {{
        background-color: {theme['bg_tertiary']} !important;
        color: {theme['text_primary']} !important;
        border-bottom: 1px solid {theme['card_border']} !important;
      }}
      .stDataFrame td {{
        color: {theme['text_primary']} !important;
        border-bottom: 1px solid {theme['card_border']} !important;
      }}
      .stDataFrame .dataframe-header {{
        background-color: {theme['bg_tertiary']} !important;
      }}
      .stDataFrame .data-row {{
        background-color: {theme['card_bg']} !important;
      }}
      .stDataFrame .data-row:nth-child(even) {{
        background-color: {theme['bg_secondary']} !important;
      }}
      .stDataFrame .data-row:hover {{
        background-color: {theme['accent']}20 !important;
      }}

      /* Expander */
      .stExpander {{
        background-color: {theme['card_bg']} !important;
        border: 1px solid {theme['card_border']} !important;
        border-radius: 8px !important;
      }}
      .stExpander > div > div > div > p {{
        color: {theme['text_primary']} !important;
      }}
      .stExpander > div > div > div > svg {{
        fill: {theme['text_primary']} !important;
      }}

      /* Info/Warning/Error */
      .stAlert {{
        background-color: {theme['card_bg']} !important;
        border: 1px solid {theme['card_border']} !important;
        color: {theme['text_primary']} !important;
      }}
      .stAlert > div > div > p {{
        color: {theme['text_primary']} !important;
      }}
      .stAlert > div > div > svg {{
        fill: {theme['text_primary']} !important;
      }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DE TEMA PARA PLOTLY
# ══════════════════════════════════════════════════════════════════════════════

DARK_PLOTLY_THEME = {
    "plot_bgcolor": "rgba(17,27,46,0.95)",
    "paper_bgcolor": "rgba(17,27,46,0.95)",
    "font_color": "#ffffff",
    "xaxis": {
        "gridcolor": "rgba(255,255,255,0.1)",
        "linecolor": "rgba(255,255,255,0.2)",
        "zerolinecolor": "rgba(255,255,255,0.2)",
        "tickfont": {"color": "#ffffff"},
        "title_font": {"color": "#ffffff"},
    },
    "yaxis": {
        "gridcolor": "rgba(255,255,255,0.1)",
        "linecolor": "rgba(255,255,255,0.2)",
        "zerolinecolor": "rgba(255,255,255,0.2)",
        "tickfont": {"color": "#ffffff"},
        "title_font": {"color": "#ffffff"},
    },
    "legend": {"font": {"color": "#ffffff"}},
    "title": {"font": {"color": "#ffffff"}},
}

LIGHT_PLOTLY_THEME = {
    "plot_bgcolor": "#ffffff",
    "paper_bgcolor": "#ffffff",
    "font_color": "#1a1a1a",
    "xaxis": {
        "gridcolor": "rgba(0,0,0,0.1)",
        "linecolor": "rgba(0,0,0,0.2)",
        "zerolinecolor": "rgba(0,0,0,0.2)",
        "tickfont": {"color": "#1a1a1a"},
        "title_font": {"color": "#1a1a1a"},
    },
    "yaxis": {
        "gridcolor": "rgba(0,0,0,0.1)",
        "linecolor": "rgba(0,0,0,0.2)",
        "zerolinecolor": "rgba(0,0,0,0.2)",
        "tickfont": {"color": "#1a1a1a"},
        "title_font": {"color": "#1a1a1a"},
    },
    "legend": {"font": {"color": "#1a1a1a"}},
    "title": {"font": {"color": "#1a1a1a"}},
}

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES DE PROCESSAMENTO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

def calcular_idade(data_nascimento: str) -> int:
    """Calcula a idade a partir da data de nascimento."""
    if pd.isna(data_nascimento):
        return np.nan
    try:
        # Tenta converter para datetime, suportando múltiplos formatos
        if isinstance(data_nascimento, datetime):
            dob = data_nascimento
        else:
            dob = pd.to_datetime(data_nascimento, errors='coerce', dayfirst=True)

        if pd.isna(dob):
            return np.nan

        today = datetime.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except Exception:
        return np.nan

def remover_acentos(texto: str) -> str:
    """Remove acentos e caracteres especiais de uma string."""
    if not isinstance(texto, str):
        return texto
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def parse_corrida_value(value):
    """
    Tenta parsear o valor da Corrida.
    Retorna (distancia_m, tempo_seg, is_tempo).
    """
    if pd.isna(value) or value == "" or str(value).strip().upper() in ["NÃO COMPARECEU", "NÃO", "NC"]:
        return np.nan, np.nan, False

    s_value = str(value).strip().replace(",", ".")

    # Tenta parsear como tempo (MM'SS" ou SS")
    match_min_sec = re.match(r"(\d+)'(\d+)\"", s_value)
    match_sec = re.match(r"(\d+)\"", s_value)

    if match_min_sec:
        minutes = int(match_min_sec.group(1))
        seconds = int(match_min_sec.group(2))
        return np.nan, (minutes * 60) + seconds, True
    elif match_sec:
        seconds = int(match_sec.group(1))
        return np.nan, seconds, True
    else:
        # Tenta parsear como distância em metros
        try:
            distancia = float(s_value)
            return distancia, np.nan, False
        except ValueError:
            return np.nan, np.nan, False # Não conseguiu parsear

def parse_barra_value(value):
    """
    Tenta parsear o valor da Barra.
    Retorna (repeticoes, tempo_seg, is_tempo).
    """
    if pd.isna(value) or value == "" or str(value).strip().upper() in ["NÃO COMPARECEU", "NÃO", "NC"]:
        return np.nan, np.nan, False

    s_value = str(value).strip().replace(",", ".")

    # Tenta parsear como tempo (MM'SS" ou SS")
    match_min_sec = re.match(r"(\d+)'(\d+)\"", s_value)
    match_sec = re.match(r"(\d+)\"", s_value)

    if match_min_sec:
        minutes = int(match_min_sec.group(1))
        seconds = int(match_min_sec.group(2))
        return np.nan, (minutes * 60) + seconds, True
    elif match_sec:
        seconds = int(match_sec.group(1))
        return np.nan, seconds, True
    else:
        # Tenta parsear como repetições
        try:
            # Remove qualquer texto como " P" ou " estát"
            s_value_clean = re.sub(r"[^\d.]", "", s_value).strip()
            repeticoes = float(s_value_clean)
            return repeticoes, np.nan, False
        except ValueError:
            return np.nan, np.nan, False # Não conseguiu parsear

def parse_abdominal_flexao_natacao(value):
    """Tenta parsear valores de Abdominal, Flexao, Natacao."""
    if pd.isna(value) or value == "" or str(value).strip().upper() in ["NÃO COMPARECEU", "NÃO", "NC"]:
        return np.nan
    s_value = str(value).strip().replace(",", ".")
    try:
        # Remove " rep" ou outros textos não numéricos
        s_value_clean = re.sub(r"[^\d.]", "", s_value).strip()
        return float(s_value_clean)
    except ValueError:
        return np.nan

def ordem_posto(posto):
    """Define uma ordem para os postos/graduações para ordenação."""
    ordem = {
        "CORONEL": 1, "TENENTE-CORONEL": 2, "MAJOR": 3, "CAP": 4,
        "1º TEN": 5, "2º TEN": 6, "ASPIRANTE": 7, "SUBTENENTE": 8,
        "1º SGT": 9, "2º SGT": 10, "3º SGT": 11, "CABO": 12, "SOLDADO": 13
    }
    return ordem.get(posto.upper(), 99) # 99 para postos não mapeados

# ══════════════════════════════════════════════════════════════════════════════
# REGRAS DE PONTUAÇÃO (EXEMPLO - ADAPTE CONFORME AS REGRAS REAIS DO CBMAM)
# ══════════════════════════════════════════════════════════════════════════════

# Estrutura: {faixa_etaria: {exercicio: {pontuacao_min: pontos}}}
# Para corrida: distância em metros. Para natação: tempo em segundos (menor é melhor).
# Para barra feminina: tempo em segundos (maior é melhor).
# Para abdominal/flexão/barra masculina: repetições (maior é melhor).

REGRAS_MASCULINO = {
    "18-24": {
        "CORRIDA": {2800: 100, 2700: 90, 2600: 80, 2500: 70, 2400: 60, 2300: 50, 2200: 40, 2100: 30, 2000: 20, 1900: 10, 1800: 0},
        "ABDOMINAL": {45: 100, 40: 90, 35: 80, 30: 70, 25: 60, 20: 50, 15: 40, 10: 30, 5: 20, 1: 10, 0: 0},
        "FLEXAO": {35: 100, 30: 90, 25: 80, 20: 70, 15: 60, 10: 50, 8: 40, 6: 30, 4: 20, 2: 10, 0: 0},
        "NATACAO": {30: 100, 35: 90, 40: 80, 45: 70, 50: 60, 55: 50, 60: 40, 65: 30, 70: 20, 75: 10, 80: 0}, # Tempo em segundos
        "BARRA": {12: 100, 10: 90, 8: 80, 6: 70, 5: 60, 4: 50, 3: 40, 2: 30, 1: 20, 0: 0}, # Repetições
    },
    "25-29": {
        "CORRIDA": {2700: 100, 2600: 90, 2500: 80, 2400: 70, 2300: 60, 2200: 50, 2100: 40, 2000: 30, 1900: 20, 1800: 10, 1700: 0},
        "ABDOMINAL": {40: 100, 35: 90, 30: 80, 25: 70, 20: 60, 18: 50, 16: 40, 14: 30, 12: 20, 10: 10, 0: 0},
        "FLEXAO": {30: 100, 25: 90, 20: 80, 18: 70, 16: 60, 14: 50, 12: 40, 10: 30, 8: 20, 6: 10, 0: 0},
        "NATACAO": {35: 100, 40: 90, 45: 80, 50: 70, 55: 60, 60: 50, 65: 40, 70: 30, 75: 20, 80: 10, 85: 0},
        "BARRA": {10: 100, 8: 90, 6: 80, 5: 70, 4: 60, 3: 50, 2: 40, 1: 30, 0: 0},
    },
    "30-34": {
        "CORRIDA": {2600: 100, 2500: 90, 2400: 80, 2300: 70, 2200: 60, 2100: 50, 2000: 40, 1900: 30, 1800: 20, 1700: 10, 1600: 0},
        "ABDOMINAL": {35: 100, 30: 90, 25: 80, 20: 70, 18: 60, 16: 50, 14: 40, 12: 30, 10: 20, 8: 10, 0: 0},
        "FLEXAO": {25: 100, 20: 90, 18: 80, 16: 70, 14: 60, 12: 50, 10: 40, 8: 30, 6: 20, 4: 10, 0: 0},
        "NATACAO": {40: 100, 45: 90, 50: 80, 55: 70, 60: 60, 65: 50, 70: 40, 75: 30, 80: 20, 85: 10, 90: 0},
        "BARRA": {8: 100, 6: 90, 5: 80, 4: 70, 3: 60, 2: 50, 1: 40, 0: 0},
    },
    "35-39": {
        "CORRIDA": {2500: 100, 2400: 90, 2300: 80, 2200: 70, 2100: 60, 2000: 50, 1900: 40, 1800: 30, 1700: 20, 1600: 10, 1500: 0},
        "ABDOMINAL": {30: 100, 25: 90, 20: 80, 18: 70, 16: 60, 14: 50, 12: 40, 10: 30, 8: 20, 6: 10, 0: 0},
        "FLEXAO": {20: 100, 18: 90, 16: 80, 14: 70, 12: 60, 10: 50, 8: 40, 6: 30, 4: 20, 2: 10, 0: 0},
        "NATACAO": {45: 100, 50: 90, 55: 80, 60: 70, 65: 60, 70: 50, 75: 40, 80: 30, 85: 20, 90: 10, 95: 0},
        "BARRA": {6: 100, 5: 90, 4: 80, 3: 70, 2: 60, 1: 50, 0: 0},
    },
    "40-44": {
        "CORRIDA": {2400: 100, 2300: 90, 2200: 80, 2100: 70, 2000: 60, 1900: 50, 1800: 40, 1700: 30, 1600: 20, 1500: 10, 1400: 0},
        "ABDOMINAL": {25: 100, 20: 90, 18: 80, 16: 70, 14: 60, 12: 50, 10: 40, 8: 30, 6: 20, 4: 10, 0: 0},
        "FLEXAO": {18: 100, 16: 90, 14: 80, 12: 70, 10: 60, 8: 50, 6: 40, 4: 30, 2: 20, 0: 0},
        "NATACAO": {50: 100, 55: 90, 60: 80, 65: 70, 70: 60, 75: 50, 80: 40, 85: 30, 90: 20, 95: 10, 100: 0},
        "BARRA": {5: 100, 4: 90, 3: 80, 2: 70, 1: 60, 0: 0},
    },
    "45-49": {
        "CORRIDA": {2300: 100, 2200: 90, 2100: 80, 2000: 70, 1900: 60, 1800: 50, 1700: 40, 1600: 30, 1500: 20, 1400: 10, 1300: 0},
        "ABDOMINAL": {20: 100, 18: 90, 16: 80, 14: 70, 12: 60, 10: 50, 8: 40, 6: 30, 4: 20, 2: 10, 0: 0},
        "FLEXAO": {16: 100, 14: 90, 12: 80, 10: 70, 8: 60, 6: 50, 4: 40, 2: 30, 0: 0},
        "NATACAO": {55: 100, 60: 90, 65: 80, 70: 70, 75: 60, 80: 50, 85: 40, 90: 30, 95: 20, 100: 10, 105: 0},
        "BARRA": {4: 100, 3: 90, 2: 80, 1: 70, 0: 0},
    },
    "50+": {
        "CORRIDA": {2200: 100, 2100: 90, 2000: 80, 1900: 70, 1800: 60, 1700: 50, 1600: 40, 1500: 30, 1400: 20, 1300: 10, 1200: 0},
        "ABDOMINAL": {18: 100, 16: 90, 14: 80, 12: 70, 10: 60, 8: 50, 6: 40, 4: 30, 2: 20, 0: 0},
        "FLEXAO": {14: 100, 12: 90, 10: 80, 8: 70, 6: 60, 4: 50, 2: 40, 0: 0},
        "NATACAO": {60: 100, 65: 90, 70: 80, 75: 70, 80: 60, 85: 50, 90: 40, 95: 30, 100: 20, 105: 10, 110: 0},
        "BARRA": {3: 100, 2: 90, 1: 80, 0: 0},
    },
}

REGRAS_FEMININO = {
    "18-24": {
        "CORRIDA": {2400: 100, 2300: 90, 2200: 80, 2100: 70, 2000: 60, 1900: 50, 1800: 40, 1700: 30, 1600: 20, 1500: 10, 1400: 0},
        "ABDOMINAL": {40: 100, 35: 90, 30: 80, 25: 70, 20: 60, 15: 50, 10: 40, 8: 30, 6: 20, 4: 10, 0: 0},
        "FLEXAO": {30: 100, 25: 90, 20: 80, 18: 70, 16: 60, 14: 50, 12: 40, 10: 30, 8: 20, 6: 10, 0: 0},
        "NATACAO": {35: 100, 40: 90, 45: 80, 50: 70, 55: 60, 60: 50, 65: 40, 70: 30, 75: 20, 80: 10, 85: 0},
        "BARRA": {60: 100, 55: 90, 50: 80, 45: 70, 40: 60, 35: 50, 30: 40, 25: 30, 20: 20, 15: 10, 0: 0}, # Tempo em segundos (maior é melhor)
    },
    "25-29": {
        "CORRIDA": {2300: 100, 2200: 90, 2100: 80, 2000: 70, 1900: 60, 1800: 50, 1700: 40, 1600: 30, 1500: 20, 1400: 10, 1300: 0},
        "ABDOMINAL": {35: 100, 30: 90, 25: 80, 20: 70, 18: 60, 16: 50, 14: 40, 12: 30, 10: 20, 8: 10, 0: 0},
        "FLEXAO": {25: 100, 20: 90, 18: 80, 16: 70, 14: 60, 12: 50, 10: 40, 8: 30, 6: 20, 4: 10, 0: 0},
        "NATACAO": {40: 100, 45: 90, 50: 80, 55: 70, 60: 60, 65: 50, 70: 40, 75: 30, 80: 20, 85: 10, 90: 0},
        "BARRA": {55: 100, 50: 90, 45: 80, 40: 70, 35: 60, 30: 50, 25: 40, 20: 30, 15: 20, 10: 10, 0: 0},
    },
    "30-34": {
        "CORRIDA": {2200: 100, 2100: 90, 2000: 80, 1900: 70, 1800: 60, 1700: 50, 1600: 40, 1500: 30, 1400: 20, 1300: 10, 1200: 0},
        "ABDOMINAL": {30: 100, 25: 90, 20: 80, 18: 70, 16: 60, 14: 50, 12: 40, 10: 30, 8: 20, 6: 10, 0: 0},
        "FLEXAO": {20: 100, 18: 90, 16: 80, 14: 70, 12: 60, 10: 50, 8: 40, 6: 30, 4: 20, 0: 0},
        "NATACAO": {45: 100, 50: 90, 55: 80, 60: 70, 65: 60, 70: 50, 75: 40, 80: 30, 85: 20, 90: 10, 95: 0},
        "BARRA": {50: 100, 45: 90, 40: 80, 35: 70, 30: 60, 25: 50, 20: 40, 15: 30, 10: 20, 5: 10, 0: 0},
    },
    "35-39": {
        "CORRIDA": {2100: 100, 2000: 90, 1900: 80, 1800: 70, 1700: 60, 1600: 50, 1500: 40, 1400: 30, 1300: 20, 1200: 10, 1100: 0},
        "ABDOMINAL": {25: 100, 20: 90, 18: 80, 16: 70, 14: 60, 12: 50, 10: 40, 8: 30, 6: 20, 4: 10, 0: 0},
        "FLEXAO": {18: 100, 16: 90, 14: 80, 12: 70, 10: 60, 8: 50, 6: 40, 4: 30, 2: 20, 0: 0},
        "NATACAO": {50: 100, 55: 90, 60: 80, 65: 70, 70: 60, 75: 50, 80: 40, 85: 30, 90: 20, 95: 10, 100: 0},
        "BARRA": {45: 100, 40: 90, 35: 80, 30: 70, 25: 60, 20: 50, 15: 40, 10: 30, 5: 20, 0: 0},
    },
    "40-44": {
        "CORRIDA": {2000: 100, 1900: 90, 1800: 80, 1700: 70, 1600: 60, 1500: 50, 1400: 40, 1300: 30, 1200: 20, 1100: 10, 1000: 0},
        "ABDOMINAL": {20: 100, 18: 90, 16: 80, 14: 70, 12: 60, 10: 50, 8: 40, 6: 30, 4: 20, 2: 10, 0: 0},
        "FLEXAO": {16: 100, 14: 90, 12: 80, 10: 70, 8: 60, 6: 50, 4: 40, 2: 30, 0: 0},
        "NATACAO": {55: 100, 60: 90, 65: 80, 70: 70, 75: 60, 80: 50, 85: 40, 90: 30, 95: 20, 100: 10, 105: 0},
        "BARRA": {40: 100, 35: 90, 30: 80, 25: 70, 20: 60, 15: 50, 10: 40, 5: 30, 0: 0},
    },
    "45-49": {
        "CORRIDA": {1900: 100, 1800: 90, 1700: 80, 1600: 70, 1500: 60, 1400: 50, 1300: 40, 1200: 30, 1100: 20, 1000: 10, 900: 0},
        "ABDOMINAL": {18: 100, 16: 90, 14: 80, 12: 70, 10: 60, 8: 50, 6: 40, 4: 30, 2: 20, 0: 0},
        "FLEXAO": {14: 100, 12: 90, 10: 80, 8: 70, 6: 60, 4: 50, 2: 40, 0: 0},
        "NATACAO": {60: 100, 65: 90, 70: 80, 75: 70, 80: 60, 85: 50, 90: 40, 95: 30, 100: 20, 105: 10, 110: 0},
        "BARRA": {35: 100, 30: 90, 25: 80, 20: 70, 15: 60, 10: 50, 5: 40, 0: 0},
    },
    "50+": {
        "CORRIDA": {1800: 100, 1700: 90, 1600: 80, 1500: 70, 1400: 60, 1300: 50, 1200: 40, 1100: 30, 1000: 20, 900: 10, 800: 0},
        "ABDOMINAL": {16: 100, 14: 90, 12: 80, 10: 70, 8: 60, 6: 50, 4: 40, 2: 30, 0: 0},
        "FLEXAO": {12: 100, 10: 90, 8: 80, 6: 70, 4: 60, 2: 50, 0: 0},
        "NATACAO": {65: 100, 70: 90, 75: 80, 80: 70, 85: 60, 90: 50, 95: 40, 100: 30, 105: 20, 110: 10, 115: 0},
        "BARRA": {30: 100, 25: 90, 20: 80, 15: 70, 10: 60, 5: 50, 0: 0},
    },
}

def get_faixa_etaria(idade):
    """Determina a faixa etária com base na idade."""
    if pd.isna(idade):
        return "Não Informado"
    if 18 <= idade <= 24: return "18-24"
    if 25 <= idade <= 29: return "25-29"
    if 30 <= idade <= 34: return "30-34"
    if 35 <= idade <= 39: return "35-39"
    if 40 <= idade <= 44: return "40-44"
    if 45 <= idade <= 49: return "45-49"
    if idade >= 50: return "50+"
    return "Não Classificado"

def calcular_pontuacao(sexo, idade, exercicio, valor):
    """Calcula a pontuação para um exercício específico."""
    if pd.isna(valor) or pd.isna(idade) or pd.isna(sexo):
        return 0 # Ausente ou dados incompletos

    faixa_etaria = get_faixa_etaria(idade)
    if faixa_etaria == "Não Classificado" or faixa_etaria == "Não Informado":
        return 0

    regras = REGRAS_MASCULINO if sexo == "Masculino" else REGRAS_FEMININO
    regras_exercicio = regras.get(faixa_etaria, {}).get(exercicio)

    if not regras_exercicio:
        return 0 # Regras não definidas para esta faixa/exercício

    pontuacao = 0
    if exercicio in ["CORRIDA", "ABDOMINAL", "FLEXAO"]: # Maior é melhor
        for limite, pontos in sorted(regras_exercicio.items(), reverse=True):
            if valor >= limite:
                pontuacao = pontos
                break
    elif exercicio == "NATACAO": # Menor é melhor (tempo)
        for limite, pontos in sorted(regras_exercicio.items(), reverse=False):
            if valor <= limite:
                pontuacao = pontos
                break
    elif exercicio == "BARRA":
        if sexo == "Masculino": # Repetições (maior é melhor)
            for limite, pontos in sorted(regras_exercicio.items(), reverse=True):
                if valor >= limite:
                    pontuacao = pontos
                    break
        else: # Feminino: Tempo em segundos (maior é melhor)
            for limite, pontos in sorted(regras_exercicio.items(), reverse=True):
                if valor >= limite:
                    pontuacao = pontos
                    break
    return pontuacao

def classificar_desempenho(media_final):
    """Classifica o desempenho geral com base na média final."""
    if pd.isna(media_final):
        return "Não Avaliado", "badge-neutral"
    if media_final >= 70:
        return "Excelente", "badge-good"
    elif media_final >= 50:
        return "Bom", "badge-avg"
    elif media_final >= 30:
        return "Regular", "badge-bad"
    else:
        return "Insuficiente", "badge-bad"

# ══════════════════════════════════════════════════════════════════════════════
# CARREGAMENTO E PRÉ-PROCESSAMENTO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    """Carrega e pré-processa os dados do TAF."""
    df = pd.read_csv("master_taf_consolidado.csv", sep="|", skipinitialspace=True)

    # Limpar espaços em branco dos nomes das colunas e remover a coluna 'ORD'
    df.columns = df.columns.str.strip()
    if 'ORD' in df.columns:
        df = df.drop(columns=['ORD'])

    # Renomear colunas para padronização
    df = df.rename(columns={
        "Posto": "POSTO_GRAD",
        "Nome": "NOME",
        "DataNascimento": "DATA_NASCIMENTO",
        "Raça/Cor": "RACA_COR",
        "Idade": "IDADE_CSV" # Manter a idade do CSV para referência, mas recalcular
    })

    # Remover espaços em branco do início/fim dos valores string
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # Remover acentos e padronizar "Masculino"/"Feminino"
    df["SEXO"] = df["SEXO"].apply(lambda x: remover_acentos(x).capitalize() if isinstance(x, str) else x)
    df["SEXO"] = df["SEXO"].replace({"MASCULINO": "Masculino", "FEMININO": "Feminino"})

    # Limpar NOME
    df["NOME"] = df["NOME"].str.strip()

    # Criar colunas _Original para manter os valores brutos
    df["Corrida_Original"] = df["Corrida"]
    df["Abdominal_Original"] = df["Abdominal"]
    df["Flexao_Original"] = df["Flexao"]
    df["Natacao_Original"] = df["Natacao"]
    df["Barra_Original"] = df["Barra"]

    # Processar DATA_NASCIMENTO e calcular IDADE
    df["DATA_NASCIMENTO"] = pd.to_datetime(df["DATA_NASCIMENTO"], format="%d/%m/%Y", errors='coerce')
    df["IDADE"] = df["DATA_NASCIMENTO"].apply(calcular_idade)
    df["FAIXA_ETARIA"] = df["IDADE"].apply(get_faixa_etaria)

    # Aplicar funções de parse para Corrida e Barra
    # Usar apply com axis=1 para acessar outras colunas da linha
    df[['CORRIDA_DISTANCIA_M', 'CORRIDA_TEMPO_SEG', 'CORRIDA_IS_TEMPO']] = df.apply(
        lambda row: pd.Series(parse_corrida_value(row['Corrida_Original'])), axis=1
    )
    df[['BARRA_REPETICOES', 'BARRA_TEMPO_SEG', 'BARRA_IS_TEMPO']] = df.apply(
        lambda row: pd.Series(parse_barra_value(row['Barra_Original'])), axis=1
    )

    # Processar Abdominal, Flexao, Natacao
    df["ABDOMINAL"] = df["Abdominal_Original"].apply(parse_abdominal_flexao_natacao)
    df["FLEXAO"] = df["Flexao_Original"].apply(parse_abdominal_flexao_natacao)
    df["NATACAO"] = df["Natacao_Original"].apply(parse_abdominal_flexao_natacao) # Tempo em segundos

    # Definir valores para pontuação (CORRIDA e BARRA)
    # Para CORRIDA: se for tempo, não pontua no regular. Se for distância, usa a distância.
    df["CORRIDA"] = df.apply(
        lambda row: row["CORRIDA_DISTANCIA_M"] if not row["CORRIDA_IS_TEMPO"] else np.nan, axis=1
    )

    # Para BARRA: Masculino (repetições), Feminino (tempo em segundos)
    df["BARRA"] = np.nan
    df.loc[df["SEXO"] == "Masculino", "BARRA"] = df.loc[df["SEXO"] == "Masculino", "BARRA_REPETICOES"]
    df.loc[df["SEXO"] == "Feminino", "BARRA"] = df.loc[df["SEXO"] == "Feminino", "BARRA_TEMPO_SEG"]

    # Calcular pontuações para cada exercício
    exercicios = ["CORRIDA", "ABDOMINAL", "FLEXAO", "NATACAO", "BARRA"]
    for ex in exercicios:
        df[f"PONTUACAO_{ex}"] = df.apply(
            lambda row: calcular_pontuacao(row["SEXO"], row["IDADE"], ex, row[ex]), axis=1
        )

    # Identificar militares que não compareceram a NENHUM exercício regular
    # ou que fizeram exercícios em formato "adaptado" para seu sexo/prova

    # Condição para não comparecimento geral
    nao_compareceu_geral = df[exercicios].isnull().all(axis=1)

    # Condições para TAF Adaptado (exercícios com formato diferente do esperado para pontuação regular)
    # Corrida: se registrou tempo (CORRIDA_IS_TEMPO == True)
    corrida_adaptada = df["CORRIDA_IS_TEMPO"] == True

    # Barra: se homem fez tempo (BARRA_IS_TEMPO == True) ou mulher fez repetições (BARRA_IS_TEMPO == False e BARRA_REPETICOES não é NaN)
    barra_adaptada_masculino = (df["SEXO"] == "Masculino") & (df["BARRA_IS_TEMPO"] == True)
    barra_adaptada_feminino = (df["SEXO"] == "Feminino") & (df["BARRA_IS_TEMPO"] == False) & (df["BARRA_REPETICOES"].notna())
    barra_adaptada = barra_adaptada_masculino | barra_adaptada_feminino

    # Combinar condições para TAF Adaptado
    df["TAF_ADAPTADO"] = nao_compareceu_geral | corrida_adaptada | barra_adaptada

    # Separar DataFrames
    df_regular = df[~df["TAF_ADAPTADO"]].copy()
    df_adaptado = df[df["TAF_ADAPTADO"]].copy()

    # Calcular Média Final e Classificação para df_regular
    pontuacoes_cols = [f"PONTUACAO_{ex}" for ex in exercicios]
    df_regular["MEDIA_FINAL"] = df_regular[pontuacoes_cols].mean(axis=1)
    df_regular["CLASSIFICACAO"], df_regular["CLASSIFICACAO_BADGE"] = zip(*df_regular["MEDIA_FINAL"].apply(classificar_desempenho))

    # Para df_adaptado, se não compareceu a nada, marcar como "Não Compareceu"
    df_adaptado["CLASSIFICACAO"] = "TAF Adaptado"
    df_adaptado["CLASSIFICACAO_BADGE"] = "badge-neutral"
    df_adaptado.loc[df_adaptado[exercicios].isnull().all(axis=1), "CLASSIFICACAO"] = "Não Compareceu"
    df_adaptado.loc[df_adaptado[exercicios].isnull().all(axis=1), "CLASSIFICACAO_BADGE"] = "badge-neutral"


    return df_regular, df_adaptado

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE GERAÇÃO DE GRÁFICOS
# ══════════════════════════════════════════════════════════════════════════════

def create_radar_chart(df_militar, theme):
    """Cria um gráfico de radar para as pontuações de um militar."""
    if df_militar.empty:
        return go.Figure()

    pontuacoes = df_militar[[f"PONTUACAO_{ex}" for ex in ["CORRIDA", "ABDOMINAL", "FLEXAO", "NATACAO", "BARRA"]]].iloc[0].tolist()
    exercicios_nomes = ["Corrida", "Abdominal", "Flexão", "Natação", "Barra"]

    fig = go.Figure(data=go.Scatterpolar(
        r=pontuacoes + [pontuacoes[0]], # Fechar o círculo
        theta=exercicios_nomes + [exercicios_nomes[0]],
        fill='toself',
        name='Pontuação',
        line_color=theme['accent'],
        marker_color=theme['accent'],
        hovertemplate='<b>%{theta}</b>: %{r:.0f} pontos<extra></extra>'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor=theme['border_color'],
                linecolor=theme['border_color'],
                tickfont_color=theme['text_secondary'],
                title_font_color=theme['text_primary']
            ),
            angularaxis=dict(
                linecolor=theme['border_color'],
                tickfont_color=theme['text_primary']
            )
        ),
        showlegend=False,
        title_text="Desempenho por Exercício",
        title_x=0.5,
        ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
        height=400,
        margin=dict(l=50, r=50, t=70, b=50)
    )
    return fig

def create_bar_chart_pontuacoes(df_militar, theme):
    """Cria um gráfico de barras para as pontuações de um militar."""
    if df_militar.empty:
        return go.Figure()

    pontuacoes = df_militar[[f"PONTUACAO_{ex}" for ex in ["CORRIDA", "ABDOMINAL", "FLEXAO", "NATACAO", "BARRA"]]].iloc[0].tolist()
    exercicios_nomes = ["Corrida", "Abdominal", "Flexão", "Natação", "Barra"]

    fig = px.bar(
        x=exercicios_nomes,
        y=pontuacoes,
        labels={"x": "Exercício", "y": "Pontuação"},
        title="Pontuação Detalhada por Exercício",
        color=pontuacoes,
        color_continuous_scale=[theme['accent'], "#22c55e"],
        text_auto=True
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
        height=400,
        xaxis=dict(title="Exercício", **(DARK_PLOTLY_THEME['xaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['xaxis'])),
        yaxis=dict(title="Pontuação", range=[0, 100], **(DARK_PLOTLY_THEME['yaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['yaxis'])),
        margin=dict(l=50, r=50, t=70, b=50),
        coloraxis_showscale=False
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÃO DE GERAÇÃO DE PDF
# ══════════════════════════════════════════════════════════════════════════════

def create_pdf_report(df_militar, theme):
    """Gera um relatório PDF da ficha individual de um militar."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0.1, 0.1, 0.1) # Cor escura para o título no PDF
    c.drawString(50, height - 50, "Ficha Individual de TAF")

    # Informações do Militar
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    y_pos = height - 100

    info_militar = {
        "Nome": df_militar["NOME"].iloc[0],
        "Posto/Graduação": df_militar["POSTO_GRAD"].iloc[0],
        "Quadro": df_militar["QUADRO"].iloc[0],
        "Sexo": df_militar["SEXO"].iloc[0],
        "Idade": f"{int(df_militar['IDADE'].iloc[0])} anos" if pd.notna(df_militar['IDADE'].iloc[0]) else "N/A",
        "Faixa Etária": df_militar["FAIXA_ETARIA"].iloc[0],
        "Média Final": f"{df_militar['MEDIA_FINAL'].iloc[0]:.2f}" if pd.notna(df_militar['MEDIA_FINAL'].iloc[0]) else "N/A",
        "Classificação": df_militar["CLASSIFICACAO"].iloc[0],
    }

    for key, value in info_militar.items():
        c.drawString(50, y_pos, f"• {key}: {value}")
        y_pos -= 15

    y_pos -= 20 # Espaço extra

    # Tabela de Pontuações
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos, "Pontuações por Exercício:")
    y_pos -= 20

    data = [["Exercício", "Valor Real", "Pontuação"]]
    exercicios_map = {
        "CORRIDA": "Corrida (m)",
        "ABDOMINAL": "Abdominal (reps)",
        "FLEXAO": "Flexão (reps)",
        "NATACAO": "Natação (seg)",
        "BARRA": "Barra (reps/seg)"
    }

    for ex_key, ex_display_name in exercicios_map.items():
        valor_real = df_militar[ex_key].iloc[0]
        pontuacao = df_militar[f"PONTUACAO_{ex_key}"].iloc[0]

        # Formatar valor real
        if ex_key == "CORRIDA" and df_militar["CORRIDA_IS_TEMPO"].iloc[0]:
            valor_real_str = f"{df_militar['CORRIDA_TEMPO_SEG'].iloc[0]:.0f} seg (adaptado)" if pd.notna(df_militar['CORRIDA_TEMPO_SEG'].iloc[0]) else "N/A"
        elif ex_key == "BARRA" and df_militar["SEXO"].iloc[0] == "Masculino" and df_militar["BARRA_IS_TEMPO"].iloc[0]:
            valor_real_str = f"{df_militar['BARRA_TEMPO_SEG'].iloc[0]:.0f} seg (adaptado)" if pd.notna(df_militar['BARRA_TEMPO_SEG'].iloc[0]) else "N/A"
        elif ex_key == "BARRA" and df_militar["SEXO"].iloc[0] == "Feminino" and not df_militar["BARRA_IS_TEMPO"].iloc[0] and pd.notna(df_militar["BARRA_REPETICOES"].iloc[0]):
             valor_real_str = f"{df_militar['BARRA_REPETICOES'].iloc[0]:.0f} reps (adaptado)" if pd.notna(df_militar['BARRA_REPETICOES'].iloc[0]) else "N/A"
        else:
            valor_real_str = f"{valor_real:.0f}" if pd.notna(valor_real) else "N/A"

        data.append([
            ex_display_name,
            valor_real_str,
            f"{pontuacao:.0f}" if pd.notna(pontuacao) else "0"
        ])

    table_x = 50
    table_y = y_pos
    col_widths = [150, 100, 80]
    row_height = 20

    c.setFont("Helvetica-Bold", 10)
    for i, header in enumerate(data[0]):
        c.drawString(table_x + sum(col_widths[:i]), table_y, header)

    y_pos = table_y - row_height
    c.setFont("Helvetica", 10)
    for row_data in data[1:]:
        for i, cell in enumerate(row_data):
            c.drawString(table_x + sum(col_widths[:i]), y_pos, str(cell))
        y_pos -= row_height

    # Adicionar gráficos
    y_pos -= 30

    # Gráfico de Radar
    radar_fig = create_radar_chart(df_militar, theme)
    img_radar_buffer = io.BytesIO()
    radar_fig.write_image(img_radar_buffer, format="png", width=500, height=400, scale=2)
    img_radar_buffer.seek(0)
    img_radar = ImageReader(img_radar_buffer)

    # Ajustar posição para caber na página
    if y_pos - 400 < 50: # Se não houver espaço suficiente, vai para a próxima página
        c.showPage()
        y_pos = height - 50 - 50 # Reinicia a posição no topo da nova página
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_pos + 20, "Gráficos de Desempenho:")
        y_pos -= 20

    c.drawImage(img_radar, 50, y_pos - 400, width=250, height=200) # Reduzir tamanho para caber
    y_pos -= 210 # Ajustar para o próximo elemento

    # Gráfico de Barras
    bar_fig = create_bar_chart_pontuacoes(df_militar, theme)
    img_bar_buffer = io.BytesIO()
    bar_fig.write_image(img_bar_buffer, format="png", width=500, height=400, scale=2)
    img_bar_buffer.seek(0)
    img_bar = ImageReader(img_bar_buffer)

    if y_pos - 400 < 50: # Se não houver espaço suficiente, vai para a próxima página
        c.showPage()
        y_pos = height - 50 - 50 # Reinicia a posição no topo da nova página
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_pos + 20, "Gráficos de Desempenho (continuação):")
        y_pos -= 20

    c.drawImage(img_bar, 50, y_pos - 400, width=250, height=200) # Reduzir tamanho para caber
    y_pos -= 210

    c.save()
    buffer.seek(0)
    return buffer

# ══════════════════════════════════════════════════════════════════════════════
# APLICAÇÃO STREAMLIT
# ══════════════════════════════════════════════════════════════════════════════

# Carregar dados
df_regular, df_adaptado = load_data()

# Obter configuração de tema
theme = get_theme_config()
apply_dynamic_css(theme)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Logo do CBMAM
    if _LOCAL_LOGO_PATH:
        st.image(str(_LOCAL_LOGO_PATH), width=150)
    else:
        st.image(_get_cbmam_image_url(), width=150)

    st.markdown(f"""
    <h2 style="margin:0;font-size:1.5rem;color:{theme['text_primary']}">Dashboard TAF</h2>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Análise do Teste de Aptidão Física
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    pagina = st.radio(
        "Navegação",
        ["📊 Visão Geral", "👤 Ficha Individual", "♿ TAF Adaptado"],
        index=0,
        key="main_navigation",
    )

    st.divider()

    # Botão de tema
    if st.session_state.tema == "escuro":
        if st.button("☀️ Mudar para Tema Claro"):
            st.session_state.tema = "claro"
            st.rerun()
    else:
        if st.button("🌙 Mudar para Tema Escuro"):
            st.session_state.tema = "escuro"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: VISÃO GERAL
# ══════════════════════════════════════════════════════════════════════════════

if pagina == "📊 Visão Geral":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">📊 Visão Geral</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Análise consolidada do desempenho no TAF
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    # KPIs
    total_militares = len(df_regular) + len(df_adaptado)
    total_regular = len(df_regular)
    total_adaptado = len(df_adaptado)

    # Militares presentes no TAF regular (que não são NaN em nenhuma prova)
    exercicios_regulares = ["CORRIDA", "ABDOMINAL", "FLEXAO", "NATACAO", "BARRA"]
    presentes_regular = df_regular[exercicios_regulares].notna().all(axis=1).sum()
    ausentes_regular = total_regular - presentes_regular

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("👥 Total Militares", total_militares)
    with k2:
        st.metric("🏃 TAF Regular", total_regular)
    with k3:
        st.metric("✅ Presentes (Regular)", presentes_regular)
    with k4:
        st.metric("❌ Ausentes (Regular)", ausentes_regular)

    st.divider()

    # Distribuição por Sexo
    st.markdown(f"<p class='section-title'>👫 Distribuição por Sexo</p>", unsafe_allow_html=True)
    sexo_counts = df_regular["SEXO"].value_counts().reset_index()
    sexo_counts.columns = ["Sexo", "Quantidade"]
    fig_sexo = px.pie(
        sexo_counts,
        values="Quantidade",
        names="Sexo",
        title="Distribuição de Militares por Sexo (TAF Regular)",
        color_discrete_sequence=[theme['accent'], "#ef4444"]
    )
    fig_sexo.update_traces(textposition='inside', textinfo='percent+label')
    fig_sexo.update_layout(
        ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
        height=400,
        margin=dict(t=50, b=20),
        legend=dict(font_color=theme['text_primary'])
    )
    st.plotly_chart(fig_sexo, use_column_width=True)

    st.divider()

    # Distribuição por Faixa Etária
    st.markdown(f"<p class='section-title'>👴 Distribuição por Faixa Etária</p>", unsafe_allow_html=True)
    faixa_etaria_counts = df_regular["FAIXA_ETARIA"].value_counts().reset_index()
    faixa_etaria_counts.columns = ["Faixa Etária", "Quantidade"]

    # Ordenar faixas etárias
    faixa_etaria_order = ["18-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50+", "Não Classificado", "Não Informado"]
    faixa_etaria_counts["_ordem"] = faixa_etaria_counts["Faixa Etária"].apply(lambda x: faixa_etaria_order.index(x) if x in faixa_etaria_order else 99)
    faixa_etaria_counts = faixa_etaria_counts.sort_values("_ordem").drop(columns=["_ordem"])

    fig_idade = px.bar(
        faixa_etaria_counts,
        x="Faixa Etária",
        y="Quantidade",
        title="Distribuição de Militares por Faixa Etária (TAF Regular)",
        color="Quantidade",
        color_continuous_scale=[theme['accent'], "#22c55e"],
        text="Quantidade"
    )
    fig_idade.update_traces(textposition="outside")
    fig_idade.update_layout(
        ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
        height=400,
        xaxis=dict(title="Faixa Etária", **(DARK_PLOTLY_THEME['xaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['xaxis'])),
        yaxis=dict(title="Quantidade", **(DARK_PLOTLY_THEME['yaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['yaxis'])),
        margin=dict(t=50, b=20),
        coloraxis_showscale=False,
        legend=dict(font_color=theme['text_primary'])
    )
    st.plotly_chart(fig_idade, use_column_width=True)

    st.divider()

    # Desempenho por Posto/Graduação
    st.markdown(f"<p class='section-title'>🎖️ Desempenho por Posto/Graduação</p>", unsafe_allow_html=True)
    avg_pontuacao_posto = df_regular.groupby("POSTO_GRAD")["MEDIA_FINAL"].mean().reset_index()
    avg_pontuacao_posto.columns = ["Posto/Graduação", "Média de Pontuação"]

    avg_pontuacao_posto["_ordem"] = avg_pontuacao_posto["Posto/Graduação"].apply(ordem_posto)
    avg_pontuacao_posto = avg_pontuacao_posto.sort_values("_ordem").drop(columns=["_ordem"])

    fig_posto = px.bar(
        avg_pontuacao_posto,
        x="Posto/Graduação",
        y="Média de Pontuação",
        title="Média de Pontuação por Posto/Graduação (TAF Regular)",
        color="Média de Pontuação",
        color_continuous_scale=["#ef4444", "#22c55e"],
        text_auto=".2f"
    )
    fig_posto.update_traces(textposition="outside")
    fig_posto.update_layout(
        ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
        height=400,
        xaxis=dict(title="Posto/Graduação", **(DARK_PLOTLY_THEME['xaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['xaxis']), tickangle=-45),
        yaxis=dict(title="Média de Pontuação", range=[0, 100], **(DARK_PLOTLY_THEME['yaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['yaxis'])),
        margin=dict(t=50, b=20),
        coloraxis_showscale=False,
        legend=dict(font_color=theme['text_primary'])
    )
    st.plotly_chart(fig_posto, use_column_width=True)

    st.divider()

    # Desempenho por Quadro
    st.markdown(f"<p class='section-title'>🗂️ Desempenho por Quadro</p>", unsafe_allow_html=True)
    avg_pontuacao_quadro = df_regular.groupby("QUADRO")["MEDIA_FINAL"].mean().reset_index()
    avg_pontuacao_quadro.columns = ["Quadro", "Média de Pontuação"]

    fig_quadro = px.bar(
        avg_pontuacao_quadro,
        x="Quadro",
        y="Média de Pontuação",
        title="Média de Pontuação por Quadro (TAF Regular)",
        color="Média de Pontuação",
        color_continuous_scale=["#ef4444", "#22c55e"],
        text_auto=".2f"
    )
    fig_quadro.update_traces(textposition="outside")
    fig_quadro.update_layout(
        ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
        height=400,
        xaxis=dict(title="Quadro", **(DARK_PLOTLY_THEME['xaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['xaxis'])),
        yaxis=dict(title="Média de Pontuação", range=[0, 100], **(DARK_PLOTLY_THEME['yaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['yaxis'])),
        margin=dict(t=50, b=20),
        coloraxis_showscale=False,
        legend=dict(font_color=theme['text_primary'])
    )
    st.plotly_chart(fig_quadro, use_column_width=True)

    st.divider()

    # Distribuição de Classificação
    st.markdown(f"<p class='section-title'>🏆 Distribuição de Classificação</p>", unsafe_allow_html=True)
    classificacao_counts = df_regular["CLASSIFICACAO"].value_counts().reset_index()
    classificacao_counts.columns = ["Classificação", "Quantidade"]

    classificacao_order = ["Excelente", "Bom", "Regular", "Insuficiente", "Não Avaliado"]
    classificacao_colors = {
        "Excelente": "#22c55e", "Bom": "#f59e0b", "Regular": "#f97316", "Insuficiente": "#ef4444", "Não Avaliado": "#94a3b8"
    }
    classificacao_counts["_ordem"] = classificacao_counts["Classificação"].apply(lambda x: classificacao_order.index(x) if x in classificacao_order else 99)
    classificacao_counts = classificacao_counts.sort_values("_ordem").drop(columns=["_ordem"])

    fig_classificacao = px.bar(
        classificacao_counts,
        x="Classificação",
        y="Quantidade",
        title="Distribuição de Classificação (TAF Regular)",
        color="Classificação",
        color_discrete_map=classificacao_colors,
        text="Quantidade"
    )
    fig_classificacao.update_traces(textposition="outside")
    fig_classificacao.update_layout(
        ** (DARK_PLOTLY_THEME if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME),
        height=400,
        xaxis=dict(title="Classificação", **(DARK_PLOTLY_THEME['xaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['xaxis'])),
        yaxis=dict(title="Quantidade", **(DARK_PLOTLY_THEME['yaxis'] if st.session_state.tema == "escuro" else LIGHT_PLOTLY_THEME['yaxis'])),
        margin=dict(t=50, b=20),
        legend=dict(font_color=theme['text_primary'])
    )
    st.plotly_chart(fig_classificacao, use_column_width=True)

    st.divider()

    # Estatísticas por Exercício
    st.markdown(f"<p class='section-title'>📈 Estatísticas por Exercício</p>", unsafe_allow_html=True)

    exercicio_selecionado = st.selectbox(
        "Selecione o Exercício para Análise Detalhada:",
        ["Corrida", "Abdominal", "Flexão", "Natação", "Barra"],
        key="exercicio_stats"
    )

    coluna_pontuacao = f"PONTUACAO_{exercicio_selecionado.upper()}"

    if coluna_pontuacao in df_regular.columns:
        fig_dist_exercicio = px.histogram(
            df_regular,
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
        st.plotly_chart(fig_dist_exercicio, use_column_width=True)
    else:
        st.warning(f"Coluna de pontuação '{coluna_pontuacao}' não encontrada.")

    st.divider()

    # Top 10 e Bottom 10
    st.markdown(f"<p class='section-title'>🏅 Melhores e Piores Desempenhos</p>", unsafe_allow_html=True)

    col_top, col_bot = st.columns(2)
    with col_top:
        st.markdown(f"**Top 10 Militares (Média Final)**")
        top10 = df_regular.nlargest(10, "MEDIA_FINAL")[
            ["NOME", "POSTO_GRAD", "QUADRO", "MEDIA_FINAL", "CLASSIFICACAO"]
        ].reset_index(drop=True)
        top10.index += 1
        st.dataframe(top10)
    with col_bot:
        st.markdown(f"**Bottom 10 Militares (Média Final)**")
        bot10 = df_regular.nsmallest(10, "MEDIA_FINAL")[
            ["NOME", "POSTO_GRAD", "QUADRO", "MEDIA_FINAL", "CLASSIFICACAO"]
        ].reset_index(drop=True)
        bot10.index += 1
        st.dataframe(bot10)

    st.divider()

    # Valores brutos — desempenho real
    st.markdown(f"<p class='section-title'>🔢 Desempenho Bruto (Valores Reais)</p>", unsafe_allow_html=True)

    # Filtrar apenas os militares que realmente realizaram todas as provas regulares
    df_presentes_para_stats = df_regular[df_regular[exercicios_regulares].notna().all(axis=1)]

    if not df_presentes_para_stats.empty:
        raw_stats = pd.DataFrame({
            "Exercício": ["Corrida (m)", "Abdominal (reps)", "Flexão (reps)",
                        "Natação (seg)", "Barra (valor)"],
            "Média": [
                df_presentes_para_stats["CORRIDA"].mean(),
                df_presentes_para_stats["ABDOMINAL"].mean(),
                df_presentes_para_stats["FLEXAO"].mean(),
                df_presentes_para_stats["NATACAO"].mean(),
                df_presentes_para_stats["BARRA"].mean(),
            ],
            "Mediana": [
                df_presentes_para_stats["CORRIDA"].median(),
                df_presentes_para_stats["ABDOMINAL"].median(),
                df_presentes_para_stats["FLEXAO"].median(),
                df_presentes_para_stats["NATACAO"].median(),
                df_presentes_para_stats["BARRA"].median(),
            ],
            "Mínimo": [
                df_presentes_para_stats["CORRIDA"].min(),
                df_presentes_para_stats["ABDOMINAL"].min(),
                df_presentes_para_stats["FLEXAO"].min(),
                df_presentes_para_stats["NATACAO"].min(),
                df_presentes_para_stats["BARRA"].min(),
            ],
            "Máximo": [
                df_presentes_para_stats["CORRIDA"].max(),
                df_presentes_para_stats["ABDOMINAL"].max(),
                df_presentes_para_stats["FLEXAO"].max(),
                df_presentes_para_stats["NATACAO"].max(),
                df_presentes_para_stats["BARRA"].max(),
            ],
        }).round(1)
        st.dataframe(raw_stats, hide_index=True)
    else:
        st.info("Não há dados suficientes de militares presentes em todas as provas para exibir estatísticas brutas.")


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: FICHA INDIVIDUAL
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "👤 Ficha Individual":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">👤 Ficha Individual</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Perfil detalhado de desempenho de cada militar
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    militares_nomes = df_regular["NOME"].sort_values().unique()
    militar_selecionado = st.selectbox(
        "Selecione o Militar:",
        militares_nomes,
        index=0 if militares_nomes.size > 0 else None,
        key="militar_ficha_individual"
    )

    if militar_selecionado:
        df_militar = df_regular[df_regular["NOME"] == militar_selecionado].iloc[0]

        st.markdown(f"## {df_militar['POSTO_GRAD']} {df_militar['NOME']}")
        st.markdown(f"**Quadro:** {df_militar['QUADRO']} | **Sexo:** {df_militar['SEXO']} | **Idade:** {int(df_militar['IDADE'])} anos ({df_militar['FAIXA_ETARIA']})")
        st.markdown(f"**Média Final:** <span class='{df_militar['CLASSIFICACAO_BADGE']}'>{df_militar['MEDIA_FINAL']:.2f}</span> | **Classificação:** <span class='{df_militar['CLASSIFICACAO_BADGE']}'>{df_militar['CLASSIFICACAO']}</span>", unsafe_allow_html=True)

        st.divider()

        st.markdown(f"<p class='section-title'>💪 Desempenho nos Exercícios</p>", unsafe_allow_html=True)

        col_ex1, col_ex2, col_ex3, col_ex4, col_ex5 = st.columns(5)
        with col_ex1:
            st.metric("Corrida", f"{df_militar['CORRIDA']:.0f} m" if pd.notna(df_militar['CORRIDA']) else "N/A", delta=f"{df_militar['PONTUACAO_CORRIDA']:.0f} pts")
        with col_ex2:
            st.metric("Abdominal", f"{df_militar['ABDOMINAL']:.0f} reps" if pd.notna(df_militar['ABDOMINAL']) else "N/A", delta=f"{df_militar['PONTUACAO_ABDOMINAL']:.0f} pts")
        with col_ex3:
            st.metric("Flexão", f"{df_militar['FLEXAO']:.0f} reps" if pd.notna(df_militar['FLEXAO']) else "N/A", delta=f"{df_militar['PONTUACAO_FLEXAO']:.0f} pts")
        with col_ex4:
            st.metric("Natação", f"{df_militar['NATACAO']:.0f} seg" if pd.notna(df_militar['NATACAO']) else "N/A", delta=f"{df_militar['PONTUACAO_NATACAO']:.0f} pts")
        with col_ex5:
            if df_militar['SEXO'] == "Masculino":
                st.metric("Barra", f"{df_militar['BARRA']:.0f} reps" if pd.notna(df_militar['BARRA']) else "N/A", delta=f"{df_militar['PONTUACAO_BARRA']:.0f} pts")
            else:
                st.metric("Barra", f"{df_militar['BARRA']:.0f} seg" if pd.notna(df_militar['BARRA']) else "N/A", delta=f"{df_militar['PONTUACAO_BARRA']:.0f} pts")

        st.divider()

        st.markdown(f"<p class='section-title'>📊 Gráficos de Desempenho</p>", unsafe_allow_html=True)
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
        st.plotly_chart(fig_adapt, use_column_width=True)

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
            st.plotly_chart(fig_ex, use_column_width=True)
        else:
            st.info("Nenhum exercício adaptado com dados válidos encontrado.")

        st.info(
            f"ℹ️ O TAF Adaptado avalia militares com necessidades especiais ou "
            f"restrições médicas, utilizando exercícios alternativos conforme "
            f"aptidão individual. Cada militar realiza um conjunto diferente de provas."
        )
