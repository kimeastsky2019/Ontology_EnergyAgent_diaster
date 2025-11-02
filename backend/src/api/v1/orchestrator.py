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
from src.agents.data_quality_agent import DataQualityAgent
from src.agents.demand_sector_agent import DemandSectorAgent
from src.agents.supply_sector_agent import SupplySectorAgent
from src.agents.weather_agent import WeatherAgent

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize agents
data_quality_agent = DataQualityAgent()
demand_sector_agent = DemandSectorAgent()
supply_sector_agent = SupplySectorAgent()
weather_agent = WeatherAgent()


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
    """Analyze data using a specific agent"""
    agents = {
        "data-quality-agent": data_quality_agent,
        "demand-sector-agent": demand_sector_agent,
        "supply-sector-agent": supply_sector_agent,
        "weather-agent": weather_agent
    }
    
    agent = agents.get(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    
    try:
        result = await agent.analyze(data)
        return result
    except Exception as e:
        logger.error(f"Agent analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )




