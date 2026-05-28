"""Pydantic schemas for ChatbotTool module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ChatbotToolCreate(BaseModel):
    """Schema for creating a new chatbot_tool."""
    chatbot_id: int
    name: str
    tool_type: str = "api"  # "api", "code", "builtin"
    
    # API Tool settings
    method: Optional[HttpMethod] = "POST"
    url: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None
    body_template: Optional[str] = None
    
    # Code tool settings
    is_code: bool = False
    code_content: Optional[str] = None
    
    # Variable resolution
    variable_pattern: Optional[str] = None
    dynamic_script: Optional[str] = None
    
    # Tool definition
    description: Optional[str] = None
    tool_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    tool_config: Optional[Dict[str, Any]] = None
    
    # Execution settings
    is_active: bool = True
    timeout_seconds: int = 30
    requires_auth: bool = False


class ChatbotToolUpdate(BaseModel):
    """Schema for updating a chatbot_tool."""
    name: Optional[str] = None
    tool_type: Optional[str] = None
    method: Optional[HttpMethod] = None
    url: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None
    body_template: Optional[str] = None
    is_code: Optional[bool] = None
    code_content: Optional[str] = None
    variable_pattern: Optional[str] = None
    dynamic_script: Optional[str] = None
    description: Optional[str] = None
    tool_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    tool_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    timeout_seconds: Optional[int] = None
    requires_auth: Optional[bool] = None


class ChatbotToolResponse(BaseModel):
    """Schema for chatbot_tool response."""
    id: int
    chatbot_id: int
    name: str
    tool_type: str
    method: Optional[str] = None
    url: Optional[str] = None
    is_code: bool
    description: Optional[str] = None
    tool_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    is_active: bool
    timeout_seconds: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
