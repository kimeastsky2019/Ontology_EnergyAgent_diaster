"""AI Orchestrator endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from src.database import get_db
from src.models.user import User
from src.api.v1.auth import get_current_user
from src.agents.disaster_analyzer import DisasterAnalyzerAgent
from src.agents.energy_analyzer import EnergyAnalyzerAgent

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze")
async def analyze_situation(
    disaster_data: Dict[str, Any],
    energy_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze disaster and energy situation"""
    try:
        # Initialize agents
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




