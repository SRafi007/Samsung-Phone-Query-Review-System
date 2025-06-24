# database/setup.py

from config.database import engine
from database.models import Base


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("Tables created successfully.")
