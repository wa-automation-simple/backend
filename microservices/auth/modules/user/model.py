"""User module - Auto-generated."""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

from core.database import Base


# Association table for User-Role many-to-many relationship
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", PG_UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True  # <--- WAJIB TAMBAHKAN BARIS INI
)


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class User(Base):
    """User table for authentication and authorization."""
    
    __tablename__ = "users"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    username = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(50), unique=True, index=True, nullable=False)

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Made nullable for Google OAuth users
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Google OAuth fields
    google_account_connected = Column(Boolean, default=False, nullable=False)
    google_sub = Column(String(255), unique=True, index=True, nullable=True)  # Google subject ID
    google_email = Column(String(255), nullable=True)
    google_name = Column(String(255), nullable=True)
    google_picture = Column(Text, nullable=True)
    
    # Relationships
    token_transactions = relationship("TokenTransaction", back_populates="user", foreign_keys="TokenTransaction.user_id")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', google_connected={self.google_account_connected})>"


class TokenTransaction(Base):
    """Token transaction table for tracking token usage."""
    
    __tablename__ = "token_transactions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_type = Column(String(50), nullable=False)  # e.g., "access", "refresh"
    token_hash = Column(String(255), nullable=False, index=True)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="token_transactions")
    
    def __repr__(self):
        return f"<TokenTransaction(id={self.id}, user_id={self.user_id}, type='{self.token_type}')>"

