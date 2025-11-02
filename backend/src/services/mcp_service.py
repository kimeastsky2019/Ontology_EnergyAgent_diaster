"""MCP (Model Context Protocol) Service"""
from typing import Dict, Any, Optional, Callable
import logging
from datetime import datetime
import asyncio
from uuid import uuid4

from src.schemas.mcp import MCPRequest, MCPResponse, MCPMessageType

logger = logging.getLogger(__name__)


class MCPAgentRegistry:
    """Registry for MCP agents"""
    
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Dict[str, Callable]] = {}  # {agent_id: {method: handler}}
    
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register an agent"""
        self.agents[agent_id] = {
            **agent_info,
            "registered_at": datetime.utcnow().isoformat()
        }
        if agent_id not in self.handlers:
            self.handlers[agent_id] = {}
        logger.info(f"Agent registered: {agent_id}")
    
    def register_handler(self, agent_id: str, method: str, handler: Callable):
        """Register a method handler for an agent"""
        if agent_id not in self.handlers:
            self.handlers[agent_id] = {}
        self.handlers[agent_id][method] = handler
        logger.info(f"Handler registered: {agent_id}.{method}")
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information"""
        return self.agents.get(agent_id)
    
    def get_handler(self, agent_id: str, method: str) -> Optional[Callable]:
        """Get handler for agent method"""
        return self.handlers.get(agent_id, {}).get(method)
    
    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all registered agents"""
        return self.agents.copy()


class MCPService:
    """MCP service for agent communication"""
    
    def __init__(self, registry: Optional[MCPAgentRegistry] = None):
        self.registry = registry or MCPAgentRegistry()
        self.pending_requests: Dict[str, asyncio.Future] = {}
    
    async def send_request(
        self,
        agent_id: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0
    ) -> MCPResponse:
        """Send a request to an agent"""
        request = MCPRequest(
            id=str(uuid4()),
            agent_id=agent_id,
            method=method,
            params=params or {}
        )
        
        # Check if agent exists
        agent = self.registry.get_agent(agent_id)
        if not agent:
            return MCPResponse(
                id=request.id,
                agent_id=agent_id,
                error={
                    "code": "AGENT_NOT_FOUND",
                    "message": f"Agent {agent_id} not found"
                }
            )
        
        # Get handler
        handler = self.registry.get_handler(agent_id, method)
        if not handler:
            return MCPResponse(
                id=request.id,
                agent_id=agent_id,
                error={
                    "code": "METHOD_NOT_FOUND",
                    "message": f"Method {method} not found for agent {agent_id}"
                }
            )
        
        # Execute handler
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(request.params or {})
            else:
                result = handler(request.params or {})
            
            return MCPResponse(
                id=request.id,
                agent_id=agent_id,
                result=result
            )
        except Exception as e:
            logger.error(f"Error executing handler {agent_id}.{method}: {e}", exc_info=True)
            return MCPResponse(
                id=request.id,
                agent_id=agent_id,
                error={
                    "code": "EXECUTION_ERROR",
                    "message": str(e)
                }
            )
    
    async def broadcast_notification(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Broadcast notification to all agents"""
        results = {}
        for agent_id in self.registry.agents.keys():
            handler = self.registry.get_handler(agent_id, method)
            if handler:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(params or {})
                    else:
                        result = handler(params or {})
                    results[agent_id] = result
                except Exception as e:
                    logger.error(f"Error broadcasting to {agent_id}: {e}")
                    results[agent_id] = {"error": str(e)}
        return results


# Global MCP service instance
mcp_service = MCPService()

