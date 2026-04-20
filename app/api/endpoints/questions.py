from fastapi import APIRouter, HTTPException
from app.services.question_service import QuestionService

router = APIRouter()

@router.get("/")
async def list_questions():
    """Returns a simplified list of all active questions."""
    return QuestionService.get_public_questions()

@router.get("/{code}")
async def get_question(code: str):
    """Returns detailed metadata for a specific question."""
    return QuestionService.get_question_by_code(code)
