# chatbot/chatbot.py

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from chatbot.retriever import search_phones
from chatbot.prompts import generate_prompt


MODEL_NAME = "google/flan-t5-xl"

print("🔄 Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def answer_query(query: str, top_k: int = 3) -> str:
    """
    Runs the full chatbot pipeline: retrieve → prompt → generate.
    """
    print("🔎 Retrieving relevant phones...")
    phones = search_phones(query, top_k=top_k)

    if not phones:
        return "Sorry, I couldn't find any relevant Samsung phones for your question."

    print("📝 Generating prompt...")
    prompt = generate_prompt(query, phones)

    print("🤖 Generating response from model...")
    input_ids = tokenizer(
        prompt, return_tensors="pt", truncation=True, max_length=1024
    ).input_ids
    output = model.generate(input_ids, max_new_tokens=256)
    answer = tokenizer.decode(output[0], skip_special_tokens=True)

    return answer


# Test it
if __name__ == "__main__":
    user_question = "Which Samsung phone has the best camera?"
    response = answer_query(user_question)
    print("\n💬 Chatbot Response:")
    print(response)
