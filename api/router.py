# api/router.py

from fastapi import APIRouter
from api.chatbot.routes import router as chatbot_router

from api.phone_review.routes import router as review_router

api_router = APIRouter()

# Mount feature-specific routers
api_router.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
api_router.include_router(review_router, prefix="/review", tags=["Phone Review"])
