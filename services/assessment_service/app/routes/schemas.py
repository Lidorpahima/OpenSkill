from pydantic import BaseModel
from typing import List, Dict, Optional



class ChatMessage(BaseModel):
    user_id: int
    message: str

class CareerRecommendation(BaseModel):
    title: str
    description: str
    match_percentage: int

class ChatResponse(BaseModel):
    response: str

