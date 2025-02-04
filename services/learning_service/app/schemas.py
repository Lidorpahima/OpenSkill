from pydantic import BaseModel

# יצירת מטרה לימודית
class LearningGoalCreate(BaseModel):
    title: str
    description: str

# תשובה עם נתוני מטרה לימודית
class LearningGoalResponse(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        from_attributes  = True

class GoalDescription(BaseModel):
    description: str

    class Config:
        from_attributes = True
