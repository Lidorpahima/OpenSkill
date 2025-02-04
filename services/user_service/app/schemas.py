from pydantic import BaseModel

# רישום משתמש
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# תשובת API עם פרטי משתמש
class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

# בקשת התחברות (Login)
class UserLogin(BaseModel):
    username: str
    password: str

# תשובה לאחר התחברות (Token)
class Token(BaseModel):
    access_token: str
    token_type: str
