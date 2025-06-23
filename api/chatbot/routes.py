# api/chatbot/routes.py

from fastapi import APIRouter
from api.chatbot.schemas import ChatbotQueryRequest, ChatbotQueryResponse
from api.chatbot.services import generate_chatbot_response

router = APIRouter()


@router.post("/query", response_model=ChatbotQueryResponse)
def query_chatbot(payload: ChatbotQueryRequest):
    """
    Ask a question about Samsung phones and get a smart answer.
    """
    answer = generate_chatbot_response(payload.question)
    return ChatbotQueryResponse(answer=answer)
