"""
Gateway Service - API Gateway routing to all microservices
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(
    title="WhatsApp Marketing SaaS - API Gateway",
    description="Central API Gateway for all microservices",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    "auth": "http://auth-service:8001",
    "whatsapp": "http://whatsapp-service:8003",
    "blast": "http://blast-service:8004",
    "ai": "http://ai-service:8005",
    "payment": "http://payment-service:8006",
    "followup": "http://followup-service:8007",
    "scheduler": "http://scheduler-service:8008",
}


@app.get("/health")
async def health_check():
    """Gateway health check."""
    return {
        "status": "healthy",
        "service": "gateway",
        "port": 8000
    }


@app.get("/services/health")
async def services_health():
    """Check health of all downstream services."""
    results = {}
    async with httpx.AsyncClient() as client:
        for name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=5.0)
                results[name] = {"status": "healthy", "url": url}
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
    
    return results


# Proxy requests to appropriate services
@app.api_route("/api/v1/{service:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(service: str, request: Request):
    """Proxy requests to appropriate microservice."""
    
    # Map service prefixes to actual services
    service_map = {
        "auth": "auth",
        "users": "auth",
        "whatsapp": "whatsapp",
        "wa": "whatsapp",
        "blast": "blast",
        "campaigns": "blast",
        "ai": "ai",
        "auto-reply": "ai",
        "tokens": "ai",
        "payment": "payment",
        "billing": "payment",
        "followup": "followup",
        "leads": "followup",
        "scheduler": "scheduler",
        "jobs": "scheduler",
    }
    
    target_service = service_map.get(service.split("/")[0])
    if not target_service or target_service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    base_url = SERVICES[target_service]
    url = f"{base_url}/api/v1/{service}"
    
    # Forward the request
    async with httpx.AsyncClient() as client:
        try:
            # Get headers (exclude hop-by-hop headers)
            headers = {
                key: value for key, value in request.headers.items()
                if key.lower() not in ["host", "content-length"]
            }
            
            # Get body
            body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None
            
            # Make request to downstream service
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=body,
                timeout=30.0
            )
            
            # Return response
            return JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.content else {},
                headers=dict(response.headers)
            )
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=e.response.status_code if hasattr(e, 'response') and e.response else 502,
                detail=f"Service error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Gateway error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
