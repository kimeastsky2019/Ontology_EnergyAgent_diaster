#!/bin/bash
# 서버 복구 스크립트
# damcp.gngmeta.com 서버 문제 해결

set -e

# 설정
SERVER_IP="34.47.89.217"
SERVER_USER="metal"
PEM_FILE="google_compute_engine.pem"
DOMAIN="damcp.gngmeta.com"
REMOTE_DIR="/home/metal/energy-platform"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# PEM 파일 확인 및 SSH 옵션 설정
if [ -f "$PEM_FILE" ]; then
    chmod 600 "$PEM_FILE"
    SSH_OPTS="-i $PEM_FILE -o IdentitiesOnly=yes -o ServerAliveInterval=60 -o StrictHostKeyChecking=no"
    log_info "PEM 파일 사용: $PEM_FILE"
else
    SSH_OPTS="-o ServerAliveInterval=60 -o StrictHostKeyChecking=no"
    log_warning "PEM 파일 없음. 기본 SSH 키 사용"
fi

echo ""
echo "=========================================="
echo "🔧 서버 복구 시작: ${DOMAIN}"
echo "=========================================="
echo ""

# 서버 연결 테스트
log_info "서버 연결 테스트..."
if ! ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} "echo '연결 성공'" 2>/dev/null; then
    log_error "서버 연결 실패"
    exit 1
fi
log_success "서버 연결 성공"

# 1. 백엔드 서비스 확인 및 시작
echo ""
log_info "1️⃣ 백엔드 서비스 확인 및 시작..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

# 백엔드 디렉토리 확인
if [ ! -d "${REMOTE_DIR}/backend" ]; then
    echo "❌ 백엔드 디렉토리 없음: ${REMOTE_DIR}/backend"
    exit 1
fi

cd ${REMOTE_DIR}/backend

# 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
    echo "📦 Python 가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화 및 의존성 설치
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
fi

# systemd 서비스 파일 확인
if [ ! -f "/etc/systemd/system/energy-backend.service" ]; then
    echo "📝 systemd 서비스 파일 생성 중..."
    sudo tee /etc/systemd/system/energy-backend.service > /dev/null << 'EOF'
[Unit]
Description=Energy Platform Backend API
After=network.target

[Service]
Type=simple
User=metal
WorkingDirectory=${REMOTE_DIR}/backend
Environment="PATH=${REMOTE_DIR}/backend/venv/bin"
ExecStart=${REMOTE_DIR}/backend/venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
fi

# 서비스 시작
echo "🚀 백엔드 서비스 시작 중..."
sudo systemctl enable energy-backend
sudo systemctl restart energy-backend
sleep 2

if systemctl is-active --quiet energy-backend; then
    echo "✅ 백엔드 서비스 시작 성공"
else
    echo "❌ 백엔드 서비스 시작 실패"
    sudo journalctl -u energy-backend -n 10 --no-pager
    exit 1
fi
ENDSSH

# 2. 프론트엔드 서비스 확인 및 시작
echo ""
log_info "2️⃣ 프론트엔드 서비스 확인 및 시작..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

# 프론트엔드 디렉토리 확인
if [ ! -d "${REMOTE_DIR}/frontend" ]; then
    echo "⚠️  프론트엔드 디렉토리 없음: ${REMOTE_DIR}/frontend"
    echo "   server_cloud.py만 사용하는 경우 정상입니다."
    exit 0
fi

cd ${REMOTE_DIR}/frontend

# 의존성 설치
if [ -f "package.json" ]; then
    echo "📦 프론트엔드 의존성 설치 중..."
    npm install > /dev/null 2>&1
    
    # 빌드
    if [ -f "package.json" ] && grep -q "build" package.json; then
        echo "🏗️  프론트엔드 빌드 중..."
        npm run build > /dev/null 2>&1 || echo "⚠️  빌드 경고 (계속 진행)"
    fi
fi

# systemd 서비스 파일 확인
if [ ! -f "/etc/systemd/system/energy-frontend.service" ]; then
    echo "📝 systemd 서비스 파일 생성 중..."
    sudo tee /etc/systemd/system/energy-frontend.service > /dev/null << 'EOF'
[Unit]
Description=Energy Platform Frontend
After=network.target

[Service]
Type=simple
User=metal
WorkingDirectory=${REMOTE_DIR}/frontend
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/npm run preview -- --host 127.0.0.1 --port 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
fi

# 서비스 시작
echo "🚀 프론트엔드 서비스 시작 중..."
sudo systemctl enable energy-frontend
sudo systemctl restart energy-frontend
sleep 2

if systemctl is-active --quiet energy-frontend; then
    echo "✅ 프론트엔드 서비스 시작 성공"
else
    echo "⚠️  프론트엔드 서비스 시작 실패 (서버가 server_cloud.py만 사용할 수 있음)"
    sudo journalctl -u energy-frontend -n 10 --no-pager || true
fi
ENDSSH

# 3. Nginx 설정 확인 및 시작
echo ""
log_info "3️⃣ Nginx 설정 확인 및 시작..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

DOMAIN="damcp.gngmeta.com"
REMOTE_DIR="/home/metal/energy-platform"

# Nginx 설치 확인
if ! command -v nginx &> /dev/null; then
    echo "📦 Nginx 설치 중..."
    sudo apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq nginx
fi

# Nginx 설정 파일 생성
if [ ! -f "/etc/nginx/sites-available/${DOMAIN}" ]; then
    echo "📝 Nginx 설정 파일 생성 중..."
    sudo tee /etc/nginx/sites-available/${DOMAIN} > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name damcp.gngmeta.com;

    # Let's Encrypt 인증용
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        access_log off;
    }

    # API 문서
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Redoc
    location /redoc {
        proxy_pass http://127.0.0.1:8000/redoc;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    # Frontend (프론트엔드가 있는 경우)
    location / {
        # 프론트엔드가 있으면 프론트엔드로, 없으면 백엔드로
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        
        # 프론트엔드가 없으면 백엔드로 폴백
        error_page 502 = @backend;
    }
    
    location @backend {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF
fi

# Nginx 설정 활성화
sudo ln -sf /etc/nginx/sites-available/${DOMAIN} /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx 설정 검증
if sudo nginx -t 2>&1 | grep -q "successful"; then
    echo "✅ Nginx 설정 유효"
else
    echo "❌ Nginx 설정 오류"
    sudo nginx -t 2>&1
    exit 1
fi

# Nginx 시작
echo "🚀 Nginx 시작 중..."
sudo systemctl enable nginx
sudo systemctl restart nginx
sleep 2

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx 시작 성공"
else
    echo "❌ Nginx 시작 실패"
    sudo journalctl -u nginx -n 10 --no-pager
    exit 1
fi
ENDSSH

# 4. 최종 상태 확인
echo ""
log_info "4️⃣ 최종 상태 확인..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo "=== 서비스 상태 ==="
echo "Backend:"
systemctl is-active energy-backend && echo "✅" || echo "❌"

echo "Frontend:"
systemctl is-active energy-frontend 2>/dev/null && echo "✅" || echo "⚠️  (선택사항)"

echo "Nginx:"
systemctl is-active nginx && echo "✅" || echo "❌"

echo ""
echo "=== 포트 리스닝 ==="
ss -tlnp 2>/dev/null | grep -E ":(80|443|8000|3000) " || netstat -tlnp 2>/dev/null | grep -E ":(80|443|8000|3000) "

echo ""
echo "=== 로컬 접속 테스트 ==="
echo "Backend health:"
curl -s http://127.0.0.1:8000/health | head -1 || echo "❌"

echo "Nginx:"
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1 || echo "❌"
ENDSSH

# 5. 도메인 접속 테스트
echo ""
log_info "5️⃣ 도메인 접속 테스트..."
sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${DOMAIN} 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    log_success "도메인 응답: $HTTP_CODE"
else
    log_warning "도메인 응답: $HTTP_CODE (DNS 전파 대기 필요 가능)"
fi

echo ""
echo "=========================================="
log_success "✅ 서버 복구 완료"
echo "=========================================="
echo ""
echo "📋 접속 정보:"
echo "  HTTP: http://${DOMAIN}"
echo "  Health: http://${DOMAIN}/health"
echo "  Docs: http://${DOMAIN}/docs"
echo ""
echo "🔍 서비스 상태 확인:"
echo "  ssh ${SERVER_USER}@${SERVER_IP}"
echo "  sudo systemctl status energy-backend"
echo "  sudo systemctl status nginx"
echo ""

