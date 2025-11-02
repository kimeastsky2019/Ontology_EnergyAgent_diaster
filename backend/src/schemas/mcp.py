"""MCP (Model Context Protocol) schemas"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4


class MCPMessageType(str, Enum):
    """MCP message types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MCPRequest(BaseModel):
    """MCP request schema"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    method: str
    params: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "agent_id": "data-quality-agent",
                "method": "validate_data",
                "params": {
                    "data_source": "demand_sector",
                    "data": {...}
                }
            }
        }


class MCPResponse(BaseModel):
    """MCP response schema"""
    id: str
    agent_id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "agent_id": "data-quality-agent",
                "result": {
                    "quality_score": 0.95,
                    "issues": []
                }
            }
        }


class MCPMessage(BaseModel):
    """MCP message wrapper"""
    type: MCPMessageType
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "request",
                "payload": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "agent_id": "data-quality-agent",
                    "method": "validate_data",
                    "params": {...}
                }
            }
        }

