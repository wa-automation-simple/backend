"""Pydantic schemas for Chatbot module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


# Agent schemas
class ChatbotAgentCreate(BaseModel):
    """Schema for creating a chatbot agent."""
    name: str = Field(..., description="Agent name")
    role: str = Field(..., description="Agent role (e.g., researcher, writer)")
    description: Optional[str] = Field(None, description="Agent description")
    model_name: str = Field(default="gpt-4o-mini", description="LLM model name")
    temperature: float = Field(default=0.7, ge=0, le=2, description="Temperature for LLM")
    system_prompt: Optional[str] = Field(None, description="System prompt for the agent")
    
    # Variable resolution
    variable_pattern: Optional[str] = Field(None, description="Regex pattern to extract variables from state")
    dynamic_script: Optional[str] = Field(None, description="One-line Python script for dynamic config")
    
    # Output schema
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Expected output schema")
    
    # Agent behavior
    is_active: bool = Field(default=True, description="Whether agent is active")
    priority: int = Field(default=0, description="Agent priority")
    agent_config: Optional[Dict[str, Any]] = Field(None, description="Additional agent config")


# Tool schemas
class ChatbotToolCreate(BaseModel):
    """Schema for creating a chatbot tool."""
    name: str = Field(..., description="Tool name")
    tool_type: str = Field(default="api", description="Tool type: api, code, builtin")
    description: Optional[str] = Field(None, description="Tool description")
    
    # API Tool settings
    method: str = Field(default="POST", description="HTTP method")
    url: Optional[str] = Field(None, description="API URL")
    headers: Optional[Dict[str, Any]] = Field(None, description="HTTP headers")
    body_template: Optional[str] = Field(None, description="Request body template")
    
    # Code tool settings
    is_code: bool = Field(default=False, description="Whether this is a code tool")
    code_content: Optional[str] = Field(None, description="Python code to execute")
    
    # Variable resolution
    variable_pattern: Optional[str] = Field(None, description="Regex pattern to extract variables")
    dynamic_script: Optional[str] = Field(None, description="One-line Python script for dynamic config")
    
    # Schema definitions
    tool_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for tool parameters")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Expected output schema")
    tool_config: Optional[Dict[str, Any]] = Field(None, description="Tool configuration")
    
    # Execution settings
    is_active: bool = Field(default=True, description="Whether tool is active")
    timeout_seconds: int = Field(default=30, description="Tool timeout")
    requires_auth: bool = Field(default=False, description="Whether tool requires auth")


# Node schemas
class ChatbotNodeCreate(BaseModel):
    """Schema for creating a chatbot node."""
    node_name: str = Field(..., description="Node name")
    node_type: str = Field(..., description="Node type: agent, tool, conditional, entry, exit")
    description: Optional[str] = Field(None, description="Node description")
    node_config: Optional[Dict[str, Any]] = Field(None, description="Node configuration")
    edges: Optional[List[Dict[str, Any]]] = Field(None, description="Edge connections")
    is_entry_point: bool = Field(default=False, description="Whether node is entry point")
    is_exit_point: bool = Field(default=False, description="Whether node is exit point")
    is_active: bool = Field(default=True, description="Whether node is active")
    timeout_seconds: int = Field(default=30, description="Node timeout")
    retry_count: int = Field(default=3, description="Retry count")
    
    # References to agent and tool (IDs will be assigned during creation)
    agent_id: Optional[UUID] = Field(None, description="Reference to agent ID")
    tool_id: Optional[UUID] = Field(None, description="Reference to tool ID")
    # For linking by name during creation
    agent_name: Optional[str] = Field(None, description="Name of agent to link")
    tool_name: Optional[str] = Field(None, description="Name of tool to link")


# Chatbot creation schema with nested components
class ChatbotCreate(BaseModel):
    """Schema for creating a new chatbot with agents, tools, and nodes."""
    name: str = Field(..., description="Chatbot name")
    description: Optional[str] = Field(None, description="Chatbot description")
    
    # LangGraph configuration
    graph_config: Optional[Dict[str, Any]] = Field(None, description="Graph structure configuration")
    
    # Settings
    is_active: bool = Field(default=True, description="Whether chatbot is active")
    max_context_length: int = Field(default=10, description="Max context length")
    temperature: float = Field(default=0.7, ge=0, le=2, description="Temperature for LLM")
    max_tokens: int = Field(default=2048, description="Max tokens")
    
    # Components to create together
    agents: List[ChatbotAgentCreate] = Field(default_factory=list, description="Agents to create")
    tools: List[ChatbotToolCreate] = Field(default_factory=list, description="Tools to create")
    nodes: List[ChatbotNodeCreate] = Field(default_factory=list, description="Nodes to create")


class ChatbotUpdate(BaseModel):
    """Schema for updating a chatbot."""
    name: Optional[str] = None
    description: Optional[str] = None
    graph_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    max_context_length: Optional[int] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ChatbotAgentResponse(BaseModel):
    """Schema for agent response."""
    id: UUID
    name: str
    role: str
    description: Optional[str]
    model_name: str
    temperature: float
    system_prompt: Optional[str]
    output_schema: Optional[Dict[str, Any]]
    is_active: bool
    priority: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatbotToolResponse(BaseModel):
    """Schema for tool response."""
    id: UUID
    name: str
    tool_type: str
    method: Optional[str]
    url: Optional[str]
    is_code: bool
    description: Optional[str]
    tool_schema: Optional[Dict[str, Any]]
    output_schema: Optional[Dict[str, Any]]
    is_active: bool
    timeout_seconds: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatbotNodeResponse(BaseModel):
    """Schema for node response."""
    id: UUID
    chatbot_id: UUID
    agent_id: Optional[UUID]
    tool_id: Optional[UUID]
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


class ChatbotResponse(BaseModel):
    """Schema for chatbot response."""
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    graph_config: Optional[Dict[str, Any]]
    is_active: bool
    max_context_length: int
    temperature: float
    max_tokens: int
    static_token: str
    created_at: datetime
    updated_at: datetime
    
    # Nested components
    nodes: List[ChatbotNodeResponse] = []
    
    class Config:
        from_attributes = True
