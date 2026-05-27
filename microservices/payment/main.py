"""Payment Service Main Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from payment.config import settings

# Import routers from each module
from payment.models.wallet.routes import router as wallet_router
from payment.models.transaction.routes import router as transaction_router
from payment.models.package.routes import router as package_router
from payment.models.subscription.routes import router as subscription_router

app = FastAPI(
    title=settings.SERVICE_NAME,
    description="Payment & Token Management Service for WhatsApp Marketing SaaS",
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

# Include routers from each module
app.include_router(wallet_router)
app.include_router(transaction_router)
app.include_router(package_router)
app.include_router(subscription_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    from payment.core.database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    # Create default token packages
    from payment.core.database import SessionLocal
    from payment.models.package.repository import PackageRepository
    
    db = SessionLocal()
    try:
        repo = PackageRepository(db)
        packages = repo.get_packages(active_only=False)
        
        if not packages:
            # Create default packages with markup pricing
            default_packages = [
                {
                    "name": "Starter Pack",
                    "description": "Perfect for small businesses starting with AI auto-replies",
                    "tokens_included": 100,
                    "base_price": 300.0,  # $3 x 100
                    "sell_price": 1000.0,  # $10 x 100 (markup)
                    "discount_percentage": 0.0,
                    "bonus_tokens": 0,
                    "is_popular": False
                },
                {
                    "name": "Pro Pack",
                    "description": "Best value for growing businesses with high message volume",
                    "tokens_included": 500,
                    "base_price": 1500.0,
                    "sell_price": 4500.0,  # 10% discount from $10/token
                    "discount_percentage": 10.0,
                    "bonus_tokens": 50,
                    "is_popular": True
                },
                {
                    "name": "Enterprise Pack",
                    "description": "Maximum savings for large-scale operations",
                    "tokens_included": 2000,
                    "base_price": 6000.0,
                    "sell_price": 15000.0,  # 25% discount from $10/token
                    "discount_percentage": 25.0,
                    "bonus_tokens": 500,
                    "is_popular": False
                }
            ]
            
            for pkg_data in default_packages:
                repo.create_package(**pkg_data)
                print(f"✅ Created package: {pkg_data['name']}")
    finally:
        db.close()
    
    print(f"✅ {settings.SERVICE_NAME} service started on port {settings.PORT}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
