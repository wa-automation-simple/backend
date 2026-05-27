"""
Django-like serializers for request validation using Pydantic
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


# ============== Chatbot Serializers ==============

class ChatbotCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    system_prompt: Optional[str] = Field(None, max_length=10000)
    max_context_length: int = Field(default=10, ge=1, le=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=100, le=8192)


class ChatbotUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    system_prompt: Optional[str] = Field(None, max_length=10000)
    is_active: Optional[bool] = None
    max_context_length: Optional[int] = Field(None, ge=1, le=100)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=8192)


class ChatbotResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    system_prompt: Optional[str]
    is_active: bool
    max_context_length: int
    temperature: float
    max_tokens: int
    static_token: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Agent Serializers ==============

class ChatbotAgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    model_name: str = Field(default="gpt-4o-mini", max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    system_prompt: Optional[str] = Field(None, max_length=10000)
    priority: int = Field(default=0, ge=-100, le=100)
    agent_config: Optional[Dict[str, Any]] = None


class ChatbotAgentResponse(BaseModel):
    id: int
    chatbot_id: int
    name: str
    role: str
    description: Optional[str]
    model_name: str
    temperature: float
    system_prompt: Optional[str]
    is_active: bool
    priority: int
    agent_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Node Serializers ==============

class ChatbotNodeCreate(BaseModel):
    node_name: str = Field(..., min_length=1, max_length=255)
    node_type: str = Field(..., pattern="^(agent|tool|conditional|entry|exit)$")
    description: Optional[str] = Field(None, max_length=2000)
    node_config: Optional[Dict[str, Any]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    is_entry_point: bool = False
    is_exit_point: bool = False
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    retry_count: int = Field(default=3, ge=0, le=10)


class ChatbotNodeResponse(BaseModel):
    id: int
    chatbot_id: int
    node_name: str
    node_type: str
    description: Optional[str]
    node_config: Optional[Dict[str, Any]]
    edges: Optional[List[Dict[str, Any]]]
    is_entry_point: bool
    is_exit_point: bool
    is_active: bool
    timeout_seconds: int
    retry_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Tool Serializers ==============

class ChatbotToolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    tool_type: str = Field(..., pattern="^(builtin|custom|api)$")
    description: Optional[str] = Field(None, max_length=2000)
    tool_schema: Optional[Dict[str, Any]] = None
    tool_config: Optional[Dict[str, Any]] = None
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    requires_auth: bool = False


class ChatbotToolResponse(BaseModel):
    id: int
    chatbot_id: int
    name: str
    tool_type: str
    description: Optional[str]
    tool_schema: Optional[Dict[str, Any]]
    tool_config: Optional[Dict[str, Any]]
    is_active: bool
    timeout_seconds: int
    requires_auth: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Chat Serializers ==============

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = Field(None, max_length=255)
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    message_type: str
    agent_name: Optional[str]
    node_name: Optional[str]
    total_tokens: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    conversation_id: int
    message: ChatMessageResponse
    tokens_used: int
    response_time_ms: float


# ============== Conversation Serializers ==============

class ConversationResponse(BaseModel):
    id: int
    chatbot_id: int
    user_id: int
    title: Optional[str]
    session_id: Optional[str]
    is_active: bool
    is_archived: bool
    message_count: int
    total_tokens_used: int
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Static Token Authentication ==============

class StaticTokenAuth(BaseModel):
    token: str = Field(..., min_length=10)
    
    @validator('token')
    def validate_token_format(cls, v):
        if not v.startswith("chat_"):
            raise ValueError("Invalid token format. Must start with 'chat_'")
        return v
