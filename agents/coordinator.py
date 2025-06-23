# agents/coordinator.py

from agents.data_agent import get_phone_data, format_phone_specs
from agents.review_agent import generate_review


def generate_phone_summary(phone_name: str) -> dict:
    """
    Coordinates between agents to generate a full phone summary.
    Returns both the specs and a natural-language review.
    """
    phone_data = get_phone_data(phone_name)

    if "error" in phone_data:
        return {"error": phone_data["error"], "review": None, "formatted_specs": None}

    formatted_specs = format_phone_specs(phone_data)
    review = generate_review(phone_name)

    return {
        "phone_name": phone_name,
        "formatted_specs": formatted_specs,
        "review": review,
    }


# Test
if __name__ == "__main__":
    phone = "Galaxy S23"
    result = generate_phone_summary(phone)

    print("\n🧾 Phone Specs:\n")
    print(result["formatted_specs"])
    print("\n📝 Review:\n")
    print(result["review"])
