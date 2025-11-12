import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- CONFIGURAÇÃO DA PÁGINA ----------
st.set_page_config(page_title="Dashboard de Carros", layout="wide")
st.title("🚘 Dashboard de Anúncios de Carros")

# ---------- CARREGAR OS DADOS ----------
@st.cache_data
def load_data():
    df = pd.read_csv("data/vehicles.csv")

    df.rename(columns={
        "make": "marca",
        "model": "modelo",
        "model_year": "ano_modelo",
        "condition": "condicao",
        "cylinders": "cilindros",
        "fuel": "combustivel",
        "odometer": "quilometragem",
        "transmission": "transmissao",
        "type": "tipo",
        "paint_color": "cor",
        "is_4wd": "tracao_4wd",
        "date_posted": "data_postagem",
        "days_listed": "dias_anuncio",
    }, inplace=True)

    # cria a coluna "marca" se necessário
    if "marca" not in df.columns:
        if "modelo" in df.columns:
            df["marca"] = df["modelo"].astype(str).str.split().str[0]
        elif "model_name" in df.columns:
            df["marca"] = df["model_name"].astype(str).str.split().str[0]
        else:
            st.error("Nenhuma coluna de modelo encontrada no dataset.")
            st.stop()

    return df

df = load_data()

# ---------- FILTROS NA BARRA LATERAL ----------S
st.sidebar.header("Filtros")

marcas = st.sidebar.multiselect(
    "Marca:",
    options=df["marca"].dropna().unique(),
    default=None
)

anos = st.sidebar.slider(
    "Ano do Modelo:",
    int(df["ano_modelo"].min()),
    int(df["ano_modelo"].max()),
    (int(df["ano_modelo"].min()), int(df["ano_modelo"].max()))
)

combustiveis = st.sidebar.multiselect(
    "Combustível:",
    options=df["combustivel"].dropna().unique(),
    default=None
)

# Aplicar filtros
df_filtered = df.copy()

if marcas:
    df_filtered = df_filtered[df_filtered["marca"].isin(marcas)]

df_filtered = df_filtered[
    (df_filtered["ano_modelo"] >= anos[0]) & (df_filtered["ano_modelo"] <= anos[1])
]

if combustiveis:
    df_filtered = df_filtered[df_filtered["combustivel"].isin(combustiveis)]

st.sidebar.write(f"**Total de veículos filtrados:** {len(df_filtered)}")

# ---------- HISTOGRAMA ----------
st.subheader("📊 Distribuição de Preços")
variavel_hist = st.selectbox("Escolha a variável para o histograma:", ["marca", "combustivel", "condicao", "tipo"])
bins = st.slider("Número de divisões (bins):", 10, 100, 30)

fig_hist = px.histogram(
    df_filtered,
    x="price",
    color=variavel_hist,
    nbins=bins,
    title="Distribuição de Preços por " + variavel_hist.capitalize(),
    labels={"price": "Preço (USD)", variavel_hist: variavel_hist.capitalize()},
    color_discrete_sequence=px.colors.qualitative.Safe
)
st.plotly_chart(fig_hist, use_container_width=True)

# ---------- GRÁFICO DE DISPERSÃO ----------
st.subheader("💰 Relação entre Preço e Quilometragem")
colorir_por = st.selectbox("Colorir pontos por:", ["marca", "ano_modelo", "condicao"])
tamanho_por = st.selectbox("Tamanho do ponto por:", ["price", "quilometragem"])

scatter_fig = px.scatter(
    df_filtered,
    x="quilometragem",
    y="price",
    color=colorir_por if colorir_por in df_filtered.columns else "marca",
    size=tamanho_por,
    hover_data=["marca", "ano_modelo", "price"],
    labels={
        "quilometragem": "Quilometragem",
        "price": "Preço (USD)",
        "marca": "Marca",
        "ano_modelo": "Ano do Modelo"
    },
    title=f"Preço x Quilometragem ({colorir_por.capitalize()})",
    color_discrete_sequence=px.colors.qualitative.Safe
)
st.plotly_chart(scatter_fig, use_container_width=True)

# ---------- NOVOS GRÁFICOS: PREÇO x ANO ----------
st.subheader("📈 Relação entre Preço e Ano do Modelo")

# Gráfico geral
fig_year = px.scatter(
    df_filtered,
    x="ano_modelo",
    y="price",
    color="marca",
    hover_data=["marca", "quilometragem"],
    labels={
        "ano_modelo": "Ano do Modelo",
        "price": "Preço (USD)",
        "marca": "Marca"
    },
    title="Preço x Ano do Modelo (todos os veículos)",
    color_discrete_sequence=px.colors.qualitative.Safe
)
st.plotly_chart(fig_year, use_container_width=True)

# Separar novos e usados
if "quilometragem" in df_filtered.columns:
    novos = df_filtered[df_filtered["quilometragem"] == 0]
    usados = df_filtered[df_filtered["quilometragem"] > 0]

    st.subheader("🚗 Comparativo: Carros Novos (0 km) vs Usados")
    col_novo, col_usado = st.columns(2)

    with col_novo:
        if not novos.empty:
            fig_novos = px.scatter(
                novos,
                x="ano_modelo",
                y="price",
                color="marca",
                title="Carros Novos (0 km)",
                labels={"ano_modelo": "Ano do Modelo", "price": "Preço (USD)"},
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            st.plotly_chart(fig_novos, use_container_width=True)
        else:
            st.info("Não há carros com 0 km nos filtros atuais.")

    with col_usado:
        if not usados.empty:
            fig_usados = px.scatter(
                usados,
                x="ano_modelo",
                y="price",
                color="marca",
                title="Carros Usados",
                labels={"ano_modelo": "Ano do Modelo", "price": "Preço (USD)"},
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            st.plotly_chart(fig_usados, use_container_width=True)
        else:
            st.info("Não há carros usados nos filtros atuais.")