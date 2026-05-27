"""Auth service main entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.config import settings
from auth.core.database import init_db, get_db
from auth.api.v1.users import router as users_router


# Create FastAPI application
app = FastAPI(
    title=settings.SERVICE_NAME.title() + " Service",
    version=settings.SERVICE_VERSION,
    description="Authentication and Authorization Service for WhatsApp Marketing SaaS"
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
app.include_router(users_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
