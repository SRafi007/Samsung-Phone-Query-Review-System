# api/phone_review/services.py

from agents.coordinator import generate_phone_summary


def get_phone_review(phone_name: str):
    """
    Coordinates the agents and returns specs + review.
    """
    return generate_phone_summary(phone_name)
