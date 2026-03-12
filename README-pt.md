# RAG CV Assistant 🤖📄

Este projeto implementa um sistema de **Retrieval-Augmented Generation (RAG)** para consulta inteligente em documentos profissionais (Currículos, Teses, Artigos e Cartas de Apresentação). Ele permite que você "converse" com seus documentos usando IA generativa.

## 🚀 Como Funciona?

O fluxo do projeto é dividido em três etapas principais:
1.  **Indexação**: Seus documentos (.pdf, .docx, .pptx, .txt) são processados, divididos em partes e transformados em vetores (embeddings) armazenados no banco de dados **Qdrant**.
2.  **API**: Um servidor **FastAPI** que recebe perguntas, busca o contexto mais relevante no banco vetorial e consulta um LLM (via **Groq**) para gerar uma resposta precisa.
3.  **Interface Web**: Uma aplicação **Streamlit** amigável para interagir com o assistente.

---

## 🛠️ Tecnologias Utilizadas

-   **Linguagem**: Python 3.x
-   **Banco Vetorial**: [Qdrant](https://qdrant.tech/)
-   **IA/LLM**: Groq (Llama 3 ou similar)
-   **Frameworks**: FastAPI, Streamlit, LangChain
-   **Embeddings**: HuggingFace (`msmarco-bert-base-dot-v5`)

---

## 📋 Pré-requisitos

-   Python instalado.
-   Docker instalado (para rodar o Qdrant).
-   Chave de API da [Groq](https://console.groq.com/).

---

## ⚙️ Configuração e Instalação

### 1. Ambiente Virtual
Crie e ative um ambiente virtual para manter as dependências isoladas:
```bash
python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No Linux/Mac:
source .venv/bin/activate
```

### 2. Dependências
Instale os pacotes necessários:
```bash
pip install -r requirements.txt
```

### 3. Banco de Dados (Qdrant)
Inicie o container do Qdrant usando Docker:
```bash
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
```

### 4. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com sua chave da Groq:
```env
GROQ_API_KEY=sua_chave_aqui
```

---

## 🏃 Como Executar

Siga estas etapas em ordem:

### Passo 1: Indexar Documentos
Coloque seus arquivos na pasta `documents/` (crie-a se não existir) e execute:
```bash
python 01_rag.py documents
```

### Passo 2: Iniciar a API
Em um novo terminal (com o ambiente ativado), inicie o servidor backend:
```bash
python 03_start_api.py
```

### Passo 3: Iniciar a Interface Web
Em outro terminal, execute o Streamlit:
```bash
streamlit run 04_web_app.py
```

---

## ⚡ Execução Rápida (Para quem já conhece o projeto)

Use estes comandos em terminais separados para rodar o projeto rapidamente:

**Terminal 1: Docker e API**
```bash
docker start vector_db
python 03_start_api.py
```

**Terminal 2: Streamlit (Front-end)**
```bash
streamlit run 04_web_app.py
```

**Terminal 3: Cloudflared (Expor a aplicação)**
```bash
cloudflared tunnel --url http://127.0.0.1:8501
```

---

## 💡 Exemplos de Perguntas
-   "Quais são as principais experiências acadêmicas do Ulisses?"
-   "O Ulisses tem experiência com Python e IA?"
-   "Resuma as conquistas profissionais listadas no currículo."

---

## 📂 Estrutura do Projeto
-   `01_rag.py`: Script para leitura de arquivos e população do banco vetorial.
-   `02_api.py`: Lógica central da API e integração com LLM.
-   `03_start_api.py`: Script para subir o servidor FastAPI (Uvicorn).
-   `04_web_app.py`: Interface de usuário com Streamlit.
-   `documents/`: Pasta local para seus documentos (ignorada pelo Git).
-   `.gitignore`: Proteção para não subir arquivos sensíveis ou pesados.
