import json
import os
import threading
import warnings

warnings.filterwarnings("ignore")
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

DOCS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "documentation.json")
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "storage", "chroma")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

_VECTOR_STORE = None
_STORE_LOCK = threading.Lock()

def get_vector_store() -> Chroma:
    """Thread-safe singleton getter to prevent PyTorch initialization race conditions."""
    global _VECTOR_STORE
    if _VECTOR_STORE is None:
        with _STORE_LOCK:
            if _VECTOR_STORE is None:
                embeddings = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL_NAME,
                    model_kwargs={"device": "cpu"}
                )
                _VECTOR_STORE = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    return _VECTOR_STORE

def search_docs(query: str, top_k: int = 5):
    """Performs similarity search with converted distance-to-similarity scoring [0, 1]."""
    store = get_vector_store()
    with _STORE_LOCK:
        results = store.similarity_search_with_score(query, k=top_k)
    
    hits = []
    for doc, dist in results:
        similarity = 1.0 / (1.0 + float(dist))
        hits.append({
            "doc_id": doc.metadata.get("doc_id"),
            "title": doc.metadata.get("title"),
            "chunk_id": doc.metadata.get("chunk_id"),
            "content": doc.page_content,
            "score": round(similarity, 4)
        })
    return hits

if __name__ == "__main__":
    print(f"Testing document search from {CHROMA_PATH}...")
    sample_hits = search_docs("How do I configure custom domains and SSL certificates?", top_k=2)
    for h in sample_hits:
        print(f"-> Match: {h['doc_id']} ({h['title']}) | Normalized Score: {h['score']:.4f}")
