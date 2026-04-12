# Smart GenAI Bot

Citation-aware Agentic RAG chatbot (LangGraph + LlamaIndex + OpenAI Responses API) served via FastAPI, with a single-file HTML chat UI.

## Requirements

- Python 3.12
- [`uv`](https://github.com/astral-sh/uv)
- An OpenAI API key

## 1. Install

```bash
git clone https://github.com/shafiqaust/smart-genai-bot.git
cd smart-genai-bot
uv sync
```

## 2. Configure the API key

Create a `.env` file in the repo root:

```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

## 3. Run the RAG server

From the repo root:

```bash
uv run uvicorn server:server --host 127.0.0.1 --port 8000
```

On first boot the server indexes every file under `processed_data/` (PDF, TXT, MD). When you see:

```
Uvicorn running on http://127.0.0.1:8000
```

the backend is ready. Smoke test:

```bash
curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"What is prompt engineering?"}'
```

You should get back a JSON `{"response": "..."}` with inline `[1]`, `[2]` citations and a `Sources:` block.

## 4. Run the frontend

The chat UI is a single self-contained file at `frontend/index.html`. It POSTs to `http://127.0.0.1:8000/chat`, so as long as the backend from step 3 is running, it just works.

Serve it over HTTP in a second terminal:

```bash
cd frontend
python3 -m http.server 5500
```

Then open http://127.0.0.1:5500 in your browser.

You can also open `frontend/index.html` directly as a `file://` URL — the backend has `allow_origins=["*"]` so CORS is fine either way.

## Pointing the frontend at a different backend

If the backend is not on `127.0.0.1:8000`, edit the `fetch(...)` call in [frontend/index.html](frontend/index.html) and change the URL to wherever your backend is reachable.

## Project layout

```
smart-genai-bot/
├── rag_bot.py          # LangGraph retrieve → answer pipeline
├── server.py           # FastAPI app exposing POST /chat
├── processed_data/     # Source corpus (PDF + transcripts)
├── frontend/
│   └── index.html      # Self-contained chat UI
├── .env                # OPENAI_API_KEY (not committed)
└── pyproject.toml
```
