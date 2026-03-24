# IA Generativa, RAG com Qdrant e API
# Módulo da Interface Web e Consulta à API

import re
import streamlit as st
import requests
import json
import warnings
warnings.filterwarnings('ignore')

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================

st.set_page_config(page_title="CV - Ulisses", page_icon=":100:", layout="centered")

# ==============================
# SIDEBAR (TECNOLOGIAS DO PROJETO)
# ==============================

with st.sidebar:

    st.markdown("### Tecnologias do Projeto")
    st.markdown("---")

    st.markdown("""
**RAG (Retrieval-Augmented Generation)**  
Técnica que combina busca em documentos com IA generativa para produzir respostas mais precisas.

**Qdrant**  
Banco de dados vetorial utilizado para armazenar embeddings e permitir busca semântica eficiente.

**Docker**  
Ferramenta de containerização usada para rodar os serviços do projeto de forma isolada e reproduzível.

**Streamlit**  
Framework Python utilizado para criar rapidamente a interface web interativa do projeto.

**FastAPI**  
Framework moderno para construção da API que conecta a interface ao sistema de RAG.

**Cloudflare Tunnel**  
Permite expor a aplicação local de forma segura na internet sem necessidade de abrir portas no roteador.
""")

    st.markdown("---")
    st.caption("Projeto de demonstração de IA com RAG")

# ==============================
# TÍTULO PRINCIPAL
# ==============================

st.title("CV Interativo — Ulisses Cuani")

st.subheader(
"Assistente de IA que responde perguntas sobre o currículo de Ulisses."
)

# ==============================
# EXEMPLOS DE PERGUNTAS
# ==============================

st.markdown("### Exemplos rápidos")

if "input_question" not in st.session_state:
    st.session_state.input_question = ""

if st.button("Quais são as formações acadêmicas do Ulisses?", use_container_width=True):
    st.session_state.input_question = "Quais são as formações acadêmicas do Ulisses?"

if st.button("Quantos anos de experiência profissional ele possui?", use_container_width=True):
    st.session_state.input_question = "Quantos anos de experiência profissional ele possui?"

if st.button("Quais projetos acadêmicos ou profissionais ele já desenvolveu?", use_container_width=True):
    st.session_state.input_question = "Quais projetos acadêmicos ou profissionais ele já desenvolveu?"

# ==============================
# FORMULÁRIO (ENTER + BOTÃO)
# ==============================

with st.form("question_form"):

    question = st.text_input(
        "Digite uma pergunta sobre o currículo de Ulisses:",
        key="input_question",
        placeholder="Exemplo: Quais são as experiências profissionais do Ulisses?"
    )

    submitted = st.form_submit_button("Enviar")

# ==============================
# PROCESSAMENTO DA PERGUNTA
# ==============================

if submitted and st.session_state.input_question:

    question = st.session_state.input_question

    st.write(f'A pergunta foi: "{question}"')

    url = "http://127.0.0.1:8000/api"

    payload = json.dumps({"query": question})

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data=payload)

    answer = json.loads(response.text)["answer"]

    rege = re.compile("\[Document\ [0-9]+\]|\[[0-9]+\]")

    m = rege.findall(answer)

    num = []

    for n in m:
        num = num + [int(s) for s in re.findall(r'\b\d+\b', n)]

    st.markdown(answer)

    documents = json.loads(response.text)['context']

    show_docs = []

    for n in num:
        for doc in documents:
            if int(doc['id']) == n:
                show_docs.append(doc)

    id = 12991345567899999

    for doc in show_docs:

        with st.expander(str(doc['id'])+" - "+doc['path']):

            st.write(doc['content'])

            with open(doc['path'], 'rb') as f:

                st.download_button(
                    "Download do Arquivo",
                    f,
                    file_name = doc['path'].split('/')[-1],
                    key = id
                )

                id = id + 1