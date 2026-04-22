from pydantic import BaseModel, model_validator
from typing import Optional

class HintRequest(BaseModel):
    question_code: Optional[str] = None
    question_id: Optional[str] = None  # Legacy support
    student_question: str
    model: Optional[str] = None
    fast_mode: bool = False

    @model_validator(mode="after")
    def validate_code(self):
        if not (self.question_code or self.question_id):
            raise ValueError("question_code is required.")
        return self

    def get_code(self) -> str:
        return (self.question_code or self.question_id or "").strip()

class AnalyzeRequest(BaseModel):
    question_code: str
    student_code: str
    model: Optional[str] = None
    fast_mode: bool = False

class CompareRequest(BaseModel):
    question_code: str
    old_code: str
    new_code: str
    student_question: Optional[str] = None
    model: Optional[str] = None
    fast_mode: bool = False

class OllamaConfigRequest(BaseModel):
    url: str
    model: str
    embedding_model: Optional[str] = "nomic-embed-text"
