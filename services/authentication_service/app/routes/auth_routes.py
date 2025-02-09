import requests
from fastapi import APIRouter, HTTPException, Query
from ..auth import create_access_token, verify_token
from ..schemas import TokenResponse, LoginRequest , UserCreate, UserResponse
from fastapi import Header


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

@router.post("/register/", response_model= UserResponse)
async def register_user(user: UserCreate):

    response = requests.post(f"{USER_SERVICE_URL}/users/register/", json=user.dict())

    if response.status_code == 400:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if response.status_code != 201 and response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to create user")

    return response.json()


@router.get("/verify_token")
async def verify_token_route(authorization: str = Header(None)):  
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.split("Bearer ")[1]

    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"user_id": int(user["user_id"])}