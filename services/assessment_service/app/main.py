from fastapi import FastAPI
from app.routes import ai_chat  # ודא שהנתיב הזה תקין
from contextlib import asynccontextmanager
from . import models, schemas, database


async def init_models():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_models()
    yield


app = FastAPI(lifespan=lifespan)




app.include_router(ai_chat.router, prefix="/ai_chat", tags=["AI Chat"])

@app.get("/")
async def root():
    return {"message": "Assessment Service is running"}


