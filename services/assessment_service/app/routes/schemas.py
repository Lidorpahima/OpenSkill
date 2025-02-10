from pydantic import BaseModel
from typing import List, Dict, Optional



class ChatMessage(BaseModel):
    message: str

class CareerRecommendation(BaseModel):
    title: str
    description: str
    match_percentage: int

class ChatResponse(BaseModel):
    response: str
    recommendation: Optional[List[CareerRecommendation]] = None 
     
class CareerSelectRequest(BaseModel):
    career_id: int
