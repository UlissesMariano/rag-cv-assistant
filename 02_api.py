# IA Generativa, RAG com Qdrant e API
# Módulo da API

# Importa o módulo os
import os

# Importa o módulo para carregar variáveis de ambiente
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Importa a classe FastAPI do módulo fastapi para criar a API
from fastapi import FastAPI

# Importa a classe QdrantVectorStore do módulo langchain_qdrant para instanciar o banco de dados vetorial
from langchain_qdrant import QdrantVectorStore

# Importa a classe QdrantClient do módulo qdrant_client para conectar no banco de dados vetorial
from qdrant_client import QdrantClient

# Importa os modelos do qdrant_client
from qdrant_client.models import Distance

# Importa a classe BaseModel do módulo pydantic para validar os dados que forem enviados para a API
from pydantic import BaseModel

# Importa a classe HuggingFaceEmbeddings do módulo langchain_huggingface para gerar as embeddings
from langchain_huggingface import HuggingFaceEmbeddings

# Importa a classe Groq do módulo groq
from groq import Groq

# Filtra warnings
import warnings
warnings.filterwarnings('ignore')

# Define a classe Item que herda de BaseModel
class Item(BaseModel):
    query: str


# ==========================================================================
# 1. Cria uma instância de HuggingFaceEmbeddings
# ==========================================================================

# Define o nome do modelo (tokenizador)
model_name = "sentence-transformers/msmarco-bert-base-dot-v5"

# Define os argumentos do modelo
model_kwargs = {'device': 'cpu'}

# Define os argumentos de codificação
encode_kwargs = {'normalize_embeddings': True}

hf = HuggingFaceEmbeddings(
    model_name = model_name,
    model_kwargs = model_kwargs,
    encode_kwargs = encode_kwargs)


# ==========================================================================
# 2. Puxa a API do modelo que será usado (LLM)
# ==========================================================================

# Define a variável use_groq_api como False
use_groq_api = False

# Verifica se a chave da Groq está disponível
if os.getenv("GROQ_API_KEY"):
    
    # Cria uma instância Groq com a chave da API
    client_ai = Groq(api_key = os.getenv("GROQ_API_KEY"))

    # Define use_groq_api como True
    use_groq_api = True

else:
    # Imprime uma mensagem indicando que não é possível usar um LLM
    print("Não é possível usar um LLM.")


# ==========================================================================
# 3. Instancia o banco vetorial (QDrant)
# ==========================================================================

# Cria uma instância para conectar ao banco vetorial
client = QdrantClient("http://localhost:6333")

# Define o nome da coleção
collection_name = "VectorDB"

# Cria uma instância de QdrantVectorStore para enviar os dados para o banco vetorial
try:
    qdrant = QdrantVectorStore(
        client = client, 
        collection_name = collection_name, 
        embedding = hf,
        distance = Distance.DOT
    )
except Exception as e:
    print(f"Erro ao inicializar Qdrant: {e}")
    qdrant = None


# ==========================================================================
# 4. Instancia a API
# ==========================================================================

# Cria uma instância 
app = FastAPI()

# Define a rota raiz com o método GET
@app.get("/")
async def root():
    return {"message": "Back-end - API para IA Generativa"}

# Define a rota /api com o método POST
@app.post("/api")
async def api(item: Item):

    # Obtém a query a partir do item
    query = item.query
    
    # Verifica se o banco vetorial está inicializado
    if qdrant is None:
        return {"context": [], "answer": "Erro: O banco de dados vetorial Qdrant não pôde ser inicializado."}


    # 4.1 Realiza a busca de similaridade (RETRIEVAL)
    # ==========================================================================
    search_result = qdrant.similarity_search(query = query, k = 10)

    
    # Inicializa a lista de resultados, contexto e mapeamento
    list_res = []
    context = ""
    mappings = {}
    
    # Constrói o contexto e a lista de resultados
    for i, res in enumerate(search_result):
        context += f"{i}\n{res.page_content}\n\n"
        mappings[i] = res.metadata.get("path")
        list_res.append({"id": i, "path": res.metadata.get("path"), "content": res.page_content})

    # Define a mensagem de sistema
    rolemsg = {"role": "system",
               "content": """
               Você é um trabalhador e responsável por conversar e apresentar toda informação necessária sobre o Ulisses, para recrutadores de vagas.
               O usuário vai perguntar algo sobre o currículo, experiências acadêmicas e profissionais e conhecimentos do Ulisses. 
               Sua tarefa é ser como um acessor dele. 
               Não invente nenhum dado, você só pode falar o que estiver contido nos documentos fornecidos. 
               
               Você deve tentar ajudar ao máximo o usuário a ter toda informação que precisar, então busque saber o perfil da vaga e forneça todo 
               conhecimento que o Ulisses tem para aquela determinada vaga."""}

    
    # Define as mensagens
    messages = [rolemsg, {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {query}"}]
    
    # Verifica se a API da Groq está sendo usada
    if use_groq_api:

        # Cria a instância do LLM usando a API da Groq
        resposta = client_ai.chat.completions.create(model = "openai/gpt-oss-120b",
                                                     messages = messages,
                                                     temperature = 0.5,
                                                     top_p = 1,
                                                     max_tokens = 1024,
                                                     stream = False)
        
        # 4.3 Obtém a resposta do LLM
        # ==========================================================================
        response = resposta.choices[0].message.content
    
    else:

        # Imprime uma mensagem indicando que não é possível usar um LLM
        print("Não é possível usar um LLM.")
    
    return {"context": list_res, "answer": response}




