#!/usr/bin/env python3
"""
Script to refactor microservices to Module/Feature Based Architecture.
Each model gets its own module with: model.py, schemas.py, repository.py, service.py, routes.py
"""

import os
import re
from pathlib import Path

BASE_DIR = Path("/workspace/microservices")

# Define the structure for each microservice
# Format: {service_name: [(model_file, model_class_name), ...]}
MICROSERVICES = {
    "chatbot": [
        ("chatbot.py", "Chatbot"),
        ("chatbot_agent.py", "ChatbotAgent"),
        ("chatbot_node.py", "ChatbotNode"),
        ("chatbot_tool.py", "ChatbotTool"),
        ("chatbot_state.py", "ChatbotState"),
        ("chat_message.py", "ChatMessage"),
        ("conversation.py", "Conversation"),
    ],
    "auth": [
        ("user.py", "User"),
    ],
    "ai": [
        ("ai_reply.py", "AIReply"),
    ],
    "blast": [
        ("blast_campaign.py", "BlastCampaign"),
    ],
    "followup": [
        ("follow_up.py", "FollowUp"),
    ],
    "whatsapp": [
        ("whatsapp_account.py", "WhatsAppAccount"),
    ],
}


def extract_model_content(file_path: Path, class_name: str) -> str:
    """Extract model class content from existing file."""
    if not file_path.exists():
        return ""
    
    content = file_path.read_text()
    # Find the class definition
    pattern = rf'class\s+{class_name}\([^)]*\):.*?(?=\nclass\s+\w|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(0)
    return ""


def create_module_files(service_dir: Path, model_file: str, class_name: str):
    """Create module directory with all required files."""
    module_name = model_file.replace('.py', '').lower()
    module_dir = service_dir / "modules" / module_name
    
    # Create module directory
    module_dir.mkdir(parents=True, exist_ok=True)
    
    # Read original model file
    original_model_path = service_dir / "models" / model_file
    original_content = original_model_path.read_text() if original_model_path.exists() else ""
    
    # Create model.py
    model_content = f'''"""{class_name} module - Auto-generated."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from {service_dir.name}.core.database import Base


{extract_model_content(original_model_path, class_name) or f"class {class_name}(Base):\n    __tablename__ = \"{module_name}s\"\n    id = Column(Integer, primary_key=True, index=True)\n"}
'''
    (module_dir / "model.py").write_text(model_content)
    
    # Create schemas.py
    schema_content = f'''"""Pydantic schemas for {class_name} module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class {class_name}Create(BaseModel):
    """Schema for creating a new {module_name}."""
    # Add fields as needed
    pass


class {class_name}Update(BaseModel):
    """Schema for updating a {module_name}."""
    # Add fields as needed
    pass


class {class_name}Response(BaseModel):
    """Schema for {module_name} response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
'''
    (module_dir / "schemas.py").write_text(schema_content)
    
    # Create repository.py
    repo_content = f'''"""Repository for {class_name} database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from {service_dir.name}.modules.{module_name}.model import {class_name}


class {class_name}Repository:
    """Repository for {class_name} model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> {class_name}:
        """Create a new {module_name}."""
        item = {class_name}(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[{class_name}]:
        """Get {module_name} by ID."""
        return self.db.query({class_name}).filter({class_name}.id == item_id).first()
    
    def list_all(self) -> List[{class_name}]:
        """List all items."""
        return self.db.query({class_name}).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[{class_name}]:
        """Update {module_name} fields."""
        item = self.get_by_id(item_id)
        if not item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete(self, item_id: int) -> bool:
        """Delete a {module_name}."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
'''
    (module_dir / "repository.py").write_text(repo_content)
    
    # Create service.py
    service_content = f'''"""Service layer for {class_name} business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from {service_dir.name}.modules.{module_name}.model import {class_name}
from {service_dir.name}.modules.{module_name}.repository import {class_name}Repository
from {service_dir.name}.modules.{module_name}.schemas import {class_name}Create, {class_name}Update


class {class_name}Service:
    """Service layer for {class_name} business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = {class_name}Repository(db)
    
    def create_item(self, item_data: {class_name}Create) -> {class_name}:
        """Create a new {module_name}."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[{class_name}]:
        """Get {module_name} by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[{class_name}]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: {class_name}Update) -> Optional[{class_name}]:
        """Update {module_name}."""
        update_data = {{k: v for k, v in item_data.model_dump().items() if v is not None}}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a {module_name}."""
        return self.repo.delete(item_id)
'''
    (module_dir / "service.py").write_text(service_content)
    
    # Create routes.py
    routes_content = f'''"""API routes for {class_name} module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from {service_dir.name}.core.database import get_db
from {service_dir.name}.modules.{module_name}.schemas import {class_name}Create, {class_name}Update, {class_name}Response
from {service_dir.name}.modules.{module_name}.service import {class_name}Service

router = APIRouter(prefix="/{module_name}s", tags=["{class_name}s"])


@router.post("", response_model={class_name}Response, status_code=status.HTTP_201_CREATED)
def create_item(item_data: {class_name}Create, db: Session = Depends(get_db)):
    """Create a new {module_name}."""
    service = {class_name}Service(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[{class_name}Response])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = {class_name}Service(db)
    return service.list_items()


@router.get("/{{item_id}}", response_model={class_name}Response)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get {module_name} by ID."""
    service = {class_name}Service(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    return item


@router.put("/{{item_id}}", response_model={class_name}Response)
def update_item(item_id: int, item_data: {class_name}Update, db: Session = Depends(get_db)):
    """Update {module_name}."""
    service = {class_name}Service(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    return item


@router.delete("/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a {module_name}."""
    service = {class_name}Service(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="{class_name} not found")
'''
    (module_dir / "routes.py").write_text(routes_content)
    
    # Create __init__.py
    init_content = f'''"""{class_name} module - Auto-generated."""

from {service_dir.name}.modules.{module_name}.model import {class_name}
from {service_dir.name}.modules.{module_name}.schemas import {class_name}Create, {class_name}Update, {class_name}Response
from {service_dir.name}.modules.{module_name}.repository import {class_name}Repository
from {service_dir.name}.modules.{module_name}.service import {class_name}Service
from {service_dir.name}.modules.{module_name}.routes import router

__all__ = [
    "{class_name}",
    "{class_name}Create",
    "{class_name}Update",
    "{class_name}Response",
    "{class_name}Repository",
    "{class_name}Service",
    "router",
]
'''
    (module_dir / "__init__.py").write_text(init_content)
    
    print(f"  Created module: {module_dir}")


def create_modules_init(service_dir: Path):
    """Create main modules/__init__.py file."""
    modules_dir = service_dir / "modules"
    if not modules_dir.exists():
        return
    
    # Get all module directories
    module_dirs = [d for d in modules_dir.iterdir() if d.is_dir() and not d.name.startswith('_')]
    
    init_content = '"""Modules package - Feature based architecture."""\n\n'
    
    for module_dir in module_dirs:
        module_name = module_dir.name
        init_content += f'from {service_dir.name}.modules.{module_name} import *\n'
    
    (modules_dir / "__init__.py").write_text(init_content)
    print(f"  Created modules/__init__.py")


def refactor_service(service_name: str, models: list):
    """Refactor a single microservice to module-based architecture."""
    service_dir = BASE_DIR / service_name
    
    if not service_dir.exists():
        print(f"Service {service_name} not found, skipping...")
        return
    
    print(f"\nRefactoring {service_name}...")
    
    # Create modules directory
    modules_dir = service_dir / "modules"
    modules_dir.mkdir(exist_ok=True)
    
    # Create module for each model
    for model_file, class_name in models:
        create_module_files(service_dir, model_file, class_name)
    
    # Create main modules/__init__.py
    create_modules_init(service_dir)


def main():
    """Main entry point."""
    print("Starting microservices refactoring to Module/Feature Based Architecture...")
    print("=" * 70)
    
    for service_name, models in MICROSERVICES.items():
        refactor_service(service_name, models)
    
    print("\n" + "=" * 70)
    print("Refactoring complete!")
    print("\nNext steps:")
    print("1. Review generated files and adjust field definitions in schemas")
    print("2. Update main.py to include new route routers")
    print("3. Remove old model/service/schema/route files")
    print("4. Test each service thoroughly")


if __name__ == "__main__":
    main()
