import ollama
from typing import Dict, Any, Generator
from app.services.ollama_service import OllamaService

# ใช้ร่วมทุก route ภายใต้ /api/ai — คำตอบที่ส่งถึงผู้ใช้ต้องไม่มีโค้ดหรือ pseudo code
_SYSTEM_OUTPUT_POLICY = (
    "นโยบายการตอบ (บังคับ): ห้ามใส่โค้ดจริง ข้อความที่จัดรูปแบบให้อ่านเหมือนโปรแกรม "
    "pseudo code ตัวอย่าง syntax คำสั่ง หรือบล็อก markdown แบบ ``` ในคำตอบของคุณ "
    "ห้ามเลียนแบบโครงสร้างภาษาโปรแกรมมิ่ง (เช่น บรรทัดละคำสั่งที่ดูเหมือน script) "
    "ให้อธิบายด้วยภาษาธรรมดา แนวคิด ขั้นตอนทางความคิด หรือคำถามชี้ทางเท่านั้น"
)


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

    @staticmethod
    def _get_base_system_prompt(model_name: str) -> str:
        name = "Qwen" if "qwen" in model_name.lower() else "Gemma" if "gemma" in model_name.lower() else "AI"
        return f"""คุณคือ "AI Tutor ({name})" ผู้ช่วยสอน (Tutor) ด้านการเขียนโปรแกรมและอัลกอริทึม
หน้าที่หลักของคุณคือ:
1. เป็นโค้ชหรือติวเตอร์ที่ช่วยไกด์นักเรียนให้คิดแก้ปัญหาด้วยตัวเอง ห้ามใจอ่อนเขียนโค้ดเฉลยให้เด็ดขาด (ในโหมด Hint)
2. เป็นผู้ตรวจสอบ (Code Reviewer) ที่ละเอียดรอบคอบ คอยหาบั๊ก ประเมิน Time/Space Complexity (Big O) และแนะนำ Best Practices
3. ตอบคำถามอย่างสุภาพและให้กำลังใจเสมอ ใช้ภาษาไทยที่อ่านง่ายและเป็นธรรมชาติ
4. คุณจะยึดตามคำสั่งใน โหมดการทำงาน (Mode) และ กฎสำคัญ (Rules) ที่ระบุให้ในแต่ละครั้งอย่างเคร่งครัด

"""

    @staticmethod
    def _get_model_options(model_name: str) -> dict:
        is_qwen = "qwen" in model_name.lower()
        options = {
            "num_ctx": 8192,
            "temperature": 0.1 if is_qwen else 0.4,
            "top_p": 0.3 if is_qwen else 0.6,
        }
        if is_qwen:
            options["top_k"] = 20
            options["repeat_penalty"] = 1.2
        return options

    @classmethod
    def generate_hint(cls, context: str, metadata: Dict, student_question: str, model: str = None) -> Generator[str, None, None]:
        client, target_model = cls._get_client_and_model(model)
        
        system = (
            cls._get_base_system_prompt(target_model) +
            "คำสั่งเฉพาะกิจ: คุณต้องช่วยนักเรียนแก้ปัญหาเชิงตรรกะและแนวคิดโดยให้คำใบ้เท่านั้น ไม่เฉลยเป็นขั้นตอนโปรแกรม\n\n"
            + _SYSTEM_OUTPUT_POLICY
        )
        prompt = f"โจทย์: {metadata['title']}\nรายละเอียด: {metadata['description']}\nคำถาม: {student_question}\nบริบท: {context}"
        
        try:
            stream = client.chat(model=target_model, messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': prompt}
            ], stream=True, options=cls._get_model_options(target_model))
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
        
        system = (
            cls._get_base_system_prompt(target_model) +
            "คำสั่งเฉพาะกิจ: คุณวิเคราะห์โค้ดที่ผู้ใช้ส่ง (ใช้เฉพาะภายในการคิด) แล้วสรุปเป็นข้อความธรรมดาเท่านั้น "
            "เช่น จุดที่ควรปรับ ความซับซ้อนเชิง asymptotic หรือความเสี่ยง โดยไม่คัดลอกหรือเขียนซ้ำโค้ดใด ๆ ในคำตอบ หรือแนวทางที่จะทำให้ดีคิดให้ผู้ใช้เกิดการเรียนรู้หรือ citical thinking\n\n"
            + _SYSTEM_OUTPUT_POLICY
        )
        prompt = f"โจทย์: {metadata['title']}\nโค้ดนักเรียน: {student_code}\nบริบท: {context}"
        
        try:
            stream = client.chat(model=target_model, messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': prompt}
            ], stream=True, options=cls._get_model_options(target_model))
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
        
        system = (
            cls._get_base_system_prompt(target_model) +
            "คำสั่งเฉพาะกิจ: คุณเปรียบเทียบสองเวอร์ชันที่ผู้ใช้ส่ง (ใช้เฉพาะภายในการคิด) แล้วอธิบายความแตกต่าง ข้อดีข้อเสีย และจุดที่ควรปรับเป็นภาษาธรรมดาเท่านั้น "
            "ห้ามสะท้อนโค้ดกลับมาในคำตอบ\n\n"
            + _SYSTEM_OUTPUT_POLICY
        )
        prompt = f"โจทย์: {metadata['title']}\nโค้ดเก่า: {old_code}\nโค้ดใหม่: {new_code}\nบริบท: {context}"
        
        try:
            stream = client.chat(model=target_model, messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': prompt}
            ], stream=True, options=cls._get_model_options(target_model))
            for chunk in stream:
                yield chunk['message']['content']
        except Exception as e:
            msg = str(e)
            if "does not support chat" in msg or "400" in msg:
                yield f"Model Configuration Error: โมเดล '{target_model}' ไม่รองรับการแชท กรุณาเลือกโมเดลที่ถูกต้องในหน้าตั้งค่า"
            else:
                yield f"Connection Error: {msg}"
