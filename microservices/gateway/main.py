"""API Gateway Main Entry Point"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(
    title="WhatsApp Marketing SaaS - API Gateway",
    description="Central API Gateway for all microservices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    "auth": "http://auth:8001",
    "whatsapp": "http://whatsapp:8003",
    "blast": "http://blast:8004",
    "ai": "http://ai:8005",
    "payment": "http://payment:8006",
    "followup": "http://followup:8007",
    "scheduler": "http://scheduler:8008"
}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    """Proxy requests to appropriate microservice"""
    url = request.url.path
    parts = url.strip("/").split("/")
    
    if len(parts) < 2 or parts[0] != "api":
        return JSONResponse({"error": "Invalid path"}, status_code=400)
    
    # Determine service from path (e.g., /api/v1/users -> auth, /api/v1/campaigns -> blast)
    service_map = {
        "users": "auth",
        "accounts": "whatsapp",
        "warmup": "whatsapp",
        "campaigns": "blast",
        "replies": "ai",
        "balance": "payment",
        "packages": "payment",
        "topup": "payment",
        "leads": "followup",
        "followups": "followup",
        "tasks": "scheduler"
    }
    
    # Find matching service
    target_service = None
    for key, service in service_map.items():
        if key in url.lower():
            target_service = service
            break
    
    if not target_service:
        return JSONResponse({"error": "Service not found"}, status_code=404)
    
    service_url = SERVICES.get(target_service)
    if not service_url:
        return JSONResponse({"error": "Service unavailable"}, status_code=503)
    
    # Proxy the request
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=f"{service_url}{url}",
                headers=dict(request.headers),
                content=await request.body()
            )
            return JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.content else {}
            )
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
