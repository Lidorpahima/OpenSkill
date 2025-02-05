from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas, database
import asyncio
from fastapi import Depends, HTTPException, status
from .auth import verify_token
from sqlalchemy.sql import func
from fastapi import Query, Depends
from sqlalchemy.future import select
from . import models, schemas, database
from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas, database
from .auth import verify_token
from typing import List, Optional
from contextlib import asynccontextmanager



async def init_models():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/create_goal/", response_model=schemas.LearningGoalResponse)
async def create_goal(goal: schemas.LearningGoalCreate, user=Depends(verify_token), db: AsyncSession = Depends(database.get_db)):
    try:
        print(f"User ID: {user['user_id']} is creating a goal with title: {goal.title}")
        
        db_goal = models.LearningGoal(
            user_id=user["user_id"],
            title=goal.title,
            description=goal.description,
            progress=0.0
        )
        db.add(db_goal)
        await db.commit()
        await db.refresh(db_goal)
        print("Goal created successfully:", db_goal)
        return db_goal

    except Exception as e:
        await db.rollback()
        print(f"Error: {str(e)}")  # הדפסה ל-debug
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/goals/", response_model=List[schemas.LearningGoalResponse])
async def get_goals(
    status: Optional[schemas.GoalStatus] = Query(None),  # אפשרות לסנן לפי סטטוס
    user=Depends(verify_token),
    db: AsyncSession = Depends(database.get_db)
):
    query = select(models.LearningGoal).filter(models.LearningGoal.user_id == user["user_id"])
    
    if status:
        query = query.filter(models.LearningGoal.status == status)

    result = await db.execute(query)
    goals = result.scalars().all()
    if not goals: 
        return []
    return goals

# עדכון מטרה
@app.put("/update_goal/{goal_id}", response_model=schemas.LearningGoalResponse)
async def update_goal(goal_id: int, goal: schemas.LearningGoalCreate, user=Depends(verify_token), db: AsyncSession = Depends(database.get_db)):
    # בדוק אם המטרה קיימת
    db_goal = await db.execute(select(models.LearningGoal).filter(models.LearningGoal.id == goal_id, models.LearningGoal.user_id == user["user_id"]))
    db_goal = db_goal.scalar_one_or_none()

    if not db_goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    # עדכון המטרה
    db_goal.title = goal.title
    db_goal.description = goal.description
    await db.commit()
    await db.refresh(db_goal)
    return db_goal


# מחיקת מטרה
@app.delete("/delete_goal/{goal_id}", response_model=schemas.LearningGoalResponse)
async def delete_goal(goal_id: int, user=Depends(verify_token), db: AsyncSession = Depends(database.get_db)):
    # בדוק אם המטרה קיימת
    db_goal = await db.execute(select(models.LearningGoal).filter(models.LearningGoal.id == goal_id, models.LearningGoal.user_id == user["user_id"]))
    db_goal = db_goal.scalar_one_or_none()

    if not db_goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    # מחיקת המטרה
    await db.delete(db_goal)
    await db.commit()
    return db_goal

from fastapi import Query

# חיפוש וסינון מטרות
@app.get("/search", response_model=list[schemas.LearningGoalResponse])
async def search_goals(
    title: str = Query(None), 
    description: str = Query(None), 
    user=Depends(verify_token), 
    db: AsyncSession = Depends(database.get_db)
):
    # התחלת השאילתה בצורה אסינכרונית
    query = select(models.LearningGoal).filter(models.LearningGoal.user_id == user["user_id"])

    if title:
        query = query.filter(models.LearningGoal.title.ilike(f"%{title}%"))
    if description:
        query = query.filter(models.LearningGoal.description.ilike(f"%{description}%"))
    
    # הרצת השאילתה בצורה אסינכרונית
    result = await db.execute(query)
    goals = result.scalars().all()  # הפוך את התוצאה לרשימה של אובייקטים
    return goals









'''
 UPDATE PROGRESS FOR A LEARNING GOAL PROGRESS 
async def update_progress(goal_id: int, db: AsyncSession):
    result = await db.execute(select(models.LearningGoal).filter(models.LearningGoal.id == goal_id))
    goal = result.scalar_one_or_none()

    if goal:
        # כאן נחשב את אחוז ההתקדמות (לדוגמה, לפי מספר מבחנים שהושלמו)
        # כרגע נשתמש בערך דמי (50%) כדוגמה
        goal.progress = 50.0  
        
        # אם ההתקדמות 100%, נשנה את הסטטוס ל-COMPLETED
        if goal.progress == 100.0:
            goal.status = models.GoalStatus.COMPLETED

        await db.commit()
        await db.refresh(goal)
'''