from fastapi import APIRouter
from datetime import datetime
import random

router = APIRouter()

# 샘플 시설 데이터
SAMPLE_FACILITIES = [
    {
        "id": "U0089",
        "name": "光点试验电站01",
        "type": "solar",
        "capacity": 100000,  # 100kW
        "location": "Pyeongtaek, Gyeonggi-do, KR",
        "status": "online",
        "currentPower": random.uniform(0, 80000),
        "efficiency": random.uniform(80, 95),
        "installation_date": "2023-01-15"
    }
]

@router.get("")
async def get_all_facilities():
    """모든 시설 목록 조회"""
    return {
        "total": len(SAMPLE_FACILITIES),
        "facilities": SAMPLE_FACILITIES
    }

@router.get("/current")
async def get_current_facility():
    """현재 시설 정보 조회 (메인 시설)"""
    facility = SAMPLE_FACILITIES[0].copy()
    facility["currentPower"] = random.uniform(0, 80000)
    facility["efficiency"] = random.uniform(80, 95)
    facility["last_updated"] = datetime.now().isoformat()
    
    return facility

@router.get("/{facility_id}")
async def get_facility_by_id(facility_id: str):
    """특정 시설 정보 조회"""
    facility = next((f for f in SAMPLE_FACILITIES if f["id"] == facility_id), None)
    
    if not facility:
        return {"error": "Facility not found"}, 404
    
    facility_copy = facility.copy()
    facility_copy["currentPower"] = random.uniform(0, 80000)
    facility_copy["efficiency"] = random.uniform(80, 95)
    facility_copy["last_updated"] = datetime.now().isoformat()
    
    return facility_copy

@router.get("/{facility_id}/stats")
async def get_facility_stats(facility_id: str):
    """시설 통계 정보 조회"""
    return {
        "facility_id": facility_id,
        "daily_production": random.uniform(500, 800),
        "monthly_production": random.uniform(15000, 25000),
        "yearly_production": random.uniform(180000, 300000),
        "uptime_percentage": random.uniform(95, 99.5),
        "maintenance_count": random.randint(2, 8),
        "last_maintenance": "2024-10-15"
    }
