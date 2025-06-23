# chatbot/schemas.py

from pydantic import BaseModel


class ChatbotQueryRequest(BaseModel):
    question: str


class ChatbotQueryResponse(BaseModel):
    answer: str
