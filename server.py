from typing import List, Optional
import traceback

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from rag_bot import (
    app as rag_app,
    ingest_catalog_url,
    ingest_transcript_file,
    ingest_transcript_text,
)

server = FastAPI(title="Smart Academic Bot API")

session_known_concepts: List[str] = []
session_conversation_concepts: List[str] = []
session_last_response_id: Optional[str] = None


def _known_concepts_footer(concepts: List[str]) -> str:
    body = ", ".join(concepts) if concepts else "Nothing recorded yet."
    return "\n\n---\n**What the system knows you know:** " + body


# Serve frontend files
server.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@server.get("/")
def root():
    return FileResponse("frontend/index.html")


@server.get("/health")
def health():
    return {"status": "ok"}


@server.post("/reset")
def reset():
    global session_known_concepts, session_conversation_concepts, session_last_response_id
    session_known_concepts = []
    session_conversation_concepts = []
    session_last_response_id = None
    return {"status": "ok"}


@server.post("/chat")
async def chat(
    message: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    global session_known_concepts, session_conversation_concepts, session_last_response_id

    try:
        message = (message or "").strip()

        if file is not None:
            content = await file.read()
            result = ingest_transcript_file(
                file_bytes=content,
                filename=file.filename or "uploaded_file",
                content_type=file.content_type or "application/octet-stream",
            )

            if result.get("status") != "success":
                return {"response": result.get("message", "File upload failed.")}

            file_msg = f"Uploaded and processed file: {file.filename}"

            if message:
                chat_result = rag_app.invoke(
                    {
                        "question": message,
                        "route": "",
                        "conversation_concepts": session_conversation_concepts,
                        "search_query": "",
                        "last_response_id": session_last_response_id,
                        "response_id": "",
                        "retrieved_chunks": [],
                        "citations": [],
                        "catalog_rules": {},
                        "transcript_record": {},
                        "calc_result": {},
                        "known_concepts": session_known_concepts,
                        "answer": "",
                    }
                )
                session_known_concepts = chat_result.get("known_concepts", session_known_concepts)
                session_conversation_concepts = chat_result.get("conversation_concepts", session_conversation_concepts)
                session_last_response_id = chat_result.get("response_id") or session_last_response_id
                return {"response": f"{file_msg}\n\n{chat_result['answer']}{_known_concepts_footer(session_known_concepts)}"}

            return {"response": file_msg}

        if message.startswith("http://") or message.startswith("https://"):
            result = ingest_catalog_url(message)
            if result.get("status") == "success":
                return {
                    "response": (
                        "Catalog URL ingested successfully. "
                        "You can now ask questions about program requirements."
                    )
                }
            return {"response": result.get("message", "Catalog ingestion failed.")}

        if message and len(message) > 300 and "\n" in message:
            result = ingest_transcript_text(message)
            if result.get("status") == "success":
                return {
                    "response": (
                        "Transcript text processed successfully. "
                        "You can now ask questions like 'What is my CGPA?' "
                        "or 'How many credits do I still need?'"
                    )
                }
            return {"response": result.get("message", "Transcript text processing failed.")}

        if message:
            chat_result = rag_app.invoke(
                {
                    "question": message,
                    "route": "",
                    "conversation_concepts": session_conversation_concepts,
                    "search_query": "",
                    "last_response_id": session_last_response_id,
                    "response_id": "",
                    "retrieved_chunks": [],
                    "citations": [],
                    "catalog_rules": {},
                    "transcript_record": {},
                    "calc_result": {},
                    "known_concepts": session_known_concepts,
                    "answer": "",
                }
            )
            session_known_concepts = chat_result.get("known_concepts", session_known_concepts)
            session_conversation_concepts = chat_result.get("conversation_concepts", session_conversation_concepts)
            session_last_response_id = chat_result.get("response_id") or session_last_response_id
            return {"response": chat_result["answer"] + _known_concepts_footer(session_known_concepts)}

        return {"response": "Please type a message, paste a URL, or upload a file."}

    except Exception as e:
        traceback.print_exc()
        return {"response": f"Backend error: {str(e)}"}
