#!/bin/bash
# 도메인 설정 스크립트 (서버에서 실행)

set -e

DOMAIN="damcp.gngmeta.com"
SERVER_IP="34.47.89.217"
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo "🌐 도메인 설정 시작..."
echo "도메인: ${DOMAIN}"
echo "서버 IP: ${SERVER_IP}"
echo ""

# 이 스크립트는 서버에서 실행해야 합니다
echo "⚠️  이 스크립트는 서버에서 실행하세요:"
echo "  ssh metal@${SERVER_IP}"
echo "  cd /home/metal/energy-platform"
echo "  bash scripts/setup_domain.sh"
echo ""

cat << 'ENDOFSCRIPT'
# 서버에서 실행할 명령어:

# 1. Nginx 설치
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# 2. Nginx 설정 파일 생성
sudo tee /etc/nginx/sites-available/damcp.gngmeta.com > /dev/null << 'EOF'
# Backend API (damcp.gngmeta.com/api)
server {
    listen 80;
    server_name damcp.gngmeta.com;

    # API 프록시
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
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Ready check
    location /ready {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API 문서
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Redoc
    location /redoc {
        proxy_pass http://127.0.0.1:8000;
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
    }
}
EOF

# 3. Nginx 설정 활성화
sudo ln -sf /etc/nginx/sites-available/damcp.gngmeta.com /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 4. Nginx 설정 테스트
sudo nginx -t

# 5. Nginx 재시작
sudo systemctl restart nginx
sudo systemctl enable nginx

# 6. SSL 인증서 발급 (Let's Encrypt)
echo ""
echo "🔒 SSL 인증서 발급 중..."
sudo certbot --nginx -d damcp.gngmeta.com --non-interactive --agree-tos --email admin@gngmeta.com --redirect

# 7. 방화벽 설정 확인
echo ""
echo "🔥 방화벽 설정 확인..."
echo "다음 포트가 열려있는지 확인하세요:"
echo "  - 80 (HTTP)"
echo "  - 443 (HTTPS)"
echo ""
echo "GCP 콘솔에서 방화벽 규칙 확인:"
echo "  https://console.cloud.google.com/compute/firewalls"

echo ""
echo "✅ 도메인 설정 완료!"
echo ""
echo "확인:"
echo "  http://damcp.gngmeta.com"
echo "  https://damcp.gngmeta.com"
echo "  https://damcp.gngmeta.com/api/health"
echo "  https://damcp.gngmeta.com/docs"

ENDOFSCRIPT

