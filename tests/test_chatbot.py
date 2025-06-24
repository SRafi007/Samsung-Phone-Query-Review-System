# scripts/test_chatbot.py

from chatbot.chatbot import answer_question
from chatbot.prompts import generate_prompt
from chatbot.retriever import search_phones


def main():
    print("🤖 Samsung Chatbot is ready. Ask your question:")
    while True:
        question = input("🟢 You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break

        response = answer_question(question)
        print(f"🤖 Bot: {response}\n")


def test_prompts():
    query = "Which Samsung phone has the best camera?"
    phones = search_phones(query)
    prompt = generate_prompt(query, phones)

    print("Generated Prompt:\n")
    print(prompt)


if __name__ == "__main__":
    main()
    # test_prompts()
