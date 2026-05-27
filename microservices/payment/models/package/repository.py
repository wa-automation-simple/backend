"""Token Package Repository"""
from sqlalchemy.orm import Session
from typing import List, Optional
from payment.models.package.package import TokenPackage


class PackageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_packages(self, active_only: bool = True) -> List[TokenPackage]:
        """Get all token packages"""
        query = self.db.query(TokenPackage)
        if active_only:
            query = query.filter(TokenPackage.is_active == True)
        return query.all()

    def get_package(self, package_id: int) -> Optional[TokenPackage]:
        """Get package by ID"""
        return self.db.query(TokenPackage).filter(TokenPackage.id == package_id).first()

    def create_package(self, **kwargs) -> TokenPackage:
        """Create new token package"""
        package = TokenPackage(**kwargs)
        package.total_tokens = package.tokens_included + package.bonus_tokens
        self.db.add(package)
        self.db.commit()
        self.db.refresh(package)
        return package
