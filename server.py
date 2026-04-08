from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_bot import app as rag_app

server = FastAPI()

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Request(BaseModel):
    message: str


@server.post("/chat")
def chat(req: Request):
    result = rag_app.invoke(
        {
            "question": req.message,
            "retrieved_chunks": [],
            "citations": [],
            "answer": "",
        }
    )
    return {"response": result["answer"]}
