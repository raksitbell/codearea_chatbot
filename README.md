# 📚 AI Tutor: Backend-as-a-Service (BaaS)

โปรเจกต์นี้เป็นหลักเขตของระบบ **AI Tutor** ที่ได้รับการปรับโฉมใหม่ให้เป็นสถาปัตยกรรม **Backend-as-a-Service (BaaS)** สำหรับช่วยสอนและตรวจโค้ดเรื่อง **"Vector (Dynamic Array)"** โดยเน้นความง่ายในการเชื่อมต่อและการบริหารจัดการจากศูนย์กลาง

### ✨ ฟีเจอร์เด่นในเวอร์ชัน BaaS
- **Centralized API:** รวมศูนย์ทุกฟังก์ชัน AI (Hint, Analyze, Compare) ไว้ที่เดียว
- **Dynamic Configuration:** รองรับการตั้งค่า Ollama URL และ Model ผ่าน API และฐานข้อมูล (Bypass .env)
- **Model Listing Proxy:** มี Endpoint สำหรับดึงรายการโมเดลจาก Ollama เพื่อให้ Frontend ใช้งานผ่าน Backend หลักได้ทันที
- **Container-First:** ออกแบบมาเพื่อรันบน Docker พร้อมระบบ Hot-Reload สำหรับการพัฒนา

---

## ⚙️ 1. โครงสร้างโฟลเดอร์ (Project Structure)
```text
ai-tutor/
├── app/                  # โค้ดหลักของบริการ (FastAPI)
│   ├── main.py           # Entry point และ API Routes
│   ├── ai_service.py     # ตรรกะการสื่อสารกับโมเดล AI (Ollama)
│   ├── db_service.py     # การเชื่อมต่อฐานข้อมูล (Supabase) และจัดการ Config
│   └── rag_service.py    # ระบบ Retrieval-Augmented Generation (PDF Ingestion)
├── data/                 # ที่เก็บข้อมูลชั่วคราว
├── static/ & templates/  # ไฟล์หน้าเว็บจำลอง (Legacy/Test UI)
├── Dockerfile            # การตั้งค่าสำหรับสร้าง Image
└── docker-compose.yml    # การตั้งค่าสำหรับรัน Service พร้อม Volume Mount
```

---

## 🚀 2. การเริ่มใช้งานด้วย Docker (แนะนำ)

เพื่อความสะดวกและสเถียรภาพ แนะนำให้รันผ่าน Docker:

1.  **เตรียม Ollama บนเครื่อง Host**:
    - ตรวจสอบว่า Ollama รันอยู่และเปิดการเข้าถึงจาก Network:
      ```bash
      # สำหรับ macOS ตั้งค่าให้ฟังทุก IP
      launchctl setenv OLLAMA_HOST "0.0.0.0"
      ```
    - รีสตาร์ทแอป Ollama

2.  **รัน Service**:
    ```bash
    # เข้ามาที่โฟลเดอร์ ai-tutor
    docker compose up -d --build
    ```
    ระบบจะพร้อมใช้งานที่ [http://localhost:8080](http://localhost:8080)

---

## 🛠 3. API Endpoints ที่สำคัญ (BaaS)

นอกจากระบบ Hint/Analyze เดิมแล้ว เวอร์ชันนี้เพิ่ม Endpoint สำหรับการจัดการระบบ:

- **`GET /api/health`**: ตรวจสอบสถานะ Service และความสามารถในการเชื่อมต่อกับ Ollama
- **`GET /api/models`**: ดึงรายการโมเดลที่มีอยู่ในเครื่อง (Proxy จาก Ollama)
- **`GET /api/config/ollama`**: ดูการตั้งค่า Ollama ที่กำลังใช้งานอยู่
- **`POST /api/config/ollama`**: อัปเดตการตั้งค่า Ollama ลงฐานข้อมูล

---

## 🧪 4. การจัดการ connectivity (Docker)

ระบบมีกลไก **URL Translation** อัตโนมัติ:
- หากคุณตั้งค่า URL ใน Dashboard เป็น `http://localhost:11434`
- เมื่อรันข้างใน Docker ระบบจะแปลงเป็น `http://host.docker.internal:11434` ให้โดยอัตโนมัติ เพื่อให้สามารถเข้าถึง Ollama ที่รันอยู่บนเครื่องจริงได้

---

## 📥 5. การเตรียมโมเดล (Ollama)
อย่าลืมโหลดโมเดลที่จำเป็นก่อนใช้งาน:
```bash
ollama pull ai-tutor     # (หรือโมเดลที่ตั้งค่าไว้)
ollama pull nomic-embed-text
```

> [!TIP]
> **Hot Reload Active**: เนื่องจากมีการใช้ Volume Mount ใน `docker-compose.yml` คุณสามารถแก้ไขโค้ดในโฟลเดอร์ `app/` และ Service จะทำการรีสตาร์ทตัวเองภายในคอนเทนเนอร์ทันที
