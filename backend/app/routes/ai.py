from fastapi import APIRouter, status
from app.schemas.task import AISummarizeRequest, AISummarizeResponse
from app.services.ai_service import summarize_tasks_with_ai

router = APIRouter(prefix="/api/ai", tags=["AI Tasks"])


@router.post("/summarize", response_model=AISummarizeResponse, status_code=status.HTTP_200_OK)
def summarize_tasks(request: AISummarizeRequest):
    """Receives a list of tasks and returns an AI-generated summary, priority list, and recommendation."""
    return summarize_tasks_with_ai(request.tasks)
