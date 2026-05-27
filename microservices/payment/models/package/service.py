"""Token Package Service"""
from typing import List
from sqlalchemy.orm import Session
from payment.models.package.repository import PackageRepository
from payment.models.package.schemas import TokenPackageCreate


class PackageService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PackageRepository(db)

    def get_packages(self) -> List:
        """Get all available token packages"""
        return self.repo.get_packages()

    def get_package(self, package_id: int):
        """Get package by ID"""
        return self.repo.get_package(package_id)

    def create_package(self, data: TokenPackageCreate):
        """Create new token package"""
        return self.repo.create_package(**data.dict())
