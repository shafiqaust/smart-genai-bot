from typing import Optional
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

# Serve frontend files
server.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@server.get("/")
def root():
    return FileResponse("frontend/index.html")


@server.get("/health")
def health():
    return {"status": "ok"}


@server.post("/chat")
async def chat(
    message: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
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
                        "retrieved_chunks": [],
                        "citations": [],
                        "catalog_rules": {},
                        "transcript_record": {},
                        "calc_result": {},
                        "answer": "",
                    }
                )
                return {"response": f"{file_msg}\n\n{chat_result['answer']}"}

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
            result = rag_app.invoke(
                {
                    "question": message,
                    "route": "",
                    "retrieved_chunks": [],
                    "citations": [],
                    "catalog_rules": {},
                    "transcript_record": {},
                    "calc_result": {},
                    "answer": "",
                }
            )
            return {"response": result["answer"]}

        return {"response": "Please type a message, paste a URL, or upload a file."}

    except Exception as e:
        traceback.print_exc()
        return {"response": f"Backend error: {str(e)}"}
