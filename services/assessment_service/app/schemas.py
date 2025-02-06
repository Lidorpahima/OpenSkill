from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    user_id: int
    message: str

class ChatResponse(BaseModel):
    response: str

class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    message: str
    response: str

    class Config:
        from_attributes = True
