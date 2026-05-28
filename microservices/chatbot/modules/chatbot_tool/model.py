"""ChatbotTool module - Auto-generated."""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from chatbot.core.database import Base


class HttpMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ChatbotTool(Base):
    __tablename__ = "chatbot_tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chatbots.id"), nullable=False)
    
    # Tool configuration
    name = Column(String(255), nullable=False)
    tool_type = Column(String(100), nullable=False)  # "api", "code", "builtin"
    
    # API Tool settings
    method = Column(SQLEnum(HttpMethod), default="POST")
    url = Column(Text, nullable=True)
    headers = Column(JSON, nullable=True)
    body_template = Column(Text, nullable=True)
    
    # Code tool settings
    is_code = Column(Boolean, default=False)
    code_content = Column(Text, nullable=True)  # Python code to execute
    
    # Variable resolution
    variable_pattern = Column(String(500), nullable=True)  # Regex pattern to extract variables
    dynamic_script = Column(Text, nullable=True)  # One-line Python script for dynamic config
    input_variables = Column(JSON, nullable=True)  # List of variable names to extract from state for this tool
    output_variables = Column(JSON, nullable=True)  # List of variable names where tool output should be stored
    
    # Tool definition
    description = Column(Text, nullable=True)
    tool_schema = Column(JSON, nullable=True)  # JSON Schema for tool parameters
    output_schema = Column(JSON, nullable=True)  # Expected output schema
    tool_config = Column(JSON, nullable=True)  # Additional config
    
    # Execution settings
    is_active = Column(Boolean, default=True)
    timeout_seconds = Column(Integer, default=30)
    requires_auth = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chatbot = relationship("Chatbot", back_populates="tools")
    nodes = relationship("ChatbotNode", back_populates="tool", foreign_keys="ChatbotNode.tool_id")

