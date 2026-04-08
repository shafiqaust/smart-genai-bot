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
- Self-contained chat UI on the `frontend` branch
- Ready to connect with `tau2-bench`

---

## Repository Layout

The repo has two long-lived branches:

| Branch     | Purpose                                                                 |
| ---------- | ----------------------------------------------------------------------- |
| `main`     | Backend — FastAPI server, RAG pipeline, processed corpus                |
| `frontend` | Chat UI — single self-contained `static/index.html` (HTML + CSS + JS)   |

The frontend talks to the backend over HTTP (`POST /chat`). They can run on the same machine or on different machines as long as the URL in the frontend points at a reachable backend.

---

## Requirements

- Conda
- Python 3.12
- OpenAI API key
- `uv` installed
- A modern browser (for the frontend)

---

## 1. Clone and Install the Backend (`main` branch)

```bash
git clone https://github.com/shafiqaust/smart-genai-bot.git
cd smart-genai-bot

conda create -n tau2 python=3.12 -y
conda activate tau2

pip install uv
uv sync
```

If `uv sync` does not pull every dependency, install them explicitly:

```bash
uv add openai langgraph langchain llama-index llama-index-readers-file \
       pypdf python-dotenv fastapi uvicorn
```

Create your `.env` file and add your OpenAI key:

```bash
cp .env.example .env
echo "OPENAI_API_KEY=sk-..." >> .env
```

---

## 2. Run the Backend Server

From the repo root on the `main` branch:

```bash
uv run uvicorn server:server --host 127.0.0.1 --port 8000 --reload
```

On first launch the server will index every file under `processed_data/` (PDF, TXT, MD), so the initial boot takes a few seconds. You should see log lines like:

```
Loaded N documents
Document 1 metadata: {...}
Uvicorn running on http://127.0.0.1:8000
```

Smoke-test the `/chat` endpoint:

```bash
curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"Give me two components of GAN"}'
```

You should get back a JSON response of the form `{"response": "..."}` containing an answer and a `Sources:` block.

---

## 3. Get the Frontend (`frontend` branch)

The chat UI lives on a separate branch as a single self-contained HTML file at `static/index.html`. Pick **one** of the options below.

### Option A — Use a separate clone of the `frontend` branch

```bash
cd ..
git clone -b frontend https://github.com/shafiqaust/smart-genai-bot.git smart-genai-bot-ui
```

The file you want is `smart-genai-bot-ui/static/index.html`.

### Option B — Pull just the frontend file into your existing clone with `git worktree`

From inside your existing `smart-genai-bot` checkout:

```bash
git fetch origin frontend
git worktree add ../smart-genai-bot-ui frontend
```

The file you want is `../smart-genai-bot-ui/static/index.html`. This keeps the frontend tree separate from `main` so you can keep the backend running without switching branches.

### Option C — Grab the single file directly

```bash
git fetch origin frontend
git show origin/frontend:static/index.html > /tmp/chat.html
```

---

## 4. Open the Frontend and Connect to the Backend

The frontend is a static HTML file. There is **no build step**. You can use it in either of two ways:

### Open it directly as a file

Just double-click `static/index.html` (or `/tmp/chat.html`) in your file browser. It opens as `file://...` in your browser. The backend has CORS configured with `allow_origins=["*"]`, so this works out of the box.

### Or serve it over HTTP

```bash
cd path/to/static     # the directory containing index.html
python -m http.server 5500
# then open http://127.0.0.1:5500 in your browser
```

Either way, the frontend is hard-coded to POST to:

```
http://127.0.0.1:8000/chat
```

So as long as the backend from step 2 is still running on port 8000 of the same machine, the chat UI will be wired up automatically.

#### Pointing the frontend at a different host

If your backend is running somewhere other than `127.0.0.1:8000` (a remote machine, a different port, a tunnel), edit the top of the script section in `static/index.html` and change:

```js
const API_URL = "http://127.0.0.1:8000/chat";
```

to whatever URL your backend is reachable at.

---

## 5. Test the Full Loop

1. Confirm the backend log shows `Uvicorn running on http://127.0.0.1:8000`.
2. Open the frontend in your browser.
3. Type a question grounded in the corpus, e.g. **"Give me two components of GAN"** or **"What is prompt engineering?"**.
4. You should see a streamed answer with inline `[1]`, `[2]` citations and a `Sources:` block at the bottom.

If the UI shows `Make sure the backend is running on http://127.0.0.1:8000`, the frontend reached your browser but couldn't reach the API — re-check that step 2 is still running and that no firewall is blocking port 8000.

---

## Project Structure (`main` branch)

```
smart-genai-bot/
├── __init__.py
├── rag_bot.py           # LangGraph pipeline (retrieve → answer)
├── server.py            # FastAPI app exposing POST /chat
├── processed_data/
│   ├── pdf/             # PDF source documents
│   └── video/           # Transcript text files
├── .env                 # OPENAI_API_KEY (not committed)
├── .gitignore
├── pyproject.toml
└── README.md
```

On the `frontend` branch the only file you need is `static/index.html` — a single self-contained chat UI with inline CSS and JS, no build tooling required.
