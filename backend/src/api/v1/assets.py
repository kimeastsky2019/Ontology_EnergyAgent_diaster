"""Energy assets endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from src.database import get_db
from src.models.user import User
from src.models.asset import EnergyAsset
from src.api.v1.auth import get_current_user
from src.schemas.asset import AssetCreate, AssetResponse, AssetList

router = APIRouter()


@router.get("/", response_model=AssetList)
async def get_assets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of energy assets"""
    # Get total count
    count_result = await db.execute(select(EnergyAsset))
    total = len(count_result.scalars().all())
    
    # Get paginated assets
    result = await db.execute(
        select(EnergyAsset)
        .offset(skip)
        .limit(limit)
    )
    assets = result.scalars().all()
    
    return AssetList(
        items=[
            AssetResponse(
                id=str(asset.id),
                name=asset.name,
                type=asset.type,
                capacity_kw=float(asset.capacity_kw) if asset.capacity_kw else None,
                status=asset.status,
                organization_id=str(asset.organization_id) if asset.organization_id else None,
                metadata=asset.metadata,
                created_at=asset.created_at
            )
            for asset in assets
        ],
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/", response_model=AssetResponse)
async def create_asset(
    asset_data: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new energy asset"""
    asset = EnergyAsset(
        name=asset_data.name,
        type=asset_data.type,
        capacity_kw=asset_data.capacity_kw,
        organization_id=asset_data.organization_id or current_user.organization_id,
        status="online",
        metadata=asset_data.metadata
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    
    return AssetResponse(
        id=str(asset.id),
        name=asset.name,
        type=asset.type,
        capacity_kw=float(asset.capacity_kw) if asset.capacity_kw else None,
        status=asset.status,
        organization_id=str(asset.organization_id) if asset.organization_id else None,
        metadata=asset.metadata,
        created_at=asset.created_at
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get energy asset by ID"""
    result = await db.execute(
        select(EnergyAsset).filter(EnergyAsset.id == asset_id)
    )
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    return AssetResponse(
        id=str(asset.id),
        name=asset.name,
        type=asset.type,
        capacity_kw=float(asset.capacity_kw) if asset.capacity_kw else None,
        status=asset.status,
        organization_id=str(asset.organization_id) if asset.organization_id else None,
        metadata=asset.metadata,
        created_at=asset.created_at
    )




