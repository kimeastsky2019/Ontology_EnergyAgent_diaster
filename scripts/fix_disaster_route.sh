#!/bin/bash
# 서버에서 /disaster 경로 문제 해결 스크립트

set -e

DOMAIN="damcp.gngmeta.com"
NGINX_CONFIG="/etc/nginx/sites-available/${DOMAIN}"
PROJECT_DIR="/home/metal/energy-platform"

echo "🔧 /disaster 경로 문제 해결"
echo ""

# 서버에서 실행해야 함
if [ "$USER" != "metal" ]; then
    echo "⚠️  이 스크립트는 서버(metal@34.47.89.217)에서 실행하세요:"
    echo "  ssh metal@34.47.89.217"
    echo "  cd ${PROJECT_DIR}"
    echo "  bash scripts/fix_disaster_route.sh"
    exit 1
fi

echo "1️⃣  코드 업데이트 중..."
cd "$PROJECT_DIR" || exit 1
git pull origin main || echo "⚠️  Git pull 실패 (이미 최신이거나 권한 문제)"

echo ""
echo "2️⃣  Nginx 설정 업데이트 중..."
if [ -f "scripts/nginx_config.conf" ]; then
    sudo cp scripts/nginx_config.conf "$NGINX_CONFIG"
    echo "✅ Nginx 설정 파일 업데이트 완료"
else
    echo "❌ scripts/nginx_config.conf 파일을 찾을 수 없습니다"
    exit 1
fi

echo ""
echo "3️⃣  Nginx 설정 테스트 중..."
if sudo nginx -t; then
    echo "✅ Nginx 설정 검증 성공"
else
    echo "❌ Nginx 설정 검증 실패"
    exit 1
fi

echo ""
echo "4️⃣  Nginx 재시작 중..."
sudo systemctl reload nginx
echo "✅ Nginx 재시작 완료"

echo ""
echo "5️⃣  프론트엔드 서버 확인 중..."
if curl -s http://127.0.0.1:3000 > /dev/null; then
    echo "✅ 프론트엔드 서버 실행 중 (포트 3000)"
else
    echo "⚠️  프론트엔드 서버가 실행되지 않음 (포트 3000)"
    echo "   프론트엔드를 시작하세요:"
    echo "   cd ${PROJECT_DIR}/frontend && npm run dev"
fi

echo ""
echo "6️⃣  백엔드 서버 확인 중..."
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ 백엔드 서버 실행 중 (포트 8000)"
else
    echo "⚠️  백엔드 서버가 실행되지 않음 (포트 8000)"
    echo "   백엔드를 시작하세요:"
    echo "   cd ${PROJECT_DIR}/backend && uvicorn src.main:app --host 0.0.0.0 --port 8000"
fi

echo ""
echo "✅ 설정 완료!"
echo ""
echo "확인:"
echo "  https://${DOMAIN}/disaster"
echo "  https://${DOMAIN}/api/health"
echo ""
echo "Nginx 로그 확인:"
echo "  sudo tail -f /var/log/nginx/damcp-access.log"
echo "  sudo tail -f /var/log/nginx/damcp-error.log"

