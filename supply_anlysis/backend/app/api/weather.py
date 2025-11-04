from fastapi import APIRouter, Query
from datetime import datetime, timedelta
import random

router = APIRouter()

WEATHER_CONDITIONS = ["sunny", "cloudy", "rainy", "snowy"]
WEATHER_CONDITIONS_KR = {
    "sunny": "맑음",
    "cloudy": "흐림",
    "rainy": "비",
    "snowy": "눈"
}

def generate_weather_condition():
    """랜덤 날씨 상태 생성 (현실적인 확률 적용)"""
    rand = random.random()
    if rand < 0.5:
        return "sunny"
    elif rand < 0.8:
        return "cloudy"
    elif rand < 0.95:
        return "rainy"
    else:
        return "snowy"

@router.get("/current")
async def get_current_weather():
    """현재 날씨 정보 조회"""
    condition = generate_weather_condition()
    
    return {
        "current": {
            "temp": random.randint(10, 25),
            "condition": condition,
            "condition_kr": WEATHER_CONDITIONS_KR[condition],
            "humidity": random.randint(40, 80),
            "windSpeed": round(random.uniform(0.5, 5.0), 1),
            "visibility": random.randint(5, 15),
            "pressure": random.randint(1005, 1025),
            "sunrise": "06:30",
            "sunset": "18:45",
            "uv_index": random.randint(1, 10)
        },
        "location": {
            "city": "Pyeongtaek",
            "region": "Gyeonggi-do",
            "country": "KR",
            "lat": 36.9922,
            "lon": 127.1128
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/forecast")
async def get_weather_forecast(days: int = Query(7, ge=1, le=14)):
    """날씨 예보 조회"""
    now = datetime.now()
    forecast = []
    
    weekdays_kr = ["월", "화", "수", "목", "금", "토", "일"]
    
    for i in range(days):
        date = now + timedelta(days=i)
        condition = generate_weather_condition()
        
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": weekdays_kr[date.weekday()],
            "temp": random.randint(10, 25),
            "temp_min": random.randint(5, 15),
            "temp_max": random.randint(18, 30),
            "condition": condition,
            "condition_kr": WEATHER_CONDITIONS_KR[condition],
            "precipitation_chance": random.randint(0, 100),
            "humidity": random.randint(40, 80),
            "wind_speed": round(random.uniform(0.5, 5.0), 1)
        })
    
    return {
        "forecast_period": f"{days} days",
        "forecast": forecast,
        "generated_at": datetime.now().isoformat()
    }

@router.get("/hourly")
async def get_hourly_weather():
    """시간별 날씨 조회 (24시간)"""
    now = datetime.now()
    hourly = []
    
    for i in range(24):
        time = now + timedelta(hours=i)
        condition = generate_weather_condition()
        
        hourly.append({
            "time": time.strftime("%H:%M"),
            "datetime": time.isoformat(),
            "temp": random.randint(10, 25),
            "condition": condition,
            "condition_kr": WEATHER_CONDITIONS_KR[condition],
            "precipitation_chance": random.randint(0, 100),
            "wind_speed": round(random.uniform(0.5, 5.0), 1)
        })
    
    return {
        "hourly": hourly,
        "generated_at": datetime.now().isoformat()
    }

@router.get("/alerts")
async def get_weather_alerts():
    """기상 경보 조회"""
    # 랜덤하게 경보 생성 (10% 확률)
    has_alert = random.random() < 0.1
    
    if not has_alert:
        return {"alerts": []}
    
    alert_types = [
        {"type": "storm", "severity": "warning", "message": "강풍 주의보"},
        {"type": "rain", "severity": "watch", "message": "호우 주의보"},
        {"type": "heat", "severity": "advisory", "message": "폭염 주의보"}
    ]
    
    alert = random.choice(alert_types)
    
    return {
        "alerts": [
            {
                **alert,
                "issued_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=6)).isoformat()
            }
        ]
    }
