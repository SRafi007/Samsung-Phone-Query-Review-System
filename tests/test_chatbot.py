# tests/test_chatbot.py

from chatbot.chatbot import answer_query
from chatbot.prompts import generate_prompt
from chatbot.retriever import search_phones


def main():
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


def test_prompts():
    query = "Which Samsung phone has the best camera?"
    phones = search_phones(query)
    prompt = generate_prompt(query, phones)

    print("Generated Prompt:\n")
    print(prompt)


def test_retriever():
    test_queries = [
        "Which Samsung phone has the best camera?",
        "Latest Samsung phone with good battery life?",
        "Best Samsung phone for performance?",
    ]

    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        results = search_phones(query, top_k=3)
        print("Results:")
        for i, phone in enumerate(results, 1):
            print(f"{i}. {phone.name} - {phone.camera_main}")


if __name__ == "__main__":
    main()
    # test_prompts()
