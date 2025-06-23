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
    Create a comprehensive text representation for better embedding
    """
    # Get specifications from the separate table
    specs = db.query(Specification).filter(Specification.phone_id == phone.id).all()
    specs_text = " ".join([f"{s.key} {s.value}" for s in specs])

    # Core phone information with keywords for better matching
    core_info = f"""
    {phone.name} smartphone
    Operating System: {phone.os or 'Android'}
    Processor Chipset: {phone.chipset or 'Unknown'}
    Memory RAM: {phone.ram or 'Unknown'}
    Storage Capacity: {phone.storage or 'Unknown'}
    Camera Photography: {phone.camera_main or 'Unknown'} megapixel MP
    Battery Power: {phone.battery or 'Unknown'} mAh battery life
    Display Screen: {phone.display_size or 'Unknown'} size
    Resolution: {phone.resolution or 'Unknown'}
    Network: {phone.network or '5G LTE'}
    Dimensions: {phone.dimensions or 'Unknown'}
    Weight: {phone.weight or 'Unknown'}
    Release Date: {phone.release_date or 'Unknown'}
    """

    # Combine everything for rich embedding
    full_text = core_info.strip()
    if specs_text.strip():
        full_text += f"\nAdditional Specifications: {specs_text}"

    # Add relevant search terms
    search_terms = []
    if phone.camera_main and "MP" in phone.camera_main:
        search_terms.append("high resolution camera photography")
    if phone.battery and "5000" in phone.battery:
        search_terms.append("long battery life all day usage")
    if "2025" in (phone.release_date or ""):
        search_terms.append("latest newest recent modern smartphone")
    if "Ultra" in phone.name:
        search_terms.append("premium flagship top best high-end")

    if search_terms:
        full_text += f"\nSearch Keywords: {' '.join(search_terms)}"

    return full_text


def build_faiss_index():
    """
    Builds FAISS index with enhanced phone representations.
    """
    print("🔍 Loading data from database...")
    db = SessionLocal()
    phones = db.query(Phone).all()

    if not phones:
        print("❌ No phone data found in the database.")
        print("💡 Make sure to populate the database first with phone data.")
        return

    print(f"📦 Found {len(phones)} phones. Creating enhanced embeddings...")

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    texts = []
    metadata = []

    for phone in phones:
        text = get_phone_text_representation(db, phone)
        texts.append(text)
        metadata.append(
            {
                "id": phone.id,
                "name": phone.name,
                "release_date": phone.release_date,
                "camera": phone.camera_main,
                "battery": phone.battery,
            }
        )

    print("🧠 Generating embeddings...")
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

    # Build FAISS index
    print("🔗 Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Create directory if it doesn't exist
    os.makedirs("chatbot", exist_ok=True)

    # Save index and metadata
    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(metadata, f)

    print(f"✅ FAISS index saved with {len(phones)} phone embeddings!")
    print(f"📂 Files created: {FAISS_INDEX_FILE}, {METADATA_FILE}")

    db.close()


def verify_index():
    """
    Verify that the FAISS index was created correctly
    """
    if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(METADATA_FILE):
        index = faiss.read_index(FAISS_INDEX_FILE)
        with open(METADATA_FILE, "rb") as f:
            metadata = pickle.load(f)

        print(
            f"✅ Index verified: {index.ntotal} embeddings, {len(metadata)} metadata entries"
        )
        print("📱 Sample phones in index:")
        for i, meta in enumerate(metadata[:3]):
            print(f"  {i+1}. {meta['name']} (ID: {meta['id']})")
        return True
    else:
        print("❌ Index files not found")
        return False


if __name__ == "__main__":
    print("🚀 Building FAISS index for Samsung phone search...")
    build_faiss_index()
    print("\n🔍 Verifying index...")
    verify_index()
