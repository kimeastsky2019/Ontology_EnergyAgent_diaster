"""Energy analyzer agent"""
from src.agents.base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class EnergyAnalyzerAgent(BaseAgent):
    """Energy supply-demand analysis agent"""
    
    def __init__(self):
        super().__init__("EnergyAnalyzer")
    
    async def analyze(self, energy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze energy situation"""
        assets = energy_data.get("assets", [])
        current_production = energy_data.get("total_production", 0)
        current_demand = energy_data.get("total_demand", 0)
        
        # Calculate energy balance
        balance = current_production - current_demand
        balance_ratio = balance / current_demand if current_demand > 0 else 0
        
        # Identify surplus/deficit regions
        surplus_assets = [a for a in assets if a.get("net_energy", 0) > 0]
        deficit_assets = [a for a in assets if a.get("net_energy", 0) < 0]
        
        result = {
            "agent": self.agent_name,
            "balance": balance,
            "balance_ratio": balance_ratio,
            "status": "surplus" if balance > 0 else "deficit",
            "surplus_assets": [a["id"] for a in surplus_assets],
            "deficit_assets": [a["id"] for a in deficit_assets],
            "redistribution_needed": abs(balance) > current_demand * 0.1 if current_demand > 0 else False
        }
        
        self.add_to_memory(result)
        logger.info(f"Energy analysis completed: Balance: {balance:.2f} kW")
        
        return result




