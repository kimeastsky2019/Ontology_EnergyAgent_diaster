"""Disaster analyzer agent"""
from src.agents.base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DisasterAnalyzerAgent(BaseAgent):
    """Disaster situation analysis agent"""
    
    def __init__(self):
        super().__init__("DisasterAnalyzer")
        self.severity_threshold = {
            "earthquake": {"minor": 3.0, "moderate": 5.0, "severe": 7.0},
            "typhoon": {"minor": 60, "moderate": 100, "severe": 150},  # km/h
        }
    
    async def analyze(self, disaster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze disaster data"""
        disaster_type = disaster_data.get("type")
        magnitude = disaster_data.get("magnitude", 0)
        location = disaster_data.get("location")
        
        # Evaluate severity
        severity = self._evaluate_severity(disaster_type, magnitude)
        
        # Estimate affected radius
        affected_radius_km = self._estimate_radius(disaster_type, magnitude)
        
        # Calculate priority
        priority = self._calculate_priority(severity, location)
        
        result = {
            "agent": self.agent_name,
            "disaster_type": disaster_type,
            "severity": severity,
            "magnitude": magnitude,
            "location": location,
            "affected_radius_km": affected_radius_km,
            "priority": priority
        }
        
        self.add_to_memory(result)
        logger.info(f"Disaster analysis completed: {disaster_type} - Severity: {severity}")
        
        return result
    
    def _evaluate_severity(self, disaster_type: str, magnitude: float) -> str:
        """Evaluate disaster severity"""
        thresholds = self.severity_threshold.get(disaster_type, {})
        
        if not thresholds:
            return "moderate"
        
        if magnitude < thresholds.get("minor", 0):
            return "minor"
        elif magnitude < thresholds.get("moderate", 0):
            return "moderate"
        elif magnitude < thresholds.get("severe", 0):
            return "severe"
        else:
            return "critical"
    
    def _estimate_radius(self, disaster_type: str, magnitude: float) -> float:
        """Estimate affected radius"""
        if disaster_type == "earthquake":
            # Simple formula: radius = magnitude^2 * 5
            return min(magnitude ** 2 * 5, 500)  # Max 500km
        elif disaster_type == "typhoon":
            return min(magnitude * 2, 300)
        return 50  # Default
    
    def _calculate_priority(self, severity: str, location: Dict = None) -> int:
        """Calculate priority (1-10, 10 is highest)"""
        severity_score = {
            "minor": 3,
            "moderate": 6,
            "severe": 8,
            "critical": 10
        }
        return severity_score.get(severity, 5)





