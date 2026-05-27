"""WhatsApp service main entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from whatsapp.config import settings
from whatsapp.core.database import init_db
from whatsapp.api.v1.accounts import router as accounts_router


# Create FastAPI application
app = FastAPI(
    title=settings.SERVICE_NAME.title() + " Service",
    version=settings.SERVICE_VERSION,
    description="WhatsApp Account Management Service for Multi-Account Support"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print(f"{settings.SERVICE_NAME} service started successfully!")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION
    }


# Include routers
app.include_router(accounts_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
