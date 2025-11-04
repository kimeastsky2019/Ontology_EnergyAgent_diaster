from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import Optional
import random
import math

router = APIRouter()

def generate_sample_power_data(range_type: str = "hour"):
    """샘플 전력 데이터 생성"""
    now = datetime.now()
    labels = []
    values = []
    
    if range_type == "hour":
        # 최근 24시간
        for i in range(24, 0, -1):
            time = now - timedelta(hours=i)
            labels.append(time.strftime("%H:%M"))
            
            # 시간대별 패턴
            hour = time.hour
            if 6 <= hour <= 18:
                base_value = 30 + math.sin((hour - 6) / 12 * math.pi) * 60
            else:
                base_value = random.uniform(0, 10)
            
            values.append(base_value + random.uniform(-5, 5))
    
    elif range_type == "day":
        # 최근 7일
        for i in range(7, 0, -1):
            date = now - timedelta(days=i)
            labels.append(date.strftime("%m/%d"))
            values.append(random.uniform(50, 150))
    
    elif range_type == "month":
        # 최근 30일
        for i in range(30, 0, -1):
            date = now - timedelta(days=i)
            labels.append(date.strftime("%m/%d"))
            values.append(random.uniform(50, 150))
    
    elif range_type == "year":
        # 최근 12개월
        for i in range(12, 0, -1):
            date = now - timedelta(days=i*30)
            labels.append(date.strftime("%Y-%m"))
            values.append(random.uniform(1000, 3000))
    
    return {"labels": labels, "values": values}

@router.get("/realtime")
async def get_realtime_power(range: str = Query("hour", regex="^(hour|day|month|year)$")):
    """
    실시간 전력 데이터 조회
    
    - **range**: 시간 범위 (hour, day, month, year)
    """
    data = generate_sample_power_data(range)
    return data

@router.get("/history")
async def get_energy_history(
    start: Optional[str] = None,
    end: Optional[str] = None
):
    """
    과거 에너지 데이터 조회
    
    - **start**: 시작 날짜 (YYYY-MM-DD)
    - **end**: 종료 날짜 (YYYY-MM-DD)
    """
    if not start:
        start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end:
        end = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "start_date": start,
        "end_date": end,
        "total_energy": random.uniform(1000, 5000),
        "average_power": random.uniform(50, 150),
        "peak_power": random.uniform(150, 200)
    }

@router.get("/daily")
async def get_daily_energy(date: Optional[str] = None):
    """
    일일 에너지 생산 데이터 조회
    
    - **date**: 날짜 (YYYY-MM-DD)
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    labels = []
    values = []
    
    for hour in range(24):
        labels.append(f"{hour:02d}:00")
        
        # 시간대별 에너지 생산 패턴
        if 6 <= hour <= 18:
            energy = 5 + math.sin((hour - 6) / 12 * math.pi) * 20 + random.uniform(0, 5)
        else:
            energy = random.uniform(0, 2)
        
        values.append(energy)
    
    return {
        "date": date,
        "labels": labels,
        "values": values,
        "total": sum(values)
    }

@router.get("/forecast")
async def get_energy_forecast(days: int = Query(7, ge=1, le=30)):
    """
    에너지 생산 예측
    
    - **days**: 예측 일수 (1-30)
    """
    labels = []
    values = []
    
    now = datetime.now()
    for i in range(days):
        date = now + timedelta(days=i+1)
        labels.append(date.strftime("%m/%d"))
        values.append(random.uniform(80, 150))
    
    return {
        "forecast_period": f"{days} days",
        "labels": labels,
        "values": values,
        "total_expected": sum(values)
    }
