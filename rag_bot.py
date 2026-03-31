import os
from typing import TypedDict, List
from dotenv import load_dotenv

from openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from langgraph.graph import StateGraph, END
from llama_index.readers.file import PDFReader
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is missing in .env")

client = OpenAI(api_key=api_key)


class ChatState(TypedDict):
    question: str
    retrieved_chunks: List[str]
    citations: List[str]
    answer: str


def build_index():
    docs = SimpleDirectoryReader(
        input_dir="processed_data",
        recursive=True,
        required_exts=[".pdf", ".txt", ".md"],
        file_extractor={".pdf":PDFReader()}
    ).load_data()

    print(f"Loaded {len(docs)} documents")

    for i, doc in enumerate(docs, start=1):
        preview = doc.text[:200].replace("\n", " ") if hasattr(doc, "text") else "NO_TEXT"
        print(f"Document {i} metadata: {doc.metadata}")
        print(f"Preview {i}: {preview}")

    if not docs:
        raise ValueError("No documents found in data/")

    index = VectorStoreIndex.from_documents(docs)
    return index.as_query_engine(similarity_top_k=4)


query_engine = build_index()


def retrieve(state: ChatState) -> ChatState:
    response = query_engine.query(state["question"])
    source_nodes = getattr(response, "source_nodes", []) or []

    chunks = []
    citations = []
    seen_files = set()

    for node in source_nodes:
        text = node.node.get_content().strip()
        if not text:
            continue

        meta = node.node.metadata or {}
        file_name = (
            meta.get("file_name")
            or meta.get("filename")
            or meta.get("source")
            or f"Source {i}"
        )

        chunks.append(text[:1200])

        if file_name not in seen_files:
            seen_files.add(file_name)
            citations.append(file_name)

    return {
        **state,
        "retrieved_chunks": chunks,
        "citations": citations,
    }


def answer(state: ChatState) -> ChatState:
    if not state["retrieved_chunks"]:
        return {
            **state,
            "answer": "I don't know based on the provided sources.",
        }

    evidence = "\n\n".join(
        f"[{i+1}] {chunk}" for i, chunk in enumerate(state["retrieved_chunks"])
    )

    prompt = f"""
You are a grounded assistant.
Answer ONLY from the evidence below.
If the evidence is insufficient, say exactly:
I don't know based on the provided sources.

Question:
{state["question"]}

Evidence:
{evidence}

Rules:
- Use inline citations like [1], [2].
- Do not invent facts.
- Keep the answer concise.
"""

    resp = client.responses.create(
        model="gpt-4.1",
        input=prompt,
    )

    final_text = resp.output_text.strip()

    if state["citations"]:
        final_text += "\n\nSources:\n" + "\n".join(
            f"[{i+1}] {name}" for i, name in enumerate(state["citations"])
    )
    return {
        **state,
        "answer": final_text,
    }


graph = StateGraph(ChatState)
graph.add_node("retrieve", retrieve)
graph.add_node("answer", answer)
graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "answer")
graph.add_edge("answer", END)

app = graph.compile()