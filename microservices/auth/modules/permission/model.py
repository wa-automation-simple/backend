"""Permission module - Permission definitions for RBAC."""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from auth.core.database import Base


class Permission(Base):
    """Permission table for RBAC."""
    
    __tablename__ = "permissions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)  # e.g., "user:create", "user:read"
    description = Column(String(255), nullable=True)
    resource = Column(String(50), nullable=False)  # e.g., "user", "post", "comment"
    action = Column(String(50), nullable=False)  # e.g., "create", "read", "update", "delete"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource='{self.resource}', action='{self.action}')>"
