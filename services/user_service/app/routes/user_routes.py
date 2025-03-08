from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import database, models, schemas, auth

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse, status_code=201)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):

    print("🔍 Received register request:", user.dict())

    existing_user = await db.execute(select(models.User).filter(models.User.email == user.email))
    if existing_user.scalar():
        print("❌ Email already exists:", user.email)
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    print("✅ User created:", db_user)
    return db_user


@router.post("/verify_user")
async def verify_user(user_data: schemas.LoginRequest, db: AsyncSession = Depends(database.get_db)):
        
    result = await db.execute(select(models.User).filter(models.User.email == user_data.email))
    db_user = result.scalar_one_or_none()

    if not db_user or not auth.verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user_id": db_user.id}
