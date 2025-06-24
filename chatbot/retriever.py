# chatbot/retriever.py

import faiss
import pickle
from sentence_transformers import SentenceTransformer
from config.database import SessionLocal
from database.models import Phone
from chatbot.embeddings import FAISS_INDEX_FILE, METADATA_FILE, EMBEDDING_MODEL_NAME
import os


def load_faiss_index():
    """
    Loads the FAISS index and metadata from disk.
    """
    if not os.path.exists(FAISS_INDEX_FILE) or not os.path.exists(METADATA_FILE):
        print(
            "⚠️ FAISS index not found. Please run embeddings.py first to build the index."
        )
        return None, None

    index = faiss.read_index(FAISS_INDEX_FILE)
    with open(METADATA_FILE, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata


def search_phones(query: str, top_k: int = 5):
    """
    Returns top_k relevant phones based on the query with improved matching.
    """
    # Load index and metadata
    index, metadata = load_faiss_index()

    if index is None:
        print("❌ Could not load FAISS index. Falling back to simple search.")
        return simple_search(query, top_k)

    # Load embedding model and embed query
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    # Expand query for better matching
    expanded_query = expand_query(query)
    query_vector = model.encode([expanded_query])

    # Search FAISS index
    distances, indices = index.search(query_vector, min(top_k, len(metadata)))

    # Map results back to phone records
    db = SessionLocal()
    results = []
    seen_phones = set()

    for idx in indices[0]:
        if idx < len(metadata):
            phone_id = metadata[idx]["id"]
            if phone_id not in seen_phones:
                phone = db.query(Phone).filter(Phone.id == phone_id).first()
                if phone:
                    results.append(phone)
                    seen_phones.add(phone_id)

    db.close()
    return results


def expand_query(query: str) -> str:
    """
    Expand query with relevant terms for better matching
    """
    query_lower = query.lower()
    expansions = []

    if "camera" in query_lower:
        expansions.extend(
            ["photography", "megapixel", "MP", "optical zoom", "wide", "telephoto"]
        )
    if "battery" in query_lower:
        expansions.extend(["mAh", "power", "charging", "long lasting"])
    if "performance" in query_lower:
        expansions.extend(["speed", "processor", "chipset", "RAM", "fast"])
    if "display" in query_lower:
        expansions.extend(["screen", "size", "resolution", "inches"])
    if "latest" in query_lower or "newest" in query_lower:
        expansions.extend(["2025", "recent", "new", "current"])
    if "best" in query_lower:
        expansions.extend(["top", "excellent", "premium", "flagship"])

    if expansions:
        return f"{query} {' '.join(expansions[:3])}"
    return query


def simple_search(query: str, top_k: int = 5):
    """
    Fallback search when FAISS is not available
    """
    db = SessionLocal()
    query_lower = query.lower()

    phones = db.query(Phone).all()
    scored_phones = []

    for phone in phones:
        score = 0
        phone_text = (
            f"{phone.name} {phone.camera_main} {phone.chipset} {phone.battery}".lower()
        )

        # Simple keyword matching
        if "camera" in query_lower and "mp" in phone_text:
            score += 3
        if "battery" in query_lower and "mah" in phone_text:
            score += 3
        if "latest" in query_lower and "2025" in (phone.release_date or ""):
            score += 5
        if "performance" in query_lower and any(
            word in phone_text for word in ["snapdragon", "exynos"]
        ):
            score += 2

        # Boost newer phones
        if "2025" in (phone.release_date or ""):
            score += 1
        elif "2024" in (phone.release_date or ""):
            score += 0.5

        scored_phones.append((phone, score))

    # Sort by score and return top_k
    scored_phones.sort(key=lambda x: x[1], reverse=True)
    db.close()

    return [phone for phone, score in scored_phones[:top_k] if score > 0]


"""
# Test
if __name__ == "__main__":
    test_queries = [
        "Which Samsung phone has the best camera?",
        "Latest Samsung phone with good battery life?",
        "Best Samsung phone for performance?",
    ]

    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        results = search_phones(query, top_k=3)
        print("Results:")
        for i, phone in enumerate(results, 1):
            print(f"{i}. {phone.name} - {phone.camera_main}")
"""
