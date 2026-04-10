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
        * {{
            color: {theme['text_primary']} !important;
        }}

        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(135deg, {theme['bg_primary']} 0%, {theme['bg_secondary']} 100%);
        }}

        [data-testid="stSidebar"] {{
            background: {theme['bg_secondary']};
            border-right: 1px solid {theme['border_color']};
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
        [data-testid="stSelectbox"] input {{
            color: {theme['text_primary']} !important;
            background-color: {theme['input_bg']} !important;
            border: 2px solid {theme['accent']} !important;
        }}

        [data-testid="stSelectbox"] input:focus {{
            outline: none !important;
            border-color: {theme['accent']} !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
        }}

        button {{
            color: {theme['text_primary']} !important;
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
    "1° TEN": 5, "2° TEN": 6, "ASP OF": 7,
    "ST": 8, "1° SGT": 9, "2° SGT": 10, "3° SGT": 11,
    "CB": 12, "SD": 13,
}

# ══════════════════════════════════════════════════════════════════════════════
# REGRAS DE PONTUAÇÃO (RESUMIDAS PARA BREVIDADE)
# ══════════════════════════════════════════════════════════════════════════════

REGRAS_MASCULINO = {
    '18-21': {
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
                   104: 2.0, 108: 1.5, 999: 0}
    }
}

REGRAS_FEMININO = {
    '18-21': {
        'Corrida': {2800: 10, 2700: 9.5, 2600: 9.0, 2500: 8.5, 2400: 8.0, 2300: 7.5, 
                   2200: 7.0, 2100: 6.5, 2000: 6.0, 1900: 5.5, 1800: 5.0, 1700: 4.5, 
                   1600: 4.0, 1500: 3.5, 1400: 3.0, 1300: 2.5, 1200: 2.0, 1100: 1.5, 0: 0},
        'Flexão': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5, 
                  22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5, 
                  14: 2.0, 13: 1.5, 0: 0},
        'Abdominal': {40: 10, 39: 9.5, 38: 9.0, 37: 8.5, 36: 8.0, 35: 7.5, 34: 7.0, 33: 6.5, 
                     32: 6.0, 31: 5.5, 30: 5.0, 29: 4.5, 28: 4.0, 27: 3.5, 26: 3.0, 25: 2.5, 
                     24: 2.0, 23: 1.5, 0: 0},
        'Barra Dinâmica': {8: 10, 7: 9.5, 6: 9.0, 5: 8.5, 4: 8.0, 3: 7.5, 2: 7.0, 1: 6.5, 0: 0},
        'Barra Estática': {50: 10, 48: 9.5, 46: 9.0, 44: 8.5, 42: 8.0, 40: 7.5, 38: 7.0, 36: 6.5, 
                          34: 6.0, 32: 5.5, 30: 5.0, 28: 4.5, 26: 4.0, 24: 3.5, 22: 3.0, 20: 2.5, 
                          18: 2.0, 16: 1.5, 0: 0},
        'Natação': {45: 10, 50: 9.5, 55: 9.0, 60: 8.5, 65: 8.0, 70: 7.5, 75: 7.0, 80: 6.5, 
                   85: 6.0, 90: 5.5, 95: 5.0, 100: 4.5, 105: 4.0, 110: 3.5, 115: 3.0, 120: 2.5, 
                   125: 2.0, 130: 1.5, 999: 0}
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════

def ordem_posto(posto):
    """Retorna ordem numérica do posto"""
    return ORDEM_POSTO.get(posto, 999)

def calcular_nota(valor, regra_dict):
    """Calcula nota baseada em regra de pontuação"""
    if pd.isna(valor) or valor == 0:
        return 0.0

    valor = float(valor)
    chaves_ordenadas = sorted([k for k in regra_dict.keys() if isinstance(k, (int, float))], reverse=True)

    for chave in chaves_ordenadas:
        if valor >= chave:
            return float(regra_dict[chave])

    return float(regra_dict.get(0, 0))

# ══════════════════════════════════════════════════════════════════════════════
# CARREGAR DADOS (SIMULADO)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    """Carrega dados de exemplo"""
    # Aqui você carregaria dados reais de um CSV ou banco de dados
    np.random.seed(42)

    postos = ["CEL", "TC", "MAJOR", "CAP", "1° TEN", "2° TEN", "ST", "1° SGT", "2° SGT", "CB", "SD"]
    quadros = ["QCOBM", "QCPBM", "QPBM"]
    nomes = [f"Militar {i}" for i in range(1, 101)]

    data = {
        "NOME": nomes,
        "POSTO_GRAD": np.random.choice(postos, 100),
        "QUADRO": np.random.choice(quadros, 100),
        "SEXO": np.random.choice(["M", "F"], 100),
        "IDADE": np.random.randint(18, 60, 100),
        "PRESENTE": np.random.choice([True, False], 100, p=[0.9, 0.1]),
        "CORRIDA": np.random.randint(1500, 3500, 100),
        "FLEXAO": np.random.randint(15, 45, 100),
        "ABDOMINAL": np.random.randint(25, 55, 100),
        "NATACAO_SEG": np.random.randint(40, 120, 100),
        "BARRA_VALOR": np.random.uniform(1, 15, 100),
    }

    df = pd.DataFrame(data)

    # Calcular notas
    for idx, row in df.iterrows():
        sexo = row["SEXO"]
        idade_range = "18-21"  # Simplificado
        regras = REGRAS_MASCULINO if sexo == "M" else REGRAS_FEMININO

        df.at[idx, "NOTA_CORRIDA"] = calcular_nota(row["CORRIDA"], regras[idade_range]["Corrida"])
        df.at[idx, "NOTA_FLEXAO"] = calcular_nota(row["FLEXAO"], regras[idade_range]["Flexão"])
        df.at[idx, "NOTA_ABDOMINAL"] = calcular_nota(row["ABDOMINAL"], regras[idade_range]["Abdominal"])
        df.at[idx, "NOTA_NATACAO"] = calcular_nota(row["NATACAO_SEG"], regras[idade_range]["Natação"])
        df.at[idx, "NOTA_BARRA"] = calcular_nota(row["BARRA_VALOR"], regras[idade_range]["Barra Dinâmica"])

    # Calcular média
    notas_cols = ["NOTA_CORRIDA", "NOTA_FLEXAO", "NOTA_ABDOMINAL", "NOTA_NATACAO", "NOTA_BARRA"]
    df["MEDIA_FINAL"] = df[notas_cols].mean(axis=1)

    # Classificação
    def classificar(media):
        if media >= 9.0:
            return "Excelente"
        elif media >= 7.5:
            return "Bom"
        elif media >= 6.0:
            return "Regular"
        elif media >= 4.0:
            return "Insuficiente"
        else:
            return "Ausente"

    df["CLASSIFICACAO"] = df["MEDIA_FINAL"].apply(classificar)
    df["PONTO_FRACO"] = "Corrida"

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
        options=df_all["POSTO_GRAD"].unique(),
        default=df_all["POSTO_GRAD"].unique(),
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
        ).reset_index().round(2)

        st.markdown(f"<p class='section-title'>📊 Resumo por Quadro</p>", unsafe_allow_html=True)
        st.dataframe(resumo_q, hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: FICHA INDIVIDUAL
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "👤 Ficha Individual":
    st.markdown(f"""
    <h1 style="margin:0;font-size:2rem;color:{theme['text_primary']}">👤 Ficha Individual</h1>
    <p style="margin:6px 0 12px;color:{theme['text_secondary']};">
    Perfil detalhado de

