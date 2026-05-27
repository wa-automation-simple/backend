"""
API Gateway - Central entry point for all microservices
Handles: routing, authentication, rate limiting
"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Optional

app = FastAPI(title="WhatsApp SaaS API Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    "auth": "http://localhost:8001",
    "whatsapp": "http://localhost:8003",
    "blast": "http://localhost:8004",
    "ai": "http://localhost:8005",
    "payment": "http://localhost:8006",
    "followup": "http://localhost:8007",
    "scheduler": "http://localhost:8008"
}


async def verify_token(request: Request) -> Optional[dict]:
    """Verify JWT token from request headers"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    
    # In production, validate with auth service
    # For now, just extract user info (mock)
    try:
        # Mock token validation
        return {"user_id": 1, "token": token}
    except Exception:
        return None


@app.get("/")
async def root():
    """Gateway root endpoint"""
    return {
        "service": "WhatsApp SaaS API Gateway",
        "version": "1.0.0",
        "status": "running",
        "available_services": list(SERVICES.keys())
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=2.0)
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": service_url
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "url": service_url
                }
    
    return {
        "gateway": "healthy",
        "services": health_status
    }


# Auth routes
@app.post("/api/auth/register")
async def register(request: Request):
    """Register new user"""
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{SERVICES['auth']}/register", json=body)
        return response.json()


@app.post("/api/auth/login")
async def login(request: Request):
    """Login user"""
    form_data = await request.form()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{SERVICES['auth']}/token", data=form_data)
        return response.json()


@app.get("/api/auth/me")
async def get_current_user(request: Request, user: dict = Depends(verify_token)):
    """Get current user"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICES['auth']}/me",
            headers={"Authorization": request.headers.get("Authorization")}
        )
        return response.json()


# WhatsApp routes
@app.post("/api/whatsapp/accounts")
async def create_whatsapp_account(request: Request, user: dict = Depends(verify_token)):
    """Create WhatsApp account"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['whatsapp']}/accounts",
            json={**body, "current_user": user}
        )
        return response.json()


@app.get("/api/whatsapp/accounts")
async def list_whatsapp_accounts(user_id: int, user: dict = Depends(verify_token)):
    """List WhatsApp accounts"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICES['whatsapp']}/accounts",
            params={"user_id": user_id}
        )
        return response.json()


@app.post("/api/whatsapp/accounts/{account_id}/connect")
async def connect_whatsapp(account_id: int, user: dict = Depends(verify_token)):
    """Connect WhatsApp account"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['whatsapp']}/accounts/{account_id}/connect"
        )
        return response.json()


@app.post("/api/whatsapp/accounts/{account_id}/warming/start")
async def start_warming(account_id: int, user: dict = Depends(verify_token)):
    """Start WhatsApp warming"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['whatsapp']}/accounts/{account_id}/warming/start"
        )
        return response.json()


@app.post("/api/whatsapp/accounts/{account_id}/recovery/click")
async def trigger_recovery(account_id: int, user: dict = Depends(verify_token)):
    """Trigger auto-click recovery"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['whatsapp']}/accounts/{account_id}/recovery/click"
        )
        return response.json()


# Blast routes
@app.post("/api/blast/campaigns")
async def create_campaign(request: Request, user: dict = Depends(verify_token)):
    """Create blast campaign"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['blast']}/campaigns",
            json=body
        )
        return response.json()


@app.get("/api/blast/campaigns")
async def list_campaigns(user_id: int, status: Optional[str] = None, user: dict = Depends(verify_token)):
    """List campaigns"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICES['blast']}/campaigns",
            params={"user_id": user_id, "status": status}
        )
        return response.json()


@app.post("/api/blast/campaigns/{campaign_id}/send")
async def send_campaign(campaign_id: int, user: dict = Depends(verify_token)):
    """Send campaign"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['blast']}/campaigns/{campaign_id}/send"
        )
        return response.json()


# AI routes
@app.post("/api/ai/auto-reply/configure")
async def configure_auto_reply(request: Request, user: dict = Depends(verify_token)):
    """Configure AI auto-reply"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['ai']}/auto-reply/configure",
            json=body
        )
        return response.json()


@app.get("/api/ai/token/balance/{user_id}")
async def get_token_balance(user_id: int, user: dict = Depends(verify_token)):
    """Get token balance"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICES['ai']}/token/balance/{user_id}"
        )
        return response.json()


@app.get("/api/ai/token/pricing")
async def get_token_pricing(user: dict = Depends(verify_token)):
    """Get token pricing"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICES['ai']}/token/pricing")
        return response.json()


# Payment routes
@app.post("/api/payment/topup")
async def topup_tokens(request: Request, user: dict = Depends(verify_token)):
    """Top up tokens"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['payment']}/topup",
            json={**body, "user_id": user["user_id"]}
        )
        return response.json()


@app.get("/api/payment/pricing")
async def get_pricing(user: dict = Depends(verify_token)):
    """Get payment pricing"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICES['payment']}/pricing")
        return response.json()


@app.post("/api/payment/packages/{package_name}/purchase")
async def purchase_package(package_name: str, request: Request, user: dict = Depends(verify_token)):
    """Purchase token package"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['payment']}/packages/{package_name}/purchase",
            json={**body, "user_id": user["user_id"]}
        )
        return response.json()


# Follow-up routes
@app.post("/api/followups")
async def create_followup(request: Request, user: dict = Depends(verify_token)):
    """Create follow-up"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['followup']}/followups",
            json=body
        )
        return response.json()


@app.get("/api/followups")
async def list_followups(user_id: int, status: Optional[str] = None, user: dict = Depends(verify_token)):
    """List follow-ups"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICES['followup']}/followups",
            params={"user_id": user_id, "status": status}
        )
        return response.json()


@app.get("/api/followups/stats/{user_id}")
async def get_followup_stats(user_id: int, user: dict = Depends(verify_token)):
    """Get follow-up statistics"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SERVICES['followup']}/followups/stats/{user_id}"
        )
        return response.json()


# Scheduler routes
@app.post("/api/scheduler/warming-schedules/auto-generate/{account_id}")
async def auto_generate_warming(account_id: int, days: int = 30, user: dict = Depends(verify_token)):
    """Auto-generate warming schedule"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['scheduler']}/warming-schedules/auto-generate/{account_id}",
            params={"days": days}
        )
        return response.json()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
