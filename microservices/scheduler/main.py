"""Scheduler Service Main Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.middleware import AuthMiddleware, log_requests
from scheduler.config import settings
from scheduler.api.v1.tasks import router as tasks_router

app = FastAPI(
    title=settings.SERVICE_NAME,
    description="Scheduler & Recovery Service for WhatsApp Marketing SaaS",
    version="1.0.0"
)

# Add authentication middleware (handles access_token for all routes)
app.add_middleware(AuthMiddleware)

# Add request logging middleware
app.middleware("http")(log_requests)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)


@app.on_event("startup")
async def startup_event():
    from scheduler.core.database import Base, engine
    Base.metadata.create_all(bind=engine)
    print(f"✅ {settings.SERVICE_NAME} service started on port {settings.PORT}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
