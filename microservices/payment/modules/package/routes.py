"""Token Package Routes"""
from fastapi import APIRouter, Depends
from typing import List
from payment.modules.package.service import PackageService
from payment.modules.package.schemas import TokenPackageResponse, TokenPackageCreate

router = APIRouter(prefix="/packages", tags=["packages"])


def get_package_service():
    """Dependency to get package service"""
    from sqlalchemy.orm import Session
    from payment.core.database import SessionLocal
    db = SessionLocal()
    try:
        return PackageService(db)
    finally:
        db.close()


@router.get("", response_model=List[TokenPackageResponse])
def get_packages(service: PackageService = Depends(get_package_service)):
    """Get all available token packages"""
    return service.get_packages()
