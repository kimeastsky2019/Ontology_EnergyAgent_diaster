# 🚀 빠른 시작 가이드

이 문서는 프로젝트를 빠르게 시작하는 방법을 안내합니다.

## 사전 요구사항

다음 소프트웨어가 설치되어 있어야 합니다:

- Docker & Docker Compose
- Node.js 20+ LTS
- Python 3.11+
- Git

## 1단계: 환경 변수 설정

```bash
# 환경 변수 파일 복사
cp .env.example .env

# 필요에 따라 .env 파일 편집
# DATABASE_URL, SECRET_KEY 등 중요 값 설정
```

## 2단계: Docker 네트워크 생성

```bash
docker network create energy-net
```

## 3단계: 인프라 서비스 시작

```bash
# Docker Compose로 인프라 서비스 시작
docker-compose -f docker-compose.dev.yml up -d

# 서비스 상태 확인
docker-compose -f docker-compose.dev.yml ps

# 로그 확인
docker-compose -f docker-compose.dev.yml logs -f
```

### 서비스 접속 정보

- PostgreSQL: localhost:5432 (user: postgres, password: password, db: energy_db)
- Redis: localhost:6379
- Kafka: localhost:9092
- MQTT: localhost:1883
- Jena Fuseki: http://localhost:3030 (admin password: admin)
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin password: admin)

## 4단계: Backend 설정

```bash
cd backend

# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션 (Alembic 사용)
# alembic upgrade head

# 또는 직접 테이블 생성 (개발용)
python -c "from src.database import Base, engine; Base.metadata.create_all(bind=engine)"

# 개발 서버 실행
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API는 http://localhost:8000 에서 실행됩니다.

API 문서는 http://localhost:8000/docs 에서 확인할 수 있습니다.

## 5단계: Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

Frontend는 http://localhost:3000 에서 실행됩니다.

## 6단계: 기본 사용자 생성 및 테스트

### API를 사용한 사용자 등록

```bash
# 사용자 등록
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
  }'

# 로그인
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

### 에너지 자산 생성

```bash
# 토큰으로 자산 생성 (TOKEN을 위에서 받은 토큰으로 교체)
curl -X POST "http://localhost:8000/api/v1/assets/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Solar Farm 1",
    "type": "solar",
    "capacity_kw": 500
  }'
```

## 문제 해결

### 데이터베이스 연결 오류

```bash
# PostgreSQL 컨테이너 상태 확인
docker-compose -f docker-compose.dev.yml ps db

# 로그 확인
docker-compose -f docker-compose.dev.yml logs db

# 재시작
docker-compose -f docker-compose.dev.yml restart db
```

### 포트 충돌

`.env` 파일이나 `docker-compose.dev.yml`에서 포트 번호를 변경하세요.

### Python 패키지 설치 오류

```bash
# 가상환경 활성화 확인
which python  # venv/bin/python 경로여야 함

# pip 업그레이드
pip install --upgrade pip setuptools wheel
```

## 다음 단계

1. [프로젝트 구조 가이드](./프로젝트_구조_및_Quick_Start.md) 참조
2. [핵심 기능 구현 코드 샘플](./핵심기능_구현_코드샘플.md) 확인
3. [플랫폼 개발 가이드](./플랫폼_개발_가이드.md) 상세 학습

## 유용한 명령어

```bash
# 전체 서비스 중지
docker-compose -f docker-compose.dev.yml down

# 볼륨까지 삭제 (데이터 삭제됨)
docker-compose -f docker-compose.dev.yml down -v

# 특정 서비스만 재시작
docker-compose -f docker-compose.dev.yml restart backend

# 데이터베이스 백업
docker exec energy_db pg_dump -U postgres energy_db > backup.sql

# 데이터베이스 복원
docker exec -i energy_db psql -U postgres energy_db < backup.sql
```





