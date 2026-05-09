# query.py
import chromadb
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3", device="cuda")
Settings.llm = Ollama(model="phi4", request_timeout=360.0)

db = chromadb.PersistentClient(path="./chroma_local_dir")
chroma_collection = db.get_collection("coursework")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
query_engine = index.as_query_engine(similarity_top_k=5)

user_query = input("Enter student question: ")
response = query_engine.query(user_query)
print(response)