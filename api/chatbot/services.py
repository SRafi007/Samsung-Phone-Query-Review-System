# api/chatbot/services.py

from chatbot.chatbot import answer_query


def generate_chatbot_response(user_question: str) -> str:
    """
    Wrapper to call the chatbot pipeline.
    """
    return answer_query(user_question)
