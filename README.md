# Smart GenAI Bot

Citation-aware Agentic RAG chatbot built with LangGraph, LlamaIndex, OpenAI Responses API, and FastAPI. Answers questions strictly from your documents with inline citations and source references.

## Features

- Document-based question answering with inline citations
- Source list at the end of every answer
- Polished chat frontend with typing indicator, suggestion chips, and responsive layout
- Recursive document loading (PDF, TXT, Markdown)
- Local FastAPI endpoint for testing and integration
- Ready to connect with `tau2-bench`

## Project Structure

```
smart-genai-bot/
├── server.py           → FastAPI backend (POST /chat + static file serving)
├── rag_bot.py          → RAG pipeline (LlamaIndex + LangGraph + OpenAI)
├── static/
│   ├── index.html      → Chat frontend (single-page UI)
│   ├── style.css       → Responsive styling, citation badges, source cards
│   └── app.js          → API calls, response parsing, chat logic
├── processed_data/     → Place your documents here
│   ├── pdf/            → PDF / TXT documents
│   └── video/          → Video-related documents
├── .env                → OpenAI API key
├── pyproject.toml      → Python dependencies
└── README.md           → This file
```

## Tech Stack

| Component     | Technology                                     |
|---------------|------------------------------------------------|
| Frontend      | HTML5, CSS3, vanilla JavaScript (no framework) |
| Backend       | FastAPI + Uvicorn                              |
| RAG Engine    | LlamaIndex (vector index, top-k=4 retrieval)  |
| Orchestration | LangGraph (retrieve → answer state graph)      |
| LLM           | OpenAI GPT-4.1 (Responses API)                |
| Runtime       | Python 3.12                                    |

## Requirements

- Conda
- Python 3.12
- OpenAI API key
- uv installed

## Installation

```bash
git clone https://github.com/shafiqaust/smart-genai-bot.git
cd smart-genai-bot
git checkout frontend
conda create -n tau2 python=3.12
conda activate tau2
pip install uv
uv add openai langgraph langchain llama-index llama-index-readers-file pypdf python-dotenv fastapi uvicorn
uv sync
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

## Add Your Documents

Place PDF, TXT, or Markdown files into the `processed_data/` directory. The RAG engine indexes all files recursively at startup.

```bash
cp /path/to/your/documents/*.pdf processed_data/pdf/
```

## Running the Application

Start the server:

```bash
PYTHONPATH=$(pwd) uv run uvicorn smart_chatbot.server:server --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

The frontend is served automatically from `static/` — no separate frontend server needed.

## Test via CLI

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Who is building the chatbot?"}'
```

## Frontend Features

- **Chat UI** with user and bot message bubbles
- **Inline citation badges** — `[1]`, `[2]` markers styled as purple tags
- **Source cards** — document filenames displayed below each answer
- **Typing indicator** — animated dots while the backend processes
- **Error handling** — clear message when the backend is unreachable
- **Suggestion chips** — starter questions on the welcome screen
- **Clear chat** button to reset the conversation
- **Responsive** — works on mobile and desktop
- **Keyboard shortcuts** — Enter to send, Shift+Enter for new line

## API Reference

### `POST /chat`

**Request:**

```json
{
  "message": "What are the key findings in the report?"
}
```

**Response:**

```json
{
  "response": "The key findings include... [1] and also... [2]\n\nSources:\n[1] report.pdf\n[2] summary.txt"
}
```

The response text contains inline citation markers (`[1]`, `[2]`) and a `Sources:` block at the end. The frontend parses and renders these automatically.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Error: Failed to fetch" in chat | Make sure the backend is running on port 8000 |
| Empty answers / "I don't know" | Check that `processed_data/` contains documents and restart the backend |
| Backend won't start | Verify `.env` has a valid `OPENAI_API_KEY` |
| Module not found errors | Run `uv sync` to install dependencies |

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## License

MIT
