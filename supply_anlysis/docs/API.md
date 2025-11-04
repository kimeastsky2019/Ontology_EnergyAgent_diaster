# API 사용 가이드

## 기본 정보

- **백엔드 API 주소**: `http://localhost:8000`
- **AI Agent API 주소**: `http://localhost:8001`
- **API 문서**: `http://localhost:8000/docs` (Swagger UI)

## 인증

현재 버전에서는 인증이 필요하지 않습니다. 프로덕션 환경에서는 JWT 기반 인증을 구현하세요.

## 엔드포인트

### 🔌 에너지 API

#### 실시간 전력 데이터
```bash
GET /api/energy/realtime?range=hour
```

**Query Parameters:**
- `range`: `hour` | `day` | `month` | `year`

**Response:**
```json
{
  "labels": ["00:00", "01:00", ...],
  "values": [45.2, 38.7, ...]
}
```

#### 일일 에너지 데이터
```bash
GET /api/energy/daily?date=2024-11-03
```

**Query Parameters:**
- `date`: YYYY-MM-DD 형식 (선택사항, 기본값: 오늘)

**Response:**
```json
{
  "date": "2024-11-03",
  "labels": ["00:00", "01:00", ...],
  "values": [5.2, 3.8, ...],
  "total": 125.5
}
```

### 🏢 시설 API

#### 현재 시설 정보
```bash
GET /api/facilities/current
```

**Response:**
```json
{
  "id": "U0089",
  "name": "光点试验电站01",
  "currentPower": 45230.5,
  "efficiency": 87.3,
  "status": "online"
}
```

### 🌤️ 날씨 API

#### 현재 날씨
```bash
GET /api/weather/current
```

**Response:**
```json
{
  "current": {
    "temp": 17,
    "condition": "sunny",
    "humidity": 65,
    "windSpeed": 3.5
  }
}
```

#### 날씨 예보
```bash
GET /api/weather/forecast?days=7
```

**Query Parameters:**
- `days`: 1-14 (기본값: 7)

### 🤖 AI Agent API

#### 이상징후 목록
```bash
GET /api/ai/anomalies
```

**Response:**
```json
[
  {
    "id": 1,
    "type": "warning",
    "title": "비정상적인 전력 변동 감지",
    "description": "예상보다 30% 낮은 전력 생산",
    "severity": "medium",
    "confidence": 85.5
  }
]
```

#### 고장 진단 결과
```bash
GET /api/ai/diagnostics
```

**Response:**
```json
[
  {
    "id": 1,
    "component": "태양광 패널 #3",
    "status": "warning",
    "issue": "효율 저하",
    "recommendation": "청소 필요 또는 음영 확인",
    "confidence": 85.5
  }
]
```

#### 즉시 분석 실행
```bash
POST /api/ai/analyze
```

**Response:**
```json
{
  "status": "completed",
  "results": {
    "anomalies": [...],
    "diagnostics": [...],
    "forecast": {...}
  }
}
```

## 사용 예시

### JavaScript (Axios)
```javascript
import axios from 'axios';

// 실시간 전력 데이터 조회
const getPowerData = async () => {
  const response = await axios.get('http://localhost:8000/api/energy/realtime?range=hour');
  console.log(response.data);
};

// AI 이상징후 조회
const getAnomalies = async () => {
  const response = await axios.get('http://localhost:8001/api/ai/anomalies');
  console.log(response.data);
};
```

### Python (Requests)
```python
import requests

# 실시간 전력 데이터 조회
response = requests.get('http://localhost:8000/api/energy/realtime?range=hour')
data = response.json()
print(data)

# AI 이상징후 조회
response = requests.get('http://localhost:8001/api/ai/anomalies')
anomalies = response.json()
print(anomalies)
```

### cURL
```bash
# 실시간 전력 데이터
curl http://localhost:8000/api/energy/realtime?range=hour

# 현재 시설 정보
curl http://localhost:8000/api/facilities/current

# AI 이상징후
curl http://localhost:8001/api/ai/anomalies
```

## 에러 처리

모든 API는 표준 HTTP 상태 코드를 반환합니다:

- `200 OK`: 성공
- `400 Bad Request`: 잘못된 요청
- `404 Not Found`: 리소스를 찾을 수 없음
- `500 Internal Server Error`: 서버 오류

**에러 응답 형식:**
```json
{
  "detail": "에러 메시지"
}
```

## Rate Limiting

현재 버전에서는 Rate Limiting이 구현되어 있지 않습니다. 프로덕션 환경에서는 Redis 기반 Rate Limiting을 구현하세요.

## CORS

개발 환경에서는 모든 도메인(`*`)에서의 요청을 허용합니다. 프로덕션 환경에서는 특정 도메인만 허용하도록 설정하세요.
