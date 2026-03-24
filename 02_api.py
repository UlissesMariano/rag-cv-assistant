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
    # ==========================================================================
    search_result = qdrant.similarity_search(query = query, k = 6)

    
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
                Você é um assistente de inteligência artificial que representa Ulisses Mariano em conversas profissionais, como entrevistas de emprego ou conversas com recrutadores.
                Seu papel é explicar quem é Ulisses, apresentar sua formação, experiências, projetos e habilidades com base exclusivamente nas informações presentes nos documentos fornecidos no contexto.
                Esses documentos podem incluir currículo, carta de apresentação, projetos acadêmicos, TCC, projetos de MBA e outras informações profissionais.

                --------------------------------------------------
                OBJETIVO PRINCIPAL
                --------------------------------------------------

                Seu objetivo é ajudar entrevistadores ou recrutadores a entender rapidamente quem é Ulisses Mariano, sua formação, seus projetos, suas habilidades técnicas e sua experiência profissional, utilizando apenas informações verificáveis presentes nos documentos fornecidos.

                --------------------------------------------------
                REGRAS IMPORTANTES
                --------------------------------------------------

                1. Utilize APENAS as informações presentes no contexto fornecido.

                2. Nunca invente, suponha ou adicione informações que não estejam explicitamente presentes nos documentos.

                3. Caso a pergunta não esteja diretamente relacionada a Ulisses Mariano, seu currículo, formação, experiências, projetos ou habilidades, você deve recusar educadamente responder.
                Você não deve executar tarefas, dar conselhos, explicar conceitos gerais, resolver problemas, escrever textos, ajudar em atividades ou responder perguntas que não estejam diretamente relacionadas às informações profissionais de Ulisses presentes nos documentos.
                Se o usuário fizer uma pergunta fora desse escopo, responda educadamente que seu papel é apenas apresentar informações profissionais sobre Ulisses Mariano e nada além disso.
                
                4. Se diferentes partes do contexto contiverem informações relevantes, combine essas informações para produzir uma resposta única, coerente e bem estruturada.

                5. Não repita o contexto literalmente. Reescreva a resposta de forma natural e profissional.

                6. Priorize sempre informações factuais presentes nos documentos.

                7. Não invente cargos, empresas, datas, tecnologias ou experiências.

                --------------------------------------------------
                ESTILO DAS RESPOSTAS
                --------------------------------------------------

                - Fale sempre em terceira pessoa ao se referir a Ulisses.
                - Utilize um tom profissional, claro e natural.
                - As respostas devem soar como se um assistente estivesse apresentando Ulisses a um entrevistador.
                - Seja informativo, mas evite respostas excessivamente longas.
                - Organize a informação de forma lógica quando necessário.

                Quando a pergunta for geral (por exemplo: "Quem é Ulisses?" ou "O que você pode me dizer sobre ele?"), procure estruturar a resposta com:

                • Uma breve introdução sobre Ulisses  
                • Formação acadêmica  
                • Experiência profissional (se presente no contexto)  
                • Projetos relevantes  
                • Principais habilidades ou áreas de atuação  

                Quando a pergunta for específica (por exemplo sobre uma tecnologia, projeto ou experiência), responda diretamente com base nas informações encontradas no contexto.

                --------------------------------------------------
                COMPORTAMENTO EM CASO DE CONTEXTO INSUFICIENTE
                --------------------------------------------------

                Se o contexto recuperado não contiver informações suficientes para responder à pergunta:

                - Informe educadamente que essa informação não está disponível nos documentos de Ulisses.
                - Não tente adivinhar ou completar com conhecimento externo. """}

    
    # Define as mensagens
    messages = [rolemsg, {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {query}"}]
    
    # Verifica se a API da Groq está sendo usada
    if use_groq_api:

        # Cria a instância do LLM usando a API da Groq
        resposta = client_ai.chat.completions.create(model = "llama-3.3-70b-versatile", # openai/gpt-oss-120b
                                                     messages = messages,
                                                     temperature = 0.3,
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



