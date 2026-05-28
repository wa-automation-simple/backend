"""Pydantic schemas for ChatbotAgent module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ChatbotAgentCreate(BaseModel):
    """Schema for creating a new chatbot_agent."""
    name: str
    role: str
    description: Optional[str] = None
    
    # LLM settings
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    
    # Variable resolution
    variable_pattern: Optional[str] = None
    dynamic_script: Optional[str] = None
    
    # Output schema
    output_schema: Optional[Dict[str, Any]] = None
    
    # Agent behavior
    is_active: bool = True
    priority: int = 0
    agent_config: Optional[Dict[str, Any]] = None


class ChatbotAgentUpdate(BaseModel):
    """Schema for updating a chatbot_agent."""
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    system_prompt: Optional[str] = None
    variable_pattern: Optional[str] = None
    dynamic_script: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    agent_config: Optional[Dict[str, Any]] = None


class ChatbotAgentResponse(BaseModel):
    """Schema for chatbot_agent response."""
    id: int
    name: str
    role: str
    description: Optional[str] = None
    model_name: str
    temperature: float
    system_prompt: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    is_active: bool
    priority: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
