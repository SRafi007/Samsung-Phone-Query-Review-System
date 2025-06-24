# api/phone_review/routes.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from api.phone_review.schemas import PhoneReviewResponse, ReviewResponse
from api.phone_review.services import get_phone_review

router = APIRouter()


@router.get("/{phone_name}", response_model=PhoneReviewResponse)
def get_review_specs(phone_name: str):
    """
    Generate a review and display specs for a Samsung phone.
    """
    result = get_phone_review(phone_name)

    if result.get("error"):
        return JSONResponse(status_code=404, content={"error": result["error"]})

    return PhoneReviewResponse(
        phone_name=result["phone_name"],
        formatted_specs=result["formatted_specs"],
        review=result["review"],
    )


@router.get("/{phone_name}", response_model=ReviewResponse)
def get_review(phone_name: str):
    """
    Generate a review for a Samsung phone.
    """
    result = get_phone_review(phone_name)

    if result.get("error"):
        return JSONResponse(status_code=404, content={"error": result["error"]})

    return ReviewResponse(
        review=result["review"],
    )
