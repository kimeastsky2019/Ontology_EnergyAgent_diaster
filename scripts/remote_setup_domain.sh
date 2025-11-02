#!/bin/bash
# 원격에서 도메인 설정 스크립트 실행

set -e

SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/metal/energy-platform"
DOMAIN="damcp.gngmeta.com"

echo "🌐 도메인 설정 시작..."
echo "도메인: ${DOMAIN}"
echo "서버: ${SERVER_USER}@${SERVER_IP}"
echo ""

# 서버에 스크립트 전송
echo "📤 도메인 설정 스크립트 전송 중..."
scp -o StrictHostKeyChecking=no scripts/setup_domain.sh gcp-energy:${REMOTE_DIR}/ 2>/dev/null || \
    scp -o StrictHostKeyChecking=no -i google_compute_engine.ppk scripts/setup_domain.sh metal@34.47.89.217:${REMOTE_DIR}/ 2>/dev/null || {
    echo "⚠️  스크립트 전송 실패. 수동으로 실행하세요."
    echo ""
    echo "수동 실행 방법:"
    echo "1. ssh metal@${SERVER_IP}"
    echo "2. cd ${REMOTE_DIR}"
    echo "3. bash scripts/setup_domain.sh"
    exit 1
}

# 서버에서 도메인 설정 실행
echo "⚙️  서버에서 도메인 설정 실행 중..."
ssh -o StrictHostKeyChecking=no gcp-energy << ENDSSH || ssh -o StrictHostKeyChecking=no -i google_compute_engine.ppk metal@34.47.89.217 << ENDSSH
cd ${REMOTE_DIR}

# Nginx 설치
if ! command -v nginx &> /dev/null; then
    echo "📦 Nginx 설치 중..."
    sudo apt-get update
    sudo apt-get install -y nginx certbot python3-certbot-nginx
fi

# Nginx 설정 파일 생성
echo "📝 Nginx 설정 파일 생성 중..."
sudo tee /etc/nginx/sites-available/${DOMAIN} > /dev/null << 'NGINXCONF'
# Backend API (damcp.gngmeta.com/api)
server {
    listen 80;
    server_name damcp.gngmeta.com;

    # API 프록시
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Ready check
    location /ready {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # API 문서
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Redoc
    location /redoc {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Frontend (나머지 모든 요청)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
NGINXCONF

# Nginx 설정 활성화
sudo ln -sf /etc/nginx/sites-available/${DOMAIN} /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx 설정 테스트
echo "🔍 Nginx 설정 테스트 중..."
sudo nginx -t

# Nginx 재시작
echo "🔄 Nginx 재시작 중..."
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "✅ Nginx 설정 완료"
ENDSSH

echo ""
echo "✅ 도메인 설정 완료!"
echo ""
echo "다음 단계:"
echo "1. DNS 설정 확인 (damcp.gngmeta.com → ${SERVER_IP})"
echo "2. SSL 인증서 발급:"
echo "   ssh ${SERVER_USER}@${SERVER_IP}"
echo "   sudo certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --email admin@gngmeta.com"
echo ""
echo "확인:"
echo "  http://${DOMAIN}"
echo "  http://${DOMAIN}/health"
echo "  http://${DOMAIN}/docs"

