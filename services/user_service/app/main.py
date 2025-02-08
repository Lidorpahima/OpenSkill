from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas, database, auth
from fastapi.security import OAuth2PasswordBearer
import asyncio
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas, database, auth
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer


async def init_models():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# להריץ את יצירת הטבלאות כשהשרת מתחיל


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_models()
    yield

app = FastAPI(lifespan=lifespan)

# נקודת בדיקה בסיסית
@app.get("/")
async def read_root():
    return {"message": "Server is running!"}


@app.post("/register/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    # בדיקת משתמש קיים לפי אימייל
    existing_user = await db.execute(select(models.User).filter(models.User.email == user.email))
    if existing_user.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # בדיקת שם משתמש קיים
    existing_username = await db.execute(select(models.User).filter(models.User.username == user.username))
    if existing_username.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # יצירת משתמש חדש
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@app.post("/login/", response_model=schemas.Token)
async def login(user: schemas.UserLogin, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.User).filter(models.User.username == user.username))
    db_user = result.scalar_one_or_none()

    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = auth.create_access_token(user_id=db_user.id) 
    return {"access_token": access_token, "token_type": "bearer"}

# נתיב מוגן עם Token
@app.get("/protected/")
async def protected_route(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"message": f"Hello, {user['sub']}! You have access."}

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": user.id, "username": user.username, "email": user.email}