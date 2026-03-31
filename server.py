from fastapi import FastAPI
from pydantic import BaseModel
from smart_chatbot.rag_bot import app as rag_app

server = FastAPI()

class Request(BaseModel):
    message: str

@server.post("/chat")
def chat(req: Request):
    result = rag_app.invoke({
        "question": req.message,
        "retrieved_chunks": [],
        "citations": [],
        "answer": "",
    })
    return {"response": result["answer"]}