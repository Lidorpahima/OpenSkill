from fastapi import FastAPI
from app.routes.auth_routes import router as auth_router
import uvicorn


app = FastAPI(title="Authentication Service")

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "Auth Service is Running"}

@app.get("/health")
async def health():
    return {"status": "ok"}