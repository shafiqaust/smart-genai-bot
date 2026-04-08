# Smart Chatbot: Agentic RAG with LangGraph, LlamaIndex, OpenAI Responses API, and Citations

This project is a citation-aware Agentic RAG chatbot built with:

- LangGraph for workflow orchestration
- LlamaIndex for document loading, indexing, and retrieval
- OpenAI Responses API for grounded answer generation
- FastAPI for serving the chatbot as a local API
- Uvicorn for running the server

The chatbot answers questions only from the provided documents and returns source citations.

This project was tested in a Conda environment named `tau2` and can also be used alongside `tau2-bench` for evaluation.

---

## Features

- Document-based question answering
- Inline citations in responses
- Source list at the end of the answer
- Recursive document loading
- PDF, TXT, and Markdown support
- Local FastAPI endpoint for testing and integration
- Ready to connect with `tau2-bench`

---

## Requirements
- Conda
- Python 3.12
- OpenAI API key
- uv installed

## Installation:
 - git clone https://github.com/YOUR_USERNAME/smart-genai-bot.git
 - cd smart-genai-bot
 - conda create -n tau2 python=3.12
 - conda activate tau2
 - pip install uv
 - uv add openai langgraph langchain llama-index llama-index-readers-file pypdf python-dotenv fastapi uvicorn
 - uv sync
 - cp .env.example .env

## Run the Server
 - uv run uvicorn server:server --host 127.0.0.1 --port 8000 --reload

## Test
 - curl -X POST http://127.0.0.1:8000/chat  -H "Content-Type: application/json" -d '{"message":"Who is building the chatbot?"}'

## Start Front Server
 - cd frontend
 - python -m http.server 5500
 - open http://127.0.0.1:5500

## Test
 - In the prompt type "Give me two components of GAN"

## Project Structure

```bash
smart-genai-bot/
├── 
│   ├── __init__.py
│   ├── rag_bot.py
│   └── server.py
├── processed_data/
│   ├── pdf/
│   └── video/
├── frontend/
│   └── index.html
├── .env
├── .gitignore
├── pyproject.toml
└── README.md
