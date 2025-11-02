# 프로젝트 구조 및 Quick Start 가이드

---

## 📁 프로젝트 디렉토리 구조

```
energy-orchestrator-platform/
├── README.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── .gitignore
│
├── frontend/                          # React Frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── public/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   ├── EnergyMap/
│   │   │   ├── DisasterAlert/
│   │   │   └── Monitoring/
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Assets.tsx
│   │   │   ├── Disasters.tsx
│   │   │   └── Analytics.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── websocket.ts
│   │   │   └── auth.ts
│   │   ├── store/
│   │   │   ├── store.ts
│   │   │   ├── slices/
│   │   │   │   ├── authSlice.ts
│   │   │   │   ├── energySlice.ts
│   │   │   │   └── disasterSlice.ts
│   │   ├── types/
│   │   ├── utils/
│   │   └── styles/
│   └── Dockerfile
│
├── backend/                           # FastAPI Backend
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── src/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── assets.py
│   │   │   │   ├── devices.py
│   │   │   │   ├── energy.py
│   │   │   │   ├── disasters.py
│   │   │   │   ├── ontology.py
│   │   │   │   ├── orchestrator.py
│   │   │   │   └── trading.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── asset.py
│   │   │   ├── device.py
│   │   │   ├── disaster.py
│   │   │   └── transaction.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── asset.py
│   │   │   ├── energy.py
│   │   │   └── disaster.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── energy_service.py
│   │   │   ├── iot_service.py
│   │   │   ├── prediction_service.py
│   │   │   ├── ontology_service.py
│   │   │   ├── orchestrator_service.py
│   │   │   └── disaster_service.py
│   │   ├── ml/
│   │   │   ├── gnn_model.py
│   │   │   ├── forecasting.py
│   │   │   └── anomaly_detection.py
│   │   ├── agents/
│   │   │   ├── base_agent.py
│   │   │   ├── disaster_analyzer.py
│   │   │   ├── energy_analyzer.py
│   │   │   ├── grid_analyzer.py
│   │   │   ├── decision_maker.py
│   │   │   └── executor.py
│   │   ├── utils/
│   │   │   ├── security.py
│   │   │   ├── mqtt_client.py
│   │   │   └── kafka_producer.py
│   │   └── tests/
│   │       ├── test_api/
│   │       ├── test_services/
│   │       └── test_agents/
│   └── Dockerfile
│
├── iot-service/                       # IoT Data Collection Service
│   ├── package.json
│   ├── src/
│   │   ├── index.ts
│   │   ├── mqtt-handler.ts
│   │   ├── data-processor.ts
│   │   └── kafka-publisher.ts
│   └── Dockerfile
│
├── ontology/                          # Ontology & Knowledge Graph
│   ├── schemas/
│   │   ├── disaster_ontology.ttl
│   │   ├── energy_ontology.ttl
│   │   └── geo_ontology.ttl
│   ├── scripts/
│   │   ├── load_ontology.py
│   │   └── sparql_queries.py
│   └── README.md
│
├── ml-models/                         # ML Models & Training
│   ├── requirements.txt
│   ├── notebooks/
│   │   ├── gnn_training.ipynb
│   │   └── forecast_analysis.ipynb
│   ├── training/
│   │   ├── train_gnn.py
│   │   └── train_forecast.py
│   ├── models/
│   │   └── saved_models/
│   └── data/
│       └── datasets/
│
├── infrastructure/                    # Infrastructure as Code
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── kubernetes/
│   │   ├── namespaces/
│   │   ├── deployments/
│   │   ├── services/
│   │   ├── ingress/
│   │   └── secrets/
│   └── helm/
│       └── energy-platform/
│           ├── Chart.yaml
│           ├── values.yaml
│           └── templates/
│
├── monitoring/                        # Monitoring & Logging
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alerts.yml
│   ├── grafana/
│   │   └── dashboards/
│   └── elasticsearch/
│       └── logstash/
│
├── scripts/                           # Utility Scripts
│   ├── init-db.sh
│   ├── seed-data.py
│   ├── backup.sh
│   └── deploy.sh
│
└── docs/                             # Documentation
    ├── API.md
    ├── Architecture.md
    ├── Deployment.md
    └── UserGuide.md
```

---

## 🚀 Quick Start Guide

### 사전 요구사항

```bash
# 필수 설치
- Docker & Docker Compose
- Node.js 20+ LTS
- Python 3.11+
- Git
```

### 1. 프로젝트 클론 및 초기 설정

```bash
# 프로젝트 클론
git clone https://github.com/your-org/energy-orchestrator-platform.git
cd energy-orchestrator-platform

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정

# Docker 네트워크 생성
docker network create energy-net
```

### 2. 개발 환경 실행

```bash
# 전체 서비스 시작
docker-compose -f docker-compose.dev.yml up -d

# 로그 확인
docker-compose -f docker-compose.dev.yml logs -f

# 특정 서비스만 시작
docker-compose -f docker-compose.dev.yml up -d db redis
```

### 3. Backend 개발 환경 설정

```bash
cd backend

# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
alembic upgrade head

# 초기 데이터 시딩
python scripts/seed_data.py

# 개발 서버 실행
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend 개발 환경 설정

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 브라우저에서 http://localhost:3000 접속
```

### 5. 서비스 접속 정보

```
Frontend:          http://localhost:3000
Backend API:       http://localhost:8000
API Docs:          http://localhost:8000/docs
PostgreSQL:        localhost:5432
Redis:             localhost:6379
MQTT Broker:       localhost:1883
Kafka:             localhost:9092
Grafana:           http://localhost:3001
```

---

## 🔧 주요 설정 파일

### .env.example

```bash
# Application
APP_NAME=Energy Orchestrator Platform
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/energy_db
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# MQTT
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_IOT_DATA=iot-data
KAFKA_TOPIC_DISASTERS=disasters

# External APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
WEATHER_API_KEY=your-weather-api-key
NIED_API_URL=https://api.nied.go.jp

# Ontology
JENA_FUSEKI_URL=http://localhost:3030
RDF_DATABASE=energy_ontology

# Monitoring
SENTRY_DSN=
GRAFANA_URL=http://localhost:3001
```

### docker-compose.dev.yml

```yaml
version: '3.8'

services:
  db:
    image: timescale/timescaledb:latest-pg15
    container_name: energy_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: energy_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - energy-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: energy_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - energy-net
    command: redis-server --appendonly yes

  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    container_name: energy_zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"
    networks:
      - energy-net

  kafka:
    image: confluentinc/cp-kafka:latest
    container_name: energy_kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    networks:
      - energy-net

  mqtt:
    image: eclipse-mosquitto:latest
    container_name: energy_mqtt
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./monitoring/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - mqtt_data:/mosquitto/data
      - mqtt_logs:/mosquitto/log
    networks:
      - energy-net

  jena:
    image: stain/jena-fuseki
    container_name: energy_jena
    ports:
      - "3030:3030"
    environment:
      ADMIN_PASSWORD: admin
      JVM_ARGS: "-Xmx2g"
    volumes:
      - jena_data:/fuseki
    networks:
      - energy-net

  prometheus:
    image: prom/prometheus:latest
    container_name: energy_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - energy-net

  grafana:
    image: grafana/grafana:latest
    container_name: energy_grafana
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_INSTALL_PLUGINS: grafana-worldmap-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - energy-net

volumes:
  postgres_data:
  redis_data:
  mqtt_data:
  mqtt_logs:
  jena_data:
  prometheus_data:
  grafana_data:

networks:
  energy-net:
    external: true
```

---

## 📝 기본 코드 예제

### Backend: main.py

```python
# backend/src/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from src.config import settings
from src.database import engine
from src.models import Base
from src.api.v1 import (
    auth, users, assets, devices, 
    energy, disasters, orchestrator
)

# Logging 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    # 테이블 생성 (개발용, 프로덕션에서는 Alembic 사용)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

@app.get("/ready")
async def readiness_check():
    # DB 연결 체크 등
    return {"status": "ready"}

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# API 라우터 등록
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])
app.include_router(energy.router, prefix="/api/v1/energy", tags=["Energy"])
app.include_router(disasters.router, prefix="/api/v1/disasters", tags=["Disasters"])
app.include_router(orchestrator.router, prefix="/api/v1/orchestrator", tags=["Orchestrator"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

### Backend: config.py

```python
# backend/src/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Energy Orchestrator Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    
    # MQTT
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_IOT_DATA: str = "iot-data"
    
    # External APIs
    OPENAI_API_KEY: str = ""
    WEATHER_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### Frontend: App.tsx

```typescript
// frontend/src/App.tsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, CssBaseline } from '@mui/material';

import { store } from './store/store';
import { theme } from './styles/theme';
import Layout from './components/Layout';
import Home from './pages/Home';
import Assets from './pages/Assets';
import Disasters from './pages/Disasters';
import Analytics from './pages/Analytics';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Router>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route element={<ProtectedRoute />}>
                <Route element={<Layout />}>
                  <Route path="/" element={<Home />} />
                  <Route path="/assets" element={<Assets />} />
                  <Route path="/disasters" element={<Disasters />} />
                  <Route path="/analytics" element={<Analytics />} />
                </Route>
              </Route>
            </Routes>
          </Router>
        </ThemeProvider>
      </QueryClientProvider>
    </Provider>
  );
}

export default App;
```

---

## 🧪 테스트 실행

### Backend Tests

```bash
cd backend

# 단위 테스트
pytest src/tests/ -v

# 커버리지와 함께
pytest src/tests/ --cov=src --cov-report=html

# 특정 테스트만
pytest src/tests/test_api/test_auth.py -v
```

### Frontend Tests

```bash
cd frontend

# 단위 테스트
npm test

# 커버리지
npm test -- --coverage

# E2E 테스트 (Playwright)
npm run test:e2e
```

---

## 📦 빌드 및 배포

### 프로덕션 빌드

```bash
# Backend Docker 이미지
cd backend
docker build -t energy-backend:latest .

# Frontend Docker 이미지
cd frontend
docker build -t energy-frontend:latest .

# 전체 서비스 빌드
docker-compose build
```

### Kubernetes 배포

```bash
# Namespace 생성
kubectl create namespace energy-platform

# Secrets 생성
kubectl create secret generic db-secret \
  --from-literal=url=$DATABASE_URL \
  -n energy-platform

# 배포
kubectl apply -f infrastructure/kubernetes/deployments/
kubectl apply -f infrastructure/kubernetes/services/
kubectl apply -f infrastructure/kubernetes/ingress/

# 상태 확인
kubectl get pods -n energy-platform
kubectl get services -n energy-platform
```

---

## 🔍 유용한 명령어

```bash
# Docker 로그 확인
docker-compose logs -f [service-name]

# 컨테이너 접속
docker exec -it energy_backend bash

# 데이터베이스 접속
docker exec -it energy_db psql -U postgres -d energy_db

# Redis CLI
docker exec -it energy_redis redis-cli

# Kafka 토픽 확인
docker exec energy_kafka kafka-topics --list --bootstrap-server localhost:9092

# 서비스 재시작
docker-compose restart [service-name]

# 전체 재시작
docker-compose down && docker-compose up -d
```

---

## 📚 추가 리소스

- [API 문서](http://localhost:8000/docs)
- [Architecture 가이드](./docs/Architecture.md)
- [개발 가이드](./docs/Development.md)
- [배포 가이드](./docs/Deployment.md)

---

이 구조를 기반으로 프로젝트를 시작하실 수 있습니다!
각 파일의 상세 구현이 필요하시면 말씀해주세요.
