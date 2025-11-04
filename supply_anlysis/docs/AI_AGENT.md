# AI Agent 가이드

## 개요

에너지 모니터링 시스템의 AI Agent는 세 가지 주요 기능을 제공합니다:

1. **이상징후 감지** (Anomaly Detection)
2. **고장 진단** (Fault Diagnostics)
3. **생산량 예측** (Production Forecasting)

## 🔍 이상징후 감지 (Anomaly Detection)

### 알고리즘
**Isolation Forest** 알고리즘을 사용하여 비정상적인 전력 생산 패턴을 실시간으로 탐지합니다.

### 작동 방식
1. 최근 100개의 전력 데이터 포인트 수집
2. Isolation Forest 모델 학습
3. 각 데이터 포인트의 이상치 점수 계산
4. 임계값을 초과하는 경우 알림 생성

### 실행 주기
- **자동 실행**: 5분마다
- **수동 실행**: `/api/ai/analyze` 엔드포인트 호출

### 감지 기준
```python
contamination=0.05  # 5%의 데이터를 이상치로 예상
```

### 심각도 분류
- **High**: 이상치 점수 < -0.5
- **Medium**: -0.5 ≤ 이상치 점수 < -0.3
- **Low**: -0.3 ≤ 이상치 점수

### 알림 예시
```json
{
  "id": 1,
  "type": "warning",
  "title": "비정상적인 전력 변동 감지",
  "description": "예상보다 30% 낮은 전력 생산",
  "severity": "medium",
  "confidence": 85.5,
  "timestamp": "2024-11-03T14:30:00"
}
```

## 🔧 고장 진단 (Fault Diagnostics)

### 알고리즘
시계열 분석과 규칙 기반 시스템을 조합하여 설비의 상태를 진단합니다.

### 진단 대상
- 태양광 패널 (3개)
- 인버터 (2개)
- 배터리 시스템
- 전력 변환 장치

### 진단 항목
1. **효율성**: 설비의 에너지 변환 효율
2. **온도**: 작동 온도
3. **전압**: 출력 전압 안정성
4. **연결 상태**: 전기적 연결 상태

### 상태 분류
- **Normal**: 정상 작동
- **Warning**: 주의 필요
- **Error**: 즉시 조치 필요

### 실행 주기
- **자동 실행**: 10분마다
- **수동 실행**: `/api/ai/analyze` 엔드포인트 호출

### 진단 결과 예시
```json
{
  "component": "태양광 패널 #3",
  "status": "warning",
  "issue": "효율 저하",
  "recommendation": "청소 필요 또는 음영 확인",
  "confidence": 85.5,
  "metrics": {
    "efficiency": 78.3,
    "temperature": 42.5,
    "voltage": 235.7
  }
}
```

### 예측 정비
고장 진단 결과를 바탕으로 예측 정비 일정을 계산합니다:

- **효율 감소율 > 0.5%/day**: 7-14일 내 정비 권장
- **효율 감소율 0.2-0.5%/day**: 14-30일 내 정비 권장
- **효율 감소율 < 0.2%/day**: 30-60일 내 정비 권장

## 📊 생산량 예측 (Production Forecasting)

### 알고리즘
시계열 분석 기반 예측 모델을 사용합니다.

### 예측 요소
1. **계절 효과**: 월별 일조량 변화
2. **요일 효과**: 평일/주말 차이
3. **과거 패턴**: 과거 생산 데이터 분석
4. **날씨 예보**: 날씨 데이터 연동 (향후 구현)

### 실행 주기
- **자동 실행**: 1시간마다
- **수동 실행**: `/api/ai/analyze` 엔드포인트 호출

### 예측 기간
- 기본: 7일
- 최대: 30일

### 신뢰 구간
예측값의 ±15% 범위로 신뢰 구간을 설정합니다.

### 예측 결과 예시
```json
{
  "forecast_period": "7 days",
  "total_expected": 735.2,
  "average_daily": 105.0,
  "forecast": [
    {
      "date": "2024-11-04",
      "predicted_production": 102.5,
      "confidence_lower": 87.1,
      "confidence_upper": 117.9,
      "confidence_level": 88.5
    }
  ]
}
```

## 🎯 성능 최적화

### 데이터 캐싱
Redis를 사용하여 분석 결과를 캐싱합니다:
- 이상징후: 5분간 캐싱
- 고장 진단: 10분간 캐싱
- 생산량 예측: 1시간간 캐싱

### 배치 처리
대량의 데이터는 배치로 처리하여 성능을 향상시킵니다.

## 🔄 모델 업데이트

### 자동 재학습
- **주기**: 매주 일요일 자정
- **데이터**: 최근 3개월 데이터 사용

### 수동 재학습
```bash
docker exec -it energy-ai-agent python -m app.agents.retrain
```

## 📈 모니터링

### 로그 확인
```bash
# AI Agent 로그
docker logs energy-ai-agent -f

# 특정 Agent 로그
docker logs energy-ai-agent | grep "anomaly"
docker logs energy-ai-agent | grep "diagnostics"
docker logs energy-ai-agent | grep "forecast"
```

### 성능 메트릭
- 분석 소요 시간
- 정확도 (실제값과 예측값 비교)
- 오탐률 (False Positive Rate)

## 🛠️ 커스터마이징

### 임계값 조정
`.env` 파일에서 임계값을 조정할 수 있습니다:

```bash
ANOMALY_THRESHOLD=0.8  # 기본값: 0.8
EFFICIENCY_THRESHOLD=80  # 효율 임계값 (%)
TEMPERATURE_THRESHOLD=60  # 온도 임계값 (°C)
```

### 알고리즘 변경
각 Agent의 Python 파일을 수정하여 알고리즘을 변경할 수 있습니다:

- `anomaly_detector.py`: 이상징후 감지
- `fault_diagnostics.py`: 고장 진단
- `production_forecaster.py`: 생산량 예측

## 🔐 보안

### API 인증
프로덕션 환경에서는 API 키 기반 인증을 구현하세요:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("AI_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

## 📚 추가 학습 자료

- [Isolation Forest 논문](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [시계열 예측 가이드](https://otexts.com/fpp3/)
- [scikit-learn 문서](https://scikit-learn.org/)
