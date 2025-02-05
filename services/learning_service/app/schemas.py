from pydantic import BaseModel
from enum import Enum
from typing import Optional

class GoalStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class LearningGoalCreate(BaseModel):
    title: str
    description: str

class LearningGoalResponse(BaseModel): 
    id: int
    title: str
    description: str
    status: GoalStatus
    progress: float

    class Config:
        from_attributes = True
