import os
import shutil
import subprocess
import tempfile
import uuid
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from app.services.rag_service import rag_service
from app.services.ai_logic import AILogicService
from app.core.config import settings

router = APIRouter()

class RunRequest(BaseModel):
    code: str

@router.post("/ingest")
async def ingest_pdf(
    file: UploadFile = File(...),
    question_code: Optional[str] = Form(None),
):
    """
    Development endpoint to manually ingest PDF files into the vector database.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    qc = (question_code or "").strip() or "__manual_upload__"
    try:
        result = rag_service.ingest_pdf(temp_path, question_code=qc, source_uri=file.filename)
        return {"message": "Success", "details": result}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

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
