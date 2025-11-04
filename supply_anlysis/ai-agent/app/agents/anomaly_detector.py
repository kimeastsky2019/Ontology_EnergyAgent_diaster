"""
이상징후 감지 AI Agent
Isolation Forest 알고리즘을 사용한 실시간 이상 패턴 탐지
"""

from sklearn.ensemble import IsolationForest
import numpy as np
from datetime import datetime, timedelta
import random

# 전역 변수로 최근 이상징후 저장
recent_anomalies = []

def generate_sample_data():
    """샘플 에너지 데이터 생성"""
    data = []
    for i in range(100):
        # 정상 패턴
        value = 50 + np.random.normal(0, 10)
        data.append(value)
    
    # 이상치 추가
    data.extend([10, 150, 5, 160])  # 명확한 이상치
    
    return np.array(data).reshape(-1, 1)

async def detect_anomalies():
    """이상징후 감지 실행"""
    global recent_anomalies
    
    print("🔍 이상징후 감지 시작...")
    
    # 실제로는 데이터베이스나 API에서 데이터를 가져옴
    data = generate_sample_data()
    
    # Isolation Forest 모델
    model = IsolationForest(
        contamination=0.05,  # 5%의 데이터를 이상치로 예상
        random_state=42
    )
    
    # 학습 및 예측
    predictions = model.fit_predict(data)
    scores = model.score_samples(data)
    
    # 이상치 탐지 (prediction이 -1인 경우)
    anomaly_indices = np.where(predictions == -1)[0]
    
    # 최근 이상징후 업데이트
    recent_anomalies.clear()
    
    for idx in anomaly_indices[-5:]:  # 최근 5개만 저장
        severity = "high" if scores[idx] < -0.5 else "medium" if scores[idx] < -0.3 else "low"
        
        anomaly = {
            "id": len(recent_anomalies) + 1,
            "type": "warning" if severity != "low" else "info",
            "title": "비정상적인 전력 변동 감지" if severity != "low" else "생산량 변동 감지",
            "description": f"예상보다 {random.randint(20, 40)}% {'낮은' if random.random() > 0.5 else '높은'} 전력 생산",
            "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 5))).isoformat(),
            "severity": severity,
            "confidence": round(abs(scores[idx]) * 100, 2),
            "value": float(data[idx][0])
        }
        recent_anomalies.append(anomaly)
    
    print(f"✅ 이상징후 {len(anomaly_indices)}개 감지 완료")
    return recent_anomalies

def get_recent_anomalies():
    """최근 이상징후 조회"""
    if not recent_anomalies:
        # 초기 샘플 데이터
        return [
            {
                "id": 1,
                "type": "warning",
                "title": "비정상적인 전력 변동 감지",
                "description": "14:30-15:00 사이 예상보다 30% 낮은 전력 생산",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "severity": "medium",
                "confidence": 85.5,
                "value": 35.2
            },
            {
                "id": 2,
                "type": "info",
                "title": "생산량 예측",
                "description": "오늘 총 생산량 예상: 85.3 kWh (평균 대비 +5%)",
                "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                "severity": "low",
                "confidence": 92.3,
                "value": 85.3
            }
        ]
    return recent_anomalies

def analyze_pattern(data):
    """패턴 분석"""
    # 추세 분석
    if len(data) < 2:
        return "insufficient_data"
    
    trend = np.polyfit(range(len(data)), data.flatten(), 1)[0]
    
    if trend > 0.5:
        return "increasing"
    elif trend < -0.5:
        return "decreasing"
    else:
        return "stable"
