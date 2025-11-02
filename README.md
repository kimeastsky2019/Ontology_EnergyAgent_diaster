# AI 재난 대응형 에너지 공유 플랫폼

AI-Orchestrated Disaster-Resilient Energy Sharing Network

## 프로젝트 개요

재난 발생 시 일본-한국-EU 간 AI 기반 실시간 에너지 재분배 시스템을 구축하는 플랫폼입니다.

### 핵심 기능

- 🚨 **재난 상황 분석**: AI 기반 재난 영향 범위 분석
- ⚡ **에너지 수급 분석**: 실시간 에너지 생산/소비 모니터링
- 🔄 **자동 재분배**: P2P 에너지 거래 자동 매칭
- 🤖 **AI 오케스트레이터**: Multi-Agent 기반 의사결정
- 📊 **실시간 모니터링**: 대시보드 및 시각화
- 🌐 **온톨로지 통합**: 지식 그래프 기반 추론

## 기술 스택

### Backend
- FastAPI (Python)
- PostgreSQL + TimescaleDB
- Redis
- Apache Kafka
- Apache Jena (RDF Store)

### Frontend
- React 18 + TypeScript
- Material-UI
- Mapbox GL JS
- Socket.io

### AI/ML
- PyTorch Geometric (GNN)
- LangChain (LLM)
- OpenAI / Anthropic Claude

### Infrastructure
- Docker & Docker Compose
- Kubernetes
- Prometheus + Grafana

## 빠른 시작

### 사전 요구사항

```bash
- Docker & Docker Compose
- Node.js 20+ LTS
- Python 3.11+
- Git
```

### 설치 및 실행

```bash
# 1. 환경 변수 설정
cp .env.example .env

# 2. Docker 네트워크 생성
docker network create energy-net

# 3. 인프라 서비스 시작
docker-compose -f docker-compose.dev.yml up -d

# 4. Backend 설정
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload

# 5. Frontend 설정
cd frontend
npm install
npm run dev
```

### 서비스 접속 정보

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Kafka: localhost:9092
- Grafana: http://localhost:3001

## 프로젝트 구조

```
energy-orchestrator-platform/
├── backend/           # FastAPI Backend
├── frontend/          # React Frontend
├── iot-service/       # IoT Data Collection
├── ontology/          # Ontology & Knowledge Graph
├── ml-models/         # ML Models & Training
├── infrastructure/    # IaC & Deployment
├── scripts/           # Utility Scripts
└── docs/             # Documentation
```

## 개발 로드맵

- [x] Phase 1: MVP (3개월) - 기본 기능 프로토타입
- [ ] Phase 2: Core Features (3개월) - 주요 기능 완성
- [ ] Phase 3: AI Orchestrator (4개월) - AI 에이전트 시스템
- [ ] Phase 4: Advanced Ontology (3개월) - 고급 온톨로지
- [ ] Phase 5: Integration & Testing (3개월) - 통합 테스트
- [ ] Phase 6: Pilot Deployment (2개월) - 파일럿 배포

## 문서

- [시작 가이드](./README_시작가이드.md)
- [플랫폼 개발 가이드](./플랫폼_개발_가이드.md)
- [프로젝트 구조](./프로젝트_구조_및_Quick_Start.md)
- [핵심 기능 코드 샘플](./핵심기능_구현_코드샘플.md)

## 라이선스

MIT License

## 컨소시엄

- 🇰🇷 **G&G International** (한국) - AI 에이전트, 프로젝트 리드
- 🇪🇺 **Beia Consult** (루마니아) - IoT 하드웨어, 통신
- 🇯🇵 **일본 파트너** (필요) - 재난 온톨로지, 테스트베드




