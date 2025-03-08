# gateway_service/app/main.py
from fastapi import FastAPI, Request
import httpx
import os
from .middleware import AuthMiddleware
import json

app = FastAPI()

# הוספת middleware
app.add_middleware(AuthMiddleware)

# הגדרת כתובות השירותים
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8000")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")
LEARNING_SERVICE_URL = os.getenv("LEARNING_SERVICE_URL", "http://learning_service:8000")
ASSESSMENT_SERVICE_URL = os.getenv("ASSESSMENT_SERVICE_URL", "http://assessment_service:8000")

# מיפוי שירותים
SERVICE_MAP = {
    "users": USER_SERVICE_URL,
    "auth": AUTH_SERVICE_URL,
    "learning": LEARNING_SERVICE_URL,
    "ai_chat": ASSESSMENT_SERVICE_URL,
}

@app.get("/health")
async def health():
    """נקודת קצה לבדיקת בריאות המערכת"""
    return {"status": "ok"}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(service: str, path: str, request: Request):
    """
    פונקציה זו מעבירה בקשות לשירותים המתאימים לפי המיפוי
    """
    if service not in SERVICE_MAP:
        print(f"❌ Service not found: {service}/{path}")
        return {"error": f"Service not found: {service}/{path}"}

    target_url = f"{SERVICE_MAP[service]}/{path}"
    print(f"🔄 Forwarding request to: {target_url}")
    
    # העברת הבקשה לשירות המתאים
    async with httpx.AsyncClient() as client:
        try:
            # קבלת גוף הבקשה
            body = await request.body() if request.method in ["POST", "PUT"] else None
            
            # העברת כל ה-headers חוץ מ-host
            headers = {key: value for key, value in request.headers.items() if key.lower() != "host"}
            
            if body:
                try:
                    print(f"📦 Request body: {json.loads(body)}")
                except:
                    print(f"📦 Request body (raw): {body}")
            
            # שליחת הבקשה לשירות היעד
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body if body else None,
                timeout=30.0  # הוספת timeout
            )
            
            # הדפסת מידע על התשובה לדיבוג
            print(f"✅ Response from {target_url}: Status {response.status_code}")
            try:
                response_json = response.json()
                print(f"📄 Response content: {response_json}")
                return response_json
            except Exception as e:
                # במקרה שהתשובה אינה JSON תקין
                print(f"⚠️ Could not parse response as JSON: {str(e)}")
                return {"content": response.text, "status_code": response.status_code}
            
        except Exception as e:
            print(f"❌ ERROR in gateway proxy ({target_url}): {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}