# gateway_service/app/main.py
from fastapi import FastAPI, Request, Response
import httpx
import os
from .middleware import AuthMiddleware
import json
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(AuthMiddleware)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
LEARNING_SERVICE_URL = os.getenv("LEARNING_SERVICE_URL")
ASSESSMENT_SERVICE_URL = os.getenv("ASSESSMENT_SERVICE_URL")

SERVICE_MAP = {
    "users": USER_SERVICE_URL,
    "auth": AUTH_SERVICE_URL,
    "learning": LEARNING_SERVICE_URL,
    "ai_chat": ASSESSMENT_SERVICE_URL,
}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(service: str, path: str, request: Request):

    if service not in SERVICE_MAP:
        print(f"❌ Service not found: {service}/{path}")
        return {"error": f"Service not found: {service}/{path}"}

    target_url = f"{SERVICE_MAP[service]}/{path}"
    print(f"🔄 Forwarding request to: {target_url}")
    
    async with httpx.AsyncClient() as client:
        try:
            body = await request.body() if request.method in ["POST", "PUT"] else None
            
            headers = {key: value for key, value in request.headers.items() if key.lower() != "host"}
            
            if body:
                try:
                    print(f"📦 Request body: {json.loads(body)}")
                except:
                    print(f"📦 Request body (raw): {body}")
            
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body if body else None,
                timeout=30.0
            )
            
            print(f"✅ Response from {target_url}: Status {response.status_code}")
            try:
                response_json = response.json()
                print(f"📄 Response content: {response_json}")
                return Response(content=response.content, status_code=response.status_code, headers=response.headers)
            except Exception as e:
                print(f"⚠️ Could not parse response as JSON: {str(e)}")
                return {"content": response.text, "status_code": response.status_code}
            
        except Exception as e:
            print(f"❌ ERROR in gateway proxy ({target_url}): {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Internal Server Error: {str(e)}"}
            )