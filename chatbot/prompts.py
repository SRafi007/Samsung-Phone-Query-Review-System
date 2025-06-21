# chatbot/prompts.py

from database.models import Phone


def generate_prompt(user_query: str, phones: list[Phone]) -> str:
    """
    Formats a prompt using the retrieved phones and the user's question.
    """

    phone_details = []
    for idx, phone in enumerate(phones, 1):
        summary = f"{idx}. {phone.name} —"
        parts = []
        if phone.battery:
            parts.append(f"Battery: {phone.battery}")
        if phone.display_size:
            parts.append(f"Display: {phone.display_size}")
        if phone.camera_main:
            parts.append(f"Camera: {phone.camera_main}")
        if phone.chipset:
            parts.append(f"Chipset: {phone.chipset}")
        if phone.ram:
            parts.append(f"RAM: {phone.ram}")
        if phone.storage:
            parts.append(f"Storage: {phone.storage}")
        summary += " | " + " | ".join(parts)
        phone_details.append(summary)

    phone_text_block = "\n".join(phone_details)

    prompt = f"""
User Question:
{user_query}

Available Samsung Phones:
{phone_text_block}

Based on the above data, please provide a helpful, clear, and concise answer to the user's question. Avoid speculation, and answer only using the provided data.
"""
    return prompt.strip()


# Test it
if __name__ == "__main__":
    from chatbot.retriever import search_phones

    query = "Which Samsung phone has the best camera?"
    phones = search_phones(query)
    prompt = generate_prompt(query, phones)

    print("\nGenerated Prompt:\n")
    print(prompt)
