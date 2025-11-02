#!/bin/bash
# 도메인 설정 명령어 (서버에서 직접 실행)

# 이 스크립트의 모든 명령어를 서버에 접속하여 실행하세요:
# ssh metal@34.47.89.217

DOMAIN="damcp.gngmeta.com"
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo "🌐 도메인 설정: ${DOMAIN}"
echo ""
echo "=========================================="
echo "# 1. Nginx 및 Certbot 설치"
echo "=========================================="
echo "sudo apt-get update"
echo "sudo apt-get install -y nginx certbot python3-certbot-nginx"
echo ""
echo "=========================================="
echo "# 2. Nginx 설정 파일 생성"
echo "=========================================="
cat << 'EOF'
sudo tee /etc/nginx/sites-available/damcp.gngmeta.com > /dev/null << 'NGINXEOF'
# Backend API 프록시
server {
    listen 80;
    server_name damcp.gngmeta.com;

    # Let's Encrypt 인증용
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # API 프록시 (/api)
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
    }

    # API 문서
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # Redoc
    location /redoc {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # Frontend (나머지)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
}
NGINXEOF
EOF

echo ""
echo "=========================================="
echo "# 3. Nginx 설정 활성화"
echo "=========================================="
echo "sudo ln -sf /etc/nginx/sites-available/damcp.gngmeta.com /etc/nginx/sites-enabled/"
echo "sudo rm -f /etc/nginx/sites-enabled/default"
echo "sudo nginx -t"
echo "sudo systemctl restart nginx"
echo "sudo systemctl enable nginx"
echo ""
echo "=========================================="
echo "# 4. SSL 인증서 발급 (Let's Encrypt)"
echo "=========================================="
echo "sudo certbot --nginx -d damcp.gngmeta.com \\"
echo "    --non-interactive \\"
echo "    --agree-tos \\"
echo "    --email admin@gngmeta.com \\"
echo "    --redirect"
echo ""
echo "=========================================="
echo "# 5. 방화벽 확인 (GCP 콘솔)"
echo "=========================================="
echo "다음 포트가 열려있는지 확인:"
echo "  - 80 (HTTP)"
echo "  - 443 (HTTPS)"
echo ""
echo "GCP 콘솔: https://console.cloud.google.com/compute/firewalls"
echo ""
echo "=========================================="
echo "✅ 완료!"
echo "=========================================="
echo ""
echo "확인:"
echo "  http://damcp.gngmeta.com/health"
echo "  https://damcp.gngmeta.com/docs (SSL 발급 후)"

