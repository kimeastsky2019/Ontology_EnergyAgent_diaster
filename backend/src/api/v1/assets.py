"""Energy assets endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List, Dict, Any, Optional
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
    # Limit assets to the current user's organization when available
    base_query = select(EnergyAsset)
    count_query = select(func.count(EnergyAsset.id))
    
    # Admin users can see all assets, others see only their organization's assets
    if current_user.role != "admin" and current_user.organization_id:
        base_query = base_query.filter(
            EnergyAsset.organization_id == current_user.organization_id
        )
        count_query = count_query.filter(
            EnergyAsset.organization_id == current_user.organization_id
        )
    elif current_user.role != "admin" and not current_user.organization_id:
        # Users without organization cannot access assets
        return AssetList(items=[], total=0, skip=skip, limit=limit)

    # Get total count efficiently
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Get paginated assets
    result = await db.execute(
        base_query
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
                metadata=asset.asset_metadata,
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
    # Determine organization context
    organization_id = asset_data.organization_id or current_user.organization_id
    
    # Admin can create assets for any organization, others must specify valid organization
    if current_user.role != "admin":
        if organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization must be specified for an asset"
            )
        # Regular users can only create assets for their own organization
        if asset_data.organization_id and asset_data.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create assets for your own organization"
            )
    
    asset = EnergyAsset(
        name=asset_data.name,
        type=asset_data.type,
        capacity_kw=asset_data.capacity_kw,
        organization_id=organization_id,
        status="online",
        metadata=asset_data.asset_metadata
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
                metadata=asset.asset_metadata,
        created_at=asset.created_at
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get energy asset by ID"""
    base_query = select(EnergyAsset).filter(EnergyAsset.id == asset_id)
    
    # Admin users can see all assets, others see only their organization's assets
    if current_user.role != "admin" and current_user.organization_id:
        base_query = base_query.filter(
            EnergyAsset.organization_id == current_user.organization_id
        )
    elif current_user.role != "admin" and not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users without organization cannot access assets"
        )

    result = await db.execute(base_query)
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
        metadata=asset.asset_metadata,
        created_at=asset.created_at
    )


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete energy asset"""
    # Get asset
    base_query = select(EnergyAsset).filter(EnergyAsset.id == asset_id)
    
    # Admin users can delete all assets, others can only delete their organization's assets
    if current_user.role != "admin" and current_user.organization_id:
        base_query = base_query.filter(
            EnergyAsset.organization_id == current_user.organization_id
        )
    elif current_user.role != "admin" and not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users without organization cannot delete assets"
        )

    result = await db.execute(base_query)
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    # Delete asset using delete statement
    delete_stmt = delete(EnergyAsset).where(EnergyAsset.id == asset_id)
    await db.execute(delete_stmt)
    await db.commit()
    
    return {"message": "Asset deleted successfully", "id": str(asset_id)}


@router.post("/generate-from-supply-mcp")
async def generate_assets_from_supply_mcp(
    request_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate assets from supply sector MCP agent with custom parameters"""
    from src.services.mcp_service import mcp_service
    
    # 요청 데이터 파싱
    asset_types = request_data.get("asset_types", ["solar", "wind", "battery"])
    count_per_type = request_data.get("count_per_type", 1)
    capacity_range = request_data.get("capacity_range")
    
    created_assets = []
    organization_id = current_user.organization_id
    
    if not organization_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization must be specified for asset creation"
        )
    
    # 각 자산 타입에 대해 자산 생성
    for asset_type in asset_types:
        for i in range(count_per_type):
            # SupplySectorAgent로 각 자산 타입 분석
            supply_result = await mcp_service.send_request(
                agent_id="supply-sector-agent",
                method="analyze",
                params={
                    "asset_type": asset_type,
                    "prediction_horizon": 24,
                    "data": {
                        "data_points": [
                            {
                                "timestamp": "2025-11-02T00:00:00",
                                "value": 100.0
                            }
                        ]
                    }
                }
            )
            
            # 용량 결정
            if capacity_range:
                capacity = capacity_range.get("default", 1000.0)
            else:
                capacity_map = {
                    "solar": 1000.0,
                    "wind": 2000.0,
                    "battery": 500.0,
                    "grid_connection": 5000.0
                }
                capacity = capacity_map.get(asset_type, 1000.0)
            
            # 자산 생성
            asset = EnergyAsset(
                name=f"{asset_type.capitalize()} Plant {i+1}",
                type=asset_type,
                capacity_kw=capacity,
                organization_id=organization_id,
                status="online",
                metadata={
                    "source": "supply_sector_mcp",
                    "asset_type": asset_type,
                    "supply_analysis": supply_result.result if supply_result.result else {},
                    "index": i
                }
            )
            db.add(asset)
            await db.flush()
            created_assets.append(asset)
    
    await db.commit()
    
    return {
        "message": f"Generated {len(created_assets)} assets from supply sector MCP",
        "assets": [
            {
                "id": str(asset.id),
                "name": asset.name,
                "type": asset.type,
                "capacity_kw": float(asset.capacity_kw) if asset.capacity_kw else None,
                "status": asset.status
            }
            for asset in created_assets
        ],
        "count": len(created_assets)
    }

