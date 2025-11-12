# ----------- IMPORTAÇÕES -----------
import streamlit as st
import pandas as pd
import plotly.express as px


# ----------- CONFIGURAÇÕES INICIAIS -----------
st.set_page_config(
    page_title="Projeto Sprint 5 - Dashboard US Vehicles",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Projeto Sprint 5 - Dashboard US Vehicles")
st.markdown(
    """
    **O que é este projeto?**  
    Dashboard interativo para explorar anúncios de veículos dos EUA.  
    Use os filtros na barra lateral para ajustar os dados e veja os indicadores e gráficos atualizarem em tempo real.
    """
)


# ----------- CARREGAR OS DADOS -----------
@st.cache_data
def load_data():
    df = pd.read_csv("data/vehicles.csv")
    df.rename(columns={
        "price": "preco",
        "model_year": "ano_modelo",
        "model": "modelo",
        "condition": "condicao",
        "cylinders": "cilindros",
        "fuel": "combustivel",
        "odometer": "quilometragem",
        "transmission": "transmissao",
        "type": "tipo",
        "paint_color": "cor",
        "is_4wd": "tracao_4wd",
        "date_posted": "data_postagem",
        "days_listed": "dias_anuncio"
    }, inplace=True)

    # cria a coluna 'marca' a partir da primeira palavra do modelo
    if "modelo" in df.columns:
        df["marca"] = df["modelo"].astype(str).str.split().str[0]
    elif "model_name" in df.columns:
        df["marca"] = df["model_name"].astype(str).str.split().str[0]
    else:
        st.error("Nenhuma coluna de modelo encontrada no dataset.")
        st.stop()

    return df


df = load_data()


# ----------- FILTROS LATERAIS -----------
st.sidebar.header("Filtros")

min_year, max_year = int(df["ano_modelo"].min()), int(df["ano_modelo"].max())
min_price, max_price = int(df["preco"].dropna().min()), int(df["preco"].dropna().max())
min_odometer, max_odometer = int(df["quilometragem"].dropna().min()), int(df["quilometragem"].dropna().max())

ano_range = st.sidebar.slider("Ano do modelo", min_year, max_year, (min_year, max_year))
preco_range = st.sidebar.slider("Faixa de preço (USD)", min_price, max_price, (min_price, 50000))
km_max = st.sidebar.slider("Quilometragem máxima", min_odometer, max_odometer, max_odometer)

marcas = st.sidebar.multiselect(
    "Selecione as marcas:",
    options=sorted(df["marca"].dropna().unique()),
    default=None
)

df_filtrado = df[
    (df["ano_modelo"].between(ano_range[0], ano_range[1])) &
    (df["preco"].between(preco_range[0], preco_range[1])) &
    (df["quilometragem"] <= km_max)
].copy()

if marcas:
    df_filtrado = df_filtrado[df_filtrado["marca"].isin(marcas)]


# ----------- MÉTRICAS / KPIs -----------
st.markdown("### Visão geral dos dados filtrados")

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    preco_medio = int(df_filtrado["preco"].mean()) if not df_filtrado.empty else 0
    st.metric("Preço médio (USD)", f"${preco_medio:,}")

with kpi2:
    km_medio = int(df_filtrado["quilometragem"].mean()) if not df_filtrado.empty else 0
    st.metric("Quilometragem média", f"{km_medio:,} km")

with kpi3:
    qtd = len(df_filtrado)
    st.metric("Veículos exibidos", f"{qtd:,}")

st.write(f"Total de registros filtrados: **{len(df_filtrado):,}** de {len(df):,}.")


# ----------- DOWNLOAD CSV -----------
csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar dados filtrados (CSV)", csv, "vehicles_filtered.csv", "text/csv")


# ----------- BOTÃO PARA MOSTRAR GRÁFICOS -----------
st.markdown("### Visualizações interativas")

mostrar_graficos = st.button("📊 Mostrar Gráficos")

if mostrar_graficos:
    left_col, right_col = st.columns((2, 1))

    with left_col:
        st.subheader("Preço vs Quilometragem (Dispersão)")
        color_by = st.selectbox("Colorir por:", options=["marca", "ano_modelo", "condicao"], index=0)
        size_by = st.selectbox("Tamanho do ponto por:", options=["preco", "quilometragem"], index=0)

        scatter_fig = px.scatter(
            df_filtrado,
            x="quilometragem",
            y="preco",
            color=color_by if color_by in df_filtrado.columns else None,
            size=size_by if size_by in df_filtrado.columns else None,
            hover_data=["modelo", "ano_modelo", "preco"],
            labels={"quilometragem": "Quilometragem", "preco": "Preço (USD)"},
            title="Preço x Quilometragem"
        )
        st.plotly_chart(scatter_fig, use_container_width=True)

    with right_col:
        st.subheader("Distribuição de Preço (Histograma)")
        bins = st.slider("Número de intervalos (bins)", 10, 120, 50)
        hist_fig = px.histogram(
            df_filtrado,
            x="preco",
            nbins=bins,
            title="Histograma de Preço"
        )
        st.plotly_chart(hist_fig, use_container_width=True)

    # ----------- NOVOS GRÁFICOS: Preço x Ano -----------
    st.markdown("---")
    st.subheader("💲 Preço Médio por Ano — Carros Novos e Usados")

    novos = df_filtrado[df_filtrado["quilometragem"] <= 5000]
    usados = df_filtrado[df_filtrado["quilometragem"] > 5000]

    fig_novos = px.scatter(
        novos,
        x="ano_modelo",
        y="preco",
        color="marca",
        title="Preço por Ano — Carros Novos (até 5.000 km)",
        labels={"ano_modelo": "Ano do Modelo", "preco": "Preço (USD)"}
    )
    st.plotly_chart(fig_novos, use_container_width=True)

    fig_usados = px.scatter(
        usados,
        x="ano_modelo",
        y="preco",
        color="marca",
        title="Preço por Ano — Carros Usados",
        labels={"ano_modelo": "Ano do Modelo", "preco": "Preço (USD)"}
    )
    st.plotly_chart(fig_usados, use_container_width=True)

else:
    st.info("Clique no botão acima para gerar as visualizações 📈")


# ----------- INFORMAÇÕES EXTRAS -----------
with st.expander("ℹ️ Dicas e observações"):
    st.markdown(
        """
        - **Dica 1:** Use o filtro por ano e preço para observar tendências de mercado.  
        - **Dica 2:** As marcas são derivadas automaticamente do nome do modelo.  
        - **Dica 3:** Os gráficos ajudam a visualizar padrões de depreciação por marca e condição.  
        """
    )

st.markdown("---")
st.caption("Desenvolvido como parte do Projeto Sprint 5 — estudo TripleTen. Dashboard educativo.")
