"""Energy Dashboard API endpoints"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

from src.database import get_db
from src.models.user import User
from src.api.v1.auth import get_current_user
from typing import Optional

router = APIRouter()


@router.get("/realtime-power")
async def get_realtime_power(
    facility_id: str = Query("U0089"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """실시간 전력 데이터 조회"""
    # TODO: 실제 DB에서 데이터 조회
    # 현재는 시뮬레이션 데이터 반환
    now = datetime.now()
    history = []
    
    # 최근 1시간 데이터 생성 (5분 간격, 총 12개 데이터 포인트)
    for i in range(12):
        timestamp = now - timedelta(minutes=(11 - i) * 5)
        # 시간대별 패턴 시뮬레이션 (태양광 발전 패턴)
        hour = timestamp.hour
        minute = timestamp.minute
        time_of_day = hour + minute / 60.0
        
        # 태양광 발전 패턴: 6시~18시에 발전, 정오(12시)에 최대
        if 6 <= time_of_day <= 18:
            # 정오를 기준으로 한 포물선 형태
            peak_hour = 12.0
            max_power = 100.0  # 최대 100kW
            hours_from_peak = abs(time_of_day - peak_hour)
            
            # 포물선 함수로 발전량 계산
            if hours_from_peak <= 6:
                power_factor = 1 - (hours_from_peak / 6) ** 2
            else:
                power_factor = 0
            
            base_power = max_power * power_factor
            
            # 날씨 변동성 추가 (구름 등으로 인한 변동)
            weather_factor = random.uniform(0.7, 1.0)
            noise = random.uniform(-2, 2)
            power_kw = max(0, base_power * weather_factor + noise)
        else:
            # 밤 시간대: 거의 발전 없음 (약간의 잔여 전력)
            power_kw = random.uniform(0, 5)
        
        history.append({
            "timestamp": timestamp.isoformat(),
            "power_kw": round(power_kw, 2)
        })
    
    current_power = history[-1]["power_kw"] if history else 0
    
    return {
        "facility_id": facility_id,
        "current_power": current_power,
        "timestamp": now.isoformat(),
        "history": history
    }


@router.get("/daily-energy")
async def get_daily_energy(
    facility_id: str = Query("U0089"),
    date: str = Query(None),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """일일 에너지 생산 데이터 조회"""
    # TODO: 실제 DB에서 데이터 조회
    # 현재는 시뮬레이션 데이터 반환
    
    if date:
        try:
            target_date = datetime.fromisoformat(date.split('T')[0])
        except:
            target_date = datetime.now()
    else:
        target_date = datetime.now()
    
    result = []
    cumulative = 0.0
    
    # 시간대별 데이터 생성 (24시간)
    for hour in range(24):
        hour_str = f"{hour:02d}:00"
        
        # 태양광 발전 패턴 시뮬레이션
        # 6시~18시에 발전, 정오(12시)에 최대
        if 6 <= hour <= 18:
            # 정오를 기준으로 한 포물선 형태
            peak_hour = 12
            max_energy = 4.5  # 시간당 최대 4.5kWh
            hours_from_peak = abs(hour - peak_hour)
            
            # 포물선 함수로 에너지 계산
            if hours_from_peak <= 6:
                energy_factor = 1 - (hours_from_peak / 6) ** 2
            else:
                energy_factor = 0
            
            base_energy = max_energy * energy_factor
            
            # 날씨 변동성 추가
            weather_factor = random.uniform(0.75, 1.0)
            energy_kwh = max(0, base_energy * weather_factor + random.uniform(-0.2, 0.2))
        else:
            # 밤 시간대: 거의 발전 없음
            energy_kwh = random.uniform(0, 0.3)
        
        cumulative += energy_kwh
        
        result.append({
            "hour": hour_str,
            "energy_kwh": round(energy_kwh, 2),
            "cumulative_kwh": round(cumulative, 2)
        })
    
    return result


@router.get("/facility-info")
async def get_facility_info(
    facility_id: str = Query("U0089"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """시설 정보 조회"""
    # TODO: 실제 DB에서 시설 정보 조회
    # 현재 전력 계산 (실시간 전력 데이터와 동일한 로직)
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    time_of_day = hour + minute / 60.0
    
    # 태양광 발전 패턴
    if 6 <= time_of_day <= 18:
        peak_hour = 12.0
        max_power = 100.0
        hours_from_peak = abs(time_of_day - peak_hour)
        
        if hours_from_peak <= 6:
            power_factor = 1 - (hours_from_peak / 6) ** 2
        else:
            power_factor = 0
        
        base_power = max_power * power_factor
        weather_factor = random.uniform(0.7, 1.0)
        noise = random.uniform(-2, 2)
        current_power = max(0, int(base_power * weather_factor + noise))
    else:
        current_power = random.randint(0, 5)
    
    return {
        "id": facility_id,
        "name": "光点试验电站01",
        "location": "Asia/Shanghai",
        "capacity_kw": 100,
        "current_power": current_power,
        "status": "online"
    }

