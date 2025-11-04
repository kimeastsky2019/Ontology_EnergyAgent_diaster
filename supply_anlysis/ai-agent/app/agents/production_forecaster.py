"""
생산량 예측 AI Agent
시계열 예측 기반 에너지 생산량 예측
"""

import numpy as np
from datetime import datetime, timedelta
import random

# 전역 변수로 최근 예측 결과 저장
recent_forecast = None

async def forecast_production(days=7):
    """생산량 예측 실행"""
    global recent_forecast
    
    print(f"📊 {days}일 생산량 예측 시작...")
    
    forecast_data = []
    base_production = 100  # 기본 생산량 (kWh)
    
    for i in range(days):
        date = datetime.now() + timedelta(days=i+1)
        
        # 요일 효과 (주말에 약간 낮음)
        weekday_factor = 0.9 if date.weekday() >= 5 else 1.0
        
        # 계절 효과 (간단한 사인 함수)
        season_factor = 1 + 0.3 * np.sin((date.month - 3) / 12 * 2 * np.pi)
        
        # 랜덤 변동
        random_factor = random.uniform(0.85, 1.15)
        
        # 예측 생산량
        predicted = base_production * weekday_factor * season_factor * random_factor
        
        # 신뢰 구간
        confidence_interval = predicted * 0.15
        
        forecast_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "day_of_week": ["월", "화", "수", "목", "금", "토", "일"][date.weekday()],
            "predicted_production": round(predicted, 2),
            "confidence_lower": round(predicted - confidence_interval, 2),
            "confidence_upper": round(predicted + confidence_interval, 2),
            "confidence_level": round(random.uniform(80, 95), 2),
            "weather_factor": round(season_factor, 2)
        })
    
    recent_forecast = {
        "forecast_period": f"{days} days",
        "generated_at": datetime.now().isoformat(),
        "total_expected": round(sum(d["predicted_production"] for d in forecast_data), 2),
        "average_daily": round(sum(d["predicted_production"] for d in forecast_data) / days, 2),
        "forecast": forecast_data,
        "model_info": {
            "algorithm": "Time Series Forecasting",
            "version": "1.0",
            "last_trained": (datetime.now() - timedelta(days=7)).isoformat()
        }
    }
    
    print(f"✅ {days}일 생산량 예측 완료: 총 {recent_forecast['total_expected']} kWh")
    return recent_forecast

def get_recent_forecast():
    """최근 예측 결과 조회"""
    if not recent_forecast:
        # 초기 샘플 데이터 생성
        return {
            "forecast_period": "7 days",
            "generated_at": datetime.now().isoformat(),
            "total_expected": 735.2,
            "average_daily": 105.0,
            "forecast": [
                {
                    "date": (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                    "day_of_week": ["월", "화", "수", "목", "금", "토", "일"][(datetime.now() + timedelta(days=i+1)).weekday()],
                    "predicted_production": round(100 + random.uniform(-10, 20), 2),
                    "confidence_lower": round(85 + random.uniform(-5, 5), 2),
                    "confidence_upper": round(115 + random.uniform(-5, 5), 2),
                    "confidence_level": round(random.uniform(85, 95), 2),
                    "weather_factor": round(random.uniform(0.9, 1.1), 2)
                }
                for i in range(7)
            ],
            "model_info": {
                "algorithm": "Time Series Forecasting",
                "version": "1.0",
                "last_trained": (datetime.now() - timedelta(days=7)).isoformat()
            }
        }
    return recent_forecast

def calculate_production_efficiency(actual, predicted):
    """생산 효율 계산"""
    if predicted == 0:
        return 0
    
    efficiency = (actual / predicted) * 100
    return round(efficiency, 2)

def analyze_trends(historical_data):
    """과거 데이터 추세 분석"""
    if len(historical_data) < 7:
        return {
            "trend": "insufficient_data",
            "message": "분석을 위한 데이터가 부족합니다"
        }
    
    # 최근 7일 평균과 이전 7일 평균 비교
    recent_avg = np.mean(historical_data[-7:])
    previous_avg = np.mean(historical_data[-14:-7])
    
    change_percent = ((recent_avg - previous_avg) / previous_avg) * 100
    
    if change_percent > 10:
        trend = "increasing"
        message = f"생산량이 {change_percent:.1f}% 증가 추세입니다"
    elif change_percent < -10:
        trend = "decreasing"
        message = f"생산량이 {abs(change_percent):.1f}% 감소 추세입니다"
    else:
        trend = "stable"
        message = "생산량이 안정적입니다"
    
    return {
        "trend": trend,
        "change_percent": round(change_percent, 2),
        "message": message,
        "recent_average": round(recent_avg, 2),
        "previous_average": round(previous_avg, 2)
    }
