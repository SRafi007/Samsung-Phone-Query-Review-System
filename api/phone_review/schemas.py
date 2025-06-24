# api/phone_review/schemas.py

from pydantic import BaseModel


class PhoneReviewResponse(BaseModel):
    phone_name: str
    formatted_specs: str
    review: str


class ReviewResponse(BaseModel):
    review: str
