# chatbot/chatbot.py

from transformers import pipeline
from chatbot.prompts import format_prompt
from chatbot.retriever import search_index


# Load LLM pipeline once — feel free to change model later
qa_pipeline = pipeline(
    "text2text-generation", model="google/flan-t5-xl", device_map="auto"
)


def answer_question(question: str, top_k=5) -> str:
    """
    Run RAG-style pipeline: retrieve specs → build prompt → query LLM
    """
    try:
        retrieved_chunks = [text for text, score in search_index(question, top_k=top_k)]
        prompt = format_prompt(retrieved_chunks, question)

        # Generate answer
        result = qa_pipeline(prompt)
        answer = result[0]["generated_text"].strip()

        return answer or "⚠️ Could not generate a meaningful response."

    except Exception as e:
        return f"❌ Error: {str(e)}"
