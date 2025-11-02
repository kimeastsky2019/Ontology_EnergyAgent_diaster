"""Energy assets endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.database import get_db
from src.models.user import User
from src.models.asset import EnergyAsset
from src.api.v1.auth import get_current_user

router = APIRouter()


@router.get("/")
async def get_assets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of energy assets"""
    assets = db.query(EnergyAsset).offset(skip).limit(limit).all()
    return [
        {
            "id": str(asset.id),
            "name": asset.name,
            "type": asset.type,
            "capacity_kw": float(asset.capacity_kw) if asset.capacity_kw else None,
            "status": asset.status,
            "organization_id": str(asset.organization_id) if asset.organization_id else None,
            "created_at": asset.created_at.isoformat() if asset.created_at else None
        }
        for asset in assets
    ]


@router.post("/")
async def create_asset(
    name: str,
    type: str,
    capacity_kw: float = None,
    organization_id: UUID = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new energy asset"""
    asset = EnergyAsset(
        name=name,
        type=type,
        capacity_kw=capacity_kw,
        organization_id=organization_id or current_user.organization_id,
        status="online"
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    return {
        "id": str(asset.id),
        "name": asset.name,
        "type": asset.type,
        "capacity_kw": float(asset.capacity_kw) if asset.capacity_kw else None,
        "status": asset.status,
        "created_at": asset.created_at.isoformat() if asset.created_at else None
    }


@router.get("/{asset_id}")
async def get_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get energy asset by ID"""
    asset = db.query(EnergyAsset).filter(EnergyAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    return {
        "id": str(asset.id),
        "name": asset.name,
        "type": asset.type,
        "capacity_kw": float(asset.capacity_kw) if asset.capacity_kw else None,
        "status": asset.status,
        "organization_id": str(asset.organization_id) if asset.organization_id else None,
        "metadata": asset.metadata,
        "created_at": asset.created_at.isoformat() if asset.created_at else None
    }




