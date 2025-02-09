from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from . import database
from . import models
from .routes.learning_routes import router as learning_router



async def init_models():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    yield

app = FastAPI(title="Learning Service", lifespan=lifespan)
app.include_router(learning_router, prefix="/learning")
