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
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child:focus {{
            outline: none !important;
            border-color: {theme['accent']} !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
        }}
        /* Opções do selectbox */
        div[data-baseweb="popover"] div[role="listbox"] {{
            background-color: {theme['input_bg']} !important;
            border: 1px solid {theme['input_border']} !important;
        }}
        div[data-baseweb="popover"] div[role="option"] {{
            color: {theme['text_primary']} !important;
        }}
        div[data-baseweb="popover"] div[role="option"]:hover {{
            background-color: {theme['bg_tertiary']} !important;
        }}

        /* Multiselect */
        [data-testid="stMultiSelect"] div[data-baseweb="select"] {{
            background-color: {theme['input_bg']} !important;
            border: 1px solid {theme['input_border']} !important;
            border-radius: 6px !important;
        }}
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div:first-child {{
            color: {theme['text_primary']} !important;
        }}
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div:first-child:hover {{
            border-color: {theme['accent']} !important;
        }}
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div:first-child:focus {{
            outline: none !important;
            border-color: {theme['accent']} !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
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

        /* Divisor */
        .st-emotion-cache-10q70f0 {{ /* Este seletor pode mudar com versões do Streamlit */
            background-color: {theme['border_color']} !important;
        }}

        .section-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: {theme['text_primary']};
            margin: 20px 0 12px 0;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

apply_theme_css()

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DE CORES E DADOS
# ══════════════════════════════════════════════════════════════════════════════

theme = get_theme_config()

DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color=theme['text_primary']
)

GRID = dict(gridcolor=f"rgba(0,0,0,0.1)" if st.session_state.tema == "claro" else "rgba(255,255,255,0.06)")

COR_MAP = {
    "Excelente": "#22c55e",
    "Bom": "#3b82f6",
    "Regular": "#f59e0b",
    "Insuficiente": "#ef4444",
    "Ausente": "#64748b",
}

ORDEM_POSTO = {
    "CEL": 1, "TC": 2, "MAJOR": 3, "CAP": 4,
    "1° TEN": 5, "1º TEN": 5, "2° TEN": 6, "2º TEN": 6, "ASP OF": 7,
    "ST": 8, "1° SGT": 9, "1º SGT": 9, "2° SGT": 10, "2º SGT": 10, "3° SGT": 11, "3º SGT": 11,
    "CB": 12, "SD": 13,
}

def ordem_posto(posto):
    return ORDEM_POSTO.get(posto, 99) # Valor alto para postos não mapeados

# ══════════════════════════════════════════════════════════════════════════════
# REGRAS DE PONTUAÇÃO (COMPLETAS E CORRIGIDAS)
# ══════════════════════════════════════════════════════════════════════════════

# As regras de pontuação devem ser completas para todas as faixas etárias
# e exercícios. Para brevidade, estou usando as que você forneceu e
# adicionando uma estrutura para outras faixas etárias.
# Você precisará preencher as demais faixas etárias com os dados corretos.

# Exemplo de estrutura para regras completas:
# REGRAS_MASCULINO = {
#     '18-21': { 'Corrida': {3200: 10, ...}, 'Flexão': {38: 10, ...}, ... },
#     '22-25': { 'Corrida': {3000: 10, ...}, 'Flexão': {35: 10, ...}, ... },
#     ...
#     '56+': { 'Corrida': {1800: 10, ...}, 'Flexão': {15: 10, ...}, ... },
# }

# Para este exemplo, vou replicar a faixa 18-21 para outras faixas
# e ajustar os limites para simular diferentes regras.
# VOCÊ DEVE SUBSTITUIR ESTES DADOS PELOS VALORES REAIS DO CBMAM.

def generate_age_rules(base_rules, age_groups, factor_corrida=100, factor_flexao=2, factor_abdominal=2, factor_barra_dinamica=1, factor_barra_estatica=5, factor_natacao=5):
    """Gera regras para diferentes faixas etárias baseadas em um conjunto base, ajustando os limites."""
    all_rules = {}
    for i, age_group in enumerate(age_groups):
        current_rules = {}
        for exercise, scores in base_rules.items():
            new_scores = {}
            if exercise == 'Corrida':
                # Corrida: diminui a distância com a idade
                for dist, score in scores.items():
                    if dist == 0:
                        new_scores[0] = 0
                    else:
                        new_dist = max(0, dist - i * factor_corrida)
                        new_scores[new_dist] = score
            elif exercise == 'Flexão':
                # Flexão: diminui o número de repetições
                for reps, score in scores.items():
                    if reps == 0:
                        new_scores[0] = 0
                    else:
                        new_reps = max(0, reps - i * factor_flexao)
                        new_scores[new_reps] = score
            elif exercise == 'Abdominal':
                # Abdominal: diminui o número de repetições
                for reps, score in scores.items():
                    if reps == 0:
                        new_scores[0] = 0
                    else:
                        new_reps = max(0, reps - i * factor_abdominal)
                        new_scores[new_reps] = score
            elif exercise == 'Barra Dinâmica':
                # Barra Dinâmica: diminui o número de repetições
                for reps, score in scores.items():
                    if reps == 0:
                        new_scores[0] = 0
                    else:
                        new_reps = max(0, reps - i * factor_barra_dinamica)
                        new_scores[new_reps] = score
            elif exercise == 'Barra Estática':
                # Barra Estática: diminui o tempo
                for time, score in scores.items():
                    if time == 0:
                        new_scores[0] = 0
                    else:
                        new_time = max(0, time - i * factor_barra_estatica)
                        new_scores[new_time] = score
            elif exercise == 'Natação':
                # Natação: aumenta o tempo
                for time, score in scores.items():
                    if time == 999: # Valor para insuficiência
                        new_scores[999] = 0
                    else:
                        new_time = time + i * factor_natacao
                        new_scores[new_time] = score
            current_rules[exercise] = dict(sorted(new_scores.items(), reverse=True if exercise != 'Natação' else False))
        all_rules[age_group] = current_rules
    return all_rules

# Faixas etárias definidas para o TAF
AGE_GROUPS = [
    '18-21', '22-25', '26-30', '31-35', '36-40', '41-45', '46-50', '51-55', '56+'
]

# Regras base (18-21) - Use as suas regras originais aqui
BASE_REGRAS_MASCULINO = {
    'Corrida': {3200: 10, 3100: 9.5, 3000: 9.0, 2900: 8.5, 2800: 8.0, 2700: 7.5,
               2600: 7.0, 2500: 6.5, 2400: 6.0, 2300: 5.5, 2200: 5.0, 2100: 4.5,
               2000: 4.0, 1900: 3.5, 1800: 3.0, 1700: 2.5, 1600: 2.0, 1500: 1.5, 0: 0},
    'Flexão': {38: 10, 37: 9.5, 36: 9.0, 35: 8.5, 34: 8.0, 33: 7.5, 32: 7.0, 31: 6.5,
              30: 6.0, 29: 5.5, 28: 5.0, 27: 4.5, 26: 4.0, 25: 3.5, 24: 3.0, 23: 2.5,
              22: 2.0, 21: 1.5, 0: 0},
    'Abdominal': {48: 10, 47: 9.5, 46: 9.0, 45: 8.5, 44: 8.0, 43: 7.5, 42: 7.0, 41: 6.5,
                 40: 6.0, 39: 5.5, 38: 5.0, 37: 4.5, 36: 4.0, 35: 3.5, 34: 3.0, 33: 2.5,
                 32: 2.0, 31: 1.5, 0: 0},
    'Barra Dinâmica': {13: 10, 12: 9.5, 11: 9.0, 10: 8.5, 9: 8.0, 8: 7.5, 7: 7.0, 6: 6.5,
                      5: 6.0, 4: 5.5, 3: 5.0, 2: 4.5, 1: 4.0, 0: 0},
    'Barra Estática': {60: 10, 57: 9.5, 55: 9.0, 53: 8.5, 51: 8.0, 49: 7.5, 47: 7.0, 45: 6.5,
                      43: 6.0, 41: 5.5, 39: 5.0, 37: 4.5, 35: 4.0, 33: 3.5, 31: 3.0, 29: 2.5,
                      27: 2.0, 25: 1.5, 0: 0},
    'Natação': {40: 10, 44: 9.5, 48: 9.0, 52: 8.5, 56: 8.0, 60: 7.5, 64: 7.0, 68: 6.5,
               72: 6.0, 76: 5.5, 80: 5.0, 84: 4.5, 88: 4.0, 92: 3.5, 96: 3.0, 100: 2.5,
               104: 2.0, 108: 1.5, 999: 0} # 999 para indicar tempo máximo para 0 pontos
}

BASE_REGRAS_FEMININO = {
    'Corrida': {2800: 10, 2700: 9.5, 2600: 9.0, 2500: 8.5, 2400: 8.0, 2300: 7.5,
               2200: 7.0, 2100: 6.5, 2000: 6.0, 1900: 5.5, 1800: 5.0, 1700: 4.5,
               1600: 4.0, 1500: 3.5, 1400: 3.0, 1300: 2.5, 1200: 2.0, 1100: 1.5, 0: 0},
    'Flexão': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5,
              22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5,
              14: 2.0, 13: 1.5, 0: 0},
    'Abdominal': {40: 10, 39: 9.5, 38: 9.0, 37: 8.5, 36: 8.0, 35: 7.5, 34: 7.0, 33: 6.5,
                 32: 6.0, 31: 5.5, 30: 5.0, 29: 4.5, 28: 4.0, 27: 3.5, 26: 3.0, 25: 2.5,
                 24: 2.0, 23: 1.5, 0: 0},
    'Barra Dinâmica': {10: 10, 9: 9.5, 8: 9.0, 7: 8.5, 6: 8.0, 5: 7.5, 4: 7.0, 3: 6.5,
                      2: 6.0, 1: 5.5, 0: 0}, # Feminino geralmente não tem barra dinâmica
    'Barra Estática': {50: 10, 47: 9.5, 45: 9.0, 43: 8.5, 41: 8.0, 39: 7.5, 37: 7.0, 35: 6.5,
                      33: 6.0, 31: 5.5, 29: 5.0, 27: 4.5, 25: 4.0, 23: 3.5, 21: 3.0, 19: 2.5,
                      17: 2.0, 15: 1.5, 0: 0},
    'Natação': {45: 10, 49: 9.5, 53: 9.0, 57: 8.5, 61: 8.0, 65: 7.5, 69: 7.0, 73: 6.5,
               77: 6.0, 81: 5.5, 85: 5.0, 89: 4.5, 93: 4.0, 97: 3.5, 101: 3.0, 105: 2.5,
               109: 2.0, 113: 1.5, 999: 0}
}

REGRAS_MASCULINO = generate_age_rules(BASE_REGRAS_MASCULINO, AGE_GROUPS, factor_corrida=100, factor_flexao=2, factor_abdominal=2, factor_barra_dinamica=1, factor_barra_estatica=5, factor_natacao=5)
REGRAS_FEMININO = generate_age_rules(BASE_REGRAS_FEMININO, AGE_GROUPS, factor_corrida=80, factor_flexao=1, factor_abdominal=1, factor_barra_dinamica=0.5, factor_barra_estatica=4, factor_natacao=4)

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE PROCESSAMENTO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    df = pd.read_csv("master_taf_consolidado.csv")

    # Renomear colunas para facilitar o uso
    df.rename(columns={
        "Posto": "POSTO_GRAD",
        "Nome": "NOME",
        "Corrida": "CORRIDA",
        "Abdominal": "ABDOMINAL",
        "Flexao": "FLEXAO",
        "Natacao": "NATACAO",
        "Barra": "BARRA",
        "Sexo": "SEXO",
        "DataNascimento": "DATA_NASCIMENTO",
        "Idade": "IDADE_CSV" # Manter original para referência, mas recalcular
    }, inplace=True)

    # Limpeza e padronização de dados
    df["POSTO_GRAD"] = df["POSTO_GRAD"].str.upper().str.strip().replace({"1º TEN": "1° TEN", "2º TEN": "2° TEN", "1º SGT": "1° SGT", "2º SGT": "2° SGT", "3º SGT": "3° SGT"})
    df["QUADRO"] = df["QUADRO"].str.upper().str.strip()
    df["SEXO"] = df["SEXO"].str.capitalize().str.strip()

    # Calcular idade a partir da DataNascimento
    df["DATA_NASCIMENTO"] = pd.to_datetime(df["DATA_NASCIMENTO"], format="%d/%m/%Y", errors='coerce')
    today = datetime(2026, 4, 12) # Data de referência para cálculo da idade
    df["IDADE"] = df.apply(lambda row: today.year - row["DATA_NASCIMENTO"].year - ((today.month, today.day) < (row["DATA_NASCIMENTO"].month, row["DATA_NASCIMENTO"].day)) if pd.notna(row["DATA_NASCIMENTO"]) else np.nan, axis=1)

    # Determinar presença
    df["PRESENTE"] = ~df["CORRIDA"].astype(str).str.contains("NÃO COMPARECEU|NÃO CONSTA NENHUM EXERCICIO|APTO", na=False)

    # Converter resultados dos exercícios para numérico
    def clean_exercise_value(value):
        if pd.isna(value) or isinstance(value, (int, float)):
            return value
        s_value = str(value).strip().upper()
        if "NÃO" in s_value or "APTO" in s_value or "COMPARECEU" in s_value or "CONSTA" in s_value:
            return np.nan
        # Corrida: pode ter ' ou " para minutos/segundos
        if "CORRIDA" in s_value: # Ex: 24'51"
            parts = re.findall(r'(\d+)\'(\d+)"', s_value)
            if parts:
                minutes, seconds = int(parts[0][0]), int(parts[0][1])
                return minutes * 60 + seconds
            return np.nan
        # Barra: pode ter ' ou " para minutos/segundos ou apenas segundos
        if "BARRA" in s_value: # Ex: 01'01", 51", 15
            parts_min_sec = re.findall(r'(\d+)\'(\d+)"', s_value)
            if parts_min_sec:
                minutes, seconds = int(parts_min_sec[0][0]), int(parts_min_sec[0][1])
                return minutes * 60 + seconds
            parts_sec = re.findall(r'(\d+)"', s_value)
            if parts_sec:
                return int(parts_sec[0])
            try:
                return float(s_value) # Se for apenas um número (segundos)
            except ValueError:
                return np.nan
        # Abdominal/Flexão: pode ter "rep"
        if "REP" in s_value:
            return float(re.sub(r'[^0-9.]', '', s_value))
        try:
            return float(s_value)
        except ValueError:
            return np.nan

    for col in ["CORRIDA", "ABDOMINAL", "FLEXAO", "NATACAO", "BARRA"]:
        df[col] = df[col].apply(clean_exercise_value)

    # Mapear idade para faixa etária
    def get_age_group(age):
        if pd.isna(age):
            return "Não Informado"
        if age >= 56:
            return '56+'
        for group in AGE_GROUPS[:-1]: # Exclui '56+'
            start, end = map(int, group.split('-'))
            if start <= age <= end:
                return group
        return "Não Informado"

    df["FAIXA_ETARIA"] = df["IDADE"].apply(get_age_group)

    # Calcular pontuação
    def calcular_pontuacao(row, exercicio, regras_sexo):
        idade = row["IDADE"]
        sexo = row["SEXO"]
        valor = row[exercicio]

        if pd.isna(valor) or pd.isna(idade) or pd.isna(sexo) or not row["PRESENTE"]:
            return np.nan

        faixa_etaria = get_age_group(idade)
        if faixa_etaria == "Não Informado":
            return np.nan

        regras_faixa = regras_sexo.get(faixa_etaria, {})
        regras_exercicio = regras_faixa.get(exercicio, {})

        if not regras_exercicio:
            return np.nan

        # Para corrida, flexão, abdominal, barra dinâmica/estática (quanto mais, melhor)
        if exercicio not in ['Natação']:
            for limite, ponto in regras_exercicio.items():
                if valor >= limite:
                    return ponto
            return 0.0 # Se não atingiu nenhum limite, 0 pontos
        # Para natação (quanto menos, melhor)
        else:
            for limite, ponto in regras_exercicio.items():
                if valor <= limite:
                    return ponto
            return 0.0 # Se não atingiu nenhum limite, 0 pontos

    df["PONTUACAO_CORRIDA"] = df.apply(lambda row: calcular_pontuacao(row, "CORRIDA", REGRAS_MASCULINO if row["SEXO"] == "Masculino" else REGRAS_FEMININO), axis=1)
    df["PONTUACAO_ABDOMINAL"] = df.apply(lambda row: calcular_pontuacao(row, "ABDOMINAL", REGRAS_MASCULINO if row["SEXO"] == "Masculino" else REGRAS_FEMININO), axis=1)
    df["PONTUACAO_FLEXAO"] = df.apply(lambda row: calcular_pontuacao(row, "FLEXAO", REGRAS_MASCULINO if row["SEXO"] == "Masculino" else REGRAS_FEMININO), axis=1)
    df["PONTUACAO_NATACAO"] = df.apply(lambda row: calcular_pontuacao(row, "NATACAO", REGRAS_MASCULINO if row["SEXO"] == "Masculino" else REGRAS_FEMININO), axis=1)
    df["PONTUACAO_BARRA"] = df.apply(lambda row: calcular_pontuacao(row, "BARRA", REGRAS_MASCULINO if row["SEXO"] == "Masculino" else REGRAS_FEMININO), axis=1)

    # Calcular média final
    exercicios_pontuados = ["PONTUACAO_CORRIDA", "PONTUACAO_ABDOMINAL", "PONTUACAO_FLEXAO", "PONTUACAO_NATACAO", "PONTUACAO_BARRA"]
    df["MEDIA_FINAL"] = df[exercicios_pontuados].mean(axis=1)

    # Classificar desempenho
    def classificar(media):
        if pd.isna(media):
            return "Ausente"
        if media >= 8.0:
            return "Excelente"
        elif media >= 6.0:
            return "Bom"
        elif media >= 4.0:
            return "Regular"
        else:
            return "Insuficiente"

    df["CLASSIFICACAO"] = df["MEDIA_FINAL"].apply(classificar)

    # Identificar ponto fraco (o exercício com menor pontuação)
    def identificar_ponto_fraco(row):
        if not row["PRESENTE"] or pd.isna(row["MEDIA_FINAL"]):
            return "N/A"
        pontuacoes = {
            "Corrida": row["PONTUACAO_CORRIDA"],
            "Abdominal": row["PONTUACAO_ABDOMINAL"],
            "Flexão": row["PONTUACAO_FLEXAO"],
            "Natação": row["PONTUACAO_NATACAO"],
            "Barra": row["PONTUACAO_BARRA"]
        }
        # Remover NaN para encontrar o mínimo entre os presentes
        valid_pontuacoes = {k: v for k, v in pontuacoes.items() if pd.notna(v)}
        if not valid_pontuacoes:
            return "N/A"
        min_score = min(valid_pontuacoes.values())
        pontos_fracos = [k for k, v in valid_pontuacoes.items() if v == min_score]
        return ", ".join(pontos_fracos) if pontos_fracos else "N/A"

    df["PONTO_FRACO"] = df.apply(identificar_ponto_fraco, axis=1)

    return df

df_all = load_data()
df_presentes = df_all[df_all["PRESENTE"]].copy()
df_adaptado = df_all[df_all["QUADRO"] == "ADAPTADO"].copy() if "ADAPTADO" in df_all["QUADRO"].values else pd.DataFrame()

# ══════════════════════════════════════════════════════════════════════════════
# HEADER COM TEMA
# ══════════════════════════════════════════════════════════════════════════════

col_header_1, col_header_2, col_header_3 = st.columns([2, 3, 1])

with col_header_1:
    st.image(_get_cbmam_image_url(), width=80)

with col_header_2:
    st.markdown(f"""
    <h1 style="margin:0;font-size:2.2rem;color:{theme['text_primary']}">
    🔥 Dashboard TAF · CBMAM
    </h1>
    <p style="margin:6px 0 0;color:{theme['text_secondary']};font-size:0.95rem;">
    Teste de Aptidão Física · Análise Completa · 2026
    </p>
    """, unsafe_allow_html=True)

with col_header_3:
    tema_atual = st.session_state.tema
    novo_tema = "claro" if tema_atual == "escuro" else "escuro"
    icone_tema = "☀️" if tema_atual == "escuro" else "🌙"

    if st.button(f"{icone_tema} {novo_tema.capitalize()}", key="btn_tema", use_container_width=True):
        st.session_state.tema = novo_tema
        st.rerun()

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - FILTROS
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"<h2 style='color:{theme['text_primary']}'>⚙️ Filtros</h2>", unsafe_allow_html=True)

    filtro_quadro = st.multiselect(
        "Quadro",
        options=df_all["QUADRO"].unique(),
        default=df_all["QUADRO"].unique(),
        key="filtro_quadro"
    )

    filtro_posto = st.multiselect(
        "Posto/Graduação",
        options=sorted(df_all["POSTO_GRAD"].unique(), key=ordem_posto),
        default=sorted(df_all["POSTO_GRAD"].unique(), key=ordem_posto),
        key="filtro_posto"
    )

    filtro_sexo = st.multiselect(
        "Sexo",
        options=df_all["SEXO"].unique(),
        default=df_all["SEXO"].unique(),
        key="filtro_sexo"
    )

    filtro_presenca = st.radio(
        "Presença",
        options=["Todos", "Apenas Presentes", "Apenas Ausentes"],
        index=1,
        key="filtro_presenca"
    )

    # Botão para gerar PDF
    st.markdown("---")
    st.markdown(f"<h2 style='color:{theme['text_primary']}'>📄 Exportar Relatório</h2>", unsafe_allow_html=True)
    if st.button("Gerar PDF do Dashboard", key="btn_pdf", use_container_width=True):
        st.session_state.generate_pdf = True
    else:
        st.session_state.generate_pdf = False

# Aplicar filtros
df_filtered = df_all[
    (df_all["QUADRO"].isin(filtro_quadro)) &
    (df_all["POSTO_GRAD"].isin(filtro_posto)) &
    (df_all["SEXO"].isin(filtro_sexo))
]

if filtro_presenca == "Apenas Presentes":
    df_filtered = df_filtered[df_filtered["PRESENTE"]]
elif filtro_presenca == "Apenas Ausentes":
    df_filtered = df_filtered[~df_filtered["PRESENTE"]]

# ══════════════════════════════════════════════════════════════════════════════
# NAVEGAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

pagina = st.selectbox(
    "Selecione a página",
    options=["📊 Dashboard", "📋 Por Quadro", "👤 Ficha Individual", "📈 Estatísticas", "♿ TAF Adaptado"],
    key="pagina"
)

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÃO PARA GERAR PDF
# ══════════════════════════════════════════════════════════════════════════════

def generate_pdf_report(df_filtered, theme_config):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(theme_config['text_primary'])
    c.drawString(50, height - 50, "Dashboard TAF · CBMAM")

    c.setFont("Helvetica", 12)
    c.setFillColor(theme_config['text_secondary'])
    c.drawString(50, height - 70, "Relatório de Desempenho no Teste de Aptidão Física")

    # Adicionar logo
    try:
        logo_url = _get_cbmam_image_url()
        c.drawImage(logo_url, width - 100, height - 80, width=50, height=50, preserveAspectRatio=True)
    except Exception as e:
        st.warning(f"Não foi possível carregar a imagem do logo para o PDF: {e}")

    y_position = height - 120

    # KPIs
    total = len(df_filtered)
    presentes = int(df_filtered["PRESENTE"].sum())
    ausentes = total - presentes
    media_geral = df_filtered[df_filtered["PRESENTE"]]["MEDIA_FINAL"].mean()

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(theme_config['text_primary'])
    c.drawString(50, y_position, "Indicadores Chave:")
    y_position -= 20
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, f"Total de Militares: {total}")
    y_position -= 15
    c.drawString(50, y_position, f"Presentes: {presentes}")
    y_position -= 15
    c.drawString(50, y_position, f"Ausentes: {ausentes}")
    y_position -= 15
    c.drawString(50, y_position, f"Média Geral de Pontuação: {media_geral:.2f}")
    y_position -= 30

    # Gráfico de Distribuição de Classificações
    if presentes > 0:
        class_dist = df_filtered[df_filtered["PRESENTE"]]["CLASSIFICACAO"].value_counts()
        fig_class = px.pie(
            values=class_dist.values,
            names=class_dist.index,
            color=class_dist.index,
            color_discrete_map=COR_MAP,
            title="Distribuição de Classificações",
        )
        fig_class.update_layout(**DARK, height=350, showlegend=True)

        img_buffer_class = io.BytesIO()
        fig_class.write_image(img_buffer_class, format="png")
        img_buffer_class.seek(0)
        img_class = ImageReader(img_buffer_class)

        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(theme_config['text_primary'])
        c.drawString(50, y_position, "Distribuição de Classificações:")
        y_position -= 20
        c.drawImage(img_class, 50, y_position - 300, width=400, height=300, preserveAspectRatio=True)
        y_position -= 320

    # Gráfico de Média por Posto
    if presentes > 0:
        media_posto = df_filtered[df_filtered["PRESENTE"]].groupby("POSTO_GRAD")["MEDIA_FINAL"].mean().reset_index()
        media_posto["_ordem"] = media_posto["POSTO_GRAD"].apply(ordem_posto)
        media_posto = media_posto.sort_values("_ordem")

        fig_posto = px.bar(
            media_posto, x="POSTO_GRAD", y="MEDIA_FINAL",
            color="MEDIA_FINAL",
            color_continuous_scale=["#ef4444", "#f59e0b", "#3b82f6", "#22c55e"],
            text="MEDIA_FINAL",
            labels={"POSTO_GRAD": "Posto", "MEDIA_FINAL": "Média"},
            title="Média por Posto",
        )
        fig_posto.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_posto.update_layout(**DARK, height=350, coloraxis_showscale=False, xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID))

        # Adicionar nova página se necessário
        if y_position < 100: # Se não houver espaço suficiente para o próximo gráfico
            c.showPage()
            y_position = height - 50

        img_buffer_posto = io.BytesIO()
        fig_posto.write_image(img_buffer_posto, format="png")
        img_buffer_posto.seek(0)
        img_posto = ImageReader(img_buffer_posto)

        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(theme_config['text_primary'])
        c.drawString(50, y_position, "Média de Pontuação por Posto/Graduação:")
        y_position -= 20
        c.drawImage(img_posto, 50, y_position - 300, width=400, height=300, preserveAspectRatio=True)
        y_position -= 320

    c.save()
    buffer.seek(0)
    return buffer

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

if pagina == "📊 Dashboard":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">📊 Dashboard Geral</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Visão geral do desempenho no TAF
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    if len(df_filtered) == 0:
        st.warning("Nenhum dado disponível com os filtros atuais.")
    else:
        # KPIs
        total = len(df_filtered)
        presentes = int(df_filtered["PRESENTE"].sum())
        ausentes = total - presentes
        media_geral = df_filtered[df_filtered["PRESENTE"]]["MEDIA_FINAL"].mean()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("👥 Total", total)
        k2.metric("✅ Presentes", presentes)
        k3.metric("❌ Ausentes", ausentes)
        k4.metric("📈 Média Geral", f"{media_geral:.2f}")

        st.divider()

        # Gráficos
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown(f"<p class='section-title'>📊 Distribuição de Classificações</p>", unsafe_allow_html=True)

            class_dist = df_filtered[df_filtered["PRESENTE"]]["CLASSIFICACAO"].value_counts()
            fig_class = px.pie(
                values=class_dist.values,
                names=class_dist.index,
                color=class_dist.index,
                color_discrete_map=COR_MAP,
                title="Classificações",
            )
            fig_class.update_layout(**DARK, height=350)
            st.plotly_chart(fig_class, use_column_width=True)

        with col_g2:
            st.markdown(f"<p class='section-title'>📈 Média por Posto</p>", unsafe_allow_html=True)

            media_posto = df_filtered[df_filtered["PRESENTE"]].groupby("POSTO_GRAD")["MEDIA_FINAL"].mean().reset_index()
            media_posto["_ordem"] = media_posto["POSTO_GRAD"].apply(ordem_posto)
            media_posto = media_posto.sort_values("_ordem")

            fig_posto = px.bar(
                media_posto, x="POSTO_GRAD", y="MEDIA_FINAL",
                color="MEDIA_FINAL",
                color_continuous_scale=["#ef4444", "#f59e0b", "#3b82f6", "#22c55e"],
                text="MEDIA_FINAL",
                labels={"POSTO_GRAD": "Posto", "MEDIA_FINAL": "Média"},
                title="Média por Posto",
            )
            fig_posto.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig_posto.update_layout(**DARK, height=350, coloraxis_showscale=False, xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID))
            st.plotly_chart(fig_posto, use_column_width=True)

    # Gerar PDF se o botão foi clicado
    if st.session_state.get("generate_pdf", False):
        with st.spinner("Gerando PDF..."):
            pdf_buffer = generate_pdf_report(df_filtered, theme)
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="relatorio_taf_dashboard.pdf",
                mime="application/pdf",
                key="download_pdf_dashboard"
            )
        st.session_state.generate_pdf = False # Resetar para não gerar novamente

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: POR QUADRO
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "📋 Por Quadro":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">📋 Análise por Quadro</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Comparativo entre quadros
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    if len(df_filtered[df_filtered["PRESENTE"]]) == 0:
        st.warning("Nenhum dado disponível.")
    else:
        df_quad = df_filtered[df_filtered["PRESENTE"]]

        resumo_q = df_quad.groupby("QUADRO").agg(
            Efetivo=("NOME", "count"),
            Média=("MEDIA_FINAL", "mean"),
            Excelente=("CLASSIFICACAO", lambda x: (x == "Excelente").sum()),
            Bom=("CLASSIFICACAO", lambda x: (x == "Bom").sum()),
            Regular=("CLASSIFICACAO", lambda x: (x == "Regular").sum()),
            Insuficiente=("CLASSIFICACAO", lambda x: (x == "Insuficiente").sum()),
        ).reset_index().round(2)

        resumo_q["% Excelente"] = (resumo_q["Excelente"] / resumo_q["Efetivo"] * 100).round(2)
        resumo_q["% Bom"] = (resumo_q["Bom"] / resumo_q["Efetivo"] * 100).round(2)
        resumo_q["% Regular"] = (resumo_q["Regular"] / resumo_q["Efetivo"] * 100).round(2)
        resumo_q["% Insuficiente"] = (resumo_q["Insuficiente"] / resumo_q["Efetivo"] * 100).round(2)

        st.markdown(f"<p class='section-title'>📊 Resumo por Quadro</p>", unsafe_allow_html=True)
        st.dataframe(resumo_q, hide_index=True, use_container_width=True)

        st.markdown(f"<p class='section-title'>📈 Média de Pontuação por Exercício e Quadro</p>", unsafe_allow_html=True)
        media_exercicios_quadro = df_quad.groupby("QUADRO")[exercicios_pontuados].mean().reset_index().melt(id_vars="QUADRO", var_name="Exercício", value_name="Média de Pontuação")
        media_exercicios_quadro["Exercício"] = media_exercicios_quadro["Exercício"].str.replace("PONTUACAO_", "")

        fig_exercicios_quadro = px.bar(
            media_exercicios_quadro,
            x="Exercício",
            y="Média de Pontuação",
            color="QUADRO",
            barmode="group",
            labels={"Média de Pontuação": "Média de Pontuação", "Exercício": "Exercício"},
            title="Média de Pontuação por Exercício e Quadro",
        )
        fig_exercicios_quadro.update_layout(**DARK, height=450, xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID))
        st.plotly_chart(fig_exercicios_quadro, use_column_width=True)

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

    if len(df_filtered) == 0:
        st.warning("Nenhum militar encontrado com os filtros aplicados.")
    else:
        nomes_militares = df_filtered["NOME"].sort_values().unique()
        militar_selecionado = st.selectbox("Selecione o Militar", nomes_militares)

        if militar_selecionado:
            ficha = df_filtered[df_filtered["NOME"] == militar_selecionado].iloc[0]

            st.markdown(f"### {ficha['POSTO_GRAD']} {ficha['NOME']}")
            st.write(f"**Quadro:** {ficha['QUADRO']}")
            st.write(f"**Sexo:** {ficha['SEXO']}")
            st.write(f"**Idade:** {int(ficha['IDADE'])} anos ({ficha['FAIXA_ETARIA']})")
            st.write(f"**CPF:** {ficha['CPF']}")
            st.write(f"**Status TAF:** {'Presente' if ficha['PRESENTE'] else 'Ausente'}")

            if ficha["PRESENTE"]:
                st.markdown(f"**Média Final:** {ficha['MEDIA_FINAL']:.2f} ({ficha['CLASSIFICACAO']})")
                st.markdown(f"**Ponto Fraco:** {ficha['PONTO_FRACO']}")

                st.markdown(f"<p class='section-title'>Resultados por Exercício</p>", unsafe_allow_html=True)
                col_ex1, col_ex2, col_ex3 = st.columns(3)
                col_ex4, col_ex5, col_ex6 = st.columns(3)

                exercicios_display = {
                    "CORRIDA": "Corrida (m)",
                    "ABDOMINAL": "Abdominal (reps)",
                    "FLEXAO": "Flexão (reps)",
                    "NATACAO": "Natação (s)",
                    "BARRA": "Barra (s/reps)"
                }
                pontuacoes_display = {
                    "PONTUACAO_CORRIDA": "Corrida",
                    "PONTUACAO_ABDOMINAL": "Abdominal",
                    "PONTUACAO_FLEXAO": "Flexão",
                    "PONTUACAO_NATACAO": "Natação",
                    "PONTUACAO_BARRA": "Barra"
                }

                cols = [col_ex1, col_ex2, col_ex3, col_ex4, col_ex5]
                for i, (ex_col, ex_label) in enumerate(exercicios_display.items()):
                    with cols[i]:
                        st.metric(ex_label, f"{ficha[ex_col] if pd.notna(ficha[ex_col]) else 'N/A'}")
                        st.write(f"**Pontuação:** {ficha[pontuacoes_display[f'PONTUACAO_{ex_col}']] if pd.notna(ficha[pontuacoes_display[f'PONTUACAO_{ex_col}']]) else 'N/A'}")

                st.markdown(f"<p class='section-title'>Gráfico de Desempenho Individual</p>", unsafe_allow_html=True)
                pontuacoes_df = pd.DataFrame({
                    "Exercício": list(pontuacoes_display.values()),
                    "Pontuação": [ficha[p] for p in pontuacoes_display.keys()]
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
                    st.plotly_chart(fig_individual, use_column_width=True)
                else:
                    st.info("Não há dados de pontuação para este militar.")
            else:
                st.info("Este militar não compareceu ou não possui dados de TAF.")

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
        st.warning("Nenhum dado disponível.")
    else:
        df_stats = df_filtered[df_filtered["PRESENTE"]]

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
        fig_media_idade_sexo.update_layout(**DARK, height=450, xaxis=dict(**GRID), yaxis=dict(range=[0, 11], **GRID))
        st.plotly_chart(fig_media_idade_sexo, use_column_width=True)

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
            fig_dist_exercicio.update_layout(**DARK, height=450, xaxis=dict(**GRID), yaxis=dict(**GRID))
            st.plotly_chart(fig_dist_exercicio, use_column_width=True)
        else:
            st.warning(f"Coluna de pontuação '{coluna_pontuacao}' não encontrada.")

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: TAF ADAPTADO
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "♿ TAF Adaptado":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">♿ TAF Adaptado</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Análise dos militares em TAF Adaptado
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    if df_adaptado.empty:
        st.info("Nenhum militar em TAF Adaptado encontrado.")
    else:
        st.dataframe(df_adaptado[["NOME", "POSTO_GRAD", "QUADRO", "SEXO", "IDADE", "DATA_NASCIMENTO"]], use_container_width=True)
        # Adicione mais análises específicas para TAF Adaptado aqui, se houver dados relevantes.
