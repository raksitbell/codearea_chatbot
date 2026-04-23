"""
เส้นทาง /api/ai — สตรีมข้อความจาก AILogicService
นโยบายคำตอบ (ห้ามโค้ด / pseudo code) กำหนดใน system prompt ที่ app/services/ai_logic.py
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.ai import HintRequest, AnalyzeRequest, CompareRequest
from app.services.ai_logic import AILogicService
from app.services.question_service import QuestionService
from app.services.rag_service import rag_service

router = APIRouter()

@router.post("/hint")
async def get_hint(request: HintRequest):
    metadata = QuestionService.get_question_by_code(request.get_code())
    ctx = rag_service.get_context(request.student_question, metadata["code"])
    return StreamingResponse(
        AILogicService.generate_hint(ctx, metadata, request.student_question, request.model),
        media_type="text/plain"
    )

@router.post("/analyze")
async def analyze_code(request: AnalyzeRequest):
    metadata = QuestionService.get_question_by_code(request.question_code)
    ctx = rag_service.get_context(request.student_code[:1000], metadata["code"])
    return StreamingResponse(
        AILogicService.generate_analysis(ctx, metadata, request.student_code, request.model),
        media_type="text/plain"
    )

@router.post("/compare")
async def compare_code(request: CompareRequest):
    metadata = QuestionService.get_question_by_code(request.question_code)
    ctx = rag_service.get_context(request.student_question or "", metadata["code"])
    return StreamingResponse(
        AILogicService.generate_comparison(ctx, metadata, request.old_code, request.new_code, request.model),
        media_type="text/plain"
    )
