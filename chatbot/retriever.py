# chatbot/retriever.py

import os
import faiss
import pickle
from typing import List, Tuple
from chatbot.embeddings import embed_texts

INDEX_FILE = "chatbot/faiss_index.idx"
DOCS_FILE = "chatbot/faiss_docs.pkl"


def build_faiss_index(texts: List[str], index_path=INDEX_FILE, doc_path=DOCS_FILE):
    """
    Build a FAISS index from a list of texts and save it.
    """
    print("🔧 Building FAISS index...")
    embeddings = embed_texts(texts)

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Save index
    faiss.write_index(index, index_path)

    # Save original text chunks
    with open(doc_path, "wb") as f:
        pickle.dump(texts, f)

    print(f"✅ Index saved to {index_path}, {len(texts)} chunks")


def search_index(query: str, top_k=5) -> List[Tuple[str, float]]:
    """
    Load the FAISS index and search for similar specs.
    Returns: List of (text, similarity_score)
    """
    if not os.path.exists(INDEX_FILE) or not os.path.exists(DOCS_FILE):
        raise FileNotFoundError("❌ FAISS index or docs not found. Build it first.")

    # Load
    index = faiss.read_index(INDEX_FILE)
    with open(DOCS_FILE, "rb") as f:
        docs = pickle.load(f)

    query_vec = embed_texts([query])[0]
    D, I = index.search([query_vec], top_k)  # distances, indices

    results = []
    for idx, dist in zip(I[0], D[0]):
        if idx < len(docs):
            results.append((docs[idx], float(dist)))

    return results
