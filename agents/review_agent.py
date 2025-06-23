# agents/review_agent.py

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from agents.data_agent import get_phone_data, format_phone_specs

MODEL_NAME = "google/flan-t5-xl"

# Load model and tokenizer once
print("🤖 Loading review model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generate_review(phone_name: str) -> str:
    """
    Fetches phone data and generates a review using a HuggingFace LLM.
    """
    phone_data = get_phone_data(phone_name)

    if "error" in phone_data:
        return phone_data["error"]

    structured = phone_data["structured"]
    review_input = "\n".join(
        [
            f"Name: {structured.get('Name', '')}",
            f"Battery: {structured.get('Battery', '')}",
            f"Display: {structured.get('Display', '')}",
            f"Camera: {structured.get('Camera', '')}",
            f"Chipset: {structured.get('Chipset', '')}",
            f"RAM: {structured.get('RAM', '')}",
            f"Storage: {structured.get('Storage', '')}",
            f"OS: {structured.get('OS', '')}",
        ]
    )

    prompt = f"""
You are a professional tech reviewer.

Write a long  human-like review of the phone below based only on its specs.

{review_input}

Mention what stands out, how the performance might feel, and whether it's a good value.
Keep it clear, helpful, and not too technical.
"""

    input_ids = tokenizer(
        prompt, return_tensors="pt", truncation=True, max_length=512
    ).input_ids
    output = model.generate(input_ids, max_new_tokens=300)
    review = tokenizer.decode(output[0], skip_special_tokens=True)

    return review


# Test
if __name__ == "__main__":
    name = "Galaxy S23"
    review = generate_review(name)
    print("\n📝 Generated Review:\n")
    print(review)
