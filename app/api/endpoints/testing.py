import os
import subprocess
import tempfile
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import rag_service
from app.services.question_service import QuestionService

router = APIRouter()

class RunRequest(BaseModel):
    code: str

@router.post("/sync/{code}")
async def sync_question(code: str):
    """
    Syncs a specific question from the database to the vector store.
    """
    try:
        question_data = QuestionService.get_question_by_code(code)
        result = rag_service.sync_question_from_db(question_data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-all")
async def sync_all_questions():
    """
    Syncs all active public questions from the database to the vector store.
    """
    try:
        questions = QuestionService.get_public_questions()
        results = []
        for q in questions:
            question_data = QuestionService.get_question_by_code(q["code"])
            res = rag_service.sync_question_from_db(question_data)
            results.append({"code": q["code"], "result": res})
        return {"status": "success", "synced": len(results), "details": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run")
async def run_code(request: RunRequest):
    """
    Sandboxed execution mock (for development purposes).
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(request.code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python3", temp_path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
    except Exception as e:
        return {"stderr": str(e), "exit_code": 1}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
