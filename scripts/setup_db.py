# scripts/setup_db.py

from database.setup import create_tables

if __name__ == "__main__":
    print("🔧 Creating tables...")
    create_tables()
    print("✅ All tables created successfully.")
