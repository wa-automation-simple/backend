"""
API Gateway - Central entry point for all microservices
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from typing import Optional

app = FastAPI(
    title="WhatsApp SaaS API Gateway",
    description="Central API Gateway for WhatsApp Marketing SaaS Platform",
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
    "auth": "http://auth-service:8001",
    "whatsapp": "http://whatsapp-service:8003",
    "blast": "http://blast-service:8004",
    "ai": "http://ai-service:8005",
    "payment": "http://payment-service:8006",
    "followup": "http://followup-service:8007",
    "scheduler": "http://scheduler-service:8008",
}


@app.get("/health")
async def gateway_health():
    """Gateway health check"""
    return {"status": "healthy", "service": "gateway"}


@app.get("/services/health")
async def services_health():
    """Check health of all microservices"""
    health_status = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, base_url in SERVICES.items():
            try:
                response = await client.get(f"{base_url}/health", timeout=2.0)
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": base_url
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "url": base_url
                }
    
    return health_status


# Proxy requests to appropriate services
@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(
    service_name: str,
    path: str,
    request: Request
):
    """Proxy requests to appropriate microservice"""
    
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found"
        )
    
    base_url = SERVICES[service_name]
    url = f"{base_url}/{path}"
    
    # Get request data
    headers = dict(request.headers)
    # Remove hop-by-hop headers
    for key in ["host", "content-length", "transfer-encoding"]:
        headers.pop(key, None)
    
    try:
        async with httpx.AsyncClient() as client:
            # Get body for non-GET requests
            body = None
            if request.method != "GET":
                body = await request.body()
            
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=30.0
            )
            
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
        raise HTTPException(
            status_code=502,
            detail=f"Gateway error: {str(e)}"
        )


@app.get("/")
async def root():
    """API Gateway root endpoint"""
    return {
        "message": "Welcome to WhatsApp SaaS API Gateway",
        "version": "1.0.0",
        "available_services": list(SERVICES.keys()),
        "endpoints": {
            "auth": "/auth/*",
            "whatsapp": "/whatsapp/*",
            "blast": "/blast/*",
            "ai": "/ai/*",
            "payment": "/payment/*",
            "followup": "/followup/*",
            "scheduler": "/scheduler/*"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
