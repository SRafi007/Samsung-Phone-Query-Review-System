# Samsung Phone Query & Review System

An system that scrapes real-world Samsung phone specifications, answers natural language queries using LLMs with RAG, generates human-like reviews through a multi-agent system, and exposes all functionality through a modular API.

🚀 Built using Python, BeautifulSoup, PostgreSQL, FastAPI, FAISS, HuggingFace Transformers, and SQLAlchemy.

![Preview](https://github.com/SRafi007/Visual-Assets-for-GitHub-Projects/blob/main/public/phone_review_ss.png?raw=true)


## 📌 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Setup & Usage](#setup--usage)
- [API Endpoints](#api-endpoints)
- [Example Queries](#example-queries)
- [Folder Structure](#folder-structure)
- [Credits](#credits)

## 📖 Project Overview

This project was developed as part of a technical assignment to build a query system that enables users to:

- View detailed specifications of Samsung smartphones.
- Ask natural language questions like "Which Samsung phone has the best battery?"
- Read auto-generated product reviews based on real specs.

The system scrapes 10–15 Samsung phones from GSMArena, stores them in a PostgreSQL database, embeds the data using SentenceTransformers, and uses a vector search (FAISS) + LLM approach to answer user queries. A multi-agent system handles review generation, and a clean FastAPI backend powers the final interface.

## 🎯 Features

✅ Web scraping with BeautifulSoup  
✅ PostgreSQL-backed structured data model  
✅ RAG-style chatbot using HuggingFace models  
✅ FAISS vector search for semantic matching  
✅ Multi-agent system for review generation  
✅ Modular FastAPI backend with clean routing  
✅ Fully testable and extensible architecture  

## 🛠️ Tech Stack

| Layer | Tools Used |
|-------|------------|
| Web Scraping | BeautifulSoup, requests |
| Backend Database | PostgreSQL, SQLAlchemy ORM |
| Embeddings | SentenceTransformer (all-MiniLM-L6) |
| Vector Index | FAISS |
| LLM | google/flan-t5-xl (Hugging Face) |
| Multi-Agent System | Custom-built (DataAgent, ReviewAgent, Coordinator) |
| API | FastAPI |
| Testing | Pytest (unit tests per module) |

## 🧠 Project Architecture

📥 **Scraper**: Collects structured and unstructured Samsung phone data from GSMArena.

🧾 **Database**: Normalized PostgreSQL schema with Phone and Specification tables.

🧠 **RAG Chatbot**:
- Embeds phone data with SentenceTransformer
- Stores in FAISS vector index
- Uses vector similarity to retrieve top phones
- Feeds prompt to FLAN-T5-XL to generate answer

🤖 **Multi-Agent System**:
- DataAgent fetches specs
- ReviewAgent writes a product review
- Coordinator combines both

🌐 **API**:
- `/chatbot/query` for open-ended questions
- `/review/{phone_name}` for detailed specs + review

## ⚙️ Setup & Usage

### Clone the repository

```bash
git clone https://github.com/your-username/samsung-phone-query.git
cd samsung-phone-query
```

### Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Setup your PostgreSQL database

```bash
# Create your DB, then set your credentials in a .env file
cp .env.example .env
```

### Initialize and seed database

```bash
python scripts/setup_db.py
python scripts/run_scraper.py
python scripts/seed_data.py
```

### Generate embeddings for chatbot

```bash
python chatbot/embeddings.py
```

### Start the FastAPI server

```bash
uvicorn api.main:app --reload
```

Visit http://127.0.0.1:8000/docs to explore the interactive Swagger UI.

## 🧪 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/chatbot/query` | Ask any question about Samsung phones |
| GET | `/review/{phone_name}` | Get full phone specs + auto-generated review |

## 💬 Example Queries

Try asking the chatbot:

- "Which Samsung phone has the best battery life?"
- "Compare the Galaxy S23 and S22."
- "What are the camera specs of the Galaxy A55?"

Or use:

```bash
curl -X POST http://localhost:8000/chatbot/query \
     -H "Content-Type: application/json" \
     -d '{"question": "Which Samsung phone has the best camera?"}'
```

## 📁 Folder Structure

```
Samsung Phone Query and Review System/
│
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── .env.example                   # Template for environment variables
├── .gitignore                     # Files/folders to ignore in Git
│
├── config/
│   ├── __init__.py
│   ├── settings.py                # Env configs, constants
│   └── database.py                # SQLAlchemy connection setup
│
├── database/
│   ├── __init__.py
│   ├── models.py                  # SQLAlchemy models
│   └── setup.py                   # DB initialization logic
│
├── scraper/
│   ├── __init__.py
│   ├── gsmarena_scraper.py        # GSMArena scraping logic
│   └── utils.py                   # Scraper helper functions
│
├── chatbot/                       # LLM & RAG system
│   ├── __init__.py
│   ├── embeddings.py              # SentenceTransformer-based embeddings
│   ├── retriever.py               # FAISS retrieval logic
│   ├── prompts.py                 # Prompt templates
│   └── chatbot.py                 # Core chatbot logic (RAG style)
│
├── agents/                        # Multi-agent system
│   ├── __init__.py
│   ├── data_agent.py              # Retrieves specs from DB
│   ├── review_agent.py            # Writes review from specs
│   └── coordinator.py             # Coordinates agents using CrewAI or LangChain
│
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entrypoint
│   ├── router.py                  # Combines all sub-routers
│   │
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── routes.py              # /query
│   │   ├── schemas.py             # Pydantic models
│   │   └── services.py            # Logic that calls chatbot pipeline
│   │
│   ├── phone_review/
│       ├── __init__.py
│       ├── routes.py              # /review/{phone}
│       ├── schemas.py             # Response schema
│       └── services.py            # Calls coordinator
│
├── tests/
│
├── scripts/
│
└── docs/
    ├── API_GUIDE.md               # Route and usage instructions
    └── SETUP.md                   # Project setup instructions
```

## 🙋‍♂️ Credits & Acknowledgements

- GSMArena (data source)
- Hugging Face 
- Sentence-Transformers by UKPLab
- FAISS (Facebook AI Similarity Search)

📧 Contact: sadmansakibrafi.hey@gmail.com
