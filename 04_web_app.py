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

st.set_page_config(page_title="CV - Ulisses", page_icon=":brain:", layout="centered")

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

    st.write(f'Pergunta: "{question}"')

    url = "http://127.0.0.1:8000/api"

    # payload = json.dumps({"query": question}) # GROQ
    payload = {"query": question}
    try:
        response = requests.post(url, json=payload, timeout=30)

        # 🔍 Verifica erro HTTP (ex: 429, 500, etc)
        if response.status_code != 200:

            if response.status_code == 429:
                st.warning("⚠️ Você atingiu o limite de requisições. Tente novamente em instantes.")
            
            elif response.status_code >= 500:
                st.error("🚨 O servidor ou o modelo de IA está indisponível no momento.")

            else:
                st.error(f"Erro na requisição: {response.status_code}")
                st.write(response.text)

        else:
            data = response.json()
            answer = data.get("answer", "Sem resposta.")
            st.markdown(f"**Assistente de IA:** {answer}")

    # 🔌 API fora do ar / conexão recusada
    except requests.exceptions.ConnectionError:
        st.error("🚨 Não foi possível conectar à API. Verifique se o backend está rodando.")

    # ⏱ Timeout (modelo demorou demais)
    except requests.exceptions.Timeout:
        st.warning("⏳ A resposta demorou muito. Tente novamente.")

    # ❌ JSON inválido (seu erro atual)
    except requests.exceptions.JSONDecodeError:
        st.error("⚠️ A resposta da IA veio em formato inválido. Pode ser instabilidade no modelo.")

    # 🧠 Qualquer outro erro
    except Exception as e:
        st.error(f"Erro inesperado: {e}")