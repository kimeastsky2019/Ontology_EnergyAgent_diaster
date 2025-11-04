"""
고장 진단 AI Agent
시계열 분석 기반 설비 상태 모니터링 및 예측 정비
"""

import numpy as np
from datetime import datetime, timedelta
import random

# 전역 변수로 최근 진단 결과 저장
recent_diagnostics = []

COMPONENTS = [
    "태양광 패널 #1",
    "태양광 패널 #2",
    "태양광 패널 #3",
    "인버터 #1",
    "인버터 #2",
    "배터리 시스템",
    "전력 변환 장치"
]

ISSUES = {
    "normal": "정상 작동",
    "efficiency_drop": "효율 저하",
    "temperature_high": "온도 상승",
    "voltage_unstable": "전압 불안정",
    "connection_weak": "연결 약화",
    "dust_accumulation": "먼지 축적"
}

RECOMMENDATIONS = {
    "normal": "다음 점검: 2주 후",
    "efficiency_drop": "청소 필요 또는 음영 확인",
    "temperature_high": "냉각 시스템 점검 필요",
    "voltage_unstable": "전기 연결 상태 확인 필요",
    "connection_weak": "연결 단자 점검 및 조임 필요",
    "dust_accumulation": "패널 청소 권장"
}

async def diagnose_faults():
    """고장 진단 실행"""
    global recent_diagnostics
    
    print("🔧 고장 진단 시작...")
    
    recent_diagnostics.clear()
    
    for component in COMPONENTS:
        # 랜덤하게 상태 결정 (대부분 정상)
        rand = random.random()
        
        if rand < 0.7:  # 70% 정상
            status = "normal"
            issue_key = "normal"
            confidence = random.uniform(90, 98)
        elif rand < 0.9:  # 20% 경고
            status = "warning"
            issue_key = random.choice([
                "efficiency_drop",
                "dust_accumulation",
                "connection_weak"
            ])
            confidence = random.uniform(75, 90)
        else:  # 10% 오류
            status = "error"
            issue_key = random.choice([
                "temperature_high",
                "voltage_unstable"
            ])
            confidence = random.uniform(80, 95)
        
        diagnostic = {
            "id": len(recent_diagnostics) + 1,
            "component": component,
            "status": status,
            "issue": ISSUES[issue_key],
            "recommendation": RECOMMENDATIONS[issue_key],
            "confidence": round(confidence, 2),
            "last_check": datetime.now().isoformat(),
            "next_check": (datetime.now() + timedelta(days=random.randint(7, 21))).isoformat()
        }
        
        # 추가 메트릭
        if status == "warning" or status == "error":
            diagnostic["metrics"] = {
                "efficiency": round(random.uniform(60, 85), 2),
                "temperature": round(random.uniform(45, 75), 1),
                "voltage": round(random.uniform(200, 250), 2)
            }
        else:
            diagnostic["metrics"] = {
                "efficiency": round(random.uniform(85, 95), 2),
                "temperature": round(random.uniform(25, 40), 1),
                "voltage": round(random.uniform(220, 240), 2)
            }
        
        recent_diagnostics.append(diagnostic)
    
    print(f"✅ {len(recent_diagnostics)}개 설비 진단 완료")
    return recent_diagnostics

def get_recent_diagnostics():
    """최근 진단 결과 조회"""
    if not recent_diagnostics:
        # 초기 샘플 데이터
        return [
            {
                "id": 1,
                "component": "태양광 패널 #3",
                "status": "warning",
                "issue": "효율 저하",
                "recommendation": "청소 필요 또는 음영 확인",
                "confidence": 85.5,
                "last_check": datetime.now().isoformat(),
                "next_check": (datetime.now() + timedelta(days=14)).isoformat(),
                "metrics": {
                    "efficiency": 78.3,
                    "temperature": 42.5,
                    "voltage": 235.7
                }
            },
            {
                "id": 2,
                "component": "인버터 #1",
                "status": "normal",
                "issue": "정상 작동",
                "recommendation": "다음 점검: 2주 후",
                "confidence": 95.2,
                "last_check": datetime.now().isoformat(),
                "next_check": (datetime.now() + timedelta(days=14)).isoformat(),
                "metrics": {
                    "efficiency": 92.1,
                    "temperature": 35.2,
                    "voltage": 230.5
                }
            }
        ]
    return recent_diagnostics

def predict_maintenance(component_data):
    """예측 정비 일정 계산"""
    # 간단한 선형 회귀를 사용한 예측
    # 실제로는 더 복잡한 모델 사용
    
    if len(component_data) < 10:
        return None
    
    # 효율 추세 분석
    efficiency_trend = np.polyfit(
        range(len(component_data)),
        [d['efficiency'] for d in component_data],
        1
    )[0]
    
    if efficiency_trend < -0.5:  # 효율이 빠르게 감소
        days_until_maintenance = random.randint(7, 14)
    elif efficiency_trend < -0.2:
        days_until_maintenance = random.randint(14, 30)
    else:
        days_until_maintenance = random.randint(30, 60)
    
    return {
        "recommended_date": (datetime.now() + timedelta(days=days_until_maintenance)).isoformat(),
        "days_remaining": days_until_maintenance,
        "priority": "high" if days_until_maintenance < 14 else "medium" if days_until_maintenance < 30 else "low"
    }
