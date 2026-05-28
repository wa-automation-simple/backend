"""Follow-up Service Main Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.middleware import AuthMiddleware, log_requests
from followup.core.config import settings

# Import routers from each module
from followup.modules.follow_up.routes import router as follow_up_router

app = FastAPI(
    title=settings.SERVICE_NAME,
    description="Lead Follow-up Service",
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
app.include_router(follow_up_router, prefix="/api/v1", tags=["Follow-ups"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    from followup.core.database import init_db
    await init_db()


@app.get("/")
async def root():
    return {"message": "Follow-up service is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("followup.main:app", host="0.0.0.0", port=8007, reload=True)
