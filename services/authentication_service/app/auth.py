# authentication_service/app/auth.py
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", )
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(user_id: int):

    to_encode = {"sub": str(user_id)}
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    try:
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"✅ Token created for user ID: {user_id}")
        return token
    except Exception as e:
        logger.error(f"❌ Error creating token: {str(e)}")
        raise

def verify_token(token: str):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            logger.warning("❌ Token missing user_id")
            return None
        
        logger.info(f"✅ Token verified for user ID: {user_id}")
        return {"user_id": user_id}
    
    except JWTError as e:
        logger.warning(f"❌ Token verification failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error in token verification: {str(e)}")
        return None