"""Weather Analysis Agent"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import httpx
import asyncio

from src.agents.base_agent import BaseAgent
from src.config import settings

logger = logging.getLogger(__name__)


class WeatherAgent(BaseAgent):
    """Agent for weather data collection, processing, and disaster prediction"""
    
    def __init__(self):
        super().__init__(
            agent_name="Weather Analysis Agent",
            agent_id="weather-agent"
        )
        self.weather_api_key = settings.WEATHER_API_KEY
        self.weather_cache: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hour
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [
            "analyze",
            "get_status",
            "fetch_weather_data",
            "process_weather_data",
            "predict_weather",
            "predict_disaster",
            "get_historical_weather"
        ]
    
    def register_custom_handlers(self):
        """Register custom MCP handlers"""
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "fetch_weather_data",
            self.fetch_weather_data
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "process_weather_data",
            self.process_weather_data
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "predict_weather",
            self.predict_weather
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "predict_disaster",
            self.predict_disaster
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "get_historical_weather",
            self.get_historical_weather
        )
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze weather data and predict disasters"""
        location = data.get("location", {})
        lat = location.get("lat")
        lon = location.get("lon")
        
        if not lat or not lon:
            return {
                "error": "location_required",
                "message": "Latitude and longitude are required"
            }
        
        # Fetch weather data
        weather_data = await self.fetch_weather_data({
            "lat": lat,
            "lon": lon,
            "days": data.get("forecast_days", 7)
        })
        
        # Process weather data
        processed = await self.process_weather_data({"weather_data": weather_data})
        
        # Predict weather
        weather_prediction = await self.predict_weather({
            "weather_data": weather_data,
            "horizon_hours": data.get("horizon_hours", 24)
        })
        
        # Predict disasters
        disaster_prediction = await self.predict_disaster({
            "weather_data": weather_data,
            "location": location
        })
        
        # Send data to data quality agent for validation
        quality_result = await self.send_mcp_request(
            "data-quality-agent",
            "validate_data",
            {
                "data": {
                    "source": "weather_api",
                    "location": location
                },
                "data_source": "weather"
            }
        )
        
        result = {
            "agent": self.agent_name,
            "location": location,
            "weather_data": weather_data,
            "processed_weather": processed,
            "weather_prediction": weather_prediction,
            "disaster_prediction": disaster_prediction,
            "quality_assessment": quality_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.add_to_memory(result)
        return result
    
    async def fetch_weather_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch weather data from API"""
        lat = params.get("lat")
        lon = params.get("lon")
        days = params.get("days", 7)
        
        if not lat or not lon:
            return {"error": "location_required"}
        
        # Check cache
        cache_key = f"{lat}_{lon}_{days}"
        if cache_key in self.weather_cache:
            cached_time = self.weather_cache[cache_key].get("cached_at")
            if cached_time:
                cached_dt = datetime.fromisoformat(cached_time)
                if (datetime.utcnow() - cached_dt).total_seconds() < self.cache_ttl:
                    logger.info(f"Returning cached weather data for {cache_key}")
                    return self.weather_cache[cache_key].get("data", {})
        
        # Fetch from API (using mock data if API key not available)
        if not self.weather_api_key:
            logger.warning("Weather API key not set, returning mock data")
            return self._generate_mock_weather_data(lat, lon, days)
        
        try:
            # Example: OpenWeatherMap API (adjust URL based on actual API)
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = "https://api.openweathermap.org/data/2.5/forecast"
                response = await client.get(
                    url,
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.weather_api_key,
                        "units": "metric",
                        "cnt": days * 8  # 3-hour intervals
                    }
                )
                
                if response.status_code == 200:
                    weather_data = response.json()
                    # Cache the result
                    self.weather_cache[cache_key] = {
                        "data": weather_data,
                        "cached_at": datetime.utcnow().isoformat()
                    }
                    return weather_data
                else:
                    logger.error(f"Weather API error: {response.status_code}")
                    return self._generate_mock_weather_data(lat, lon, days)
        
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._generate_mock_weather_data(lat, lon, days)
    
    async def process_weather_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize weather data"""
        weather_data = params.get("weather_data", {})
        
        if not weather_data or "list" not in weather_data:
            return {"error": "invalid_weather_data"}
        
        processed = {
            "temperature": [],
            "humidity": [],
            "wind_speed": [],
            "pressure": [],
            "precipitation": [],
            "cloud_cover": [],
            "timestamps": []
        }
        
        for item in weather_data.get("list", [])[:24]:  # Process first 24 items
            main = item.get("main", {})
            weather = item.get("weather", [{}])[0]
            wind = item.get("wind", {})
            clouds = item.get("clouds", {})
            rain = item.get("rain", {})
            
            processed["timestamps"].append(item.get("dt_txt", ""))
            processed["temperature"].append(main.get("temp", 0))
            processed["humidity"].append(main.get("humidity", 0))
            processed["wind_speed"].append(wind.get("speed", 0))
            processed["pressure"].append(main.get("pressure", 0))
            processed["precipitation"].append(rain.get("3h", 0))
            processed["cloud_cover"].append(clouds.get("all", 0))
        
        # Calculate statistics
        stats = {
            "avg_temperature": sum(processed["temperature"]) / len(processed["temperature"]) if processed["temperature"] else 0,
            "max_wind_speed": max(processed["wind_speed"]) if processed["wind_speed"] else 0,
            "total_precipitation": sum(processed["precipitation"]),
            "avg_humidity": sum(processed["humidity"]) / len(processed["humidity"]) if processed["humidity"] else 0
        }
        
        return {
            "processed": processed,
            "statistics": stats,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def predict_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Predict future weather conditions"""
        weather_data = params.get("weather_data", {})
        horizon_hours = params.get("horizon_hours", 24)
        
        if not weather_data:
            return {"predictions": [], "error": "no_weather_data"}
        
        # Extract recent weather
        recent_items = weather_data.get("list", [])[:8]  # Last 8 readings
        
        if not recent_items:
            return {"predictions": [], "error": "insufficient_data"}
        
        # Simple trend-based prediction
        temperatures = [item.get("main", {}).get("temp", 0) for item in recent_items]
        wind_speeds = [item.get("wind", {}).get("speed", 0) for item in recent_items]
        
        avg_temp = sum(temperatures) / len(temperatures)
        avg_wind = sum(wind_speeds) / len(wind_speeds)
        
        predictions = []
        base_time = datetime.utcnow()
        
        for i in range(min(horizon_hours, 24)):
            # Simple prediction: use average with small variation
            predicted_temp = avg_temp + (i * 0.1)  # Small temperature trend
            predicted_wind = max(0, avg_wind + (i * 0.05))
            
            predictions.append({
                "timestamp": (base_time + timedelta(hours=i+1)).isoformat(),
                "temperature": round(predicted_temp, 2),
                "wind_speed": round(predicted_wind, 2),
                "confidence": round(0.85 - (i * 0.01), 2)
            })
        
        return {
            "predictions": predictions,
            "horizon_hours": len(predictions),
            "forecast_start": base_time.isoformat(),
            "forecast_end": (base_time + timedelta(hours=len(predictions))).isoformat()
        }
    
    async def predict_disaster(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Predict potential disasters based on weather data"""
        weather_data = params.get("weather_data", {})
        location = params.get("location", {})
        
        if not weather_data:
            return {"disaster_risks": [], "error": "no_weather_data"}
        
        # Process recent weather for disaster assessment
        processed = await self.process_weather_data({"weather_data": weather_data})
        stats = processed.get("statistics", {})
        
        disaster_risks = []
        
        # Typhoon/Hurricane risk
        max_wind = stats.get("max_wind_speed", 0)
        if max_wind > 100:  # km/h
            disaster_risks.append({
                "type": "typhoon",
                "severity": "critical" if max_wind > 150 else "severe",
                "probability": 0.9 if max_wind > 150 else 0.7,
                "estimated_strength": max_wind,
                "location": location
            })
        elif max_wind > 60:
            disaster_risks.append({
                "type": "typhoon",
                "severity": "moderate",
                "probability": 0.4,
                "estimated_strength": max_wind,
                "location": location
            })
        
        # Heavy rain/Flooding risk
        total_precipitation = stats.get("total_precipitation", 0)
        if total_precipitation > 200:  # mm
            disaster_risks.append({
                "type": "flooding",
                "severity": "severe",
                "probability": 0.8,
                "precipitation_mm": total_precipitation,
                "location": location
            })
        elif total_precipitation > 100:
            disaster_risks.append({
                "type": "flooding",
                "severity": "moderate",
                "probability": 0.5,
                "precipitation_mm": total_precipitation,
                "location": location
            })
        
        # Send to data quality agent for validation
        if disaster_risks:
            # Request disaster analysis from disaster analyzer agent (if exists)
            try:
                disaster_analysis = await self.send_mcp_request(
                    "disaster-analyzer-agent",
                    "analyze",
                    {
                        "disaster_data": {
                            "type": disaster_risks[0].get("type"),
                            "magnitude": disaster_risks[0].get("estimated_strength", 0),
                            "location": location
                        }
                    }
                )
                if disaster_analysis:
                    disaster_risks[0]["analysis"] = disaster_analysis
            except Exception as e:
                logger.warning(f"Could not connect to disaster analyzer: {e}")
        
        return {
            "disaster_risks": disaster_risks,
            "assessment_timestamp": datetime.utcnow().isoformat(),
            "location": location
        }
    
    async def get_historical_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical weather data"""
        # This would typically call a weather API for historical data
        # For now, return mock data
        return {
            "message": "Historical weather data retrieval not fully implemented",
            "note": "Would fetch from weather API or database"
        }
    
    def _generate_mock_weather_data(self, lat: float, lon: float, days: int) -> Dict[str, Any]:
        """Generate mock weather data for testing"""
        base_time = datetime.utcnow()
        mock_data = {
            "cod": "200",
            "message": 0,
            "cnt": days * 8,
            "list": []
        }
        
        for i in range(days * 8):
            timestamp = base_time + timedelta(hours=i*3)
            mock_data["list"].append({
                "dt": int(timestamp.timestamp()),
                "dt_txt": timestamp.isoformat(),
                "main": {
                    "temp": 20 + (i % 24) * 2,
                    "feels_like": 19 + (i % 24) * 2,
                    "temp_min": 15 + (i % 24),
                    "temp_max": 25 + (i % 24),
                    "pressure": 1013 + (i % 10) - 5,
                    "humidity": 60 + (i % 20) - 10
                },
                "weather": [{
                    "id": 800,
                    "main": "Clear",
                    "description": "clear sky",
                    "icon": "01d"
                }],
                "wind": {
                    "speed": 10 + (i % 15) - 5,
                    "deg": (i * 10) % 360
                },
                "clouds": {
                    "all": (i % 50)
                },
                "rain": {
                    "3h": (i % 5) * 2 if i % 10 == 0 else 0
                }
            })
        
        return mock_data

