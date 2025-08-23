import streamlit as st

# Título e autoria
st.title("Análise de Dados Educacionais das Escolas Estaduais do Espírito Santo")
st.subheader("Por: Maria Eduarda Gomes")

# Tema
st.markdown("Este projeto tem como objetivo explorar dados educacionais públicos para gerar insights úteis sobre o sistema educacional do Estado do Espírito Santo.")

# Menu de navegação
secoes = ["Introdução", "Visualização de Dados", "Análise Exploratória", "Modelos Preditivos (futuro)"]
selecao = st.sidebar.selectbox("Navegue pelo app", secoes)

if selecao == "Introdução":
    st.markdown("""
    Este é um protótipo de aplicação desenvolvida com **Streamlit** para a disciplina de Cloud Computing na pós-graduação em Mineração de Dados.  
    O foco do projeto é aplicar técnicas de mineração de dados no contexto da **educação do estado do Espírito Santo**.
    """)
    
elif selecao == "Visualização de Dados":
    st.write("Em breve, gráficos interativos com dados educacionais serão exibidos aqui.")

elif selecao == "Análise Exploratória":
    st.write("Esta seção apresentará estatísticas descritivas e insights sobre os dados educacionais.")

elif selecao == "Modelos Preditivos (futuro)":
    st.write("Aqui serão aplicados modelos para prever indicadores educacionais com base em dados históricos.")

# Bases de dados
st.markdown("### Fontes de dados previstas:")
st.markdown("""
- INEP (Instituto Nacional de Estudos e Pesquisas Educacionais)
- Censo Escolar
- SAEB
- Dados abertos da SEDU
""")
