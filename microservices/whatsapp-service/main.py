from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from whatsapp_service.config.database import engine, Base
from whatsapp_service.routes.whatsapp_routes import router as whatsapp_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WhatsApp Service",
    description="WhatsApp Account Management Service for WhatsApp SaaS",
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

# Include routers
app.include_router(whatsapp_router)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "whatsapp-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
