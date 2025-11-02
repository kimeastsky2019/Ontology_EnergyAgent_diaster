#!/bin/bash

# Energy Analysis MCP - Docker 배포 스크립트
# 사용법: ./deploy_docker.sh [production|development]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 환경 설정
ENVIRONMENT=${1:-development}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info "🐳 Energy Analysis MCP Docker 배포를 시작합니다 (환경: $ENVIRONMENT)..."

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    log_error "Docker가 설치되지 않았습니다. 먼저 Docker를 설치하세요."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose가 설치되지 않았습니다. 먼저 Docker Compose를 설치하세요."
    exit 1
fi

# Docker Compose 파일 생성
log_info "Docker Compose 파일을 생성합니다..."
cat > docker-compose.yml << EOF
version: '3.8'

services:
  energy-analysis-mcp:
    build: .
    container_name: energy-analysis-mcp
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=$ENVIRONMENT
      - DEBUG=$([ "$ENVIRONMENT" = "development" ] && echo "True" || echo "False")
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env
    networks:
      - energy-network
    depends_on:
      - nginx

  nginx:
    image: nginx:alpine
    container_name: energy-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./react-weather-app/build:/usr/share/nginx/html/weather
      - ./integration/static:/usr/share/nginx/html/static
    networks:
      - energy-network
    depends_on:
      - energy-analysis-mcp

  react-app:
    build:
      context: ./react-weather-app
      dockerfile: Dockerfile
    container_name: energy-react
    restart: unless-stopped
    volumes:
      - ./react-weather-app/build:/usr/share/nginx/html/weather
    networks:
      - energy-network

networks:
  energy-network:
    driver: bridge

volumes:
  data:
  logs:
EOF

# Dockerfile 생성
log_info "Dockerfile을 생성합니다..."
cat > Dockerfile << EOF
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 데이터 및 로그 디렉토리 생성
RUN mkdir -p data/cache logs

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# 애플리케이션 실행
CMD ["python", "server.py"]
EOF

# React 앱 Dockerfile 생성
log_info "React 앱 Dockerfile을 생성합니다..."
cat > react-weather-app/Dockerfile << EOF
FROM node:16-alpine as build

WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm ci --only=production

# 소스 코드 복사
COPY . .

# 앱 빌드
RUN npm run build

# Nginx를 사용한 정적 파일 서빙
FROM nginx:alpine

# 빌드된 파일을 nginx 디렉토리로 복사
COPY --from=build /app/build /usr/share/nginx/html

# Nginx 설정
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF

# React 앱 Nginx 설정
log_info "React 앱 Nginx 설정을 생성합니다..."
cat > react-weather-app/nginx.conf << EOF
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # React Router 지원
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # 정적 파일 캐싱
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 프록시
    location /api/ {
        proxy_pass http://energy-analysis-mcp:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 기존 컨테이너 정리
log_info "기존 컨테이너를 정리합니다..."
docker-compose down 2>/dev/null || true
docker system prune -f

# 이미지 빌드
log_info "Docker 이미지를 빌드합니다..."
docker-compose build

# 컨테이너 시작
log_info "컨테이너를 시작합니다..."
docker-compose up -d

# 컨테이너 상태 확인
log_info "컨테이너 상태를 확인합니다..."
docker-compose ps

# 헬스체크
log_info "헬스체크를 수행합니다..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "헬스체크 성공!"
        break
    else
        log_warning "헬스체크 시도 $i/10..."
        sleep 5
    fi
done

# 로그 확인
log_info "컨테이너 로그를 확인합니다..."
docker-compose logs --tail=20

log_success "🎉 Docker 배포가 완료되었습니다!"
log_info "접속 URL:"
echo "  - 메인 대시보드: http://localhost:8000"
echo "  - React 앱: http://localhost/weather"
echo "  - Nginx: http://localhost"

log_info "Docker 관리 명령어:"
echo "  - 상태 확인: docker-compose ps"
echo "  - 로그 확인: docker-compose logs -f"
echo "  - 서비스 중지: docker-compose down"
echo "  - 서비스 시작: docker-compose up -d"
echo "  - 재빌드: docker-compose up --build -d"
