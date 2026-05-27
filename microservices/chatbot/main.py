"""Chatbot Service Main Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

# Import routers from each module
from .modules.chatbot.routes import router as chatbot_router
from .modules.chatbot_agent.routes import router as chatbot_agent_router
from .modules.chatbot_node.routes import router as chatbot_node_router
from .modules.chatbot_tool.routes import router as chatbot_tool_router
from .modules.chatbot_state.routes import router as chatbot_state_router
from .modules.chat_message.routes import router as chat_message_router
from .modules.conversation.routes import router as conversation_router

app = FastAPI(
    title=settings.SERVICE_NAME,
    description="AI Chatbot Service with LangGraph",
    version=settings.VERSION
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
app.include_router(chatbot_router, prefix="/api/v1/chatbots", tags=["Chatbots"])
app.include_router(chatbot_agent_router, prefix="/api/v1/chatbot-agents", tags=["Chatbot Agents"])
app.include_router(chatbot_node_router, prefix="/api/v1/chatbot-nodes", tags=["Chatbot Nodes"])
app.include_router(chatbot_tool_router, prefix="/api/v1/chatbot-tools", tags=["Chatbot Tools"])
app.include_router(chatbot_state_router, prefix="/api/v1/chatbot-states", tags=["Chatbot States"])
app.include_router(chat_message_router, prefix="/api/v1/chat-messages", tags=["Chat Messages"])
app.include_router(conversation_router, prefix="/api/v1/conversations", tags=["Conversations"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    from .database import init_db
    init_db()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}
