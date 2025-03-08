# gateway_service/app/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from fastapi import HTTPException
import httpx
import os

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")  

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        exempt_paths = [
            "/health", 
            "/docs", 
            "/openapi.json", 
            "/redoc"
        ]

        path = request.url.path
        print(f"🔍 Processing request path: {path}")
        
        if (path.startswith("/auth") or 
            path.startswith("/users/verify_user") or 
            path.startswith("/users/register") or 
            any(path == exempt for exempt in exempt_paths)):
            print(f"✅ Path {path} is exempt from authentication")
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        print(f"🔐 Authorization header: {auth_header}")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            print(f"❌ Missing or invalid Authorization header for path: {path}")
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        try:
            async with httpx.AsyncClient() as client:
                print(f"🔄 Verifying token with auth service: {AUTH_SERVICE_URL}/auth/verify_token")
                response = await client.get(
                    f"{AUTH_SERVICE_URL}/auth/verify_token", 
                    headers={"Authorization": auth_header},
                    timeout=10.0 
                )
                
                if response.status_code != 200:
                    print(f"❌ Invalid token: {response.status_code} - {response.text}")
                    raise HTTPException(status_code=401, detail="Invalid token")
                
                print(f"✅ Token verified successfully")
        
        except httpx.RequestError as exc:
            print(f"❌ Error connecting to auth service: {str(exc)}")
            raise HTTPException(status_code=503, detail="Authentication service unavailable")

        return await call_next(request)