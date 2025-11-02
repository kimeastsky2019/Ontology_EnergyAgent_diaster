"""Energy asset model"""
from sqlalchemy import Column, String, Numeric, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.database import Base


class EnergyAsset(Base):
    """Energy asset model"""
    __tablename__ = "energy_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # solar, wind, battery, grid_connection
    capacity_kw = Column(Numeric(10, 2))
    # location = Column(Geography(Point))  # TODO: Enable PostGIS
    status = Column(String(50))  # online, offline, maintenance, emergency
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="assets")
    devices = relationship("IoTDevice", back_populates="asset")


class IoTDevice(Base):
    """IoT device model"""
    __tablename__ = "iot_devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("energy_assets.id"))
    device_id = Column(String(255), unique=True, nullable=False)
    device_type = Column(String(50))  # meter, sensor, controller
    protocol = Column(String(50))  # mqtt, http, coap
    firmware_version = Column(String(50))
    last_seen = Column(DateTime(timezone=True))
    status = Column(String(50))
    config = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    asset = relationship("EnergyAsset", back_populates="devices")




