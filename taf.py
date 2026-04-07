
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


# ══════════════════════════════════════════════════════════════════════════════
# IMAGEM CBMAM (extraída de cbmam.html)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def _get_cbmam_image_url() -> str:
    """Extrai a URL da primeira imagem CBMAM encontrada em cbmam.html."""
    html_path = Path("cbmam.html")
    if html_path.exists():
        try:
            content = html_path.read_text(encoding="utf-8", errors="ignore")
            for m in re.findall(r'mediaurl=([^&"\$|+)', content):
                url = unquote(m)
                if re.search(r'\.(png|jpe?g|svg|webp)$', url, re.I):
                    return url
        except Exception:
            pass
    return (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/"
        "Bras%C3%A3o_do_Corpo_de_Bombeiros_Militar_do_Amazonas.svg/"
        "200px-Bras%C3%A3o_do_Corpo_de_Bombeiros_Militar_do_Amazonas.svg.png"
    )


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CBMAM · Dashboard TAF",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0b1220 0%, #0f172a 100%);
    color: #e7eefc;
  }
  [data-testid="stSidebar"] {
    background: #111b2e;
    border-right: 1px solid rgba(255,255,255,.08);
  }
  [data-testid="metric-container"] {
    background: rgba(17,27,46,.8);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 14px;
    padding: 18px 20px;
  }
  .section-title {
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: .5px;
    color: #ef4444;
    margin: 28px 0 8px;
    border-left: 4px solid #ef4444;
    padding-left: 10px;
  }
  footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

DARK = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e7eefc")
GRID = dict(gridcolor="rgba(255,255,255,.06)")

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
    '50-53': {'Corrida': {2000: 10, 1900: 9.5, 1800: 9.0, 1700: 8.5, 1600: 8.0, 1500: 7.5, 1400: 7.0, 1300: 6.5, 1200: 6.0, 1100: 5.5, 1000: 5.0, 900: 4.5, 800: 4.0, 700: 3.5, 600: 3.0, 500: 2.5, 400: 2.0, 300: 1.5, 0: 0}, 'Flexão': {28: 10, 27: 9.5, 26: 9.0, 25: 8.5, 24: 8.0, 23: 7.5, 22: 7.0, 21: 6.5, 20: 6.0, 19: 5.5, 18: 5.0, 17: 4.5, 16: 4.0, 15: 3.5, 14: 3.0, 13: 2.5, 12: 2.0, 11: 1.5, 0: 0}, 'Abdominal': {37: 10, 36: 9.5, 35: 9.0, 34: 8.5, 33: 8.0, 32: 7.5, 31: 7.0, 30: 6.5, 29: 6.0, 28: 5.5, 27: 5.0, 26: 4.5, 25: 4.0, 24: 3.5, 23: 3.0, 22: 2.5, 21: 2.0, 20: 1.5, 0: 0}, 'Barra Dinâmica': {6: 10, 5: 9.5, 4: 9.0, 3: 8.5, 2: 8.0, 1: 7.5, 0: 0}, 'Barra Estática': {45: 10, 43: 9.5, 41: 9.0, 39: 8.5, 37: 8.0, 35: 7.5, 33: 7.0, 31: 6.5, 29: 6.0, 27: 5.5, 25: 5.0, 23: 4.5, 21: 4.0, 19: 3.5, 17: 3.0, 15: 2.5, 13: 2.0, 11: 1.5, 0: 0}, 'Natação': {68: 10, 72: 9.5, 76: 9.0, 80: 8.5, 84: 8.0, 88: 7.5, 92: 7.0, 96: 6.5, 100: 6.0, 104: 5.5, 108: 5.0, 112: 4.5, 116: 4.0, 120: 3.5, 124: 3.0, 128: 2.5, 132: 2.0, 136: 1.5, 999: 0}},
    '54-57': {'Corrida': {1800: 10, 1700: 9.5, 1600: 9.0, 1500: 8.5, 1400: 8.0, 1300: 7.5, 1200: 7.0, 1100: 6.5, 1000: 6.0, 900: 5.5, 800: 5.0, 700: 4.5, 600: 4.0, 500: 3.5, 400: 3.0, 300: 2.5, 200: 2.0, 100: 1.5, 0: 0}, 'Flexão': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0}, 'Abdominal': {35: 10, 34: 9.5, 33: 9.0, 32: 8.5, 31: 8.0, 30: 7.5, 29: 7.0, 28: 6.5, 27: 6.0, 26: 5.5, 25: 5.0, 24: 4.5, 23: 4.0, 22: 3.5, 21: 3.0, 20: 2.5, 19: 2.0, 18: 1.5, 0: 0}, 'Barra Dinâmica': {5: 10, 4: 9.5, 3: 9.0, 2: 8.5, 1: 8.0, 0: 0}, 'Barra Estática': {43: 10, 41: 9.5, 39: 9.0, 37: 8.5, 35: 8.0, 33: 7.5, 31: 7.0, 29: 6.5, 27: 6.0, 25: 5.5, 23: 5.0, 21: 4.5, 19: 4.0, 17: 3.5, 15: 3.0, 13: 2.5, 11: 2.0, 9: 1.5, 0: 0}, 'Natação': {72: 10, 76: 9.5, 80: 9.0, 84: 8.5, 88: 8.0, 92: 7.5, 96: 7.0, 100: 6.5, 104: 6.0, 108: 5.5, 112: 5.0, 116: 4.5, 120: 4.0, 124: 3.5, 128: 3.0, 132: 2.5, 136: 2.0, 140: 1.5, 999: 0}},
    '58+': {'Corrida': {1600: 10, 1500: 9.5, 1400: 9.0, 1300: 8.5, 1200: 8.0, 1100: 7.5, 1000: 7.0, 900: 6.5, 800: 6.0, 700: 5.5, 600: 5.0, 500: 4.5, 400: 4.0, 300: 3.5, 200: 3.0, 100: 2.5, 50: 2.0, 25: 1.5, 0: 0}, 'Flexão': {24: 10, 23: 9.5, 22: 9.0, 21: 8.5, 20: 8.0, 19: 7.5, 18: 7.0, 17: 6.5, 16: 6.0, 15: 5.5, 14: 5.0, 13: 4.5, 12: 4.0, 11: 3.5, 10: 3.0, 9: 2.5, 8: 2.0, 7: 1.5, 0: 0}, 'Abdominal': {33: 10, 32: 9.5, 31: 9.0, 30: 8.5, 29: 8.0, 28: 7.5, 27: 7.0, 26: 6.5, 25: 6.0, 24: 5.5, 23: 5.0, 22: 4.5, 21: 4.0, 20: 3.5, 19: 3.0, 18: 2.5, 17: 2.0, 16: 1.5, 0: 0}, 'Barra Dinâmica': {4: 10, 3: 9.5, 2: 9.0, 1: 8.5, 0: 0}, 'Barra Estática': {41: 10, 39: 9.5, 37: 9.0, 35: 8.5, 33: 8.0, 31: 7.5, 29: 7.0, 27: 6.5, 25: 6.0, 23: 5.5, 21: 5.0, 19: 4.5, 17: 4.0, 15: 3.5, 13: 3.0, 11: 2.5, 9: 2.0, 7: 1.5, 0: 0}, 'Natação': {76: 10, 80: 9.5, 84: 9.0, 88: 8.5, 92: 8.0, 96: 7.5, 100: 7.0, 104: 6.5, 108: 6.0, 112: 5.5, 116: 5.0, 120: 4.5, 124: 4.0, 128: 3.5, 132: 3.0, 136: 2.5, 140: 2.0, 144: 1.5, 999: 0}}
}

# ══════════════════════════════════════════════════════════════════════════════
# REGRAS DE PONTUAÇÃO - FEMININO (10 FAIXAS ETÁRIAS)
# ══════════════════════════════════════════════════════════════════════════════
REGRAS_FEMININO = {
    '18-21': {'Corrida': {2800: 10, 2700: 9.5, 2600: 9.0, 2500: 8.5, 2400: 8.0, 2300: 7.5, 2200: 7.0, 2100: 6.5, 2000: 6.0, 1900: 5.5, 1800: 5.0, 1700: 4.5, 1600: 4.0, 1500: 3.5, 1400: 3.0, 1300: 2.5, 1200: 2.0, 1100: 1.5, 0: 0}, 'Flexão': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5, 22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5, 14: 2.0, 13: 1.5, 0: 0}, 'Abdominal': {40: 10, 39: 9.5, 38: 9.0, 37: 8.5, 36: 8.0, 35: 7.5, 34: 7.0, 33: 6.5, 32: 6.0, 31: 5.5, 30: 5.0, 29: 4.5, 28: 4.0, 27: 3.5, 26: 3.0, 25: 2.5, 24: 2.0, 23: 1.5, 0: 0}, 'Barra Dinâmica': {8: 10, 7: 9.5, 6: 9.0, 5: 8.5, 4: 8.0, 3: 7.5, 2: 7.0, 1: 6.5, 0: 0}, 'Barra Estática': {50: 10, 48: 9.5, 46: 9.0, 44: 8.5, 42: 8.0, 40: 7.5, 38: 7.0, 36: 6.5, 34: 6.0, 32: 5.5, 30: 5.0, 28: 4.5, 26: 4.0, 24: 3.5, 22: 3.0, 20: 2.5, 18: 2.0, 16: 1.5, 0: 0}, 'Natação': {45: 10, 50: 9.5, 55: 9.0, 60: 8.5, 65: 8.0, 70: 7.5, 75: 7.0, 80: 6.5, 85: 6.0, 90: 5.5, 95: 5.0, 100: 4.5, 105: 4.0, 110: 3.5, 115: 3.0, 120: 2.5, 125: 2.0, 130: 1.5, 999: 0}},
    '22-25': {'Corrida': {2600: 10, 2500: 9.5, 2400: 9.0, 2300: 8.5, 2200: 8.0, 2100: 7.5, 2000: 7.0, 1900: 6.5, 1800: 6.0, 1700: 5.5, 1600: 5.0, 1500: 4.5, 1400: 4.0, 1300: 3.5, 1200: 3.0, 1100: 2.5, 1000: 2.0, 900: 1.5, 0: 0}, 'Flexão': {28: 10, 27: 9.5, 26: 9.0, 25: 8.5, 24: 8.0, 23: 7.5, 22: 7.0, 21: 6.5, 20: 6.0, 19: 5.5, 18: 5.0, 17: 4.5, 16: 4.0, 15: 3.5, 14: 3.0, 13: 2.5, 12: 2.0, 11: 1.5, 0: 0}, 'Abdominal': {37: 10, 36: 9.5, 35: 9.0, 34: 8.5, 33: 8.0, 32: 7.5, 31: 7.0, 30: 6.5, 29: 6.0, 28: 5.5, 27: 5.0, 26: 4.5, 25: 4.0, 24: 3.5, 23: 3.0, 22: 2.5, 21: 2.0, 20: 1.5, 0: 0}, 'Barra Dinâmica': {7: 10, 6: 9.5, 5: 9.0, 4: 8.5, 3: 8.0, 2: 7.5, 1: 7.0, 0: 0}, 'Barra Estática': {48: 10, 46: 9.5, 44: 9.0, 42: 8.5, 40: 8.0, 38: 7.5, 36: 7.0, 34: 6.5, 32: 6.0, 30: 5.5, 28: 5.0, 26: 4.5, 24: 4.0, 22: 3.5, 20: 3.0, 18: 2.5, 16: 2.0, 14: 1.5, 0: 0}, 'Natação': {47: 10, 52: 9.5, 57: 9.0, 62: 8.5, 67: 8.0, 72: 7.5, 77: 7.0, 82: 6.5, 87: 6.0, 92: 5.5, 97: 5.0, 102: 4.5, 107: 4.0, 112: 3.5, 117: 3.0, 122: 2.5, 127: 2.0, 132: 1.5, 999: 0}},
    '26-29': {'Corrida': {2400: 10, 2300: 9.5, 2200: 9.0, 2100: 8.5, 2000: 8.0, 1900: 7.5, 1800: 7.0, 1700: 6.5, 1600: 6.0, 1500: 5.5, 1400: 5.0, 1300: 4.5, 1200: 4.0, 1100: 3.5, 1000: 3.0, 900: 2.5, 800: 2.0, 700: 1.5, 0: 0}, 'Flexão': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0}, 'Abdominal': {34: 10, 33: 9.5, 32: 9.0, 31: 8.5, 30: 8.0, 29: 7.5, 28: 7.0, 27: 6.5, 26: 6.0, 25: 5.5, 24: 5.0, 23: 4.5, 22: 4.0, 21: 3.5, 20: 3.0, 19: 2.5, 18: 2.0, 17: 1.5, 0: 0}, 'Barra Dinâmica': {6: 10, 5: 9.5, 4: 9.0, 3: 8.5, 2: 8.0, 1: 7.5, 0: 0}, 'Barra Estática': {46: 10, 44: 9.5, 42: 9.0, 40: 8.5, 38: 8.0, 36: 7.5, 34: 7.0, 32: 6.5, 30: 6.0, 28: 5.5, 26: 5.0, 24: 4.5, 22: 4.0, 20: 3.5, 18: 3.0, 16: 2.5, 14: 2.0, 12: 1.5, 0: 0}, 'Natação': {49: 10, 54: 9.5, 59: 9.0, 64: 8.5, 69: 8.0, 74: 7.5, 79: 7.0, 84: 6.5, 89: 6.0, 94: 5.5, 99: 5.0, 104: 4.5, 109: 4.0, 114: 3.5, 119: 3.0, 124: 2.5, 129: 2.0, 134: 1.5, 999: 0}},
    '30-34': {'Corrida': {2200: 10, 2100: 9.5, 2000: 9.0, 1900: 8.5, 1800: 8.0, 1700: 7.5, 1600: 7.0, 1500: 6.5, 1400: 6.0, 1300: 5.5, 1200: 5.0, 1100: 4.5, 1000: 4.0, 900: 3.5, 800: 3.0, 700: 2.5, 600: 2.0, 500: 1.5, 0: 0}, 'Flexão': {24: 10, 23: 9.5, 22: 9.0, 21: 8.5, 20: 8.0, 19: 7.5, 18: 7.0, 17: 6.5, 16: 6.0, 15: 5.5, 14: 5.0, 13: 4.5, 12: 4.0, 11: 3.5, 10: 3.0, 9: 2.5, 8: 2.0, 7: 1.5, 0: 0}, 'Abdominal': {32: 10, 31: 9.5, 30: 9.0, 29: 8.5, 28: 8.0, 27: 7.5, 26: 7.0, 25: 6.5, 24: 6.0, 23: 5.5, 22: 5.0, 21: 4.5, 20: 4.0, 19: 3.5, 18: 3.0, 17: 2.5, 16: 2.0, 15: 1.5, 0: 0}, 'Barra Dinâmica': {5: 10, 4: 9.5, 3: 9.0, 2: 8.5, 1: 8.0, 0: 0}, 'Barra Estática': {44: 10, 42: 9.5, 40: 9.0, 38: 8.5, 36: 8.0, 34: 7.5, 32: 7.0, 30: 6.5, 28: 6.0, 26: 5.5, 24: 5.0, 22: 4.5, 20: 4.0, 18: 3.5, 16: 3.0, 14: 2.5, 12: 2.0, 10: 1.5, 0: 0}, 'Natação': {51: 10, 56: 9.5, 61: 9.0, 66: 8.5, 71: 8.0, 76: 7.5, 81: 7.0, 86: 6.5, 91: 6.0, 96: 5.5, 101: 5.0, 106: 4.5, 111: 4.0, 116: 3.5, 121: 3.0, 126: 2.5, 131: 2.0, 136: 1.5, 999: 0}},
    '35-39': {'Corrida': {2000: 10, 1900: 9.5, 1800: 9.0, 1700: 8.5, 1600: 8.0, 1500: 7.5, 1400: 7.0, 1300: 6.5, 1200: 6.0, 1100: 5.5, 1000: 5.0, 900: 4.5, 800: 4.0, 700: 3.5, 600: 3.0, 500: 2.5, 400: 2.0, 300: 1.5, 0: 0}, 'Flexão': {22: 10, 21: 9.5, 20: 9.0, 19: 8.5, 18: 8.0, 17: 7.5, 16: 7.0, 15: 6.5, 14: 6.0, 13: 5.5, 12: 5.0, 11: 4.5, 10: 4.0, 9: 3.5, 8: 3.0, 7: 2.5, 6: 2.0, 5: 1.5, 0: 0}, 'Abdominal': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5, 22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5, 14: 2.0, 13: 1.5, 0: 0}, 'Barra Dinâmica': {4: 10, 3: 9.5, 2: 9.0, 1: 8.5, 0: 0}, 'Barra Estática': {42: 10, 40: 9.5, 38: 9.0, 36: 8.5, 34: 8.0, 32: 7.5, 30: 7.0, 28: 6.5, 26: 6.0, 24: 5.5, 22: 5.0, 20: 4.5, 18: 4.0, 16: 3.5, 14: 3.0, 12: 2.5, 10: 2.0, 8: 1.5, 0: 0}, 'Natação': {53: 10, 58: 9.5, 63: 9.0, 68: 8.5, 73: 8.0, 78: 7.5, 83: 7.0, 88: 6.5, 93: 6.0, 98: 5.5, 103: 5.0, 108: 4.5, 113: 4.0, 118: 3.5, 123: 3.0, 128: 2.5, 133: 2.0, 138: 1.5, 999: 0}},
    '40-44': {'Corrida': {1800: 10, 1700: 9.5, 1600: 9.0, 1500: 8.5, 1400: 8.0, 1300: 7.5, 1200: 7.0, 1100: 6.5, 1000: 6.0, 900: 5.5, 800: 5.0, 700: 4.5, 600: 4.0, 500: 3.5, 400: 3.0, 300: 2.5, 200: 2.0, 100: 1.5, 0: 0}, 'Flexão': {20: 10, 19: 9.5, 18: 9.0, 17: 8.5, 16: 8.0, 15: 7.5, 14: 7.0, 13: 6.5, 12: 6.0, 11: 5.5, 10: 5.0, 9: 4.5, 8: 4.0, 7: 3.5, 6: 3.0, 5: 2.5, 4: 2.0, 3: 1.5, 0: 0}, 'Abdominal': {28: 10, 27: 9.5, 26: 9.0, 25: 8.5, 24: 8.0, 23: 7.5, 22: 7.0, 21: 6.5, 20: 6.0, 19: 5.5, 18: 5.0, 17: 4.5, 16: 4.0, 15: 3.5, 14: 3.0, 13: 2.5, 12: 2.0, 11: 1.5, 0: 0}, 'Barra Dinâmica': {3: 10, 2: 9.5, 1: 9.0, 0: 0}, 'Barra Estática': {40: 10, 38: 9.5, 36: 9.0, 34: 8.5, 32: 8.0, 30: 7.5, 28: 7.0, 26: 6.5, 24: 6.0, 22: 5.5, 20: 5.0, 18: 4.5, 16: 4.0, 14: 3.5, 12: 3.0, 10: 2.5, 8: 2.0, 6: 1.5, 0: 0}, 'Natação': {55: 10, 60: 9.5, 65: 9.0, 70: 8.5, 75: 8.0, 80: 7.5, 85: 7.0, 90: 6.5, 95: 6.0, 100: 5.5, 105: 5.0, 110: 4.5, 115: 4.0, 120: 3.5, 125: 3.0, 130: 2.5, 135: 2.0, 140: 1.5, 999: 0}},
    '45-49': {'Corrida': {1600: 10, 1500: 9.5, 1400: 9.0, 1300: 8.5, 1200: 8.0, 1100: 7.5, 1000: 7.0, 900: 6.5, 800: 6.0, 700: 5.5, 600: 5.0, 500: 4.5, 400: 4.0, 300: 3.5, 200: 3.0, 100: 2.5, 50: 2.0, 25: 1.5, 0: 0}, 'Flexão': {18: 10, 17: 9.5, 16: 9.0, 15: 8.5, 14: 8.0, 13: 7.5, 12: 7.0, 11: 6.5, 10: 6.0, 9: 5.5, 8: 5.0, 7: 4.5, 6: 4.0, 5: 3.5, 4: 3.0, 3: 2.5, 2: 2.0, 1: 1.5, 0: 0}, 'Abdominal': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0}, 'Barra Dinâmica': {2: 10, 1: 9.5, 0: 0}, 'Barra Estática': {38: 10, 36: 9.5, 34: 9.0, 32: 8.5, 30: 8.0, 28: 7.5, 26: 7.0, 24: 6.5, 22: 6.0, 20: 5.5, 18: 5.0, 16: 4.5, 14: 4.0, 12: 3.5, 10: 3.0, 8: 2.5, 6: 2.0, 4: 1.5, 0: 0}, 'Natação': {57: 10, 62: 9.5, 67: 9.0, 72: 8.5, 77: 8.0, 82: 7.5, 87: 7.0, 92: 6.5, 97: 6.0, 102: 5.5, 107: 5.0, 112: 4.5, 117: 4.0, 122: 3.5, 127: 3.0, 132: 2.5, 137: 2.0, 142: 1.5, 999: 0}},
    '50-53': {'Corrida': {1400: 10, 1300: 9.5, 1200: 9.0, 1100: 8.5, 1000: 8.0, 900: 7.5, 800: 7.0, 700: 6.5, 600: 6.0, 500: 5.5, 400: 5.0, 300: 4.5, 200: 4.0, 100: 3.5, 50: 3.0, 25: 2.5, 10: 2.0, 5: 1.5, 0: 0}, 'Flexão': {16: 10, 15: 9.5, 14: 9.0, 13: 8.5, 12: 8.0, 11: 7.5, 10: 7.0, 9: 6.5, 8: 6.0, 7: 5.5, 6: 5.0, 5: 4.5, 4: 4.0, 3: 3.5, 2: 3.0, 1: 2.5, 0: 0}, 'Abdominal': {24: 10, 23: 9.5, 22: 9.0, 21: 8.5, 20: 8.0, 19: 7.5, 18: 7.0, 17: 6.5, 16: 6.0, 15: 5.5, 14: 5.0, 13: 4.5, 12: 4.0, 11: 3.5, 10: 3.0, 9: 2.5, 8: 2.0, 7: 1.5, 0: 0}, 'Barra Dinâmica': {1: 10, 0: 0}, 'Barra Estática': {36: 10, 34: 9.5, 32: 9.0, 30: 8.5, 28: 8.0, 26: 7.5, 24: 7.0, 22: 6.5, 20: 6.0, 18: 5.5, 16: 5.0, 14: 4.5, 12: 4.0, 10: 3.5, 8: 3.0, 6: 2.5, 4: 2.0, 2: 1.5, 0: 0}, 'Natação': {59: 10, 64: 9.5, 69: 9.0, 74: 8.5, 79: 8.0, 84: 7.5, 89: 7.0, 94: 6.5, 99: 6.0, 104: 5.5, 109: 5.0, 114: 4.5, 119: 4.0, 124: 3.5, 129: 3.0, 134: 2.5, 139: 2.0, 144: 1.5, 999: 0}},
    '54-57': {'Corrida': {1200: 10, 1100: 9.5, 1000: 9.0, 900: 8.5, 800: 8.0, 700: 7.5, 600: 7.0, 500: 6.5, 400: 6.0, 300: 5.5, 200: 5.0, 100: 4.5, 50: 4.0, 25: 3.5, 10: 3.0, 5: 2.5, 0: 0}, 'Flexão': {14: 10, 13: 9.5, 12: 9.0, 11: 8.5, 10: 8.0, 9: 7.5, 8: 7.0, 7: 6.5, 6: 6.0, 5: 5.5, 4: 5.0, 3: 4.5, 2: 4.0, 1: 3.5, 0: 0}, 'Abdominal': {22: 10, 21: 9.5, 20: 9.0, 19: 8.5, 18: 8.0, 17: 7.5, 16: 7.0, 15: 6.5, 14: 6.0, 13: 5.5, 12: 5.0, 11: 4.5, 10: 4.0, 9: 3.5, 8: 3.0, 7: 2.5, 6: 2.0, 5: 1.5, 0: 0}, 'Barra Dinâmica': {0: 10}, 'Barra Estática': {34: 10, 32: 9.5, 30: 9.0, 28: 8.5, 26: 8.0, 24: 7.5, 22: 7.0, 20: 6.5, 18: 6.0, 16: 5.5, 14: 5.0, 12: 4.5, 10: 4.0, 8: 3.5, 6: 3.0, 4: 2.5, 2: 2.0, 0: 0}, 'Natação': {61: 10, 66: 9.5, 71: 9.0, 76: 8.5, 81: 8.0, 86: 7.5, 91: 7.0, 96: 6.5, 101: 6.0, 106: 5.5, 111: 5.0, 116: 4.5, 121: 4.0, 126: 3.5, 131: 3.0, 136: 2.5, 141: 2.0, 146: 1.5, 999: 0}},
    '58+': {'Corrida': {1000: 10, 900: 9.5, 800: 9.0, 700: 8.5, 600: 8.0, 500: 7.5, 400: 7.0, 300: 6.5, 200: 6.0, 100: 5.5, 50: 5.0, 25: 4.5, 10: 4.0, 5: 3.5, 0: 0}, 'Flexão': {12: 10, 11: 9.5, 10: 9.0, 9: 8.5, 8: 8.0, 7: 7.5, 6: 7.0, 5: 6.5, 4: 6.0, 3: 5.5, 2: 5.0, 1: 4.5, 0: 0}, 'Abdominal': {20: 10, 19: 9.5, 18: 9.0, 17: 8.5, 16: 8.0, 15: 7.5, 14: 7.0, 13: 6.5, 12: 6.0, 11: 5.5, 10: 5.0, 9: 4.5, 8: 4.0, 7: 3.5, 6: 3.0, 5: 2.5, 4: 2.0, 3: 1.5, 0: 0}, 'Barra Dinâmica': {0: 10}, 'Barra Estática': {32: 10, 30: 9.5, 28: 9.0, 26: 8.5, 24: 8.0, 22: 7.5, 20: 7.0, 18: 6.5, 16: 6.0, 14: 5.5, 12: 5.0, 10: 4.5, 8: 4.0, 6: 3.5, 4: 3.0, 2: 2.5, 0: 0}, 'Natação': {63: 10, 68: 9.5, 73: 9.0, 78: 8.5, 83: 8.0, 88: 7.5, 93: 7.0, 98: 6.5, 103: 6.0, 108: 5.5, 113: 5.0, 118: 4.5, 123: 4.0, 128: 3.5, 133: 3.0, 138: 2.5, 143: 2.0, 148: 1.5, 999: 0}}
}


# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════

def remover_acentos(texto):
    """Remove acentos de uma string."""
    if pd.isna(texto):
        return ''
    texto_norm = unicodedata.normalize('NFKD', str(texto))
    return ''.join([c for c in texto_norm if not unicodedata.combining(c)]).upper().strip()


def calcular_idade(data_nascimento):
    """Calcula idade a partir da data de nascimento."""
    try:
        if pd.isna(data_nascimento):
            return None
        if isinstance(data_nascimento, str):
            data = pd.to_datetime(data_nascimento, format='%d/%m/%Y', errors='coerce')
        else:
            data = pd.to_datetime(data_nascimento, errors='coerce')
        if pd.isna(data):
            return None
        hoje = datetime.now()
        return hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))
    except:
        return None


def obter_faixa_etaria(idade):
    """Retorna faixa etária baseada na idade."""
    if idade is None:
        return None
    if idade <= 21:
        return '18-21'
    elif idade <= 25:
        return '22-25'
    elif idade <= 29:
        return '26-29'
    elif idade <= 34:
        return '30-34'
    elif idade <= 39:
        return '35-39'
    elif idade <= 44:
        return '40-44'
    elif idade <= 49:
        return '45-49'
    elif idade <= 53:
        return '50-53'
    elif idade <= 57:
        return '54-57'
    else:
        return '58+'


def obter_nota_por_regra(exercicio, valor, idade, sexo):
    """Obtém a nota de um exercício baseado na idade e sexo."""
    if pd.isna(valor):
        return np.nan
    
    idade_int = int(idade) if pd.notna(idade) else None
    if idade_int is None:
        return np.nan
    
    faixa = obter_faixa_etaria(idade_int)
    if faixa is None:
        return np.nan
    
    # Garantir que sexo é string válido
    sexo_str = str(sexo).strip().upper() if pd.notna(sexo) else 'M'
    sexo_str = sexo_str[0] if sexo_str else 'M'
    
    regras = REGRAS_MASCULINO if sexo_str == 'M' else REGRAS_FEMININO
    
    if faixa not in regras or exercicio not in regras[faixa]:
        return np.nan
    
    tabela = regras[faixa][exercicio]
    
    # Converter valor para número
    try:
        valor_int = int(float(valor))
    except:
        return np.nan
    
    # Lógica diferente para Corrida e Natação (tempos - menor é melhor)
    # vs Flexão, Abdominal, Barra (contagens/reps - maior é melhor)
    if exercicio in ['Corrida', 'Natação']:
        # Para tempos: encontrar o maior threshold que é MENOR OU IGUAL ao valor
        # Exemplo: se 45s e tabela tem 56:10, 60:9.5, 45 < 56 então pega 10
        thresholds = sorted(tabela.keys())
        resultado_nota = 0  # Padrão se não encontrar
        for threshold in thresholds:
            if valor_int <= threshold:
                resultado_nota = tabela[threshold]
                break
        # Se valor é menor que o menor threshold, retorna a melhor nota
        if valor_int < thresholds[0]:
            resultado_nota = tabela[thresholds[0]]
        return resultado_nota
    else:
        # Para contagens: encontrar o maior threshold que é MAIOR OU IGUAL ao valor
        for threshold in sorted(tabela.keys(), reverse=True):
            if valor_int >= threshold:
                return tabela[threshold]
        return 0

def parse_time(val):
    """Converte formatos de tempo como 01'04", 47", 1'09" para segundos."""
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if any(x in s.upper() for x in ["NÃO", "COMPARECEU", "APTO"]):
        return np.nan
    s = s.replace('"', "'").replace("''", "'").strip("'").strip()
    m = re.match(r"^0*(\d+)'(\d+)$", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    m = re.match(r"^(\d+)$", s)
    if m:
        return int(m.group(1))
    return np.nan


def classificar_barra_tipo(val_raw):
    """Classifica se o valor da barra é dinâmica (reps) ou estática (tempo)."""
    if pd.isna(val_raw):
        return None
    s = str(val_raw).strip()
    if any(x in s.upper() for x in ["NÃO", "COMPARECEU"]):
        return None
    if "'" in s or '"' in s:
        return "ESTATICA"
    try:
        float(s)
        return "DINAMICA"
    except ValueError:
        return None


# ── Tabelas de Pontuação TAF ────────────────────────────────────────────────

def nota_corrida(metros):
    if pd.isna(metros): return np.nan
    m = float(metros)
    if m > 5000: m = m / 10
    if m >= 2800: return 10.0
    if m >= 2600: return 9.0
    if m >= 2400: return 8.0
    if m >= 2200: return 7.0
    if m >= 2000: return 6.0
    if m >= 1800: return 5.0
    return 4.0


def nota_abdominal(reps):
    if pd.isna(reps): return np.nan
    r = float(reps)
    if r >= 48: return 10.0
    if r >= 42: return 9.0
    if r >= 38: return 8.0
    if r >= 33: return 7.0
    if r >= 28: return 6.0
    if r >= 22: return 5.0
    return 4.0


def nota_flexao(reps):
    if pd.isna(reps): return np.nan
    r = float(reps)
    if r >= 38: return 10.0
    if r >= 33: return 9.0
    if r >= 28: return 8.0
    if r >= 23: return 7.0
    if r >= 18: return 6.0
    if r >= 13: return 5.0
    return 4.0


def nota_natacao(segs):
    if pd.isna(segs): return np.nan
    s = float(segs)
    if s <= 35: return 10.0
    if s <= 40: return 9.0
    if s <= 45: return 8.0
    if s <= 50: return 7.0
    if s <= 55: return 6.0
    if s <= 60: return 5.0
    if s <= 70: return 4.0
    return 3.0


def nota_barra_din(reps):
    if pd.isna(reps): return np.nan
    r = float(reps)
    if r >= 14: return 10.0
    if r >= 12: return 9.0
    if r >= 10: return 8.0
    if r >= 8: return 7.0
    if r >= 6: return 6.0
    if r >= 4: return 5.0
    return 4.0


def nota_barra_est(segs):
    if pd.isna(segs): return np.nan
    s = float(segs)
    if s >= 70: return 10.0
    if s >= 60: return 9.0
    if s >= 50: return 8.0
    if s >= 40: return 7.0
    if s >= 30: return 6.0
    if s >= 20: return 5.0
    return 4.0


def classificar_media(m):
    if pd.isna(m): return "Ausente"
    if m >= 9.0: return "Excelente"
    if m >= 7.5: return "Bom"
    if m >= 6.0: return "Regular"
    return "Insuficiente"


def normalizar_posto(p):
    """Normaliza variações de posto/graduação (º vs °)."""
    s = str(p).strip().upper()
    s = s.replace("º", "°")
    return s


def ordem_posto(p):
    return ORDEM_POSTO.get(p, 99)


# ══════════════════════════════════════════════════════════════════════════════
# CARREGAMENTO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def carregar_dados():
    """Carrega e processa o TAF.csv — seção Regular (TAF completo)."""
    df_raw = pd.read_csv("TAF.csv", header=None, encoding="utf-8-sig", dtype=str)

    # Encontrar marcadores de seção
    headers = []
    adapted_marker = None
    for i in range(len(df_raw)):
        cell = str(df_raw.iloc[i, 0]).strip()
        if cell == "ORD":
            headers.append(i)
        if "TAF ADAPTADO" in cell:
            adapted_marker = i

    # Seções regulares: antes do TAF ADAPTADO
    regular_headers = [h for h in headers if adapted_marker is None or h < adapted_marker]

    sections = []
    for idx, h in enumerate(regular_headers):
        if idx + 1 < len(regular_headers):
            end = regular_headers[idx + 1] - 3
        elif adapted_marker:
            end = adapted_marker
        else:
            end = len(df_raw)

        section = df_raw.iloc[h + 1:end].copy()
        section = section[section.iloc[:, 0].notna()]
        section = section[~section.iloc[:, 0].astype(str).str.strip().isin(["", "nan"])]
        section = section[~section.iloc[:, 0].astype(str).str.contains(
            r"TAF|FALTOU|MILITARES|^B$|^A$|DESEMPENHO", case=False, na=False
        )]
        section = section[pd.to_numeric(section.iloc[:, 0], errors="coerce").notna()]
        sections.append(section)

    df = pd.concat(sections, ignore_index=True)
    df = df.iloc[:, :9]
    df.columns = ["ORD", "POSTO_GRAD", "QUADRO", "NOME",
                  "CORRIDA_RAW", "ABDOMINAL_RAW", "FLEXAO_RAW",
                  "NATACAO_RAW", "BARRA_RAW"]

    # Limpar strings
    df["NOME"] = df["NOME"].astype(str).str.strip().str.upper()
    df["POSTO_GRAD"] = df["POSTO_GRAD"].astype(str).apply(normalizar_posto)
    df["QUADRO"] = df["QUADRO"].astype(str).str.strip().str.upper()
    df["ORD"] = pd.to_numeric(df["ORD"], errors="coerce").astype("Int64")

    # Marcar presentes/ausentes
    df["PRESENTE"] = ~df["CORRIDA_RAW"].astype(str).str.upper().str.contains(
        "NÃO COMPARECEU", na=False
    )

    # Parsear valores brutos
    # Corrida: pode ser metros (2400) ou tempo (24'51") - priorizar metros
    def processar_corrida(val_raw):
        """Processa valor de corrida - pode ser metros ou tempo."""
        if pd.isna(val_raw) or str(val_raw).strip().upper() in ['NÃO COMPARECEU', 'NÃO CONSTA', 'NÃO']:
            return np.nan
        s = str(val_raw).strip()
        
        # Se tem apóstrofo, é tempo em minutos'segundos - converter para metros (aproximado)
        if "'" in s or '"' in s:
            tempo_seg = parse_time(s)
            if not pd.isna(tempo_seg) and tempo_seg > 0:
                # Estimar metros a partir do tempo (aproximadamente 12min = 3000m)
                # Relação: tempo(seg) -> metros
                # 12min=720seg -> 3000m: metros= 3000 * (720/tempo)
                metros_estimado = int(3000 * 720 / tempo_seg)
                return metros_estimado
        
        # Tentar conversão direta para número
        try:
            val_num = float(s.replace(',', '.'))
            # Se entre 1500 e 5000, é metro
            if 1500 <= val_num <= 5000:
                return val_num
            # Se maior que 5000, pode ser erro (ex: 25000) - ignorar
            if val_num > 5000:
                return np.nan
            # Senão é válido
            return val_num
        except:
            return np.nan
    
    df["CORRIDA"] = df["CORRIDA_RAW"].apply(processar_corrida)
    df["ABDOMINAL"] = pd.to_numeric(
        df["ABDOMINAL_RAW"].astype(str).str.replace(",", ".", regex=False).str.strip(),
        errors="coerce"
    )
    df["FLEXAO"] = pd.to_numeric(
        df["FLEXAO_RAW"].astype(str).str.replace(",", ".", regex=False).str.strip(),
        errors="coerce"
    )
    df["NATACAO_SEG"] = df["NATACAO_RAW"].apply(parse_time)
    df["BARRA_TIPO"] = df["BARRA_RAW"].apply(classificar_barra_tipo)
    df["BARRA_VALOR"] = df["BARRA_RAW"].apply(parse_time)

    # CARREGA DADOS DE MILITARES (DATA NASCIMENTO E SEXO)
    militares_dict = {}
    arquivo_militares = None
    
    # Tentar múltiplos caminhos possíveis
    caminhos_possiveis = [
        "militaresALL.csv",           # Mesmo diretório de taf.py
        "../data/militaresALL.csv",   # Subdiretório data (um nível acima)
        "data/militaresALL.csv",      # Subdiretório data (mesmo nível)
    ]
    
    for caminho in caminhos_possiveis:
        try:
            df_militares = pd.read_csv(caminho, encoding="utf-8-sig", dtype=str)
            arquivo_militares = caminho
            
            # Mapear colunas corretamente - militaresALL.csv tem estrutura:
            # [0]: Nome Completo, [4]: Sexo, [18]: Data de Nascimento
            for _, row in df_militares.iterrows():
                nome_norm = remover_acentos(str(row.iloc[0]).upper()) if pd.notna(row.iloc[0]) else ""
                if nome_norm:
                    # Extrair primeira letra do sexo (M/F) com padrão 'M'
                    sexo = str(row.iloc[4]).strip().upper()[0] if pd.notna(row.iloc[4]) else 'M'
                    data_nasc = str(row.iloc[18]).strip() if pd.notna(row.iloc[18]) else None
                    
                    militares_dict[nome_norm] = {
                        'DATA_NASC': data_nasc,
                        'SEXO': sexo
                    }
            break  # Se conseguiu carregar, sai do loop
        except Exception:
            continue

    def buscar_militares(nome):
        nome_norm = remover_acentos(str(nome).upper())
        return militares_dict.get(nome_norm, {'DATA_NASC': None, 'SEXO': 'M'})

    militares_info = df["NOME"].apply(buscar_militares)
    df["DATA_NASC"] = militares_info.apply(lambda x: x['DATA_NASC'])
    df["SEXO"] = militares_info.apply(lambda x: x['SEXO'])
    df["IDADE"] = df["DATA_NASC"].apply(calcular_idade)
    df["FAIXA_ETARIA"] = df["IDADE"].apply(obter_faixa_etaria)

    # Calcular notas
    df["NOTA_CORRIDA"] = df.apply(lambda row: obter_nota_por_regra("Corrida", row["CORRIDA"], row["IDADE"], row["SEXO"]), axis=1)
    df["NOTA_ABDOMINAL"] = df.apply(lambda row: obter_nota_por_regra("Abdominal", row["ABDOMINAL"], row["IDADE"], row["SEXO"]), axis=1)
    df["NOTA_FLEXAO"] = df.apply(lambda row: obter_nota_por_regra("Flexão", row["FLEXAO"], row["IDADE"], row["SEXO"]), axis=1)
    df["NOTA_NATACAO"] = df.apply(lambda row: obter_nota_por_regra("Natação", row["NATACAO_SEG"], row["IDADE"], row["SEXO"]), axis=1)
    df["NOTA_BARRA"] = df.apply(lambda row: obter_nota_por_regra("Barra Dinâmica", row["BARRA_VALOR"], row["IDADE"], row["SEXO"]), axis=1)

    # Média final
    nota_cols = ["NOTA_CORRIDA", "NOTA_ABDOMINAL", "NOTA_FLEXAO", "NOTA_NATACAO", "NOTA_BARRA"]
    df["MEDIA_FINAL"] = df[nota_cols].mean(axis=1)
    df["CLASSIFICACAO"] = df["MEDIA_FINAL"].apply(classificar_media)

    # Ponto fraco e forte
    notas_map = {
        "Corrida 12min": "NOTA_CORRIDA",
        "Abdominal": "NOTA_ABDOMINAL",
        "Flexão": "NOTA_FLEXAO",
        "Natação 50m": "NOTA_NATACAO",
        "Barra": "NOTA_BARRA",
    }

    def ponto_fraco(row):
        vals = {k: float(row[v]) for k, v in notas_map.items() if pd.notna(row[v])}
        return min(vals, key=vals.get) if vals else "—"

    def ponto_forte(row):
        vals = {k: float(row[v]) for k, v in notas_map.items() if pd.notna(row[v])}
        return max(vals, key=vals.get) if vals else "—"

    df["PONTO_FRACO"] = df.apply(ponto_fraco, axis=1)
    df["PONTO_FORTE"] = df.apply(ponto_forte, axis=1)

    return df, notas_map


@st.cache_data
def carregar_adaptado():
    """Carrega e processa o TAF.csv — seção TAF Adaptado."""
    df_raw = pd.read_csv("TAF.csv", header=None, encoding="utf-8-sig", dtype=str)

    adapted_marker = None
    adapted_header = None
    for i in range(len(df_raw)):
        cell = str(df_raw.iloc[i, 0]).strip()
        if "TAF ADAPTADO" in cell:
            adapted_marker = i
        if cell == "ORD" and adapted_marker is not None:
            adapted_header = i
            break

    if adapted_header is None:
        return pd.DataFrame()

    df = df_raw.iloc[adapted_header + 1:].copy()
    df = df[df.iloc[:, 0].notna()]
    df = df[pd.to_numeric(df.iloc[:, 0], errors="coerce").notna()]

    cols = ["ORD", "POSTO_GRAD", "QUADRO", "NOME", "CAMINHADA", "ABDOMINAL",
            "FLEXAO", "PRANCHA", "NATACAO", "BARRA_EST", "BARRA_DIN",
            "CORRIDA", "PUXADOR_FRONTAL", "FLUTUACAO", "SUPINO", "COOPER"]
    df = df.iloc[:, :min(16, df.shape[1])]
    while len(df.columns) < 16:
        df[f"_pad_{len(df.columns)}"] = np.nan
    df.columns = cols[:len(df.columns)]

    df["NOME"] = df["NOME"].astype(str).str.strip().str.upper()
    df["POSTO_GRAD"] = df["POSTO_GRAD"].astype(str).apply(normalizar_posto)
    df["QUADRO"] = df["QUADRO"].astype(str).str.strip().str.upper()
    df["PRESENTE"] = ~df["CAMINHADA"].astype(str).str.upper().str.contains(
        "NÃO COMPARECEU", na=False
    )
    return df


# ══════════════════════════════════════════════════════════════════════════════
# CARREGAR DADOS
# ══════════════════════════════════════════════════════════════════════════════
df_all, notas_map = carregar_dados()
df_adaptado = carregar_adaptado()

colunas_nota = list(notas_map.values())
labels_nota = list(notas_map.keys())
cats_radar = labels_nota + [labels_nota[0]]


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image(_get_cbmam_image_url(), width=80)
    st.markdown("## CBMAM · TAF 2026")
    st.markdown("**Análise de Desempenho Físico**")
    st.divider()

    pagina = st.radio(
        "📌 Navegação",
        [
            "🏠 Visão Geral",
            "🪖 Por Posto/Graduação",
            "📋 Por Quadro",
            "👤 Ficha Individual",
            "📈 Estatísticas",
            "♿ TAF Adaptado",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # Filtros globais
    if pagina not in ["👤 Ficha Individual", "♿ TAF Adaptado"]:
        st.markdown("**🔧 Filtros**")

        postos_disponiveis = sorted(
            df_all[df_all["PRESENTE"]]["POSTO_GRAD"].unique().tolist(),
            key=lambda x: ordem_posto(x),
        )
        filtro_posto = st.multiselect("Posto/Graduação", postos_disponiveis,
                                       default=postos_disponiveis)

        quadros_disponiveis = sorted(df_all[df_all["PRESENTE"]]["QUADRO"].unique().tolist())
        filtro_quadro = st.multiselect("Quadro", quadros_disponiveis,
                                        default=quadros_disponiveis)

        mostrar_ausentes = st.checkbox("Incluir ausentes", value=False)

        nota_minima = st.slider("Média mínima", 0.0, 10.0, 0.0, 0.1)
    else:
        filtro_posto = df_all["POSTO_GRAD"].unique().tolist()
        filtro_quadro = df_all["QUADRO"].unique().tolist()
        mostrar_ausentes = False
        nota_minima = 0.0

    st.divider()
    efetivo_total = len(df_all)
    presentes_total = int(df_all["PRESENTE"].sum())
    st.markdown(
        f"<small>Efetivo: {efetivo_total} · Presentes: {presentes_total}<br>"
        f"CBMAM · BM-6/EMG · 2026</small>",
        unsafe_allow_html=True,
    )


# ── Filtrar dados ────────────────────────────────────────────────────────────
df_f = df_all.copy()
if not mostrar_ausentes:
    df_f = df_f[df_f["PRESENTE"]]
df_f = df_f[df_f["POSTO_GRAD"].isin(filtro_posto)]
df_f = df_f[df_f["QUADRO"].isin(filtro_quadro)]
df_f = df_f[df_f["MEDIA_FINAL"].fillna(0) >= nota_minima]

# Dados apenas de presentes para cálculos
df_presentes = df_f[df_f["PRESENTE"] & df_f["MEDIA_FINAL"].notna()]


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: VISÃO GERAL
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "🏠 Visão Geral":

    col_txt, col_img = st.columns([2.2, 1])
    with col_txt:
        st.markdown("""
        <h1 style="margin:0;font-size:2rem;">🔥 Dashboard TAF · CBMAM</h1>
        <p style="margin:6px 0 12px;color:#94a3b8;">
          Corpo de Bombeiros Militar do Amazonas · Avaliação Física 2026
        </p>
        """, unsafe_allow_html=True)
        st.markdown("""
        > **Análise completa do Teste de Aptidão Física** com dados de desempenho
        > em corrida, abdominal, flexão, natação e barra. Filtre por posto/graduação
        > e quadro para uma visão detalhada.
        """)

    with col_img:
        st.image(_get_cbmam_image_url(), caption="CBMAM · 2026", use_column_width=True)

    st.divider()

    # KPIs
    st.markdown('<p class="section-title">📊 Indicadores Gerais</p>',
                unsafe_allow_html=True)

    if len(df_presentes) > 0:
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        media_geral = df_presentes["MEDIA_FINAL"].mean()
        melhor = df_presentes.loc[df_presentes["MEDIA_FINAL"].idxmax()]
        pior = df_presentes.loc[df_presentes["MEDIA_FINAL"].idxmin()]
        n_excelentes = len(df_presentes[df_presentes["CLASSIFICACAO"] == "Excelente"])
        n_insuficientes = len(df_presentes[df_presentes["CLASSIFICACAO"] == "Insuficiente"])
        n_ausentes = len(df_all[~df_all["PRESENTE"]])

        k1.metric("👥 Presentes", len(df_presentes))
        k2.metric("📈 Média Geral", f"{media_geral:.2f}")
        k3.metric("🥇 Maior Média", f"{melhor['MEDIA_FINAL']:.1f}",
                   melhor["NOME"].split()[0])
        k4.metric("⚠️ Menor Média", f"{pior['MEDIA_FINAL']:.1f}",
                   pior["NOME"].split()[0])
        k5.metric("✅ Excelentes", n_excelentes)
        k6.metric("🚨 Insuficientes / Ausentes", f"{n_insuficientes} / {n_ausentes}")

        st.divider()

        # Ranking
        st.markdown('<p class="section-title">🏆 Ranking — Média Final</p>',
                    unsafe_allow_html=True)

        df_rank = df_presentes.sort_values("MEDIA_FINAL", ascending=True).copy()
        df_rank["LABEL"] = df_rank.apply(
            lambda r: f"{r['POSTO_GRAD']} {' '.join(str(r['NOME']).split()[:2])}", axis=1
        )

        fig_rank = px.bar(
            df_rank, x="MEDIA_FINAL", y="LABEL", orientation="h",
            color="CLASSIFICACAO", color_discrete_map=COR_MAP,
            text="MEDIA_FINAL",
            hover_data={"NOME": True, "MEDIA_FINAL": True, "CLASSIFICACAO": True,
                       "POSTO_GRAD": True, "QUADRO": True},
            labels={"MEDIA_FINAL": "Média Final", "LABEL": ""},
        )
        fig_rank.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_rank.update_layout(
            **DARK, height=max(500, len(df_rank) * 20),
            legend_title_text="Classificação",
            xaxis=dict(range=[0, 11], **GRID),
            yaxis=dict(**GRID),
            margin=dict(l=10, r=60, t=20, b=20),
        )
        st.plotly_chart(fig_rank, use_column_width=True)

        # Distribuição
        st.markdown('<p class="section-title">📉 Distribuição de Desempenho</p>',
                    unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            contagem = df_presentes["CLASSIFICACAO"].value_counts().reset_index()
            contagem.columns = ["Classificação", "Quantidade"]
            ordem = ["Excelente", "Bom", "Regular", "Insuficiente"]
            contagem["Classificação"] = pd.Categorical(
                contagem["Classificação"], categories=ordem, ordered=True
            )
            fig_pie = px.pie(
                contagem.sort_values("Classificação"),
                names="Classificação", values="Quantidade",
                color="Classificação", color_discrete_map=COR_MAP,
                hole=0.52, title="Proporção por Classificação",
            )
            fig_pie.update_layout(
                **DARK,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                margin=dict(t=50, b=10),
            )
            st.plotly_chart(fig_pie, use_column_width=True)

        with col_b:
            fig_hist = px.histogram(
                df_presentes, x="MEDIA_FINAL", nbins=15,
                color_discrete_sequence=["#3b82f6"],
                title="Histograma de Médias",
                labels={"MEDIA_FINAL": "Média Final", "count": "Frequência"},
            )
            fig_hist.add_vline(
                x=media_geral, line_dash="dash", line_color="#ef4444",
                annotation_text=f"Média: {media_geral:.2f}",
                annotation_font_color="#ef4444",
            )
            fig_hist.update_layout(
                **DARK, margin=dict(t=50, b=10),
                yaxis=dict(**GRID), xaxis=dict(**GRID),
            )
            st.plotly_chart(fig_hist, use_column_width=True)

        # Desempenho por atividade
        st.markdown('<p class="section-title">💪 Desempenho Médio por Atividade</p>',
                    unsafe_allow_html=True)

        medias_disc = {l: df_presentes[c].mean() for l, c in notas_map.items()}
        df_disc = pd.DataFrame({
            "Atividade": list(medias_disc.keys()),
            "Média": list(medias_disc.values()),
        }).sort_values("Média")

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
        st.plotly_chart(fig_disc, use_column_width=True)

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
        st.plotly_chart(fig_radar, use_column_width=True)

        # Mapa de calor
        st.markdown('<p class="section-title">🌡️ Mapa de Calor — Notas</p>',
                    unsafe_allow_html=True)

        df_heat = df_presentes[["NOME", "POSTO_GRAD"] + colunas_nota].copy()
        df_heat["LABEL"] = df_heat.apply(
            lambda r: f"{r['POSTO_GRAD']} {' '.join(str(r['NOME']).split()[:2])}", axis=1
        )
        df_heat = df_heat.sort_values("NOTA_CORRIDA", ascending=False)

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
        st.plotly_chart(fig_heat, use_column_width=True)

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
        st.plotly_chart(fig_pf, use_column_width=True)

        if len(pf_df) > 0:
            st.warning(
                f"⚠️ **{pf_df.iloc[0]['Quantidade']} militares** têm pior desempenho em "
                f"**{pf_df.iloc[0]['Atividade']}**. Recomenda-se treino focado."
            )

        # Tabela
        st.markdown('<p class="section-title">📋 Tabela Completa</p>',
                    unsafe_allow_html=True)

        df_display = df_presentes[[
            "ORD", "POSTO_GRAD", "QUADRO", "NOME",
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
            height=420,
        )

        # Conclusões dinâmicas baseadas em dados reais
        st.divider()
        st.markdown('<p class="section-title">💡 Conclusões e Recomendações</p>',
                    unsafe_allow_html=True)

        # Gerar insights dinâmicos
        medias_exercicios = {l: df_presentes[c].mean() for l, c in notas_map.items()}
        exercicio_critico = min(medias_exercicios, key=medias_exercicios.get)
        media_critica = medias_exercicios[exercicio_critico]
        
        n_excelentes = len(df_presentes[df_presentes["CLASSIFICACAO"] == "Excelente"])
        n_insuficientes = len(df_presentes[df_presentes["CLASSIFICACAO"] == "Insuficiente"])
        n_ausentes = len(df_all[~df_all["PRESENTE"]])
        perc_ausencia = (n_ausentes / len(df_all) * 100) if len(df_all) > 0 else 0
        
        media_geral = df_presentes["MEDIA_FINAL"].mean()
        mediana_geral = df_presentes["MEDIA_FINAL"].median()
        
        # Análise por posto
        postos_pior_desempenho = df_presentes.groupby("POSTO_GRAD")["MEDIA_FINAL"].mean().nsmallest(3)
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            if media_critica < 6.5:
                icone = "🚨"
                acao = "prioritária"
            elif media_critica < 7.5:
                icone = "⚠️"
                acao = "necessária"
            else:
                icone = "✅"
                acao = "recomendada"
            
            st.markdown(f"""
            #### {icone} Reforço em **{exercicio_critico}**
            Com média de **{media_critica:.2f}**, este exercício requer ação {acao}.
            Implementar ciclo de treinamento de 8 semanas com 3 sessões/semana
            pode gerar melhoria de até 20%. Priorize os militares com notas 
            < 5.0 nesta atividade.
            """)
        
        with c2:
            taxa_critica = n_insuficientes / len(df_presentes) * 100 if len(df_presentes) > 0 else 0
            if taxa_critica > 15:
                icone2 = "🚨"
                severidade = "crítica"
            elif taxa_critica > 8:
                icone2 = "⚠️"
                severidade = "moderada"
            else:
                icone2 = "✅"
                severidade = "sob controle"
            
            st.markdown(f"""
            #### {icone2} Nível de **Insuficiência** {severidade.lower()}
            **{n_insuficientes}** militares ({taxa_critica:.1f}%) em desempenho insuficiente.
            **{n_excelentes}** em nível Excelente. Diferença de {n_excelentes - n_insuficientes:+d}.
            
            Taxa de ausência: **{perc_ausencia:.1f}%** ({n_ausentes} ausentes).
            Investigar razões de absentismo para recuperar efetivo.
            """)
        
        with c3:
            st.markdown(f"""
            #### 📊 Saúde Geral das Operações
            **Média Geral:** {media_geral:.2f} (Mediana: {mediana_geral:.2f})
            
            **Postos com menor desempenho:**
            """)
            for posto, media in postos_pior_desempenho.items():
                st.markdown(f"  • **{posto}**: {media:.2f}")
            
            st.markdown("""
            Direcionar ações de mentoria e treinamento especializado
            para estes postos/graduações, focando em ciclos de feedback
            mensal e acompanhamento individualizado.
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
        st.dataframe(resumo, hide_index=True)

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
        st.plotly_chart(fig_posto, use_column_width=True)

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
        st.plotly_chart(fig_box, use_column_width=True)

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
        st.plotly_chart(fig_stack, use_column_width=True)

        # Radar comparativo dos postos
        st.markdown('<p class="section-title">🕸️ Radar Comparativo por Posto</p>',
                    unsafe_allow_html=True)

        def hex_to_rgba(hex_color, alpha=0.2):
            """Converte cor hexadecimal para rgba com transparência."""
            hex_color = hex_color.lstrip('#')
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return f"rgba({r},{g},{b},{alpha})"
        
        postos_top = df_posto_media.head(6)["POSTO_GRAD"].tolist()
        cores_radar = ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6", "#a855f7", "#ec407a"]

        fig_radar_posto = go.Figure()
        for idx, posto in enumerate(postos_top):
            vals = df_presentes[df_presentes["POSTO_GRAD"] == posto][colunas_nota].mean().tolist()
            cor_hex = cores_radar[idx % len(cores_radar)]
            fig_radar_posto.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats_radar,
                fill="toself", name=posto,
                line_color=cor_hex,
                fillcolor=hex_to_rgba(cor_hex, 0.2),
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
            title="Perfil de desempenho por posto (Top 6)",
        )
        st.plotly_chart(fig_radar_posto, use_column_width=True)

        # Taxa de ausência por posto
        st.markdown('<p class="section-title">❌ Taxa de Ausência por Posto</p>',
                    unsafe_allow_html=True)

        ausentes_posto = df_all.groupby("POSTO_GRAD")["PRESENTE"].apply(
            lambda x: (~x).sum()
        ).reset_index(name="Ausentes")
        total_posto = df_all.groupby("POSTO_GRAD").size().reset_index(name="Total")
        df_ausencia = pd.merge(ausentes_posto, total_posto, on="POSTO_GRAD")
        df_ausencia["Taxa (%)"] = (df_ausencia["Ausentes"] / df_ausencia["Total"]) * 100
        df_ausencia["_ordem"] = df_ausencia["POSTO_GRAD"].apply(ordem_posto)
        df_ausencia = df_ausencia.sort_values("_ordem").drop(columns=["_ordem"])

        fig_aus = px.bar(
            df_ausencia, x="POSTO_GRAD", y="Taxa (%)",
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
        st.plotly_chart(fig_aus, use_column_width=True)


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
        st.dataframe(resumo_q, hide_index=True)

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
        st.plotly_chart(fig_q, use_column_width=True)

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
        st.plotly_chart(fig_box_q, use_column_width=True)

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
        st.plotly_chart(fig_stack_q, use_column_width=True)

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
        st.plotly_chart(fig_radar_q, use_column_width=True)

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
        st.plotly_chart(fig_disc_q, use_column_width=True)


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

        # Filtrar apenas militares com dados completos (presente + média final válida)
        df_busca = df_all[df_all["PRESENTE"] & df_all["MEDIA_FINAL"].notna()].copy()
        lista_nomes = df_busca["NOME"].tolist()
        if busca:
            lista_nomes = [n for n in lista_nomes if busca.upper() in n]

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

        # Comparações
        media_geral = df_all[df_all["PRESENTE"]]["MEDIA_FINAL"].mean()
        diff_geral = media_ind - media_geral

        # Média do mesmo posto
        media_posto = df_all[
            (df_all["PRESENTE"]) & (df_all["POSTO_GRAD"] == posto_ind)
        ]["MEDIA_FINAL"].mean()
        diff_posto = media_ind - media_posto

        # Ranking
        df_rank_calc = df_all[df_all["PRESENTE"] & df_all["MEDIA_FINAL"].notna()].copy()
        rank_pos = df_rank_calc["MEDIA_FINAL"].rank(ascending=False, method="min")
        
        # Proteção contra nomes não encontrados
        militar_limpo = str(militar_sel).strip() if militar_sel else ""
        rank_filtro = rank_pos[df_rank_calc["NOME"] == militar_limpo]
        
        if len(rank_filtro) == 0:
            # Tenta busca com espaços normalizados
            rank_filtro = rank_pos[df_rank_calc["NOME"].str.strip() == militar_limpo]
        
        if len(rank_filtro) == 0:
            st.error(f"❌ Militar '{militar_sel}' não encontrado no ranking. Verifique se está presente.")
            posicao = total = 0
            st.stop()  # Para a execução aqui para evitar novos erros
        else:
            posicao = int(rank_filtro.values[0])
            total = len(df_rank_calc)

        pf_notas = {l: float(row[c]) for l, c in notas_map.items() if pd.notna(row[c])}
        pf_forte = max(pf_notas, key=pf_notas.get) if pf_notas else "—"
        pf_fraco = row["PONTO_FRACO"]

        badge_cor = {
            "Excelente":    ("#bbf7d0", "#166534", "rgba(34,197,94,.3)"),
            "Bom":          ("#bfdbfe", "#1e3a5f", "rgba(59,130,246,.3)"),
            "Regular":      ("#fde68a", "#78350f", "rgba(245,158,11,.3)"),
            "Insuficiente": ("#fecaca", "#7f1d1d", "rgba(239,68,68,.3)"),
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
                {posto_ind} · {quadro_ind} · CBMAM · 2026
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
            ("🏊 Natação 50m", row["NATACAO_RAW"], ""),
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

        med_geral_vals = [df_all[df_all["PRESENTE"]][c].mean() for c in colunas_nota]
        med_posto_vals = [
            df_all[(df_all["PRESENTE"]) & (df_all["POSTO_GRAD"] == posto_ind)][c].mean()
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
            st.plotly_chart(fig_r, use_column_width=True)

        with col_b2:
            st.markdown('<p class="section-title">📊 Notas vs Referências</p>',
                        unsafe_allow_html=True)

            fig_b = go.Figure()
            fig_b.add_trace(go.Bar(
                name="Média Geral", x=labels_nota, y=med_geral_vals,
                marker_color="rgba(245,158,11,.5)",
                text=[f"{v:.1f}" for v in med_geral_vals], textposition="outside",
            ))
            # A linha abaixo estava com indentação incorreta
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
            st.plotly_chart(fig_b, use_column_width=True)

        # Cards de notas
        st.markdown('<p class="section-title">🎯 Detalhamento por Atividade</p>',
                    unsafe_allow_html=True)

        cols_disc = st.columns(5)
        for i, (label, col_n) in enumerate(zip(labels_nota, colunas_nota)):
            nota_v = float(row[col_n]) if pd.notna(row[col_n]) else 0.0
            med_v = df_all[df_all["PRESENTE"]][col_n].mean()
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
        st.plotly_chart(fig_gauge, use_column_width=True)

        # Resumo
        st.markdown(f"""
        <div style="background:rgba(17,27,46,.8);border:1px solid rgba(255,255,255,.1);
                    border-radius:14px;padding:20px;margin-top:10px;line-height:2;">
          <b>🪖 Posto/Graduação:</b> {posto_ind} · {quadro_ind}<br>
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
        st.plotly_chart(fig_box, use_column_width=True)

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
        st.plotly_chart(fig_hist_all, use_column_width=True)

        # Correlação corrida x média
        st.markdown('<p class="section-title">🏃 Correlação: Corrida × Média Final</p>',
                    unsafe_allow_html=True)

        df_corr = df_presentes[df_presentes["CORRIDA"].notna()].copy()
        fig_scatter = px.scatter(
            df_corr, x="CORRIDA", y="MEDIA_FINAL",
            color="CLASSIFICACAO", color_discrete_map=COR_MAP,
            size="MEDIA_FINAL", hover_name="NOME",
            trendline="ols", trendline_color_override="#ffffff",
            labels={"CORRIDA": "Corrida 12min (metros)", "MEDIA_FINAL": "Média Final"},
            title="Militares com maior distância na corrida têm média mais alta?",
        )
        fig_scatter.update_layout(
            **DARK, height=420,
            yaxis=dict(**GRID), xaxis=dict(**GRID),
            margin=dict(t=50, b=20),
        )
        st.plotly_chart(fig_scatter, use_column_width=True)

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
        st.dataframe(pd.DataFrame(perc_data), hide_index=True)

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
        st.dataframe(desc)

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
            st.dataframe(top10)

        with col_bt:
            st.markdown("**⚠️ Bottom 10 — Menores Médias**")
            bot10 = df_presentes.nsmallest(10, "MEDIA_FINAL")[
                ["NOME", "POSTO_GRAD", "QUADRO", "MEDIA_FINAL", "CLASSIFICACAO"]
            ].reset_index(drop=True)
            bot10.index += 1
            st.dataframe(bot10)

        # Valores brutos — desempenho real
        st.markdown('<p class="section-title">🔢 Desempenho Bruto (Valores Reais)</p>',
                    unsafe_allow_html=True)

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
        st.plotly_chart(fig_adapt, use_column_width=True)

        # Tabela de dados
        st.markdown('<p class="section-title">📋 Dados Completos — TAF Adaptado</p>',
                    unsafe_allow_html=True)

        display_cols = [c for c in df_adaptado.columns if c not in ["PRESENTE", "_ordem"]]
        df_adapt_display = df_adaptado[display_cols].copy()
        df_adapt_display = df_adapt_display.fillna("—")

        # Limpar valores "nan"
        for col in df_adapt_display.columns:
            df_adapt_display[col] = df_adapt_display[col].astype(str).replace("nan", "—")

        st.dataframe(df_adapt_display, height=500)

        # Exercícios realizados
        st.markdown('<p class="section-title">📊 Exercícios Realizados</p>',
                    unsafe_allow_html=True)

        exercicios_adapt = ["CAMINHADA", "ABDOMINAL", "FLEXAO", "PRANCHA", "NATACAO",
                            "BARRA_EST", "BARRA_DIN", "CORRIDA", "PUXADOR_FRONTAL",
                            "FLUTUACAO", "SUPINO", "COOPER"]
        ex_count = {}
        for ex in exercicios_adapt:
            if ex in df_adaptado.columns:
                count = df_adaptado[ex].dropna().apply(
                    lambda x: str(x).strip() not in ("", "nan", "NÃO COMPARECEU", "NÃO")
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
            st.plotly_chart(fig_ex, use_column_width=True)

        st.info(
            "ℹ️ O TAF Adaptado avalia militares com necessidades especiais ou "
            "restrições médicas, utilizando exercícios alternativos conforme "
            "aptidão individual. Cada militar realiza um conjunto diferente de provas."
        )
