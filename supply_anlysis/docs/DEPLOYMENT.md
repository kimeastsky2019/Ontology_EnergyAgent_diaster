# 배포 가이드

## 개발 환경

### 사전 요구사항
- Docker 20.10+
- Docker Compose 2.0+
- Git

### 빠른 시작
```bash
# 저장소 클론
git clone <repository-url>
cd energy-dashboard

# 시작 스크립트 실행
./start.sh
```

## 프로덕션 환경

### 1. 환경 변수 설정

`.env` 파일을 생성하고 프로덕션 설정을 입력합니다:

```bash
# Database - 강력한 비밀번호 사용
DATABASE_URL=postgresql://prod_user:STRONG_PASSWORD@db:5432/energy_prod_db

# Redis
REDIS_URL=redis://redis:6379

# Weather API - 실제 API 키 사용
WEATHER_API_KEY=your_production_api_key

# Security
SECRET_KEY=your_very_long_random_secret_key
JWT_SECRET=another_very_long_random_secret

# CORS - 실제 도메인 지정
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Docker Compose 프로덕션 설정

`docker-compose.prod.yml` 파일을 생성합니다:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - energy-network

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    networks:
      - energy-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - db
      - redis
    networks:
      - energy-network

  ai-agent:
    build:
      context: ./ai-agent
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
    depends_on:
      - db
      - redis
    networks:
      - energy-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        REACT_APP_API_URL: https://api.yourdomain.com
    restart: always
    networks:
      - energy-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
      - ai-agent
    networks:
      - energy-network

networks:
  energy-network:
    driver: bridge

volumes:
  postgres_data:
```

### 3. Nginx 설정

`nginx/nginx.conf` 파일을 생성합니다:

```nginx
upstream backend {
    server backend:8000;
}

upstream ai-agent {
    server ai-agent:8001;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # AI Agent API
    location /ai {
        proxy_pass http://ai-agent/api/ai;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. SSL 인증서

Let's Encrypt를 사용한 무료 SSL 인증서:

```bash
# Certbot 설치
sudo apt-get update
sudo apt-get install certbot

# 인증서 발급
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 인증서 복사
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

### 5. 프로덕션 빌드 및 배포

```bash
# 프로덕션 환경으로 빌드 및 실행
docker-compose -f docker-compose.prod.yml up -d --build

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

## 클라우드 배포

### AWS 배포

#### 1. EC2 인스턴스 설정
```bash
# 권장 사양
# - Instance Type: t3.medium (2 vCPU, 4GB RAM)
# - Storage: 30GB SSD
# - OS: Ubuntu 22.04 LTS

# Docker 설치
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER
```

#### 2. RDS (PostgreSQL) 설정
- Engine: PostgreSQL 15
- Instance Class: db.t3.micro
- Storage: 20GB

#### 3. ElastiCache (Redis) 설정
- Engine: Redis 7
- Node Type: cache.t3.micro

#### 4. 보안 그룹 설정
```
Inbound Rules:
- Port 80 (HTTP) - 0.0.0.0/0
- Port 443 (HTTPS) - 0.0.0.0/0
- Port 22 (SSH) - Your IP
```

### Google Cloud Platform 배포

#### 1. Cloud Run 사용
```bash
# Frontend 배포
gcloud run deploy energy-frontend \
  --source ./frontend \
  --region asia-northeast3 \
  --allow-unauthenticated

# Backend 배포
gcloud run deploy energy-backend \
  --source ./backend \
  --region asia-northeast3 \
  --set-env-vars DATABASE_URL=$DATABASE_URL

# AI Agent 배포
gcloud run deploy energy-ai-agent \
  --source ./ai-agent \
  --region asia-northeast3 \
  --set-env-vars DATABASE_URL=$DATABASE_URL
```

#### 2. Cloud SQL (PostgreSQL)
```bash
gcloud sql instances create energy-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-northeast3
```

### Azure 배포

#### 1. Container Instances
```bash
# 리소스 그룹 생성
az group create --name energy-dashboard --location koreacentral

# 컨테이너 인스턴스 생성
az container create \
  --resource-group energy-dashboard \
  --name energy-backend \
  --image your-registry/energy-backend \
  --dns-name-label energy-backend \
  --ports 8000
```

## 모니터링 및 로깅

### Prometheus + Grafana

`docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 로그 수집

```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f ai-agent

# 로그를 파일로 저장
docker-compose logs > logs/app.log
```

## 백업 및 복구

### 데이터베이스 백업

```bash
# 백업
docker exec energy-db pg_dump -U energy_user energy_db > backup.sql

# 복구
docker exec -i energy-db psql -U energy_user energy_db < backup.sql
```

### 전체 시스템 백업

```bash
# Docker 볼륨 백업
docker run --rm -v postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data
```

## 성능 최적화

### 1. 프론트엔드 최적화
- Code splitting
- Lazy loading
- CDN 사용
- 이미지 최적화

### 2. 백엔드 최적화
- 데이터베이스 인덱싱
- Redis 캐싱
- Connection pooling
- 비동기 처리

### 3. AI Agent 최적화
- 모델 경량화
- 배치 처리
- GPU 사용 (선택)

## 보안 체크리스트

- [ ] 강력한 비밀번호 사용
- [ ] HTTPS 적용
- [ ] CORS 설정
- [ ] Rate limiting 구현
- [ ] API 인증 구현
- [ ] SQL Injection 방지
- [ ] XSS 방지
- [ ] 정기적인 보안 업데이트
- [ ] 로그 모니터링
- [ ] 백업 자동화

## 트러블슈팅

### 컨테이너가 시작되지 않을 때
```bash
# 로그 확인
docker-compose logs

# 컨테이너 재시작
docker-compose restart

# 완전히 재시작
docker-compose down
docker-compose up -d --build
```

### 데이터베이스 연결 오류
```bash
# 데이터베이스 상태 확인
docker exec energy-db pg_isready

# 연결 테스트
docker exec energy-db psql -U energy_user -d energy_db -c "SELECT 1"
```

### 성능 저하
```bash
# 리소스 사용량 확인
docker stats

# 컨테이너 리소스 제한 설정
docker-compose.yml에 추가:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

## 업데이트 절차

```bash
# 1. 코드 업데이트
git pull origin main

# 2. 백업
./backup.sh

# 3. 재배포
docker-compose down
docker-compose up -d --build

# 4. 헬스 체크
curl http://localhost:8000/health
```

## 지원

문제가 발생하면:
1. 로그 확인
2. GitHub Issues 검색
3. 새 Issue 생성
