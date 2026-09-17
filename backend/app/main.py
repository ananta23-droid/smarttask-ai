import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.tasks import router as tasks_router
from app.routes.ai import router as ai_router
from app.database import check_db_connection

app = FastAPI(
    title="SmartTask AI API",
    description="AI-powered task management REST API built with FastAPI, MongoDB, and OpenRouter",
    version="1.0.0"
)

# CORS configuration supporting local development and production deployments
# Defaults cover standard Vite/React local dev ports and production Vercel frontend.
# Can be supplemented or overridden using the CORS_ORIGINS environment variable.
default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://smarttask-ai-plum.vercel.app",
]

env_cors = os.getenv("CORS_ORIGINS", "").strip()
if env_cors:
    extra_origins = [orig.strip() for orig in env_cors.split(",") if orig.strip()]
    allowed_origins = list(dict.fromkeys(default_origins + extra_origins))
else:
    allowed_origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API route modules
app.include_router(tasks_router)
app.include_router(ai_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend service and database connectivity."""
    db_connected = check_db_connection()
    return {
        "status": "ok" if db_connected else "degraded",
        "service": "smart-task-ai-backend",
        "database": "connected" if db_connected else "disconnected"
    }
