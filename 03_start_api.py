# IA Generativa, RAG com Qdrant e API
# Módulo de Inicialização da API

# Import
import uvicorn

# Inicializa a API
if __name__=="__main__":
    uvicorn.run("02_api:app", host = '0.0.0.0', port = 8000, reload = False,  workers = 3)