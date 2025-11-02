"""Asset schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class AssetCreate(BaseModel):
    """Asset creation schema"""
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., regex="^(solar|wind|battery|grid_connection)$")
    capacity_kw: Optional[float] = Field(None, gt=0)
    organization_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class AssetResponse(BaseModel):
    """Asset response schema"""
    id: str
    name: str
    type: str
    capacity_kw: Optional[float] = None
    status: Optional[str] = None
    organization_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AssetList(BaseModel):
    """Asset list response schema"""
    items: list[AssetResponse]
    total: int
    skip: int
    limit: int

