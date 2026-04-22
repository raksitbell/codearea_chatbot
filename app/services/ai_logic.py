import ollama
from typing import Dict, Any, Generator
from app.services.ollama_service import OllamaService

class AILogicService:
    """
    Service containing the AI prompt engineering logic and response generation.
    """

    @staticmethod
    def _get_client_and_model(request_model: str = None):
        config = OllamaService.get_config()
        host = config.get("url", "http://localhost:11434")
        model = request_model or config.get("model", "ai-tutor")
        return ollama.Client(host=host), model

    @classmethod
    def generate_hint(cls, context: str, metadata: Dict, student_question: str, model: str = None) -> Generator[str, None, None]:
        client, target_model = cls._get_client_and_model(model)
        
        system = "คุณคือ AI ติวเตอร์ที่ช่วยนักเรียนแก้ปัญหาเวกเตอร์โดยให้คำใบ้ ห้ามแสดงโค้ดเฉลย"
        prompt = f"โจทย์: {metadata['title']}\nรายละเอียด: {metadata['description']}\nคำถาม: {student_question}\nบริบท: {context}"
        
        try:
            stream = client.chat(model=target_model, messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': prompt}
            ], stream=True)
            for chunk in stream:
                yield chunk['message']['content']
        except Exception as e:
            msg = str(e)
            if "does not support chat" in msg or "400" in msg:
                yield f"Model Configuration Error: โมเดล '{target_model}' ไม่รองรับการแชท (อาจเป็นโมเดลสำหรับ Embedding เท่านั้น) กรุณาตรวจสอบการตั้งค่าใน AI Tutor Dashboard"
            else:
                yield f"Connection Error: {msg}"

    @classmethod
    def generate_analysis(cls, context: str, metadata: Dict, student_code: str, model: str = None) -> Generator[str, None, None]:
        client, target_model = cls._get_client_and_model(model)
        
        system = "คุณคือ AI ตรวจโค้ด วิเคราะห์ Big O และให้คำแนะนำที่กระชับ"
        prompt = f"โจทย์: {metadata['title']}\nโค้ดนักเรียน: {student_code}\nบริบท: {context}"
        
        try:
            stream = client.chat(model=target_model, messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': prompt}
            ], stream=True)
            for chunk in stream:
                yield chunk['message']['content']
        except Exception as e:
            msg = str(e)
            if "does not support chat" in msg or "400" in msg:
                yield f"Model Configuration Error: โมเดล '{target_model}' ไม่รองรับการแชท กรุณาเปลี่ยนเป็นโมเดล LLM เช่น llama3 ใน Dashboard"
            else:
                yield f"Connection Error: {msg}"

    @classmethod
    def generate_comparison(cls, context: str, metadata: Dict, old_code: str, new_code: str, model: str = None) -> Generator[str, None, None]:
        client, target_model = cls._get_client_and_model(model)
        
        system = "คุณคือ AI ผู้เชี่ยวชาญ เปรียบเทียบโค้ดสองเวอร์ชันและแนะนำจุดที่ดีขึ้น"
        prompt = f"โจทย์: {metadata['title']}\nโค้ดเก่า: {old_code}\nโค้ดใหม่: {new_code}\nบริบท: {context}"
        
        try:
            stream = client.chat(model=target_model, messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': prompt}
            ], stream=True)
            for chunk in stream:
                yield chunk['message']['content']
        except Exception as e:
            msg = str(e)
            if "does not support chat" in msg or "400" in msg:
                yield f"Model Configuration Error: โมเดล '{target_model}' ไม่รองรับการแชท กรุณาเลือกโมเดลที่ถูกต้องในหน้าตั้งค่า"
            else:
                yield f"Connection Error: {msg}"
