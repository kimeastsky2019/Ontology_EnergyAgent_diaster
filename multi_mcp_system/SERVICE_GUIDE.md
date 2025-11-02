# 🚀 Multi-MCP Time Series Analysis Service Guide

## 📋 서비스 개요

Multi-MCP Time Series Analysis System은 A2A (Agent-to-Agent) 기반의 멀티 MCP 아키텍처를 사용하여 시계열 예측과 이상치 탐지를 수행하는 종합적인 서비스입니다.

## 🏗️ 서비스 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Forecasting   │    │   Anomaly       │    │   Coordinator   │
│   MCP Server    │◄──►│   Detection     │◄──►│   MCP Server    │
│   (Port 8001)   │    │   MCP Server    │    │   (Port 8003)   │
│                 │    │   (Port 8002)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Web Services  │
                    │   Dashboard     │
                    │   (Port 5000)   │
                    │   REST API      │
                    │   (Port 5001)   │
                    └─────────────────┘
```

## 🚀 빠른 시작

### 1. Docker를 사용한 전체 서비스 실행

```bash
# 모든 서비스 시작
python run_service.py start

# 또는 Docker Compose 직접 사용
docker-compose up -d
```

### 2. 로컬에서 서비스 실행

```bash
# 로컬에서 모든 서비스 시작
python run_service.py start --service local

# 개별 서비스 시작
python run_service.py start --service web
python run_service.py start --service api
python run_service.py start --service forecasting
python run_service.py start --service anomaly
python run_service.py start --service coordinator
```

### 3. 서비스 관리

```bash
# 서비스 상태 확인
python run_service.py status

# 서비스 중지
python run_service.py stop

# 서비스 재시작
python run_service.py restart

# 로그 확인
python run_service.py logs
python run_service.py logs --logs-service web-dashboard
```

## 🌐 서비스 접근 URL

| 서비스 | URL | 설명 |
|--------|-----|------|
| **Web Dashboard** | http://localhost:5000 | 메인 웹 대시보드 |
| **REST API** | http://localhost:5001 | REST API 서비스 |
| **Forecasting MCP** | http://localhost:8001 | 예측 모델 MCP 서버 |
| **Anomaly MCP** | http://localhost:8002 | 이상치 탐지 MCP 서버 |
| **Coordinator MCP** | http://localhost:8003 | 조정자 MCP 서버 |
| **Prometheus** | http://localhost:9090 | 메트릭 모니터링 |
| **Grafana** | http://localhost:3000 | 시각화 대시보드 (admin/admin) |

## 📊 주요 기능

### 1. 웹 대시보드 (Port 5000)
- **실시간 모니터링**: 시스템 상태 및 메트릭 실시간 표시
- **모델 관리**: 예측 및 이상치 탐지 모델 훈련/관리
- **데이터 시각화**: 시계열 데이터 차트 및 분석 결과 표시
- **통합 분석**: 예측과 이상치 탐지를 동시에 수행
- **앙상블 예측**: 여러 모델을 조합한 예측

### 2. REST API (Port 5001)
- **모델 훈련 API**: 예측 및 이상치 탐지 모델 훈련
- **예측 API**: 시계열 예측 수행
- **이상치 탐지 API**: 이상치 탐지 수행
- **통합 분석 API**: 복합 분석 수행
- **데이터 생성 API**: 샘플 데이터 생성

### 3. MCP 서버들
- **Forecasting MCP**: LSTM, CNN, Multivariate 모델 지원
- **Anomaly MCP**: Prophet, HMM, Transformer 모델 지원
- **Coordinator MCP**: A2A 통신 및 통합 분석 조정

## 🔧 API 사용 예시

### 1. 샘플 데이터 생성

```bash
curl -X POST http://localhost:5001/api/v1/data/generate \
  -H "Content-Type: application/json" \
  -d '{
    "n_samples": 1000,
    "n_features": 1,
    "trend": true,
    "seasonality": true,
    "noise_level": 0.1
  }'
```

### 2. 예측 모델 훈련

```bash
curl -X POST http://localhost:5001/api/v1/models/forecasting/train \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "lstm",
    "data": "[[1.0], [1.1], [1.2], ...]",
    "model_name": "my_lstm_model",
    "sequence_length": 30,
    "prediction_length": 1,
    "epochs": 100
  }'
```

### 3. 예측 수행

```bash
curl -X POST http://localhost:5001/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "my_lstm_model",
    "data": "[[1.0], [1.1], [1.2], ...]",
    "steps_ahead": 10
  }'
```

### 4. 이상치 탐지

```bash
curl -X POST http://localhost:5001/api/v1/detect_anomalies \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "my_prophet_model",
    "data": "[[1.0], [1.1], [1.2], ...]",
    "threshold": 0.95
  }'
```

### 5. 통합 분석

```bash
curl -X POST http://localhost:5001/api/v1/analysis/coordinated \
  -H "Content-Type: application/json" \
  -d '{
    "data": "[[1.0], [1.1], [1.2], ...]",
    "analysis_type": "forecast_and_detect",
    "forecasting_model": "lstm",
    "anomaly_model": "prophet"
  }'
```

## 📈 모니터링 및 로깅

### 1. Prometheus 메트릭
- **시스템 메트릭**: CPU, 메모리, 디스크 사용률
- **애플리케이션 메트릭**: 요청 수, 응답 시간, 에러율
- **모델 메트릭**: 훈련 시간, 예측 성능, 이상치 탐지 성능

### 2. Grafana 대시보드
- **시스템 대시보드**: 서버 리소스 사용률
- **애플리케이션 대시보드**: API 성능 및 사용량
- **모델 대시보드**: 모델 성능 및 사용 통계

### 3. 로그 관리
```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f web-dashboard
docker-compose logs -f rest-api
docker-compose logs -f forecasting-mcp
```

## 🗄️ 데이터베이스

### 1. PostgreSQL (기본)
- **모델 정보**: 훈련된 모델 메타데이터 저장
- **분석 결과**: 예측 및 이상치 탐지 결과 저장
- **시스템 로그**: 애플리케이션 로그 및 이벤트 저장

### 2. Redis (캐싱)
- **세션 관리**: 사용자 세션 정보
- **캐싱**: 자주 사용되는 데이터 캐싱
- **메시지 큐**: 서비스 간 통신

## 🔒 보안 설정

### 1. 네트워크 보안
- **Nginx 리버스 프록시**: SSL/TLS 종료 및 로드 밸런싱
- **방화벽 설정**: 필요한 포트만 개방
- **CORS 설정**: API 접근 제어

### 2. 데이터 보안
- **데이터 암호화**: 민감한 데이터 암호화 저장
- **접근 제어**: 사용자 권한 기반 접근 제어
- **감사 로그**: 모든 활동 기록 및 추적

## 🚨 문제 해결

### 1. 서비스 시작 실패
```bash
# 로그 확인
docker-compose logs [service-name]

# 서비스 재시작
docker-compose restart [service-name]

# 전체 재시작
docker-compose down && docker-compose up -d
```

### 2. 메모리 부족
```bash
# 메모리 사용량 확인
docker stats

# 불필요한 컨테이너 정리
docker system prune -a
```

### 3. 포트 충돌
```bash
# 포트 사용 확인
netstat -tulpn | grep :5000

# docker-compose.yml에서 포트 변경
```

## 📚 추가 리소스

- **API 문서**: http://localhost:5001/api/v1/health
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **시스템 로그**: `docker-compose logs -f`

## 🤝 지원 및 문의

- **이슈 리포팅**: GitHub Issues
- **문서**: README.md 및 각 서비스별 문서
- **커뮤니티**: 개발자 포럼 및 채팅

---

**🎉 Multi-MCP Time Series Analysis System을 사용해주셔서 감사합니다!**


