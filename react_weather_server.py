#!/usr/bin/env python3
"""
React Weather Analysis Server
서버에서 React 앱을 서빙하는 FastAPI 서버
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from pathlib import Path

# FastAPI 앱 생성
app = FastAPI(title="React Weather Analysis Server")

# React 빌드 파일 경로
REACT_BUILD_PATH = Path(__file__).parent / "react-weather-app" / "build"

# 정적 파일 서빙 설정
if REACT_BUILD_PATH.exists():
    app.mount("/static", StaticFiles(directory=str(REACT_BUILD_PATH / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_weather_dashboard():
    """Weather Dashboard HTML 서빙"""
    dashboard_file = Path(__file__).parent / "weather_dashboard.html"
    
    if dashboard_file.exists():
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Weather Analysis - Dashboard Not Found</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    text-align: center;
                    padding: 2rem;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    backdrop-filter: blur(20px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌤️ Weather Analysis Dashboard</h1>
                <p>Dashboard is being deployed...</p>
                <p>Please check back in a few minutes.</p>
            </div>
        </body>
        </html>
        """)

@app.get("/react-weather", response_class=HTMLResponse)
async def serve_react_weather():
    """React Weather 앱 서빙"""
    return await serve_weather_dashboard()

@app.get("/api/weather/current")
async def get_current_weather():
    """현재 날씨 데이터 API"""
    import random
    from datetime import datetime
    
    # 모의 날씨 데이터 생성
    now = datetime.now()
    hour = now.hour
    
    # 시간대별 기본값
    base_temp = 20 + (hour - 12) * 0.5 + random.uniform(-2, 2)
    base_humidity = 70 - (hour - 12) * 1 + random.uniform(-5, 5)
    base_wind = 2 + random.uniform(-1, 3)
    base_solar = max(0, 1000 * (1 - abs(hour - 12) / 12) + random.uniform(-200, 200))
    
    return {
        "temperature": round(base_temp, 1),
        "humidity": round(max(30, min(90, base_humidity)), 0),
        "windSpeed": round(max(0, base_wind), 1),
        "irradiance": round(max(0, base_solar), 0),
        "pressure": round(1013.2 + random.uniform(-10, 10), 1),
        "visibility": round(12.5 + random.uniform(-3, 3), 1),
        "uvIndex": round(max(0, min(11, 5 + random.uniform(-2, 2))), 1),
        "timestamp": now.isoformat(),
        "location": {
            "name": "Seoul",
            "latitude": 37.5665,
            "longitude": 126.9780,
            "country": "South Korea"
        },
        "conditions": {
            "main": "Clear" if hour >= 6 and hour < 18 else "Partly Cloudy",
            "description": "Clear sky" if hour >= 6 and hour < 18 else "Partly cloudy",
            "icon": "01d" if hour >= 6 and hour < 18 else "02n"
        }
    }

@app.get("/api/weather/forecast")
async def get_weather_forecast(days: int = 5):
    """날씨 예보 데이터 API"""
    import random
    from datetime import datetime, timedelta
    
    forecasts = []
    now = datetime.now()
    
    for i in range(days):
        date = now + timedelta(days=i)
        day_of_year = date.timetuple().tm_yday
        
        # 계절별 패턴
        seasonal_temp = 15 + (day_of_year - 80) * 0.1 + random.uniform(-3, 3)
        seasonal_humidity = 60 + (day_of_year - 80) * 0.05 + random.uniform(-10, 10)
        
        forecasts.append({
            "date": date.strftime("%Y-%m-%d"),
            "temperature": {
                "min": round(seasonal_temp - 5 + random.uniform(-2, 2), 1),
                "max": round(seasonal_temp + 5 + random.uniform(-2, 2), 1),
                "avg": round(seasonal_temp + random.uniform(-1, 1), 1)
            },
            "humidity": round(max(30, min(90, seasonal_humidity)), 0),
            "windSpeed": round(2 + random.uniform(0, 4), 1),
            "pressure": round(1013 + random.uniform(-15, 15), 1),
            "conditions": {
                "main": random.choice(["Clear", "Clouds", "Rain", "Snow"]),
                "description": random.choice(["Clear sky", "Few clouds", "Scattered clouds", "Light rain"]),
                "icon": random.choice(["01d", "02d", "03d", "10d"])
            },
            "precipitation": {
                "probability": round(random.uniform(0, 100), 0),
                "amount": round(random.uniform(0, 10), 1)
            }
        })
    
    return {"forecasts": forecasts}

@app.get("/api/energy/correlations")
async def get_energy_correlations():
    """에너지 상관관계 데이터 API"""
    return {
        "correlations": [
            {
                "type": "temperature_energy",
                "value": 0.78,
                "description": "Temperature vs Energy Consumption",
                "trend": "positive"
            },
            {
                "type": "solar_generation",
                "value": 0.92,
                "description": "Solar Radiation vs Generation",
                "trend": "positive"
            },
            {
                "type": "humidity_efficiency",
                "value": -0.45,
                "description": "Humidity vs Efficiency",
                "trend": "negative"
            },
            {
                "type": "wind_turbine",
                "value": 0.65,
                "description": "Wind Speed vs Turbine Output",
                "trend": "positive"
            }
        ]
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "React Weather Analysis Server"}

if __name__ == "__main__":
    print("🌤️ Starting React Weather Analysis Server...")
    print(f"📁 React build path: {REACT_BUILD_PATH}")
    print(f"📁 Build exists: {REACT_BUILD_PATH.exists()}")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=3000,
        log_level="info"
    )
