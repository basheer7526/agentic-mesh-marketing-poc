# 📈 Marketing Intelligence Agentic Mesh

An autonomous AI solution designed to monitor industry news, evaluate relevance against business contexts, and generate executive-ready marketing insights. Built with **LangGraph**, **FastAPI**, **Streamlit**, and **Retrieval-Augmented Generation (RAG)**.

## 🏗️ Architecture

This project utilizes an Agentic Mesh architecture:
- **FastAPI / LangGraph Orchestrator:** Manages state and routes data between specialized AI agents.
- **Groq Inference Engine (Llama 3.1):** Provides lightning-fast, deterministic JSON parsing for agent cognition.
- **FAISS Vector Store:** Injects internal organizational context into the analysis via Dense Vector Semantic Search.
- **Streamlit Frontend:** A decoupled, dynamic dashboard for executives to trigger the pipeline and read the final digest.

---

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/marketing-intelligence-mesh.git
cd marketing-intelligence-mesh
```

### 3. Create a Virtual Environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Configuration
Create a `.env` file in the root directory and add your API keys:
```env
GROQ_API_KEY="your_groq_api_key_here"
```

---

## 💻 Running the Application

Because this architecture decouples the frontend from the backend, you need to run two terminal processes.

### Start the Backend (FastAPI / LangGraph)
Open your first terminal and run:
```bash
.\venv\Scripts\python.exe -m uvicorn app.main:app
```
The backend API will now be listening on `http://127.0.0.1:8000`.

### Start the Frontend (Streamlit Dashboard)
Open a **second** terminal (leave the backend running) and run:
```bash
.\venv\Scripts\streamlit.exe run frontend.py
```
This will automatically open the Executive Dashboard in your web browser at `http://localhost:8501`.

---

## ⚙️ How it Works
1. **Research Agent:** Scrapes raw XML data from 6 target RSS feeds (Marketing Week, AdWeek, HubSpot, MarTech, The Guardian, CMI) and shuffles them for diversity.
2. **Relevance Agent:** Uses Groq to filter out noise and only pass articles matching your business context.
3. **Analysis & RAG Agents:** Drafts a summary, searches the FAISS database for internal company relevance, and generates an actionable insight.
4. **Priority Agent:** Scores the urgency of the insight (High/Medium/Low).
5. **Digest Agent:** Assembles the final deterministic JSON payload for the Streamlit UI.
