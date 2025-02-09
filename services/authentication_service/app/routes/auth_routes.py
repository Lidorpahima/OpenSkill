import requests
from fastapi import APIRouter, HTTPException, Depends
from ..auth import create_access_token, verify_token
from ..schemas import TokenResponse, LoginRequest


router = APIRouter()
USER_SERVICE_URL = "http://user_service:8000/users"

@router.post("/login", response_model=TokenResponse)
async def login(user_data: LoginRequest):

    response = requests.post(f"{USER_SERVICE_URL}/verify_user", json={
        "email": user_data.email,
        "password": user_data.password
    })

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_info = response.json()
    access_token = create_access_token(user_info["user_id"])
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify_token")
async def verify_token_route(token: str):
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user