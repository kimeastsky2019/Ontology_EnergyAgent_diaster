#!/bin/bash
# 서버에서 /disaster 경로 설정 업데이트

set -e

DOMAIN="damcp.gngmeta.com"
NGINX_CONFIG="/etc/nginx/sites-available/${DOMAIN}"

echo "🌐 /disaster 경로 설정 업데이트"
echo ""

# 이 스크립트는 서버에서 실행해야 합니다
if [ ! -f "$NGINX_CONFIG" ]; then
    echo "❌ Nginx 설정 파일을 찾을 수 없습니다: $NGINX_CONFIG"
    echo ""
    echo "먼저 도메인 설정을 완료하세요:"
    echo "  bash scripts/setup_domain.sh"
    exit 1
fi

echo "📝 Nginx 설정 파일 확인 중..."
echo "설정 파일: $NGINX_CONFIG"
echo ""

# /disaster 경로가 이미 있는지 확인
if grep -q "location /disaster" "$NGINX_CONFIG" 2>/dev/null; then
    echo "✅ /disaster 경로가 이미 설정되어 있습니다."
    echo ""
    echo "설정을 다시 적용하려면:"
    echo "  sudo nginx -t"
    echo "  sudo systemctl reload nginx"
else
    echo "📝 /disaster 경로 추가 중..."
    echo ""
    echo "Nginx 설정 파일에 다음 내용을 추가하세요:"
    echo ""
    cat << 'EOF'
    # Disaster 페이지 (/disaster)
    location /disaster {
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
        proxy_connect_timeout 75s;
    }
EOF
    echo ""
    echo "또는 전체 설정 파일을 업데이트:"
    echo "  cd /home/metal/energy-platform"
    echo "  sudo cp scripts/nginx_config.conf $NGINX_CONFIG"
    echo "  sudo nginx -t"
    echo "  sudo systemctl reload nginx"
fi

echo ""
echo "✅ 설정 완료!"
echo ""
echo "확인:"
echo "  https://${DOMAIN}/disaster"

