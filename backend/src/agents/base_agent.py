"""Base agent class"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base AI agent class"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.memory: List[Dict[str, Any]] = []
        logger.info(f"Initialized agent: {agent_name}")
    
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




