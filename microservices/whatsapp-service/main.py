"""
WhatsApp Service - Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from whatsapp_service.config import settings


app = FastAPI(
    title=settings.SERVICE_NAME,
    description="WhatsApp Account Management Service",
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "port": settings.SERVICE_PORT
    }


# TODO: Include routers when created
# app.include_router(account_router)
# app.include_router(warmup_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
