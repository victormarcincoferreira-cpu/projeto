import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Projeto Sprint 5 - Dashboard Us Vehicles",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Projeto Sprint 5 - Dashboard Us Vehicles")
st.markdown(
    """
    **O que é este projeto?**  
    Pequeno dashboard interativo para explorar anúncios de veículos dos EUA.
    Use os filtros na barra lateral para ajustar o conjunto de dados e veja KPIs + gráficos atualizarem em tempo real.
    """
)

@st.cache_data
def load_data(path: str):
    df = pd.read_csv(path)
    df = df.drop_duplicates().reset_index(drop=True)
    return df

DATA_PATH = "data/vehicles.csv" 
df = load_data(DATA_PATH)

st.sidebar.header("Filtros")

min_year, max_year = int(df['model_year'].min()), int(df['model_year'].max())
min_price, max_price = int(df['price'].dropna().min()), int(df['price'].dropna().max())
min_odometer, max_odometer = int(df['odometer'].dropna().min()), int(df['odometer'].dropna().max())

year_range = st.sidebar.slider("Ano (year)", min_year, max_year, (min_year, max_year))
price_range = st.sidebar.slider("Preço (price) — $", min_price, max_price, (min_price, min(max_price, 50000)))
odometer_max = st.sidebar.slider("Quilometragem máxima (odometer)", min_odometer, max_odometer, max_odometer)

df_filtered = df[
    (df['model_year'] >= year_range[0]) & (df['model_year'] <= year_range[1]) &
    (df['price'] >= price_range[0]) & (df['price'] <= price_range[1]) &
    (df['odometer'] <= odometer_max)
].copy()

st.markdown("### Visão geral")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    avg_price = int(df_filtered['price'].dropna().mean()) if not df_filtered['price'].dropna().empty else 0
    st.metric("Preço médio (USD)", f"${avg_price:,}")

with kpi2:
    avg_km = int(df_filtered['odometer'].dropna().mean()) if not df_filtered['odometer'].dropna().empty else 0
    st.metric("Quilometragem média", f"{avg_km:,} km")

with kpi3:
    avg_year = int(df_filtered['model_year'].dropna().mean()) if not df_filtered['model_year'].dropna().empty else 0
    st.metric("Ano médio", f"{avg_year}")

st.write(f"Resultados filtrados: **{len(df_filtered):,}** linhas (de {len(df):,})")

csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button("📥 Baixar dados filtrados (CSV)", csv, "vehicles_filtered.csv", "text/csv")

st.markdown("### Visualizações interativas")

left_col, right_col = st.columns((2, 1))

with left_col:
    st.subheader("Preço vs Quilometragem (scatter)")
    # escolha de cor / tamanho
    color_by = st.selectbox("Colorir por:", options=['model_year', 'condition'] if 'condition' in df.columns else ['year', 'make'], index=0)
    size_by = st.selectbox("Tamanho do ponto por:", options=['price', 'odometer'], index=0)

    scatter_fig = px.scatter(
        df_filtered,
        x="odometer",
        y="price",
        color=color_by if color_by in df_filtered.columns else None,
        size=size_by if size_by in df_filtered.columns else None,
        hover_data=["model", "model_year", "price"],
        labels={"odometer": "Quilometragem", "price": "Preço (USD)"},
        title="Preço x Quilometragem"
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

with right_col:
    st.subheader("Distribuição de Preço (histograma)")
    bins = st.slider("Número de bins", 10, 120, 50)
    hist_fig = px.histogram(df_filtered, x="price", nbins=bins, title="Histograma de Preço")
    st.plotly_chart(hist_fig, use_container_width=True)

# ---------- Explicação / detalhes para quem está estudando ----------
with st.expander("Sobre este dataset e sugestões de exploração (clique para abrir)"):
    st.markdown(
        """
        - **Dica 1:** Compare modelos por preço médio.  
        - **Dica 2:** Use o filtro por ano para ver tendências temporais.  
        - **Dica 3:** Atenção a outliers (preços muito baixos ou quilometragens estranhas).  
        - **Objetivo do estudo:** preparar um case visual e limpo para apresentar seu entendimento do dataset.
        """
    )


# ---------- footer / créditos ----------
st.markdown("---")
st.caption("Desenvolvido como parte do Projeto Sprint 5 — estudo TripleTen. Dashboard educativo + estilo produto.")