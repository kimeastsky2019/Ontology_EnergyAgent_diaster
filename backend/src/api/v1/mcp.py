"""MCP API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional

from src.database import get_db
from src.models.user import User
from src.api.v1.auth import get_current_user
from src.services.mcp_service import mcp_service
from src.schemas.mcp import MCPRequest, MCPResponse

router = APIRouter()


@router.get("/agents")
async def list_agents(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """List all registered MCP agents"""
    agents = mcp_service.registry.list_agents()
    return {
        "agents": agents,
        "count": len(agents)
    }


@router.get("/agents/{agent_id}")
async def get_agent_info(
    agent_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get agent information"""
    agent = mcp_service.registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    return agent


@router.post("/request")
async def send_mcp_request(
    request: MCPRequest,
    current_user: User = Depends(get_current_user)
) -> MCPResponse:
    """Send MCP request to an agent"""
    response = await mcp_service.send_request(
        request.agent_id,
        request.method,
        request.params
    )
    return response


@router.post("/request/{agent_id}/{method}")
async def send_mcp_request_short(
    agent_id: str,
    method: str,
    params: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
) -> MCPResponse:
    """Send MCP request using URL parameters"""
    response = await mcp_service.send_request(
        agent_id,
        method,
        params or {}
    )
    return response

