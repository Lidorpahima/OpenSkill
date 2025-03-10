import requests
from fastapi import APIRouter, HTTPException, Query, Header
from ..auth import create_access_token, verify_token
from ..schemas import TokenResponse, LoginRequest, UserCreate, UserResponse
import os
import logging
import json
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
GATEWAY_SERVICE_URL = os.getenv("GATEWAY_SERVICE_URL")

@router.post("/login", response_model=TokenResponse)
async def login(user_data: LoginRequest):
    logger.info(f"👤 Login attempt: {user_data.email}")
    
    try:
        response = requests.post(
            f"{GATEWAY_SERVICE_URL}/users/verify_user", 
            json={
                "email": user_data.email,
                "password": user_data.password
            },
            timeout=10.0
        )

        if response.status_code != 200:
            logger.warning(f"❌ Login failed for {user_data.email}: {response.status_code}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_info = response.json()
        logger.info(f"✅ Login successful for user ID: {user_info['user_id']}")
        
        access_token = create_access_token(user_info["user_id"])
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except requests.RequestException as e:
        logger.error(f"❌ Connection error during login: {str(e)}")
        raise HTTPException(status_code=503, detail="User service unavailable")

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):

    logger.info(f"👤 Register attempt: {user.email}")
    logger.info(f"📦 Sending to: {GATEWAY_SERVICE_URL}/users/register")
    
    try:
        response = requests.post(
            f"{GATEWAY_SERVICE_URL}/users/register", 
            json=user.dict(),
            timeout=10.0
        )

        logger.info(f"📡 Register response: Status {response.status_code}")
        logger.info(f"📡 Response content: {response.text}")

        if response.status_code != 201 and response.status_code != 200:
            error_detail = "Failed to create user"
            
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
                    
                    if error_detail == "Email already registered":
                        raise HTTPException(status_code=400, detail=error_detail)
            except json.JSONDecodeError:
                logger.warning(f"❌ Could not parse error response as JSON: {response.text}")
            except Exception as e:
                logger.error(f"❌ Error processing response: {str(e)}")
            
            logger.warning(f"❌ Registration failed: {error_detail}")
            raise HTTPException(status_code=response.status_code, detail=error_detail)

        try:
            user_data = response.json()
            logger.info(f"✅ User registered successfully: {user_data}")
            
            if "id" not in user_data or "username" not in user_data or "email" not in user_data:
                logger.error(f"❌ Missing required fields in response: {user_data}")
                raise HTTPException(status_code=500, detail=user_data["detail"])
            
            return UserResponse(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"]
            )
            
        except json.JSONDecodeError:
            logger.error(f"❌ Could not parse response as JSON: {response.text}")
            raise HTTPException(status_code=500, detail=user_data["detail"])
    
    except HTTPException:
        raise
    except requests.RequestException as e:
        logger.error(f"❌ Connection error during registration: {str(e)}")
        raise HTTPException(status_code=503, detail=f"User service unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/verify_token")
async def verify_token_route(authorization: str = Header(...)):

    logger.info("🔑 Token verification request")
    
    if not authorization:
        logger.warning("❌ Missing authorization header")
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    
    if not authorization.startswith("Bearer "):
        logger.warning("❌ Invalid token format")
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = authorization.split("Bearer ")[1]
    user = verify_token(token)
    
    if not user:
        logger.warning("❌ Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    logger.info(f"✅ Token verified for user ID: {user['user_id']}")
    return {"user_id": int(user["user_id"])}