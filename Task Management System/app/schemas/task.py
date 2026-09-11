from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    due_date: datetime | None = None


class TaskPriorityUpdate(BaseModel):
    priority: TaskPriority


class TaskAssignment(BaseModel):
    assigned_to_id: int


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    assigned_to_id: int | None = None
    created_by_id: int
    priority: TaskPriority
    status: TaskStatus
    due_date: datetime | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class TaskAssignmentResponse(BaseModel):
    message: str
    task: TaskOut