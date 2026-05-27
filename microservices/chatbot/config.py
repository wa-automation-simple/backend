"""
AI Chatbot Configuration - Environment variables
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class ChatbotSettings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/chatbot_db"
    
    # Service Config
    SERVICE_NAME: str = "chatbot-service"
    SERVICE_PORT: int = 8009
    
    # LangGraph & LLM
    LLM_PROVIDER: str = "openai"  # openai, anthropic, ollama
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2048
    
    # Static Token for /chat endpoint (different from JWT)
    CHAT_STATIC_TOKEN_PREFIX: str = "chat_"
    DEFAULT_CHAT_TOKEN: str = "chat_sk_test_1234567890abcdef"  # Replace in production
    
    # Concurrency
    MAX_CONCURRENT_CHATS: int = 100
    STATE_LOCK_TIMEOUT: int = 30  # seconds
    
    # RBAC Limits
    TRIAL_MAX_CHATBOTS: int = 1
    USER_MAX_CHATBOTS: int = 3
    MANAGER_MAX_CHATBOTS: int = 10
    ADMIN_MAX_CHATBOTS: int = 50
    SUPER_ADMIN_MAX_CHATBOTS: int = -1  # Unlimited
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_chatbot_settings() -> ChatbotSettings:
    return ChatbotSettings()
