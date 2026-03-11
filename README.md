# RAG CV Assistant 🤖📄

This project implements a **Retrieval-Augmented Generation (RAG)** system for intelligent querying of professional documents (CVs, Thesis, Research Papers, and Cover Letters). It allows you to "chat" with your documents using generative AI.

## 🚀 How It Works

The project workflow is divided into three main stages:
1.  **Indexing**: Your documents (.pdf, .docx, .pptx, .txt) are processed, chunked, and transformed into vectors (embeddings) stored in the **Qdrant** vector database.
2.  **API**: A **FastAPI** server that receives queries, retrieves the most relevant context from the vector database, and consults an LLM (via **Groq**) to generate a precise answer.
3.  **Web Interface**: A user-friendly **Streamlit** application to interact with the assistant.

---

## 🛠️ Technologies Used

-   **Language**: Python 3.x
-   **Vector Database**: [Qdrant](https://qdrant.tech/)
-   **AI/LLM**: Groq (Llama 3 or similar)
-   **Frameworks**: FastAPI, Streamlit, LangChain
-   **Embeddings**: HuggingFace (`msmarco-bert-base-dot-v5`)

---

## 📋 Prerequisites

-   Python installed.
-   Docker installed (to run Qdrant).
-   API Key from [Groq](https://console.groq.com/).

---

## ⚙️ Setup and Installation

### 1. Virtual Environment
Create and activate a virtual environment to keep dependencies isolated:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate
```

### 2. Dependencies
Install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Database (Qdrant)
Start the Qdrant container using Docker:
```bash
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
```

### 4. Environment Variables
Create a `.env` file in the project root with your Groq key:
```env
GROQ_API_KEY=your_key_here
```

---

## 🏃 How to Run

Follow these steps in order:

### Step 1: Index Documents
Place your files in the `documents/` folder (create it if it doesn't exist) and run:
```bash
python 01_rag.py documents
```

### Step 2: Start the API
In a new terminal (with the environment activated), start the backend server:
```bash
python 03_start_api.py
```

### Step 3: Run the Web App
In another terminal, run the Streamlit interface:
```bash
streamlit run 04_web_app.py
```

---

## 💡 Example Queries
-   "What are Ulisses' main academic experiences?"
-   "Does Ulisses have experience with Python and AI?"
-   "Summarize the professional achievements listed in the CV."

---

## 📂 Project Structure
-   `01_rag.py`: Script for reading files and populating the vector database.
-   `02_api.py`: Central API logic and LLM integration.
-   `03_start_api.py`: Script to launch the FastAPI server (Uvicorn).
-   `04_web_app.py`: User interface using Streamlit.
-   `documents/`: Local folder for your documents (ignored by Git).
-   `README-pt.md`: Portuguese version of this documentation.
-   `.gitignore`: Protection against uploading sensitive or heavy files.
