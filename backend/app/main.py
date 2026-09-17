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

# CORS configuration allowing requests from React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
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
