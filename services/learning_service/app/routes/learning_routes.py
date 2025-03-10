import requests
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from .. import database, models, schemas
import os
from fastapi import Header

router = APIRouter()
GATEWAY_SERVICE_URL = os.getenv("GATEWAY_SERVICE_URL")

async def verify_token(authorization: str = Header(...)):

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    response = requests.get(f"{GATEWAY_SERVICE_URL}/auth/verify_token", headers={"Authorization": authorization})

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")
    return response.json()

@router.post("/create_goal/", response_model=schemas.LearningGoalResponse)
async def create_goal(goal: schemas.LearningGoalCreate, user=Depends(verify_token), db: AsyncSession = Depends(database.get_db)):
    try:
        print(f"User ID: {user['user_id']} is creating a goal with title: {goal.title}")
        
        db_goal = models.LearningGoal(
            user_id=int(user["user_id"]),
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
        print(f"Error: {str(e)}") 
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/goals/", response_model=List[schemas.LearningGoalResponse])
async def get_goals(status: Optional[schemas.GoalStatus] = Query(None), user=Depends(verify_token),db: AsyncSession = Depends(database.get_db)):
    query = select(models.LearningGoal).filter(models.LearningGoal.user_id == user["user_id"])
    
    if status:
        query = query.filter(models.LearningGoal.status == status)

    result = await db.execute(query)
    goals = result.scalars().all()
    if not goals: 
        return []
    return goals

@router.put("/update_goal/{goal_id}", response_model=schemas.LearningGoalResponse)
async def update_goal(goal_id: int, goal: schemas.LearningGoalCreate, user=Depends(verify_token), db: AsyncSession = Depends(database.get_db)):

    db_goal = await db.execute(select(models.LearningGoal).filter(models.LearningGoal.id == goal_id, models.LearningGoal.user_id == user["user_id"]))
    db_goal = db_goal.scalar_one_or_none()

    if not db_goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    db_goal.title = goal.title
    db_goal.description = goal.description
    await db.commit()
    await db.refresh(db_goal)
    return db_goal


@router.delete("/delete_goal/{goal_id}", response_model=schemas.LearningGoalResponse)
async def delete_goal(goal_id: int, user=Depends(verify_token), db: AsyncSession = Depends(database.get_db)):
    db_goal = await db.execute(select(models.LearningGoal).filter(models.LearningGoal.id == goal_id, models.LearningGoal.user_id == user["user_id"]))
    db_goal = db_goal.scalar_one_or_none()

    if not db_goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    await db.delete(db_goal)
    await db.commit()
    return db_goal


@router.get("/search", response_model=list[schemas.LearningGoalResponse])
async def search_goals(
    title: str = Query(None), 
    description: str = Query(None), 
    user=Depends(verify_token), 
    db: AsyncSession = Depends(database.get_db)
):
    query = select(models.LearningGoal).filter(models.LearningGoal.user_id == user["user_id"])

    if title:
        query = query.filter(models.LearningGoal.title.ilike(f"%{title}%"))
    if description:
        query = query.filter(models.LearningGoal.description.ilike(f"%{description}%"))
    
    result = await db.execute(query)
    goals = result.scalars().all()  
    return goals
