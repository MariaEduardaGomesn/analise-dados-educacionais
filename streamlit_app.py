import streamlit as st
import pandas as pd
import os
import plotly.express as px
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

# --- Configuração e Arquivos ---

# Configurações iniciais da página
st.set_page_config(layout="wide", page_title="Análise Educacional ES - Dashboard Otimizado")

# Nomes dos arquivos de dados (DEVE estar no mesmo diretório para o deploy)
FILE_PATH = "Taxa de rendimento_escolas estaduais.xlsx"
SHAPEFILE_PATH = "ES_Municipios_2023.shp"


# --- Funções de Carregamento e Processamento (Otimizadas com Cache) ---

@st.cache_data
def load_and_clean_data(path):
    """Carrega os dados do Excel e realiza o pré-processamento, ajustando nomes de colunas."""
    if not os.path.exists(path):
        st.error(f"O arquivo '{path}' não foi encontrado. Por favor, carregue o arquivo Excel.")
        return None

    try:
        # Carrega a aba "repasse" do novo arquivo
        df = pd.read_excel(path, sheet_name="repasse")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo Excel na aba 'repasse': {e}")
        return None

    # Colunas numéricas originais para limpeza
    numeric_cols_to_clean = ["repasse_total", "aprovacao", "ideb"]
    
    # Realiza a limpeza e conversão para numérico, tratando NaNs
    for col in numeric_cols_to_clean:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # NOTA: Não emitimos alerta para colunas não encontradas aqui para evitar poluição visual

    # Renomear colunas para o Dashboard, baseando-se no esquema da planilha
    df = df.rename(columns={
        "repasse_total": "Repasse Total (R$)",
        "aprovacao": "Taxa de Aprovação (%)",
        "ideb": "IDEB",
        "inep_id": "ID INEP",
        "ibge_id": "ID IBGE",
        "Municípios": "Município", 
        "Escola": "Nome da Escola",
        "ano": "Ano" # Adiciona renomeio para o Ano
    })
    
    # Aplica fillna APENAS nas colunas numéricas renomeadas
    renamed_numeric_cols = ["Repasse Total (R$)", "Taxa de Aprovação (%)", "IDEB"]
    cols_to_fill = [col for col in renamed_numeric_cols if col in df.columns]
    
    if cols_to_fill:
        mean_values = df[cols_to_fill].mean()
        df[cols_to_fill] = df[cols_to_fill].fillna(mean_values)

    return df

@st.cache_data
def load_and_merge_geodata(df_repasse, shapefile_path):
    """Carrega o shapefile, agrega os dados do repasse e faz a fusão geográfica."""
    
    if not os.path.exists(shapefile_path):
        return None

    try:
        # 1. Carregar Shapefile
        gdf = gpd.read_file(shapefile_path)
        # Garante que o código do município seja um inteiro de 6 dígitos
        gdf['CD_MUN'] = gdf['CD_MUN'].astype(str).str[:6].astype(int)
        
        # 2. Agregar Dados de Repasse por Município
        df_temp = df_repasse.copy()
        # Agregação usando o ID IBGE (que contém o código do município)
        # Use .mean() para todas as variáveis chave
        df_repasse_agg = df_temp.groupby('ID IBGE', as_index=False).agg(
            {'Repasse Total (R$)': 'mean', 'Taxa de Aprovação (%)': 'mean', 'IDEB': 'mean', 'Município': 'first'}
        )
        # Cria a coluna de fusão (6 dígitos)
        df_repasse_agg['CodMun'] = df_repasse_agg['ID IBGE'].astype(str).str[:6].astype(int)
        
        # 3. Fusão Geográfica (Merge)
        gdf_merged = gdf.merge(df_repasse_agg, left_on="CD_MUN", right_on="CodMun", how='left')
        gdf_merged = gdf_merged.fillna(0) # Preenche NaNs com 0 para visualização
        
        return gdf_merged

    except Exception as e:
        st.error(f"Erro ao carregar ou mesclar dados geográficos. Verifique a instalação do Geopandas e se todos os arquivos do shapefile estão presentes. Erro: {e}")
        return None
    
# Função para a simulação do modelo preditivo
def generate_and_plot_confusion_matrix(df):
    """Implementa a lógica de classificação simulada e plota a Matriz de Confusão."""
    
    # 1. Agrega dados por município (necessário para a simulação)
    df_merged_cleaned = df.groupby('Município', as_index=False).agg(
        {'Repasse Total (R$)': 'mean', 'Taxa de Aprovação (%)': 'mean', 'IDEB': 'mean'}
    )
    df_merged_cleaned = df_merged_cleaned.rename(columns={
        "Repasse Total (R$)": "Total_Repasse",
        "Taxa de Aprovação (%)": "Media_Aprovacao",
        "IDEB": "Nota_Ideb"
    })
    
    # 2. Definição das Classes e Geração de y_true (rótulos reais/observados)
    classes = ["Muito Baixo", "Baixo", "Médio", "Alto", "Muito Alto"]
    
    df_merged_cleaned['desempenho_real_composto'] = (
        (df_merged_cleaned['Media_Aprovacao'] / df_merged_cleaned['Media_Aprovacao'].max()) * 0.5 +
        (df_merged_cleaned['Nota_Ideb'] / df_merged_cleaned['Nota_Ideb'].max()) * 0.5
    )

    try:
        q_value = len(classes)
        df_merged_cleaned['desempenho_real_class'] = pd.qcut(
            df_merged_cleaned['desempenho_real_composto'], q=q_value, labels=False, duplicates='drop'
        )
    except ValueError:
        q_value = 3
        df_merged_cleaned['desempenho_real_class'] = pd.qcut(
            df_merged_cleaned['desempenho_real_composto'], q=q_value, labels=False, duplicates='drop'
        )

    unique_real_classes = sorted(df_merged_cleaned['desempenho_real_class'].dropna().unique())
    
    # 3. Gerar y_pred (rótulos previstos por um modelo simulado)
    df_merged_cleaned['simulated_score'] = (
        (df_merged_cleaned['Media_Aprovacao'] / df_merged_cleaned['Media_Aprovacao'].max()) * 0.4 +
        (df_merged_cleaned['Total_Repasse'] / df_merged_cleaned['Total_Repasse'].max()) * 0.2 +
        (df_merged_cleaned['Nota_Ideb'] / df_merged_cleaned['Nota_Ideb'].max()) * 0.4
    )

    np.random.seed(42)
    noise = np.random.normal(0, 0.05, len(df_merged_cleaned))
    df_merged_cleaned['simulated_score_noisy'] = df_merged_cleaned['simulated_score'] + noise

    try:
        df_merged_cleaned['desempenho_previsto_class'] = pd.qcut(
            df_merged_cleaned['simulated_score_noisy'], q=len(unique_real_classes), labels=False, duplicates='drop'
        )
    except ValueError as e:
        st.error(f"Erro ao simular classes previstas: {e}")
        return

    label_map = {label: unique_real_classes[i] for i, label in enumerate(sorted(df_merged_cleaned['desempenho_previsto_class'].dropna().unique()))}
    df_merged_cleaned['desempenho_previsto_class'] = df_merged_cleaned['desempenho_previsto_class'].map(label_map).fillna(unique_real_classes[0]).astype(int)

    df_final = df_merged_cleaned.dropna(subset=['desempenho_real_class', 'desempenho_previsto_class'])

    y_true_final = df_final['desempenho_real_class'].astype(int)
    y_pred_final = df_final['desempenho_previsto_class'].astype(int)
    
    if y_true_final.empty or y_pred_final.empty:
        st.warning("Dados insuficientes para gerar a Matriz de Confusão após a classificação. Verifique os dados de entrada.")
        return

    # 4. Matriz de Confusão e Plotagem
    
    

# Carrega e mescla dados
df_repasse = load_and_clean_data(FILE_PATH)
gdf_merged = load_and_merge_geodata(df_repasse, SHAPEFILE_PATH)

# Verificação crítica para continuar
if df_repasse is None:
    st.stop() # Interrompe a execução se o Excel não carregar


# --- Lógica de Navegação e Sidebar ---

if 'selecao' not in st.session_state:
    st.session_state.selecao = "Introdução"

st.sidebar.title("📚 Menu de Navegação")
st.sidebar.markdown("---")

# Seção "Dashboard Interativo" adicionada
secoes = ["Introdução","Visualização de dados", "Análise Exploratória"]

# Cria botões de navegação
for secao in secoes:
    if st.sidebar.button(secao, key=secao, use_container_width=True):
        st.session_state.selecao = secao

st.sidebar.markdown("---")


# --- Conteúdo do Aplicativo ---

selecao = st.session_state.selecao

if selecao == "Introdução":
    st.title("Painel de Análise Educacional - Espírito Santo")
    st.markdown("---")

    st.markdown("""
    Bem-vindo ao Dashboard Interativo que analisa o **desempenho escolar** e o **investimento** nas escolas estaduais do Espírito Santo.

    Neste painel, você pode:
    - **Visualizar:** A distribuição geográfica dos recursos e do desempenho (IDEB).
    - **Explorar:** A correlação entre Repasse Total, IDEB e Taxa de Aprovação (%).
    - **Filtrar:** Utilizar o novo **Dashboard Interativo** para análises segmentadas.
    """)
    
    st.info("Utilize o **Menu de Navegação** na barra lateral para acessar as visualizações e análises.")
    st.subheader("Amostra da Base de Dados")
    # Tabela descritiva da base de dados (primeiras 5 linhas)
    st.dataframe(df_repasse.head(), use_container_width=True)


elif selecao == "Análise Exploratória":
    st.title("📊 Análise Estatística e Descritiva")
    st.markdown("---")
    
    df_ana = df_repasse[['Repasse Total (R$)', 'Taxa de Aprovação (%)', 'IDEB', 'Município']]
    
    # --- 1. Estatísticas Descritivas (describe() aprimorado) ---
    st.subheader("1. Estatísticas Descritivas Detalhadas")

    descr = df_ana[['Repasse Total (R$)', 'Taxa de Aprovação (%)', 'IDEB']].describe(percentiles=[.25, .5, .75, .90]).transpose().round(2)
    descr["CV (%)"] = (descr["std"] / descr["mean"]) * 100
    descr = descr.round(2)

    st.dataframe(descr, use_container_width=True)
    st.markdown("---")
    
    # --- 3. Top 10 Municípios por IDEB ---
    st.subheader("3. Top 10 Municípios por IDEB Médio")
    df_top_ideb = df_repasse.groupby('Município', as_index=False)['IDEB'].mean().sort_values(by='IDEB', ascending=False).head(10)
    
    fig_top = px.bar(
        df_top_ideb,
        x='Município',
        y='IDEB',
        title='10 Municípios com Maior IDEB Médio',
        color='IDEB',
        color_continuous_scale=px.colors.sequential.Agsunset,
        template="plotly_white"
    )
    st.plotly_chart(fig_top, use_container_width=True)
    st.markdown("---")

        # --- 3. Top 10 Municípios por Repasse Médio (NOVO) ---
    st.subheader("3. Top 10 Municípios por Repasse Total Médio")
    df_top_repasse = df_repasse.groupby('Município', as_index=False)['Repasse Total (R$)'].mean().sort_values(by='Repasse Total (R$)', ascending=False).head(10)
    
    fig_top_repasse = px.bar(
        df_top_repasse,
        x='Município',
        y='Repasse Total (R$)',
        title='10 Municípios com Maior Repasse Total Médio (R$)',
        color='Repasse Total (R$)',
        color_continuous_scale=px.colors.sequential.Plasma,
        template="plotly_white"
    )
    # Formata o eixo Y para exibir moeda
    fig_top_repasse.update_layout(yaxis_tickprefix = 'R$ ', yaxis_tickformat = ',.0f')
    
    st.plotly_chart(fig_top_repasse, use_container_width=True)
    st.markdown("---")

elif selecao == "Visualização de dados":
    st.title("🎚️ Visualização de dados")
    st.markdown("---")
    
    # --- Sidebar de Filtros ---
    st.sidebar.markdown("## ⚙️ Filtros Interativos")
    
    # Filtro 1: Município
    municipios = ['Todos'] + sorted(df_repasse['Município'].unique().tolist())
    municipio_selecionado = st.sidebar.selectbox("Selecione o Município:", municipios)
    
    # Filtro 2: Faixa de IDEB
    min_ideb = float(df_repasse['IDEB'].min().round(1))
    max_ideb = float(df_repasse['IDEB'].max().round(1))
    ideb_range = st.sidebar.slider(
        "Faixa de IDEB:",
        min_value=min_ideb,
        max_value=max_ideb,
        value=(min_ideb, max_ideb),
        step=0.1
    )
    
    # Aplicação dos Filtros
    df_filtrado = df_repasse.copy()
    
    if municipio_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Município'] == municipio_selecionado]
        
    df_filtrado = df_filtrado[
        (df_filtrado['IDEB'] >= ideb_range[0]) & 
        (df_filtrado['IDEB'] <= ideb_range[1])
    ]
    
    if df_filtrado.empty:
        st.warning("Nenhuma escola corresponde aos filtros selecionados. Tente ajustar os parâmetros.")
        st.stop()
    
    # --- Métricas Principais (KIPs) ---
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Escolas Filtradas", len(df_filtrado))
    col2.metric("Média de IDEB", f"{df_filtrado['IDEB'].mean():.2f}", delta=f"Max: {df_filtrado['IDEB'].max():.2f}")
    col3.metric("Média de Repasse Total (R$)", f"R$ {df_filtrado['Repasse Total (R$)'].mean():,.2f}")
    
    st.markdown("---")
    
    # --- Gráficos do Dashboard ---
    
    # 1. Mapa Geográfico (Apenas se não houver filtro de município)
    if municipio_selecionado == 'Todos' and gdf_merged is not None:
        st.subheader("1. Distribuição Geográfica de Repasse por Município")
        try:
            # Filtrar o GDF para corresponder à faixa de IDEB para o mapa
            gdf_filtrado = gdf_merged[
                (gdf_merged['IDEB'] >= ideb_range[0]) & 
                (gdf_merged['IDEB'] <= ideb_range[1])
            ]
            
            # Ajuste de zoom e centralização para o estado
            fig_map = px.choropleth_mapbox(
                gdf_filtrado,
                geojson=gdf_filtrado.geometry.__geo_interface__,
                locations=gdf_filtrado.index,
                color="Repasse Total (R$)", # Cor por Repasse Total
                hover_name="NM_MUN",
                hover_data={"IDEB": True, "Repasse Total (R$)": True, "Taxa de Aprovação (%)": True},
                color_continuous_scale="Viridis",
                mapbox_style="carto-positron",
                zoom=6.8, # Ajuste para que o mapa apareça por inteiro
                center={"lat": -20.0, "lon": -40.5},
                opacity=0.7,
                title="Repasse Total, IDEB e Aprovação por Município"
            )
            # Remove margens para visualização mais limpa
            fig_map.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0}) 
            st.plotly_chart(fig_map, use_container_width=True)
            st.markdown("---")
        except Exception as e:
            st.warning(f"Não foi possível gerar o mapa geográfico com os filtros: {e}")
    
    # 2. Relação Repasse vs Desempenho (Filtrado)
    st.subheader("2. Relação entre Investimento e Desempenho")
    
    fig_scatter = px.scatter(
        df_filtrado, 
        x='Repasse Total (R$)', 
        y='Taxa de Aprovação (%)',
        color='IDEB',
        size='IDEB',
        hover_data=['Município', 'Nome da Escola'],
        title='Taxa de Aprovação vs Repasse Total (Colorido e Tamanho por IDEB)',
        template="plotly_white",
        log_x=True # Ajuda a visualizar repasses com grande dispersão
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("---")
    
    # 3. Histograma de IDEB 
    st.subheader("3. Distribuição do IDEB para Escolas")
    fig_hist = px.histogram(
        df_filtrado, 
        x='IDEB', 
        nbins=20, 
        title='Distribuição da Nota IDEB',
        template="seaborn",
        color_discrete_sequence=['teal']
    )
    st.plotly_chart(fig_hist, use_container_width=True)
