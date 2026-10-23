import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="HortaAI | Sua Horta de Varanda", page_icon="🌱", layout="wide"
)

# ==========================================
# 2. CAMADA DE DADOS
# ==========================================
CSV_PATH = "horta_janela_regional.csv"
TXT_PATH = "manual_tecnico_simples.txt"


def bootstrap_data():
    """
    Garante que os arquivos de dados existam localmente.
    Se não existirem, orienta o usuário a rodar fetch_dados.py.
    Mantém um fallback mínimo para permitir execução sem internet.
    """
    if not os.path.exists(CSV_PATH):
        st.error(
            "Dataset não encontrado. Execute `python fetch_dados.py` "
            "para gerar o arquivo com dados da Wikipedia PT-BR."
        )
        st.stop()

    if not os.path.exists(TXT_PATH):
        st.warning(
            "Manual de manejo não encontrado. Execute `python fetch_dados.py` "
            "para regenerá-lo."
        )


bootstrap_data()


@st.cache_data
def load_data() -> pd.DataFrame:
    """Carrega o dataset principal com cache para evitar releituras desnecessárias."""
    return pd.read_csv(CSV_PATH)


df = load_data()

# ==========================================
# 3. CABEÇALHO DO APLICATIVO
# ==========================================
st.title("🌱 HortAI | Sua Horta de Varanda")
st.markdown(
    "Recomendação agronômica para espaços compactos. "
    "Dados botânicos: [Wikipedia PT-BR](https://pt.wikipedia.org) · "
    "Dados agronômicos: curadoria local em `data/curadoria.json`."
)

# ==========================================
# 4. SIDEBAR (FILTROS REATIVOS)
# ==========================================
st.sidebar.header("🎛️ Parâmetros de Cultivo")
regiao_selecionada = st.sidebar.selectbox(
    "Macrorregião do Brasil",
    ["Sudeste", "Sul", "Centro-Oeste", "Nordeste", "Norte"],
    index=0,
)
max_dif = st.sidebar.slider(
    "Dificuldade Máxima (1-5)", min_value=1, max_value=5, value=3
)
luzes_disponiveis = df["luz"].unique()
filtro_luz = st.sidebar.multiselect(
    "Luminosidade Disponível",
    options=luzes_disponiveis,
    default=list(luzes_disponiveis),
)

# ==========================================
# 5. MOTOR DE FILTRAGEM (PANDAS)
# ==========================================
df_filtered = df[
    (df["dificuldade_escala_1_5"] <= max_dif)
    & (df["luz"].isin(filtro_luz))
    & (
        df["regioes_aptas"].str.contains(
            regiao_selecionada, case=False, na=False
        )
    )
]

# ==========================================
# 6. KPIS EXECUTIVOS
# ==========================================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Região Alvo", regiao_selecionada)
c2.metric("Cultivares Aptas", len(df_filtered))
c3.metric(
    "Média de Rega",
    (
        f"{df_filtered['rega_dias'].mean():.1f} dias"
        if not df_filtered.empty
        else "N/A"
    ),
)
c4.metric(
    "Dificuldade Média",
    (
        f"{df_filtered['dificuldade_escala_1_5'].mean():.1f} / 5"
        if not df_filtered.empty
        else "N/A"
    ),
)

st.divider()

# ==========================================
# 7. ABAS DE VISUALIZAÇÃO E AUDITORIA
# ==========================================
tab_grafico, tab_tabela, tab_laudo = st.tabs(
    ["📊 Análise Visual (Rega)", "📋 Matriz Relacional", "🔬 Laudo Técnico"]
)

with tab_grafico:
  if not df_filtered.empty:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    sns.barplot(
        data=df_filtered.sort_values("rega_dias"),
        x="planta",
        y="rega_dias",
        hue="luz",
        palette="viridis",
        dodge=False,
        ax=ax,
    )
    ax.set_title(
        f"Frequência de Rega (Dias) — Aptas para {regiao_selecionada}",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_xlabel("Cultivar")
    ax.set_ylabel("Dias entre regas")
    plt.xticks(rotation=20, ha="right")

    for p in ax.patches:
      height = p.get_height()
      if height > 0:
        ax.annotate(
            f"{int(height)}d",
            (p.get_x() + p.get_width() / 2.0, height),
            ha="center",
            va="bottom",
            fontsize=9,
            xytext=(0, 3),
            textcoords="offset points",
        )
    st.pyplot(fig)
  else:
    st.warning("⚠️ Nenhuma cultivar atende aos filtros combinados atuais.")

with tab_tabela:
  st.dataframe(df_filtered, use_container_width=True)

with tab_laudo:
  if not df_filtered.empty:
    escolhida = st.selectbox(
        "Selecione o cultivar para auditoria de manejo:",
        options=df_filtered["planta"].unique(),
    )
    row = df[df["planta"] == escolhida].iloc[0]

    col_a, col_b = st.columns(2)
    with col_a:
      st.markdown(f"### 🌱 {row['planta']}")
      st.write(f"- **Luz ideal:** `{row['luz']}`")
      st.write(f"- **Ciclo/Rega:** A cada `{row['rega_dias']} dias`")
      st.write(f"- **Complexidade:** `{row['dificuldade_escala_1_5']}/5`")
    with col_b:
      st.markdown("### 🗺️ Zoneamento")
      st.write(f"- **Regiões aptas:** `{row['regioes_aptas']}`")
      st.write(f"- **Temporada ideal:** `{row['temporada_ideal']}`")

    # Descrição botânica da Wikipedia
    descricao = row.get("descricao_botanica", "")
    fonte = row.get("fonte_botanica", "")
    if pd.notna(descricao) and descricao:
      st.markdown("### 📖 Descrição Botânica")
      st.write(descricao)
      if pd.notna(fonte) and fonte:
        st.caption(f"Fonte: [{fonte}]({fonte})")

    # Dicas de manejo do manual local
    encontrou_nota = False
    if os.path.exists(TXT_PATH):
      with open(TXT_PATH, "r", encoding="utf-8") as f:
        for linha in f:
          if escolhida.lower() in linha.lower():
            st.info(f"📋 **Dica de manejo:** {linha.strip()}")
            encontrou_nota = True
    if not encontrou_nota:
      st.caption("Sem diretriz de manejo cadastrada.")
  else:
    st.warning("Ajuste os filtros para habilitar a consulta de laudos.")