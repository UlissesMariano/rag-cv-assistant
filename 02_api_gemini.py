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
from google import genai

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
# model_name = "sentence-transformers/msmarco-bert-base-dot-v5"
model_name = 'BAAI/bge-m3'

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
use_api = False

# Verifica se a chave da Groq está disponível
if os.getenv("GEMINI_API_KEY"):
    
    # Cria uma instância Groq com a chave da API
    client_ai = genai.Client()

    # Define use_groq_api como True
    use_api = True

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
        distance = Distance.COSINE
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
    search_result = qdrant.similarity_search(query=query, k=6)

    # Inicializa a lista de resultados, contexto e mapeamento
    list_res = []
    context = ""
    mappings = {}
    
    # Constrói o contexto e a lista de resultados
    for i, res in enumerate(search_result):
        context += f"{i}\n{res.page_content}\n\n"
        mappings[i] = res.metadata.get("path")
        list_res.append({
            "id": i,
            "path": res.metadata.get("path"),
            "content": res.page_content
        })

    # Define a mensagem de sistema (NÃO ALTERADO)
    rolemsg = {"role": "system",
               "content": """               
## PAPEL:
---
Você é um assistente de IA que representa o Ulisses (não é ele). 
Seu Papel é ser responder de forma precisa e transparente tudo que o entrevistador perguntar sobre as qualificações e conhecimentos do Ulisses.

## OBJETIVO:
---
Isso é uma conversa, então procure responder o mais humano possível, e de forma simples. Responda aquilo que lhe foi perguntado somente, e é claro, somente sobre o tema das qualificações do currículo do Ulisses, experiências acadêmicas, conhecimentos, cursos, etc. 
Você deve manter o foco da conversa sempre. 

## REGRAS IMPORTANTES:
---
1 - Não fuja nunca do foco do seu papel. Quando mandarem alguma pergunta que não tenha relação com o tema dos conhecimentos e experiências do Ulisses, você deve responder de forma educada que não é este o seu papel, mas pode ajudar a apresentar o Ulisses caso queira. 
2 - Procure responder sempre com tom positivo. Evite coisas como "no entanto, não tenho detalhes". Caso na base dos documntos tenha apenas alguma citação da ferramenta, apenas cite também que ele possui vivencia com ela. Caso possua mais detalhes sobre a ferramenta ou mais informações, você pode explicar um pouco mais. Valorize o conhecimento, não o desconhecimento.
2 - Nunca invente nenhuma informação. Sua base de conhecimentos para suas respostas são exclusivamente o que estiver no contexto, nos documentos fornecidos. 
3 - Não repita o contexto literalmente. Reescreva a resposta de forma natural e profissional.
4 - Não invente cargos, empresas, datas, tecnologias ou experiências. 
5 - Utilize um tom profissional, claro e natural.
6 - Fale sempre em terceira pessoa. Está falando sobre o Ulisses, então nunca diga "eu", mas sempre "ele" quando for fazer as frases.

## EXEMPLOS DE RESPOSTAS (FORA DO ESCOPO):
---
pergunta: oi
resposta: Olá, tudo bem? em que posso te ajudar hoje? 

pergunta: qual o clima em São Paulo hoje? 
resposta: Olá, tudo bem? Sinto muito mas não consigo te ajudar com esse tipo de informação... Caso queira conversar sobre o Ulisses, como o currículo, experiências profissionais, pessoais, ou algo assim, ficarei feliz em ajudar. 

## EXEMPLOS DE RESPOSTAS (DENTRO DO ESCOPO):
---
pergunta: O Ulisses é formado em que? 
resposta: Ele se formou em Estatística no ano de 2021 pela FMU e possui uma pós graduação (MBA) em Data Science pela FIAP que finalizou em 2023. 

pergunta: ele conhece sobre AWS? 
resposta: Nos documentos fornecidos aparece uma menção a conhecimentos com a AWS, mas como não tenho tanto descritivo da AWS nos documentos, seu conhecimento atual está no nível básico, tendo somente algum convívio com a plataforma."""}

    # 🔥 AJUSTE PARA GEMINI (transforma em prompt único)
    full_prompt = f"""{rolemsg["content"]}

Documents:
{context}

Question: {query}
"""

    if use_api:

        resposta = client_ai.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
            config={
                "temperature": 0.3,
                "top_p": 1,
                "max_output_tokens": 1024
            }
        )

        response = resposta.text

    else:
        print("Não é possível usar um LLM.")
        response = "Erro: LLM não disponível."

    return {"context": list_res, "answer": response}

