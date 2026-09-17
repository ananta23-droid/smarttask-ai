from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """Base schema containing shared task attributes."""
    title: str = Field(..., min_length=1, max_length=150, description="The title of the task")
    description: Optional[str] = Field(default="", max_length=1000, description="Optional details about the task")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority (LOW, MEDIUM, HIGH)")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status (TODO, IN_PROGRESS, COMPLETED)")

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Task title cannot be empty or whitespace only.")
        return trimmed


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task. All fields are optional."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                raise ValueError("Task title cannot be empty or whitespace only.")
            return trimmed
        return value


class TaskResponse(BaseModel):
    """Schema for returning task details to the client."""
    id: str = Field(..., description="Unique string representation of MongoDB ObjectId")
    title: str
    description: str = ""
    priority: TaskPriority
    status: TaskStatus
    created_at: str = Field(..., description="ISO 8601 formatted timestamp")

    @classmethod
    def from_mongo(cls, data: dict) -> "TaskResponse":
        """Converts a raw MongoDB task document into a TaskResponse model."""
        return cls(
            id=str(data["_id"]),
            title=data.get("title", ""),
            description=data.get("description", "") or "",
            priority=data.get("priority", TaskPriority.MEDIUM),
            status=data.get("status", TaskStatus.TODO),
            created_at=data.get("created_at", datetime.utcnow().isoformat())
        )


class AISummarizeRequestItem(BaseModel):
    """Single task item sent to the AI summary endpoint."""
    title: str
    description: Optional[str] = ""
    priority: TaskPriority
    status: TaskStatus


class AISummarizeRequest(BaseModel):
    """Payload sent by the client to summarize tasks."""
    tasks: List[AISummarizeRequestItem]


class AISummarizeResponse(BaseModel):
    """Structured AI response analyzing current tasks."""
    summary: str
    highest_priority_tasks: List[str]
    recommended_order: List[str]
    recommendation: str
