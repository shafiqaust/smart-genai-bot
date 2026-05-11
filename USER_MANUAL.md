# Smart Academic Assistant / Agentic RAG System

User Installation & Setup Manual

Repository:  
https://github.com/shafiqaust/smart-genai-bot

---

# 1. Overview

The Smart Academic Assistant is an Agentic RAG-based academic advising system designed to assist students with:

- Academic course descriptions

The system uses:

- FastAPI
- LangGraph
- LlamaIndex
- OpenAI LLMs
- Conda environment
- Unified frontend/backend architecture

---

# 2. System Requirements

## Supported Operating Systems

- Linux
- Unix
- Ubuntu
- openSUSE
- macOS

## Required Software

- Python 3.11+
- Conda / Miniconda
- Git

---

# 3. Connect to Your Lab Machine

From your local terminal, type the following command to connect to your lab PC/server:

```bash
ssh -X <user>@<host>
```

Example:

```bash
ssh -X john@nmsu-server.edu
```

After login, you will access the remote server terminal.

---

# 4. Clone the Repository

Open the terminal and run:

```bash
git clone -b v1 https://github.com/shafiqaust/smart-genai-bot.git
cd smart-genai-bot
```

---

# 5. Create Conda Environment

Create a new Conda environment:

```bash
conda create -n smartbot python=3.11 -y
```

Activate the environment:

```bash
conda activate smartbot
```

Verify Python installation:

```bash
python --version
```

Expected output:

```text
Python 3.11.x
```

---

# 6. Install uv Package Manager

Install uv:

```bash
pip install uv
```

Verify installation:

```bash
uv --version
```

---

# 7. Install Project Dependencies

Install all dependencies from `pyproject.toml`:

```bash
uv sync
```

Alternative method:

```bash
pip install -e .
```

---

# 8. Configure Environment Variables

Create a `.env` file:

```bash
touch .env
```

Open the file and add:

```env
OPENAI_API_KEY=your_openai_api_key
```

Optional:

```env
MODEL_NAME=gpt-4.1-mini
```

---

# 9. Project Structure

```text
smart-genai-bot/
├── server.py
├── rag_bot.py
├── frontend/
│   └── index.html
├── processed_data/
├── extracted_data/
├── uploads/
├── pyproject.toml
├── README.md
└── .env
```

---

# 10. Running the Application

Run the FastAPI backend server:

```bash
uv run uvicorn server:server --host 127.0.0.1 --port 8000
```

Expected output:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

# 11. Access the Frontend

Open another terminal on your local machine and run:

```bash
ssh -L 8000:127.0.0.1:8000 <user>@<host>
```

Example:

```bash
ssh -L 8000:127.0.0.1:8000 john@nmsu-server.edu
```

Then open your browser and visit:

```text
http://127.0.0.1:8000
```

The frontend is automatically served by FastAPI.

No separate frontend server is required.

---

# 12. Supported Inputs

The system currently supports:

- Text input
- URL input
- PDF upload
- Image upload
- Transcript text

---

# 13. Main Technologies

| Technology | Purpose |
|---|---|
| FastAPI | Backend API server |
| LangGraph | Workflow orchestration |
| LlamaIndex | RAG indexing and retrieval |
| OpenAI | LLM reasoning |
| Uvicorn | ASGI server |
| Conda | Environment management |

---

# 14. Common Commands

## Activate Environment

```bash
conda activate smartbot
```

## Stop Server

```text
CTRL + C
```

## Restart Server

```bash
uv run uvicorn server:server --host 127.0.0.1 --port 8000 --reload
```

---

# 15. Common Errors and Solutions

## Error: Port Already in Use

Error message:

```text
Address already in use
```

Solution:

```bash
lsof -i :8000
kill -9 PID
```

---

## Error: Module Not Found

Error message:

```text
ModuleNotFoundError
```

Solution:

```bash
uv sync
```

or

```bash
pip install -e .
```

---

## Error: Conda Command Not Found

Install Miniconda from:

https://docs.conda.io/en/latest/miniconda.html

---

# 16. Recommended Development Workflow

```bash
conda activate smartbot
uv sync
uv run uvicorn server:server --host 127.0.0.1 --port 8000 --reload
```
