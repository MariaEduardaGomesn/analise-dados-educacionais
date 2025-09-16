import streamlit as st

# Menu de navegação
secoes = ["Introdução", "Visualização de Dados", "Análise Exploratória", "Modelos Preditivos (futuro)"]
selecao = st.sidebar.selectbox("Navegue pelo app", secoes)

if selecao == "Introdução":
    # Título, autoria e tema - Agora exibidos somente na Introdução
    st.title("Análise de Dados Educacionais das Escolas Estaduais do Espírito Santo")
    st.subheader("Por: Maria Eduarda Gomes")
    st.markdown("Este projeto tem como objetivo explorar dados educacionais públicos para gerar insights úteis sobre o sistema educacional do Estado do Espírito Santo.")
    st.markdown("""
    Este é um protótipo de aplicação desenvolvida com **Streamlit** para a disciplina de Cloud Computing na pós-graduação em Mineração de Dados.
    O foco do projeto é aplicar técnicas de mineração de dados no contexto da **educação do estado do Espírito Santo**.
    """)

    # Bases de dados - Também movidas para a seção de Introdução para manter a coerência
    st.markdown("### Fontes de dados previstas:")
    st.markdown("""
    - INEP (Instituto Nacional de Estudos e Pesquisas Educacionais)
    - Censo Escolar
    - SAEB
    - Dados abertos da SEDU
    """)
    
elif selecao == "Visualização de Dados":
    st.write("Em breve, gráficos interativos com dados educacionais serão exibidos aqui.")

elif selecao == "Análise Exploratória":
    st.write("Em breve, funcionalidades para análise exploratória de dados serão implementadas.")

elif selecao == "Modelos Preditivos (futuro)":
    st.write("Em breve, modelos preditivos baseados em machine learning serão adicionados.")
