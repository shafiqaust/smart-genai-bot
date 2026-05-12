# Smart GenAI Bot

Citation-aware Agentic RAG chatbot (LangGraph + LlamaIndex + OpenAI Responses API) served via FastAPI, with a single-file HTML chat UI.

## Requirements

- Python 3.11
- [`uv`](https://github.com/astral-sh/uv)
- An OpenAI API key

## 1. Install

```bash
git clone -b working https://github.com/shafiqaust/smart-genai-bot.git
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

in another local termial
ssh -L 8000:127.0.0.1:8000 <user>@<host>

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

Then open http://127.0.0.1:8000 in your browser.

## Project layout


smart-genai-bot/
├── rag_bot.py          # LangGraph retrieve → answer pipeline
├── server.py           # FastAPI app exposing POST /chat
├── processed_data/     # Source corpus (PDF + transcripts)
├── frontend/
│   └── index.html      # Self-contained chat UI
├── .env                # OPENAI_API_KEY (not committed)
└── pyproject.toml

test
