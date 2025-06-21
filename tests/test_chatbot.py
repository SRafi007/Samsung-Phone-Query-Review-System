# scripts/test_chatbot.py

from chatbot.chatbot import answer_question


def main():
    print("🤖 Samsung Chatbot is ready. Ask your question:")
    while True:
        question = input("🟢 You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break

        response = answer_question(question)
        print(f"🤖 Bot: {response}\n")


if __name__ == "__main__":
    main()
