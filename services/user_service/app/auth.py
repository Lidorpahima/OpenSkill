from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# סוד להצפנה (במציאות זה אמור להיות סודי ומורכב יותר)
SECRET_KEY = "OpenSkill"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# הצפנת סיסמאות עם bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# יצירת Token
def create_access_token(user_id: int):
    to_encode = {"sub": str(user_id)}  # "sub" הוא ה- user_id
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# בדיקת סיסמה
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# הצפנת סיסמה חדשה
def get_password_hash(password):
    return pwd_context.hash(password)

# אימות Token
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")  # לוג חשוב
        user_id = payload.get("sub")

        if user_id is None:
            print("User ID is missing from token!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token - user_id missing"
            )

        return {"user_id": user_id}

    except JWTError as e:
        print(f"JWT Error: {e}")  # לוג נוסף
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
