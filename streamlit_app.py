import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Caminho do arquivo Excel (lembre de subir este arquivo na pasta do projeto!)
file_path = "Taxa de rendimento_escolas estaduais.xlsx"

# Verifica se o arquivo existe
if not os.path.exists(file_path):
    st.error(f"O arquivo '{file_path}' não foi encontrado. Verifique se o nome está correto e se o arquivo foi enviado.")
    st.stop()

# Leitura da aba 'repasse'
df_repasse = pd.read_excel(file_path, sheet_name="repasse")

# Convertendo as colunas para numérico e tratando NaNs
for col in ["repasse_total", "aprovacao", "ideb"]:
    df_repasse[col] = pd.to_numeric(df_repasse[col], errors='coerce')
    mean_value = df_repasse[col].mean()
    df_repasse[col].fillna(mean_value, inplace=True)

# Menu lateral
secoes = ["Introdução", "Visualização de Dados", "Análise Exploratória", "Modelos Preditivos (futuro)"]
selecao = st.sidebar.selectbox("Navegue pelo app", secoes)

if selecao == "Introdução":
    st.title("Análise de Dados Educacionais das Escolas Estaduais do Espírito Santo")
    st.subheader("Por: Maria Eduarda Gomes")

    st.markdown("Este projeto tem como objetivo analisar dados públicos relacionados ao rendimento escolar e aos investimentos realizados por meio dos repasses financeiros do Programa Estadual de Gestão Financeira Escolar (PROGEFE) no sistema educacional do Estado do Espírito Santo.")
    st.markdown("""
    A iniciativa consiste no desenvolvimento de um protótipo de aplicação utilizando Streamlit, como parte da disciplina de Cloud Computing do curso de pós-graduação em Mineração de Dados. O foco está na aplicação de técnicas de mineração de dados para explorar e compreender o contexto educacional capixaba, buscando identificar possíveis correlações entre os investimentos escolares e o desempenho dos alunos.
    """)

    st.markdown("### Fontes de dados previstas:")
    st.markdown("""
    - INEP (Instituto Nacional de Estudos e Pesquisas Educacionais)
    - Censo Escolar
    - SAEB
    - Dados abertos da SEDU
    """)

elif selecao == "Visualização de Dados":
    st.title("Visualização de Dados")

    st.subheader("Prévia dos Dados")
    st.dataframe(df_repasse.head())

    st.markdown("### Histogramas")

    # Histograma da Média de Aprovação
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.histplot(df_repasse['aprovacao'], kde=True, ax=ax1)
    ax1.set_title('Distribuição da Média de Aprovação por Município')
    ax1.set_xlabel('Média de Aprovação (%)')
    ax1.set_ylabel('Frequência')
    st.pyplot(fig1)

    # Histograma do Total de Repasse
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.histplot(df_repasse['repasse_total'], kde=True, ax=ax2)
    ax2.set_title('Distribuição do Total de Repasse por Município')
    ax2.set_xlabel('Total de Repasse')
    ax2.set_ylabel('Frequência')
    st.pyplot(fig2)

    # Histograma da Nota IDEB
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sns.histplot(df_repasse['ideb'], kde=True, color='purple', ax=ax3)
    ax3.set_title('Distribuição da Nota IDEB por Município')
    ax3.set_xlabel('Nota IDEB')
    ax3.set_ylabel('Frequência')
    st.pyplot(fig3)

    st.markdown("### Gráficos de Dispersão")

    # Scatter plot da Média de Aprovação vs Total de Repasse
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df_repasse, x='repasse_total', y='aprovacao', ax=ax4)
    ax4.set_title('Média de Aprovação vs Total de Repasse por Município')
    ax4.set_xlabel('Total de Repasse')
    ax4.set_ylabel('Média de Aprovação (%)')
    st.pyplot(fig4)

    # Scatter plot da Nota IDEB vs Média de Aprovação
    fig5, ax5 = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df_repasse, x='aprovacao', y='ideb', color='green', ax=ax5)
    ax5.set_title('Nota IDEB vs Média de Aprovação por Município')
    ax5.set_xlabel('Média de Aprovação (%)')
    ax5.set_ylabel('Nota IDEB')
    st.pyplot(fig5)

    # Scatter plot da Nota IDEB vs Total de Repasse
    fig6, ax6 = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df_repasse, x='repasse_total', y='ideb', color='orange', ax=ax6)
    ax6.set_title('Nota IDEB vs Total de Repasse por Município')
    ax6.set_xlabel('Total de Repasse')
    ax6.set_ylabel('Nota IDEB')
    st.pyplot(fig6)

elif selecao == "Análise Exploratória":
    st.title("📊 Análise Exploratória dos Dados")
    st.subheader("📌 Estatísticas Descritivas das Variáveis")

    # Traduz colunas para exibição (opcional)
    df_display = df_repasse.rename(columns={
        "ano": "Ano",
        "inep_id": "ID INEP",
        "ibge_id": "ID IBGE",
        "repasse_total": "Repasse Total (R$)",
        "aprovacao": "Taxa de Aprovação (%)",
        "ideb": "IDEB"
    })

    # Calcula estatísticas descritivas
    descr = df_display.describe().transpose()

    # Adiciona coeficiente de variação
    descr["CV (%)"] = (descr["std"] / descr["mean"]) * 100
    descr = descr.round(2)  # arredonda para melhor visualização

    # Mostra estatísticas em tabela interativa
    st.dataframe(descr, use_container_width=True)

    # Insights automáticos (exemplo simples)
    st.markdown("### 🔍 Insights Automáticos")
    media_ideb = descr.loc["IDEB", "mean"]
    std_ideb = descr.loc["IDEB", "std"]
    max_ideb = descr.loc["IDEB", "max"]
    min_ideb = descr.loc["IDEB", "min"]

    st.markdown(f"""
    - A média do IDEB é **{media_ideb}**, com desvio padrão de **{std_ideb}**.
    - O valor mínimo do IDEB é **{min_ideb}** e o máximo é **{max_ideb}**.
    - A variável com maior variação relativa é **{descr['CV (%)'].idxmax()}** (**{descr['CV (%)'].max():.2f}%**).
    """)


elif selecao == "Modelos Preditivos (futuro)":
    st.title("Modelos Preditivos")
    st.write("Em breve, modelos preditivos baseados em machine learning serão adicionados.")
