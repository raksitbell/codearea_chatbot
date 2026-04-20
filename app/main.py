from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.endpoints import ai, config, questions, testing

app = FastAPI(
    title="AI Tutor BaaS API",
    description="Modular Backend-as-a-Service for AI-assisted programming education.",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the built UI dashboard
static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

# Register API routers
app.include_router(ai.router, prefix="/api/ai", tags=["AI logic"])
app.include_router(config.router, prefix="/api/config", tags=["System Config"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(testing.router, prefix="/api/testing", tags=["Development & Testing"])

@app.get("/", response_class=HTMLResponse)
async def serve_root():
    """Serves the integrated Vite UI or a fallback status page."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(), status_code=200)
    
    return HTMLResponse(content="""
        <html>
            <body style="font-family: sans-serif; padding: 4rem; text-align: center; background: #05060a; color: white;">
                <h1 style="color: #6366f1;">AI Tutor BaaS v2</h1>
                <p>Status: <span style="color: #10b981;">Online</span></p>
                <hr style="border: 1px solid #1a1c2e; margin: 2rem 0; max-width: 400px; margin-inline: auto;">
                <p style="opacity: 0.5; font-size: 0.8rem;">Integrated UI not found. Use API endpoints or rebuild Docker.</p>
            </body>
        </html>
    """)

@app.get("/api/health")
async def health_check():
    """Simple heartbeat check."""
    return {"status": "ok", "version": "2.0.0"}
