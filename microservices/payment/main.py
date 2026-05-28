"""Payment Service Main Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.middleware import AuthMiddleware, log_requests
from payment.core.config import settings

# Import routers from each module
from payment.modules.wallet.routes import router as wallet_router
from payment.modules.subscription.routes import router as subscription_router
from payment.modules.transaction.routes import router as transaction_router
from payment.modules.package.routes import router as package_router

app = FastAPI(
    title=settings.SERVICE_NAME,
    description="Payment & Billing Service",
    version=settings.VERSION
)

# Add authentication middleware (handles access_token for all routes)
app.add_middleware(AuthMiddleware)

# Add request logging middleware
app.middleware("http")(log_requests)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(wallet_router, prefix="/api/v1", tags=["Wallet"])
app.include_router(subscription_router, prefix="/api/v1", tags=["Subscriptions"])
app.include_router(transaction_router, prefix="/api/v1", tags=["Transactions"])
app.include_router(package_router, prefix="/api/v1", tags=["Packages"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    from payment.core.database import init_db
    await init_db()


@app.get("/")
async def root():
    return {"message": "Payment service is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("payment.main:app", host="0.0.0.0", port=8006, reload=True)
