# To load environment variables using dotenv.
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Retrieve env variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")
