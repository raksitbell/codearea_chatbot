# CodeArea — AI Tutor BaaS (Backend-as-a-Service)

ระบบหลังบ้านอัจฉริยะ (Modular Backend) สำหรับบริการ AI Tutor ในโปรเจกต์ CodeArea พัฒนาด้วย **FastAPI (Python)** ออกแบบมาในรูปแบบ **BaaS (Backend-as-a-Service)** ที่สามารถแยกไปรันเป็นบริการอิสระ (Stateless Container) และเชื่อมต่อกับระบบหลักผ่าน Proxy ได้อย่างสมบูรณ์

## 🚀 คุณสมบัติเด่น (Features)

- 🤖 **ระบบโมเดลคู่ (Dual Model System)**: รองรับการสลับโมเดลระหว่าง `Qwen-3` (เน้นการวิเคราะห์เป็นขั้นตอน CoT) และ `Gemma-3` (เน้นความเป็นกันเองและความเร็ว)
- ⚡ **การตอบกลับแบบเรียลไทม์ (Streaming)**: ใช้เทคนิค **Chunked Transfer Encoding** เพื่อให้ AI พิมพ์ตอบโต้ได้ทันทีโดยไม่ต้องรอให้เจนเสร็จทั้งหมด
- 📚 **การดึงข้อมูลอัจฉริยะ (RAG Integration)**: เชื่อมต่อข้อมูลโดยตรงจากโจทย์ (PDF) ผ่าน **ChromaDB Vector Store** และ **nomic-embed-text** เพื่อให้คำแนะนำที่แม่นยำตามเนื้อหาบทเรียน
- 🎨 **แดชบอร์ดจัดการส่วนตัว (Integrated Dashboard)**: มาพร้อมหน้าจอสำหรับตั้งค่าการเชื่อมต่อ Ollama และการจัดการโมเดลในตัว (Vite + React)
- 📜 **เอกสาร API มาตรฐาน (Swagger UI)**: มีระบบเอกสาร API แบบ Interactive ที่สามารถทดสอบได้ทันทีผ่านเส้นทาง `/docs`

---

## 💻 เทคโนโลยีที่ใช้ (Tech Stack)

<p align="left">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,fastapi,react,vite,ts,docker,ollama,supabase" />
  </a>
</p>

| หมวดหมู่ | เทคโนโลยีที่เลือกใช้ |
| :--- | :--- |
| **ภาษาหลัก / Framework** | FastAPI (Python 3.10+) |
| **แดชบอร์ดจัดการ UI** | Vite + React + TailwindCSS |
| **ระบบรัน AI (Backend)** | Ollama (Local LLM) |
| **ฐานข้อมูลเวกเตอร์** | ChromaDB |
| **ระบบประมวลผลข้อความ** | nomic-embed-text |
| **ระบบคอนเทนเนอร์** | Docker & Docker Compose |

---

## 📂 โครงสร้างโปรเจกต์ (Project Structure)

```text
ai-tutor/
├── app/                  # เลเยอร์แอปพลิเคชัน Python FastAPI
│   ├── api/              # ส่วนจัดการ API (ai, config, questions, testing)
│   ├── core/             # การตั้งค่าส่วนกลางและความปลอดภัย
│   ├── services/         # เลเยอร์ลอจิก (Ollama, RAG, Supabase)
│   ├── schemas/          # โมเดลข้อมูล Pydantic (Type Safety)
│   └── main.py           # จุดเริ่มต้นของระบบ (Entry Point)
├── ui/                   # แดชบอร์ดจัดการสำหรับแอดมิน (React)
├── Dockerfile            # การตั้งค่าสำหรับสร้าง Production Build
└── docker-compose.yml    # การตั้งค่าสำหรับการรันระบบด้วย Docker
```

---

## 🏗️ สถาปัตยกรรมระบบ (Architecture)

### 1. กลไกการส่งข้อมูลแบบสตรีมมิ่ง (Streaming Mechanism)
แอปพลิเคชันใช้ `StreamingResponse` ร่วมกับ `yield` Generator ใน Python เพื่อส่งข้อมูลออกมาทีละ Chunk ทันทีที่ AI ประมวลผลแต่ละ Token เสร็จ วิธีนี้ช่วยลดความล่าช้า (Latency) และประหยัดหน่วยความจำบนเซิร์ฟเวอร์เนื่องจากไม่ต้องเก็บสตริงขนาดใหญ่ไว้ใน RAM

### 2. ระบบการดึงข้อมูลมาเสริม (RAG Flow)
1. **การนำเข้าข้อมูล (Ingestion)**: ดึงข้อความจาก PDF → แบ่งเป็นชิ้นส่วน (Chunking) → แปลงเป็นเวกเตอร์ (Embeddings) → เก็บลง **ChromaDB**
2. **การดึงข้อมูล (Retrieval)**: เมื่อผู้ใช้อธิบายนิยามหรือติดปัญหา → ระบบค้นหาเนื้อหาที่เกี่ยวข้องที่สุดจากเวกเตอร์ DB → นำเนื้อหานั้นมาเป็นบริบท (Context)
3. **การสร้างคำตอบ (Generation)**: ส่งคำถามพร้อมบริบทให้ AI ประมวลผลและสรุปออกมาเป็นคำแนะนำแบบทีละขั้นตอน

---

## 🌓 เปรียบเทียบโมเดล (Dual Model System)

| คุณสมบัติ | `ai-tutor-qwen` | `ai-tutor-gemma` |
| :--- | :--- | :--- |
| **สไตล์การตอบ** | **คิดวิเคราะห์เจาะลึก (CoT)** | **ติวเตอร์มาตรฐาน (Standard)** |
| **วัตถุประสงค์หลัก** | แก้ไขปัญหาตรรกะที่ซับซ้อน | ให้คำใบ้และคำแนะนำทั่วไป |
| **โมเดลฐาน** | Qwen 3 (8B) | Gemma 3 (12B) |
| **ความแม่นยำ** | สูงมาก (Temperature 0.1) | ปกติ (Temperature 0.4) |

---

## 📖 คู่มือการติดตั้งและใช้งาน (Setup Guide)

### 🐳 การรันด้วย Docker (แนะนำ)
```bash
docker compose up -d --build
```
- **หน้าแดชบอร์ด**: [http://localhost:8080](http://localhost:8080)
- **เอกสาร API (Swagger)**: [http://localhost:8080/docs](http://localhost:8080/docs)

### 🛠️ การรันในโหมดพัฒนา (Local Development)
**ส่วนหลังบ้าน (Backend):**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```
**ส่วนจัดการ (UI Dashboard):**
```bash
cd ui && npm install && npm run dev
```

---

## 🎓 คำถามที่พบบ่อย (Project Defense Q&A)

> [!NOTE]
> หัวข้อสำหรับการเตรียมตัวตอบคำถามในการนำเสนอโปรเจกต์เกี่ยวกับการทำงานของ AI

- **ทำไมไม่ใช้ OpenAI หรือ Gemini?**: เพื่อรักษา **ความเป็นส่วนตัวของข้อมูล** (Data Privacy) และทำให้ระบบทำงานได้โดยไม่มีค่าใช้จ่ายต่อ Token (Cost Efficiency)
- **AI จะแอบเฉลยโค้ดให้นักเรียนไหม?**: ระบบใช้ **System Prompt Engineering** บังคับให้ AI ทำหน้าที่เป็นติวเตอร์ ซึ่งจะใบ้เฉพาะแนวคิด (Pseudo-code) เท่านั้น **ห้ามแสดงโค้ดเฉลยเด็ดขาด**
- **หากใช้งานพร้อมกันจำนวนมากจะไหวไหม?**: รันไทม์ Ollama มีข้อจำกัดทาง VRAM ในอนาคตสามารถขยายการรองรับได้ด้วยการทำ Load Balancing หรือใช้ Message Queue

---

## 📜 การอนุญาตใช้งาน (License)
จัดทำขึ้นสำหรับโปรเจกต์ **CodeArea** — มุ่งเน้นการยกระดับการเรียนการสอนโปรแกรมมิ่งด้วยเทคโนโลยี AI
