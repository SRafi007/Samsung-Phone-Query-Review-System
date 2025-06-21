# chatbot/embeddings.py

from sentence_transformers import SentenceTransformer
from typing import List

# Load once and reuse (model can be swapped later)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Given a list of strings, returns a list of dense vector embeddings.
    """
    if not texts:
        return []

    embeddings = embedding_model.encode(texts, show_progress_bar=False)
    return embeddings
