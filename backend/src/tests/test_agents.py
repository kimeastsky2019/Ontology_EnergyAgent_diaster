"""Tests for Agents"""
import pytest
from src.agents.data_quality_agent import DataQualityAgent
from src.agents.demand_sector_agent import DemandSectorAgent
from src.agents.supply_sector_agent import SupplySectorAgent
from src.agents.weather_agent import WeatherAgent


@pytest.mark.asyncio
async def test_data_quality_agent_initialization():
    """Test DataQualityAgent initialization"""
    agent = DataQualityAgent()
    assert agent.agent_id == "data-quality-agent"
    assert agent.agent_name == "Data Quality Agent"
    assert "validate_data" in agent.get_capabilities()


@pytest.mark.asyncio
async def test_data_quality_agent_validate_data():
    """Test data validation"""
    agent = DataQualityAgent()
    
    # Valid data
    result = await agent.validate_data({
        "data": {
            "timestamp": "2025-01-01T00:00:00Z",
            "value": 100.5
        },
        "data_source": "test"
    })
    
    assert result["is_valid"] is True
    assert "data_source" in result


@pytest.mark.asyncio
async def test_data_quality_agent_assess_quality():
    """Test data quality assessment"""
    agent = DataQualityAgent()
    
    data_points = [
        {"timestamp": "2025-01-01T00:00:00Z", "value": 100},
        {"timestamp": "2025-01-01T01:00:00Z", "value": 105},
        {"timestamp": "2025-01-01T02:00:00Z", "value": 98}
    ]
    
    result = await agent.assess_data_quality({"data_points": data_points})
    
    assert "quality_score" in result
    assert "status" in result
    assert "metrics" in result
    assert 0 <= result["quality_score"] <= 100


@pytest.mark.asyncio
async def test_demand_sector_agent_initialization():
    """Test DemandSectorAgent initialization"""
    agent = DemandSectorAgent()
    assert agent.agent_id == "demand-sector-agent"
    assert "preprocess_data" in agent.get_capabilities()


@pytest.mark.asyncio
async def test_demand_sector_agent_preprocess():
    """Test data preprocessing"""
    agent = DemandSectorAgent()
    
    data_points = [
        {"timestamp": "2025-01-01T00:00:00Z", "value": 100},
        {"timestamp": "2025-01-01T01:00:00Z", "value": 105}
    ]
    
    result = await agent.preprocess_data({"data": {"data_points": data_points}})
    
    assert "preprocessed_data" in result
    assert "steps" in result
    assert len(result["preprocessed_data"]) > 0


@pytest.mark.asyncio
async def test_supply_sector_agent_initialization():
    """Test SupplySectorAgent initialization"""
    agent = SupplySectorAgent()
    assert agent.agent_id == "supply-sector-agent"
    assert "predict_solar_generation" in agent.get_capabilities()


@pytest.mark.asyncio
async def test_supply_sector_agent_predict_solar():
    """Test solar generation prediction"""
    agent = SupplySectorAgent()
    
    data_points = [
        {"timestamp": "2025-01-01T00:00:00Z", "value": 500},
        {"timestamp": "2025-01-01T01:00:00Z", "value": 550}
    ]
    
    result = await agent.predict_solar_generation({
        "data_points": data_points,
        "engine": "prophet",
        "horizon": 24
    })
    
    assert "predictions" in result
    assert len(result["predictions"]) > 0
    assert "asset_type" in result
    assert result["asset_type"] == "solar"


@pytest.mark.asyncio
async def test_weather_agent_initialization():
    """Test WeatherAgent initialization"""
    agent = WeatherAgent()
    assert agent.agent_id == "weather-agent"
    assert "fetch_weather_data" in agent.get_capabilities()


@pytest.mark.asyncio
async def test_weather_agent_mock_data():
    """Test weather agent with mock data"""
    agent = WeatherAgent()
    
    # Mock weather data
    result = await agent.fetch_weather_data({
        "lat": 35.6762,
        "lon": 139.6503,
        "days": 7
    })
    
    # Should return data (even if mock)
    assert result is not None
    assert "list" in result or "error" in result

