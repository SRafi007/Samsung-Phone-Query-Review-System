# chatbot/embeddings.py

import os
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import faiss
import pickle

from config.database import SessionLocal
from database.models import Phone, Specification

# --------- Constants ---------
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_INDEX_FILE = "chatbot/faiss_index.index"
METADATA_FILE = "chatbot/faiss_metadata.pkl"


def get_phone_text_representation(db: Session, phone: Phone) -> str:
    """
    Combine structured fields + specs into a single string for embedding.
    """
    specs = db.query(Specification).filter(Specification.phone_id == phone.id).all()
    specs_text = "\n".join([f"{s.key}: {s.value}" for s in specs])

    core_info = f"""
    Name: {phone.name}
    OS: {phone.os}
    Chipset: {phone.chipset}
    RAM: {phone.ram}
    Storage: {phone.storage}
    Camera: {phone.camera_main}
    Battery: {phone.battery}
    Display: {phone.display_size}
    """

    return core_info.strip() + "\n\n" + specs_text


def build_faiss_index():
    """
    Loads all phone data, generates embeddings, and saves a FAISS index.
    """
    print("🔍 Loading data from database...")
    db = SessionLocal()
    phones = db.query(Phone).all()

    if not phones:
        print("❌ No phone data found in the database.")
        return

    print(f"📦 Found {len(phones)} phones. Embedding...")

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    texts = []
    metadata = []

    for phone in phones:
        text = get_phone_text_representation(db, phone)
        texts.append(text)
        metadata.append({"id": phone.id, "name": phone.name})

    # Create embeddings
    embeddings = model.encode(texts, convert_to_numpy=True)

    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index and metadata
    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(metadata, f)

    print("✅ FAISS index and metadata saved!")


if __name__ == "__main__":
    build_faiss_index()
