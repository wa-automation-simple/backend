"""Auth Service Main Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.middleware import AuthMiddleware, log_requests
from auth.core.config import settings

# Import routers from each module
from auth.modules.user.routes import router as user_router
from auth.modules.role.routes import router as role_router
from auth.modules.permission.routes import router as permission_router

app = FastAPI(
    title=settings.SERVICE_NAME,
    description="Authentication & User Management Service",
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
app.include_router(user_router, prefix="/api/v1", tags=["Users"])
app.include_router(role_router, prefix="/api/v1", tags=["Roles"])
app.include_router(permission_router, prefix="/api/v1", tags=["Permissions"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    from auth.core.database import init_db
    await init_db()


@app.get("/")
async def root():
    return {"message": "Auth service is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("auth.main:app", host="0.0.0.0", port=8001, reload=True)
