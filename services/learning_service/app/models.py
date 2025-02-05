from sqlalchemy import Column, Integer, String, Text, Float, Enum as SqlEnum
from sqlalchemy.ext.declarative import declarative_base
import enum
from .database import Base


class GoalStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class LearningGoal(Base):
    __tablename__ = "learning_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    status = Column(SqlEnum(GoalStatus, name="goal_status"), default=GoalStatus.IN_PROGRESS) 
    progress = Column(Float, default=0.0)
