"""Weather API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import httpx
from datetime import datetime, timedelta
import random

from src.config import settings

router = APIRouter()


@router.get("/current")
async def get_current_weather(
    location: str = Query("Shanghai")
) -> Dict[str, Any]:
    """현재 날씨 조회"""
    # TODO: 실제 날씨 API 연결 (OpenWeatherMap 등)
    # 현재는 시뮬레이션 데이터 반환
    
    try:
        # 실제 API 호출 시도 (API 키가 있는 경우)
        if settings.WEATHER_API_KEY:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params={
                        "q": location,
                        "appid": settings.WEATHER_API_KEY,
                        "units": "metric"
                    },
                    timeout=5.0
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "temperature": round(data["main"]["temp"], 1),
                    "condition": data["weather"][0]["main"],
                    "humidity": data["main"]["humidity"],
                    "windSpeed": round(data["wind"]["speed"], 1),
                    "visibility": round(data.get("visibility", 10000) / 1000, 1),  # km로 변환
                    "pressure": round(data["main"]["pressure"], 1),  # hPa
                    "sunrise": data["sys"]["sunrise"],
                    "sunset": data["sys"]["sunset"],
                    "location": location
                }
    except Exception:
        # API 키가 없거나 오류 발생 시 시뮬레이션 데이터 반환
        pass
    
    # 시뮬레이션 데이터 (더 현실적인 데이터)
    now = datetime.now()
    hour = now.hour
    
    # 계절별 온도 시뮬레이션 (월 기준)
    month = now.month
    if 3 <= month <= 5:  # 봄
        base_temp = 18
        temp_variation = 5
    elif 6 <= month <= 8:  # 여름
        base_temp = 28
        temp_variation = 4
    elif 9 <= month <= 11:  # 가을
        base_temp = 17
        temp_variation = 5
    else:  # 겨울
        base_temp = 8
        temp_variation = 6
    
    # 시간대별 온도 변화 (정오에 최고, 새벽에 최저)
    if 6 <= hour <= 18:
        time_factor = 1 - abs(hour - 12) / 6 * 0.3  # 정오에 +30% 정도
        temperature = base_temp * time_factor + random.uniform(-temp_variation/2, temp_variation/2)
    else:
        time_factor = 0.85  # 밤에는 낮아짐
        temperature = base_temp * time_factor + random.uniform(-temp_variation/2, temp_variation/2)
    
    temperature = round(max(-5, min(40, temperature)), 1)  # -5°C ~ 40°C 범위
    
    # 일출/일몰 시뮬레이션 (계절별로 달라짐)
    if 6 <= month <= 8:  # 여름 (일출 빠름, 일몰 늦음)
        sunrise_hour, sunrise_min = 5, 30
        sunset_hour, sunset_min = 19, 30
    elif 12 <= month or month <= 2:  # 겨울 (일출 늦음, 일몰 빠름)
        sunrise_hour, sunrise_min = 7, 0
        sunset_hour, sunset_min = 17, 30
    else:  # 봄/가을
        sunrise_hour, sunrise_min = 6, 30
        sunset_hour, sunset_min = 18, 30
    
    sunrise_time = now.replace(hour=sunrise_hour, minute=sunrise_min, second=0)
    sunset_time = now.replace(hour=sunset_hour, minute=sunset_min, second=0)
    
    # 날씨 조건 (온도에 따라 결정)
    if temperature > 25:
        condition = random.choice(["Clear", "Clear", "Clouds"])  # 여름은 맑음 확률 높음
    elif temperature < 5:
        condition = random.choice(["Clouds", "Clouds", "Rain"])
    else:
        condition = random.choice(["Clear", "Clouds", "Clouds", "Rain"])
    
    return {
        "temperature": temperature,
        "condition": condition,
        "humidity": random.randint(45, 85),
        "windSpeed": round(random.uniform(3, 12), 1),
        "visibility": round(random.uniform(8, 20), 1),
        "pressure": random.randint(1008, 1025),
        "sunrise": int(sunrise_time.timestamp()),
        "sunset": int(sunset_time.timestamp()),
        "location": location
    }


@router.get("/forecast")
async def get_weather_forecast(
    location: str = Query("Shanghai"),
    days: int = Query(7)
) -> List[Dict[str, Any]]:
    """날씨 예보 조회"""
    # TODO: 실제 날씨 API 연결
    # 현재는 시뮬레이션 데이터 반환
    
    try:
        if settings.WEATHER_API_KEY:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openweathermap.org/data/2.5/forecast",
                    params={
                        "q": location,
                        "appid": settings.WEATHER_API_KEY,
                        "units": "metric",
                        "cnt": days * 8  # 3시간 간격 데이터
                    },
                    timeout=5.0
                )
                response.raise_for_status()
                data = response.json()
                
                # 일별로 집계
                daily_forecast = []
                for i in range(0, len(data["list"]), 8):
                    day_data = data["list"][i : i + 8] if i + 8 <= len(data["list"]) else data["list"][i:]
                    temps = [d["main"]["temp"] for d in day_data]
                    
                    daily_forecast.append({
                        "date": day_data[0]["dt_txt"].split()[0],
                        "tempMax": round(max(temps), 1),
                        "tempMin": round(min(temps), 1),
                        "condition": day_data[0]["weather"][0]["main"],
                        "icon": day_data[0]["weather"][0]["icon"]
                    })
                
                return daily_forecast[:days]
    except Exception:
        pass
    
    # 시뮬레이션 데이터
    forecast = []
    now = datetime.now()
    
    for i in range(days):
        date = now + timedelta(days=i)
        base_temp = 20 + random.uniform(-5, 5)
        
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "tempMax": round(base_temp + random.uniform(2, 5), 1),
            "tempMin": round(base_temp - random.uniform(2, 5), 1),
            "condition": random.choice(["Clear", "Clouds", "Rain", "Sunny"]),
            "icon": random.choice(["01d", "02d", "03d", "04d"])
        })
    
    return forecast

