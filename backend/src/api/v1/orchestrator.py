"""AI Orchestrator endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging

from src.database import get_db
from src.models.user import User
from src.api.v1.auth import get_current_user
from src.agents.disaster_analyzer import DisasterAnalyzerAgent
from src.agents.energy_analyzer import EnergyAnalyzerAgent
from src.services.mcp_service import mcp_service

logger = logging.getLogger(__name__)
router = APIRouter()


def get_agent_by_id(agent_id: str):
    """Get agent instance from MCP registry"""
    from src.agents.data_quality_agent import DataQualityAgent
    from src.agents.demand_sector_agent import DemandSectorAgent
    from src.agents.supply_sector_agent import SupplySectorAgent
    from src.agents.weather_agent import WeatherAgent
    
    # Agent instances are created on module import and auto-registered
    # We can access them via MCP service or create new instances if needed
    agent_map = {
        "data-quality-agent": DataQualityAgent,
        "demand-sector-agent": DemandSectorAgent,
        "supply-sector-agent": SupplySectorAgent,
        "weather-agent": WeatherAgent
    }
    
    agent_class = agent_map.get(agent_id)
    if agent_class:
        # Create instance if needed (agents auto-register on init)
        return agent_class()
    return None


@router.post("/analyze")
async def analyze_situation(
    disaster_data: Dict[str, Any],
    energy_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze disaster and energy situation"""
    try:
        # Initialize legacy agents
        disaster_agent = DisasterAnalyzerAgent()
        energy_agent = EnergyAnalyzerAgent()
        
        # Run analysis
        disaster_analysis = await disaster_agent.analyze(disaster_data)
        energy_analysis = await energy_agent.analyze(energy_data)
        
        return {
            "disaster_analysis": disaster_analysis,
            "energy_analysis": energy_analysis,
            "recommendations": {
                "priority": disaster_analysis.get("priority"),
                "redistribution_needed": energy_analysis.get("redistribution_needed"),
                "status": "analysis_completed"
            }
        }
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/agents/{agent_id}/analyze")
async def analyze_with_agent(
    agent_id: str,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze data using a specific agent via MCP"""
    try:
        # Use MCP service to send request to agent
        response = await mcp_service.send_request(
            agent_id,
            "analyze",
            data
        )
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error.get("message", "Analysis failed")
            )
        
        return response.result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )




