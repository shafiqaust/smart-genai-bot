# ingest.py
import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.core.extractors import TitleExtractor, KeywordExtractor
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3", device="cuda")
Settings.llm = Ollama(model="phi4", request_timeout=360.0)

documents = SimpleDirectoryReader(input_dir="./processed_data").load_data()

extractors = [
    TitleExtractor(nodes=5, llm=Settings.llm),
    KeywordExtractor(keywords=5, llm=Settings.llm),
]

splitter = SemanticSplitterNodeParser(
    buffer_size=1,
    breakpoint_percentile_threshold=95,
    embed_model=Settings.embed_model
)

nodes = splitter.get_nodes_from_documents(documents)

for extractor in extractors:
    nodes = extractor(nodes)

db = chromadb.PersistentClient(path="./chroma_local_dir")
chroma_collection = db.get_or_create_collection("coursework")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex(nodes, storage_context=storage_context)
print("Ingestion complete.")