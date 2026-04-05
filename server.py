from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from smart_chatbot.rag_bot import app as rag_app

server = FastAPI()


@server.get("/")
async def root():
    return FileResponse("static/index.html")

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


server.mount("/static", StaticFiles(directory="static"), name="static")