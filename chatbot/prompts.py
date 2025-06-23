# chatbot/prompts.py

from database.models import Phone


def generate_prompt(user_query: str, phones: list[Phone]) -> str:
    """
    Creates a more detailed prompt to get better responses from the model
    """

    phone_details = []
    for idx, phone in enumerate(phones, 1):
        details = f"{idx}. {phone.name}:\n"
        details += f"   - Display: {phone.display_size or 'N/A'}\n"
        details += f"   - Camera: {phone.camera_main or 'N/A'}\n"
        details += f"   - Battery: {phone.battery or 'N/A'}\n"
        details += f"   - Chipset: {phone.chipset or 'N/A'}\n"
        details += f"   - RAM: {phone.ram or 'N/A'}\n"
        details += f"   - Storage: {phone.storage or 'N/A'}\n"
        details += f"   - Release: {phone.release_date or 'N/A'}\n"
        phone_details.append(details)

    phone_text_block = "\n".join(phone_details)

    prompt = f"""Question: {user_query}

Samsung Phone Options:
{phone_text_block}

Provide a detailed comparison and recommendation. Include specific technical details and explain why one phone might be better than others for the user's needs. Give a comprehensive answer with at least 3-4 sentences.

Answer:"""

    return prompt.strip()


def generate_simple_prompt(user_query: str, phones: list[Phone]) -> str:
    """
    Simple prompt format for basic queries
    """
    phone_list = []
    for phone in phones[:3]:
        phone_list.append(
            f"- {phone.name}: {phone.camera_main}, {phone.battery}, {phone.chipset}"
        )

    prompt = f"""Based on these Samsung phones:
{chr(10).join(phone_list)}

Question: {user_query}
Answer with details and comparison:"""

    return prompt


# Test it
if __name__ == "__main__":
    from chatbot.retriever import search_phones

    query = "Which Samsung phone has the best camera?"
    phones = search_phones(query)
    prompt = generate_prompt(query, phones)

    print("Generated Prompt:\n")
    print(prompt)
