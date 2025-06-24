# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import api_router

app = FastAPI(
    title="Samsung Phone Query API",
    description="An API for answering questions and generating reviews about Samsung phones.",
    version="1.0.0",
)

#  CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 Replace * with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Add API routes
app.include_router(api_router)


#  Root route (health check)
@app.get("/")
def read_root():
    return {"message": "Samsung Query API is live!"}
