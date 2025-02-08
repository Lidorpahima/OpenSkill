from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class UserCareerChoice(Base):
    __tablename__ = "user_career_choices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
