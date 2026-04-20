from typing import Any, List
from fastapi import HTTPException
from app.services.supabase_service import get_supabase
from app.core.config import settings

class QuestionService:
    """
    Service to manage question-related logic and database interactions.
    """
    
    @staticmethod
    def get_public_questions() -> List[dict]:
        """
        Retrieves a list of active questions for the public dashboard.
        """
        sb = get_supabase()
        res = (
            sb.table("questions")
            .select("code,title,difficulty")
            .eq("status", True)
            .order("code")
            .execute()
        )
        
        difficulty_map = {1: "Easy", 2: "Medium", 3: "Hard"}
        return [
            {
                "code": row["code"],
                "id": row["code"],
                "title": row.get("title", ""),
                "difficulty": difficulty_map.get(row.get("difficulty"), "Unknown")
            }
            for row in (res.data or [])
        ]

    @staticmethod
    def get_question_by_code(code: str) -> dict:
        """
        Fetches detailed question metadata by its unique code.
        """
        if not code or not code.strip():
            raise HTTPException(status_code=400, detail="Valid question code is required.")
            
        sb = get_supabase()
        try:
            res = (
                sb.table("questions")
                .select("*")
                .eq("code", code.strip())
                .eq("status", True)
                .single()
                .execute()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        if not res.data:
            raise HTTPException(status_code=404, detail=f"Question '{code}' not found.")

        data = res.data
        difficulty_map = {1: "Easy", 2: "Medium", 3: "Hard"}
        
        # Normalize metadata for internal use
        return {
            "code": data["code"],
            "id": data["code"],
            "db_id": data["id"],
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "constraints": data.get("constraints", ""),
            "solution": data.get("solution", ""),
            "uri": (data.get("uri") or "").strip(),
            "difficulty": difficulty_map.get(data.get("difficulty"), "Unknown"),
            "expected_complexity": data.get("expected_complexity", ""),
            "time_limit": data.get("time_limit", 1000),
            "memory_limit": data.get("memory_limit", 256),
            "starter_code": data.get("solution", "class Solution:\n    def solve(self):\n        pass\n")
        }
