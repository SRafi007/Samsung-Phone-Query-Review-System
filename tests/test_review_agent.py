from agents.review_agent import generate_review
from agents.data_agent import get_phone_data, format_phone_specs
from agents.coordinator import generate_phone_summary, compare_phones


def main():
    name = "Samsung Galaxy A56"
    review = generate_review(name)
    print("\n📝 Generated Review:\n")
    print(review)


def phone_data():
    name = "Galaxy S23"
    data = get_phone_data(name)
    formatted = format_phone_specs(data)
    print(formatted)


def test_coordinator():
    # Test single phone analysis
    print("=== Single Phone Analysis ===")
    phone = "Galaxy S25 Ultra"
    result = generate_phone_summary(phone)

    print(f"\n📱 Phone: {result['phone_name']}")
    print(f"📊 Overall Score: {result['analysis']['overall_score']}/100")
    print(f"🎯 Target Audience: {result['analysis']['target_audience']}")
    print(f"💪 Key Strengths: {', '.join(result['analysis']['key_strengths'])}")

    print(f"\n📝 Review:\n{result['review']}")

    # Test phone comparison
    print("\n\n=== Phone Comparison ===")
    comparison = compare_phones(["Galaxy S25 Ultra", "Galaxy S25", "Galaxy A56"])

    if "error" not in comparison:
        print("🏆 Category Winners:")
        for category, winner in comparison["winner_analysis"].items():
            print(f"  {category.replace('_', ' ').title()}: {winner}")

        print(f"\n📊 Analysis:")
        for category, analysis in comparison["comparison_analysis"].items():
            print(f"  {category.title()}: {analysis}")


if __name__ == "__main__":
    # main()
    # phone_data()
    test_coordinator()
