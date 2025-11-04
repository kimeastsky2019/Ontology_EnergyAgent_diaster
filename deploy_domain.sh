#!/bin/bash
# damcp.gngmeta.com 도메인 배포 통합 스크립트

set -e

# 설정
SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/$SERVER_USER/energy-platform"
GIT_REPO_HTTPS="https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git"
DOMAIN="damcp.gngmeta.com"
PROJECT_DIR="/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"
PEM_FILE="$PROJECT_DIR/google_compute_engine.pem"
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo "🚀 damcp.gngmeta.com 도메인 배포 시작..."
echo "도메인: ${DOMAIN}"
echo "서버: ${SERVER_USER}@${SERVER_IP}"
echo ""

# PEM 파일 확인
if [ -f "$PEM_FILE" ]; then
    chmod 600 "$PEM_FILE"
    SSH_OPTS="-i $PEM_FILE -o IdentitiesOnly=yes -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -F /dev/null"
    echo "✅ PEM 파일 사용"
else
    echo "⚠️  PEM 파일 없음. SSH 키를 사용합니다."
    SSH_OPTS="-o ServerAliveInterval=60 -o StrictHostKeyChecking=no"
fi

# 서버 연결 테스트
echo "🔌 서버 연결 테스트 중..."
if ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} "echo '연결 성공'" 2>/dev/null; then
    echo "✅ 서버 연결 확인"
else
    echo "❌ 서버 연결 실패"
    echo "다음 명령어로 수동 연결을 시도하세요:"
    if [ -f "$PEM_FILE" ]; then
        echo "ssh -i $PEM_FILE -o IdentitiesOnly=yes ${SERVER_USER}@${SERVER_IP}"
    else
        echo "ssh ${SERVER_USER}@${SERVER_IP}"
    fi
    exit 1
fi

# 1. 서버 환경 설정 및 배포
echo ""
echo "📦 서버 환경 설정 및 코드 배포 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

# 필요한 패키지 설치
echo "📦 필수 패키지 설치 중..."
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq git python3 python3-pip python3-venv curl nginx certbot python3-certbot-nginx

# Node.js 설치
if ! command -v node &> /dev/null; then
    echo "📦 Node.js 설치 중..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - > /dev/null 2>&1
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq nodejs
fi

# 프로젝트 디렉토리 생성
mkdir -p ${REMOTE_DIR}
cd ${REMOTE_DIR}

# Git repository 설정
if [ -d ".git" ]; then
    echo "📥 Git repository 업데이트 중..."
    git fetch origin > /dev/null 2>&1
    git reset --hard origin/main || git reset --hard origin/master
    git clean -fd
else
    echo "📥 Git repository clone 중..."
    git clone ${GIT_REPO_HTTPS} . > /dev/null 2>&1
fi

echo "✅ 코드 배포 완료"
ENDSSH

# 2. Nginx 설정 파일 생성
echo ""
echo "🌐 Nginx 설정 파일 생성 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

DOMAIN="damcp.gngmeta.com"
BACKEND_PORT=8000
FRONTEND_PORT=3000

sudo tee /etc/nginx/sites-available/${DOMAIN} > /dev/null << 'NGINXEOF'
# HTTP 서버 (SSL 인증서 발급 전)
server {
    listen 80;
    server_name damcp.gngmeta.com;

    # Let's Encrypt 인증용
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Backend API 프록시
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

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        access_log off;
    }

    # Ready check
    location /ready {
        proxy_pass http://127.0.0.1:8000/ready;
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

    # Frontend (나머지 모든 요청)
    location / {
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
    }
}
NGINXEOF

# Nginx 설정 활성화
sudo ln -sf /etc/nginx/sites-available/${DOMAIN} /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "✅ Nginx 설정 완료"
ENDSSH

# 3. 백엔드 설정 및 설치
echo ""
echo "⚙️  백엔드 설정 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

cd ${REMOTE_DIR}/backend

# Python 가상환경 설정
if [ ! -d "venv" ]; then
    echo "🐍 Python 가상환경 생성 중..."
    python3 -m venv venv
fi

source venv/bin/activate

# 의존성 설치
if [ -f "requirements.txt" ]; then
    echo "📦 백엔드 의존성 설치 중..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
fi

echo "✅ 백엔드 설정 완료"
ENDSSH

# 4. 프론트엔드 설정 및 빌드
echo ""
echo "⚙️  프론트엔드 설정 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

cd ${REMOTE_DIR}/frontend

# 의존성 설치
if [ -f "package.json" ]; then
    echo "📦 프론트엔드 의존성 설치 중..."
    npm install > /dev/null 2>&1
    
    # 빌드
    echo "🏗️  프론트엔드 빌드 중..."
    npm run build > /dev/null 2>&1 || echo "⚠️  빌드 경고 (계속 진행)"
fi

echo "✅ 프론트엔드 설정 완료"
ENDSSH

# 5. SSL 인증서 발급 (선택사항)
echo ""
echo "🔒 SSL 인증서 발급 중..."
echo "⚠️  이 단계는 DNS가 설정된 후에만 성공합니다."
echo ""

# SSL 발급 시도 (실패해도 계속 진행)
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH || true
sudo certbot --nginx -d ${DOMAIN} \
    --non-interactive \
    --agree-tos \
    --email admin@gngmeta.com \
    --redirect \
    --quiet || echo "⚠️  SSL 인증서 발급 실패 (DNS 설정 확인 필요)"
ENDSSH

# 6. 서비스 시작 스크립트 생성
echo ""
echo "🚀 서비스 시작 스크립트 생성 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

REMOTE_DIR="/home/metal/energy-platform"

# 백엔드 서비스 스크립트
sudo tee /etc/systemd/system/energy-backend.service > /dev/null << 'EOF'
[Unit]
Description=Energy Platform Backend API
After=network.target

[Service]
Type=simple
User=metal
WorkingDirectory=/home/metal/energy-platform/backend
Environment="PATH=/home/metal/energy-platform/backend/venv/bin"
ExecStart=/home/metal/energy-platform/backend/venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 프론트엔드 서비스 스크립트
sudo tee /etc/systemd/system/energy-frontend.service > /dev/null << 'EOF'
[Unit]
Description=Energy Platform Frontend
After=network.target

[Service]
Type=simple
User=metal
WorkingDirectory=/home/metal/energy-platform/frontend
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/npm run preview -- --host 127.0.0.1 --port 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable energy-backend energy-frontend
sudo systemctl restart energy-backend energy-frontend || echo "⚠️  서비스 시작 실패 (수동 확인 필요)"

echo "✅ 서비스 스크립트 생성 완료"
ENDSSH

echo ""
echo "🎉 배포 완료!"
echo ""
echo "📋 배포 정보:"
echo "  도메인: https://${DOMAIN}"
echo "  서버: ${SERVER_USER}@${SERVER_IP}"
echo "  위치: ${REMOTE_DIR}"
echo ""
echo "🌐 접속 확인:"
echo "  https://${DOMAIN}"
echo "  https://${DOMAIN}/api/health"
echo "  https://${DOMAIN}/docs"
echo ""
echo "📊 서비스 상태 확인:"
echo "  ssh ${SERVER_USER}@${SERVER_IP}"
echo "  sudo systemctl status energy-backend"
echo "  sudo systemctl status energy-frontend"
echo "  sudo systemctl status nginx"
echo ""
echo "⚠️  참고 사항:"
echo "  1. DNS가 설정되지 않은 경우 SSL 인증서 발급이 실패할 수 있습니다."
echo "  2. DNS 전파에는 최대 24-48시간이 소요될 수 있습니다."
echo "  3. SSL 인증서 발급이 실패한 경우, DNS 설정 확인 후 다음 명령 실행:"
echo "     ssh ${SERVER_USER}@${SERVER_IP}"
echo "     sudo certbot --nginx -d ${DOMAIN}"
echo ""


