# Smart GenAI Bot

Citation-aware Agentic RAG chatbot that answers questions strictly from your documents, with inline citations and source references.

## Project Structure

```
smart-genai-bot/
├── index.html          → Chat frontend (single-page UI)
├── server.py           → FastAPI backend (POST /chat endpoint)
├── rag_bot.py          → RAG pipeline (LlamaIndex + LangGraph + OpenAI)
├── processed_data/     → Place your documents here
│   ├── pdf/            → PDF documents
│   └── video/          → Video-related documents
├── .env                → OpenAI API key
├── pyproject.toml      → Python dependencies
└── README.md           → This file
```

## Tech Stack

| Component  | Technology                                    |
|------------|-----------------------------------------------|
| Frontend   | HTML5, CSS3, vanilla JavaScript (no framework)|
| Backend    | FastAPI + Uvicorn                             |
| RAG Engine | LlamaIndex (vector index, top-k=4 retrieval) |
| Orchestration | LangGraph (retrieve → answer state graph)  |
| LLM        | OpenAI GPT-4.1 (Responses API)               |
| Runtime    | Python 3.12                                   |

## Prerequisites

- **Python 3.12+** with `uv` or `pip`
- **OpenAI API key**
- **A modern web browser** (Chrome, Firefox, Safari, Edge)
- Documents (PDF, TXT, or Markdown) in the `processed_data/` directory

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/shafiqaust/smart-genai-bot.git
cd smart-genai-bot
```

### 2. Install Python dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 3. Set your OpenAI API key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-key-here
```

### 4. Add your documents

Place PDF, TXT, or Markdown files into the `processed_data/` directory. The RAG engine indexes all files recursively at startup.

```bash
cp /path/to/your/documents/*.pdf processed_data/pdf/
```

## Running the Application

### Step 1: Start the backend

```bash
uvicorn server:server --host 127.0.0.1 --port 8000 --reload
```

The API will be available at `http://127.0.0.1:8000`.

> **Important:** Before starting, add CORS middleware to `server.py` so the frontend can connect from a different port. Add this after the FastAPI app is created:
>
> ```python
> from fastapi.middleware.cors import CORSMiddleware
>
> server.add_middleware(
>     CORSMiddleware,
>     allow_origins=["*"],
>     allow_methods=["*"],
>     allow_headers=["*"],
> )
> ```

### Step 2: Serve the frontend

Use any static file server. Pick one of the options below:

#### Option A: Python (recommended — no install needed on macOS/Linux)

```bash
# From the project root, serve on a different port
python3 -m http.server 3000
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

#### Option B: Node.js (npx)

```bash
npx serve . -l 3000
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

#### Option C: VS Code Live Server

1. Install the **Live Server** extension (`ritwickdey.LiveServer`) in VS Code.
2. Open the project folder in VS Code.
3. Right-click `index.html` → **"Open with Live Server"**.

The site opens automatically with live reload on file changes.

#### Option D: Same-origin setup (no CORS needed)

Mount the frontend as a static file inside FastAPI. Add this to `server.py`:

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@server.get("/")
async def serve_frontend():
    return FileResponse("index.html")
```

Then just open [http://127.0.0.1:8000](http://127.0.0.1:8000) — no separate frontend server needed.

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
| CORS error in browser console | Add CORS middleware to `server.py` (see Step 1 above) |
| "Error: Failed to fetch" in chat | Make sure the backend is running on port 8000 |
| Empty answers / "I don't know" | Check that `processed_data/` contains documents and restart the backend |
| Backend won't start | Verify `.env` has a valid `OPENAI_API_KEY` |

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## License

MIT
