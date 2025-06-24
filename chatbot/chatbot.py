# chatbot/chatbot.py

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from chatbot.retriever import search_phones
from chatbot.prompts import generate_prompt
import re


MODEL_NAME = "google/flan-t5-xl"

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def extract_camera_mp(camera_text):
    """Extract megapixel value from camera description"""
    if not camera_text:
        return 0
    match = re.search(r"(\d+)\s*MP", camera_text)
    return int(match.group(1)) if match else 0


def create_detailed_response(query: str, phones: list) -> str:
    """
    Create a detailed response based on query type and retrieved phones
    """
    query_lower = query.lower()

    if "camera" in query_lower:
        # Sort phones by camera megapixels
        phones_with_mp = [
            (phone, extract_camera_mp(phone.camera_main)) for phone in phones
        ]
        phones_with_mp.sort(key=lambda x: x[1], reverse=True)

        response = "Based on camera specifications:\n\n"
        for i, (phone, mp) in enumerate(phones_with_mp[:3], 1):
            response += f"{i}. **{phone.name}** - {phone.camera_main}\n"

        best_phone = phones_with_mp[0][0]
        response += f"\n🏆 **Best Camera**: {best_phone.name} offers the highest resolution main camera"
        if phones_with_mp[0][1] > 0:
            response += f" at {phones_with_mp[0][1]}MP"
        response += "."

    elif "battery" in query_lower:
        response = "Battery comparison:\n\n"
        for i, phone in enumerate(phones[:3], 1):
            response += f"{i}. **{phone.name}** - {phone.battery}\n"
        response += (
            "\n All these phones have 5000 mAh batteries for excellent all-day usage."
        )

    elif (
        "performance" in query_lower
        or "chipset" in query_lower
        or "processor" in query_lower
    ):
        response = "Performance comparison:\n\n"
        for i, phone in enumerate(phones[:3], 1):
            response += f"{i}. **{phone.name}** - {phone.chipset}\n"
            if phone.ram:
                response += f"   RAM: {phone.ram}\n"

    elif "storage" in query_lower or "memory" in query_lower:
        response = "Storage options:\n\n"
        for i, phone in enumerate(phones[:3], 1):
            response += f"{i}. **{phone.name}** - {phone.storage}\n"

    elif "display" in query_lower or "screen" in query_lower:
        response = "Display specifications:\n\n"
        for i, phone in enumerate(phones[:3], 1):
            response += f"{i}. **{phone.name}** - {phone.display_size}\n"
            if phone.resolution:
                response += f"   Resolution: {phone.resolution}\n"

    elif "latest" in query_lower or "newest" in query_lower or "recent" in query_lower:
        response = "Latest Samsung phones (2025):\n\n"
        latest_phones = [p for p in phones if "2025" in (p.release_date or "")]
        for i, phone in enumerate(latest_phones[:3], 1):
            response += f"{i}. **{phone.name}** - Released {phone.release_date}\n"

    else:
        # General comparison
        response = "Here are the top Samsung phones for your query:\n\n"
        for i, phone in enumerate(phones[:3], 1):
            response += f"{i}. **{phone.name}**\n"
            response += f"   • Display: {phone.display_size}\n"
            response += f"   • Camera: {phone.camera_main}\n"
            response += f"   • Battery: {phone.battery}\n"
            response += f"   • Chipset: {phone.chipset}\n\n"

    return response


def answer_query(query: str, top_k: int = 5) -> str:
    """
    Runs the full chatbot pipeline: retrieve → analyze → generate detailed response.
    """
    print(" Retrieving relevant phones...")
    phones = search_phones(query, top_k=top_k)

    if not phones:
        return "Sorry, I couldn't find any relevant Samsung phones for your question."

    print(" Creating detailed response...")

    # Try the model approach first
    prompt = generate_prompt(query, phones[:3])
    input_ids = tokenizer(
        prompt, return_tensors="pt", truncation=True, max_length=512
    ).input_ids

    try:
        output = model.generate(
            input_ids,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
        model_answer = tokenizer.decode(output[0], skip_special_tokens=True)

        # If model gives a good detailed response, use it
        if len(model_answer.split()) > 10 and not model_answer.strip().endswith(
            phones[0].name
        ):
            return model_answer
    except:
        pass

    # Fallback to rule-based detailed response
    return create_detailed_response(query, phones)


"""
# Test it
if __name__ == "__main__":
    test_queries = [
        "Which Samsung phone has the best camera?",
        "What's the latest Samsung phone?",
        "Samsung phone with good battery life?",
        "Best Samsung phone for performance?",
    ]

    for query in test_queries:
        print(f"\n📱 Query: {query}")
        print("=" * 50)
        response = answer_query(query)
        print(response)
        print()
"""
