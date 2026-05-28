"""Pydantic schemas for ChatbotNode module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class ChatbotNodeCreate(BaseModel):
    """Schema for creating a new chatbot_node."""
    chatbot_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    tool_id: Optional[UUID] = None
    node_name: str
    node_type: str  # "agent", "tool", "conditional", "entry", "exit"
    description: Optional[str] = None
    node_config: Optional[Dict[str, Any]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    is_entry_point: bool = False
    is_exit_point: bool = False
    is_active: bool = True
    timeout_seconds: int = 30
    retry_count: int = 3
    # For linking by name during creation
    agent_name: Optional[str] = None
    tool_name: Optional[str] = None


class ChatbotNodeUpdate(BaseModel):
    """Schema for updating a chatbot_node."""
    node_name: Optional[str] = None
    node_type: Optional[str] = None
    description: Optional[str] = None
    node_config: Optional[Dict[str, Any]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    is_entry_point: Optional[bool] = None
    is_exit_point: Optional[bool] = None
    is_active: Optional[bool] = None
    timeout_seconds: Optional[int] = None
    retry_count: Optional[int] = None


class ChatbotNodeResponse(BaseModel):
    """Schema for chatbot_node response."""
    id: UUID
    chatbot_id: UUID
    agent_id: Optional[UUID] = None
    tool_id: Optional[UUID] = None
    node_name: str
    node_type: str
    description: Optional[str] = None
    node_config: Optional[Dict[str, Any]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    is_entry_point: bool
    is_exit_point: bool
    is_active: bool
    timeout_seconds: int
    retry_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
