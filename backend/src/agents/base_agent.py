"""Base agent class"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

from src.services.mcp_service import mcp_service

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base AI agent class with MCP support"""
    
    def __init__(self, agent_name: str, agent_id: Optional[str] = None):
        self.agent_name = agent_name
        self.agent_id = agent_id or agent_name.lower().replace(" ", "-")
        self.memory: List[Dict[str, Any]] = []
        self.mcp_service = mcp_service
        self._register_mcp_handlers()
        logger.info(f"Initialized agent: {agent_name} (ID: {self.agent_id})")
    
    def _register_mcp_handlers(self):
        """Register MCP handlers for this agent"""
        # Register agent in MCP registry
        self.mcp_service.registry.register_agent(
            self.agent_id,
            {
                "name": self.agent_name,
                "type": self.__class__.__name__,
                "capabilities": self.get_capabilities()
            }
        )
        
        # Register standard methods
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "analyze",
            self._handle_analyze
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "get_status",
            self._handle_get_status
        )
        
        # Register custom handlers
        self.register_custom_handlers()
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities (override in subclasses)"""
        return ["analyze", "get_status"]
    
    def register_custom_handlers(self):
        """Register custom handlers (override in subclasses)"""
        pass
    
    async def _handle_analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analyze request via MCP"""
        return await self.analyze(params)
    
    async def _handle_get_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get status request"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": "active",
            "memory_items": len(self.memory),
            "capabilities": self.get_capabilities()
        }
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data (to be implemented by subclasses)"""
        pass
    
    def add_to_memory(self, item: Dict[str, Any]):
        """Add item to memory"""
        self.memory.append(item)
        # Limit memory size (keep last 50 items)
        if len(self.memory) > 50:
            self.memory = self.memory[-50:]
    
    def get_context(self) -> str:
        """Get context from memory"""
        return "\n".join([str(m) for m in self.memory[-10:]])
    
    async def send_mcp_request(
        self,
        target_agent_id: str,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send MCP request to another agent"""
        response = await self.mcp_service.send_request(
            target_agent_id,
            method,
            params
        )
        return response.result if response.result else response.error




