# chatbot/retriever.py

import faiss
import pickle
from sentence_transformers import SentenceTransformer
from config.database import SessionLocal
from database.models import Phone
from chatbot.embeddings import FAISS_INDEX_FILE, METADATA_FILE, EMBEDDING_MODEL_NAME


def load_faiss_index():
    """
    Loads the FAISS index and metadata from disk.
    """
    index = faiss.read_index(FAISS_INDEX_FILE)
    with open(METADATA_FILE, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata


def search_phones(query: str, top_k: int = 3):
    """
    Returns top_k relevant phones based on the query.
    """
    # Load index and metadata
    index, metadata = load_faiss_index()

    # Load embedding model and embed query
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    query_vector = model.encode([query])

    # Search FAISS index
    distances, indices = index.search(query_vector, top_k)

    # Map results back to phone records
    db = SessionLocal()
    results = []
    for idx in indices[0]:
        if idx < len(metadata):
            phone_id = metadata[idx]["id"]
            phone = db.query(Phone).filter(Phone.id == phone_id).first()
            if phone:
                results.append(phone)

    return results


# Test
if __name__ == "__main__":
    results = search_phones("Which Samsung phone has the best battery life?", top_k=3)
    print("\nTop matching phones:")
    for phone in results:
        print(f"📱 {phone.name} — Battery: {phone.battery}")
