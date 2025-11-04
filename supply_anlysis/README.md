# 🔋 Energy Dashboard & AI Agent System

에너지 공급 모니터링, 생산량 분석, 이상징후 감지 및 고장 진단 AI Agent 시스템

## 🎨 주요 특징

- **주황색 톤 디자인**: 에너지를 상징하는 따뜻한 주황색 테마
- **실시간 모니터링**: 에너지 생산량 실시간 추적
- **AI 이상징후 감지**: 머신러닝 기반 이상 패턴 탐지
- **고장 진단**: 자동화된 설비 고장 예측 및 진단
- **날씨 연동**: 날씨 데이터와 에너지 생산량 상관관계 분석

## 🚀 빠른 시작

```bash
# 전체 시스템 실행
docker-compose up -d

# 접속
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 📊 대시보드 화면

### 왼쪽 패널
- 시설 정보 카드 (건물+차량 일러스트, 현재 전력)
- 날씨 정보 카드 (현재 날씨, 7일 예보)

### 오른쪽 패널
- 실시간 전력 생산 그래프 (Area Chart)
- 일일 에너지 생산 바 차트
- AI 이상징후 알림 패널

## 🤖 AI Agent 기능

1. **이상징후 감지**: Isolation Forest 알고리즘
2. **고장 진단**: 시계열 분석 기반 예측 정비
3. **생산량 예측**: LSTM 기반 예측

## 🛠️ 기술 스택

- Frontend: React 18 + Material-UI 5 + Chart.js
- Backend: FastAPI + PostgreSQL
- AI: scikit-learn + TensorFlow
- Infrastructure: Docker + Docker Compose
