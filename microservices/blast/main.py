"""Blast Service Main Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from blast.config import settings
from blast.api.v1.campaigns import router as campaigns_router

app = FastAPI(
    title=settings.SERVICE_NAME,
    description="Blast Campaign Service for WhatsApp Marketing SaaS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaigns_router)


@app.on_event("startup")
async def startup_event():
    from blast.core.database import Base, engine
    Base.metadata.create_all(bind=engine)
    print(f"✅ {settings.SERVICE_NAME} service started on port {settings.PORT}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
