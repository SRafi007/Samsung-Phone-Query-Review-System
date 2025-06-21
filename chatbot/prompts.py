# chatbot/prompts.py

SYSTEM_PROMPT = """
You are a helpful assistant specialized in Samsung smartphones.
Use only the information provided in the context to answer questions about phone features, comparisons, or recommendations.
If the answer is not in the context, say "Sorry, I don't have enough information to answer that."
Be concise, accurate, and polite.
"""


def format_prompt(context_chunks: list[str], question: str) -> str:
    """
    Build a prompt string by injecting context into the template.
    """
    context_text = "\n\n".join(context_chunks)

    prompt = f"""
{SYSTEM_PROMPT}

Context:
{context_text}

Question:
{question}

Answer:"""

    return prompt.strip()
