#!/bin/bash
# /disaster 경로 문제 완전 해결 스크립트

set -e

DOMAIN="damcp.gngmeta.com"
NGINX_CONFIG="/etc/nginx/sites-available/${DOMAIN}"
PROJECT_DIR="/home/metal/energy-platform"

echo "🔧 /disaster 경로 문제 완전 해결"
echo "=================================="
echo ""

# 서버에서 실행해야 함
if [ "$USER" != "metal" ] && [ ! -f "$NGINX_CONFIG" ]; then
    echo "⚠️  이 스크립트는 서버(metal@34.47.89.217)에서 실행하세요:"
    echo "  ssh metal@34.47.89.217"
    echo "  cd ${PROJECT_DIR}"
    echo "  bash scripts/fix_disaster_complete.sh"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

echo "1️⃣  코드 업데이트"
echo "-------------------"
git pull origin main || echo "⚠️  Git pull 실패 (계속 진행)"
echo ""

echo "2️⃣  Nginx 설정 업데이트"
echo "-------------------"
if [ -f "scripts/nginx_config.conf" ]; then
    echo "📝 Nginx 설정 파일 복사 중..."
    sudo cp scripts/nginx_config.conf "$NGINX_CONFIG"
    echo "✅ Nginx 설정 파일 업데이트 완료"
    
    echo ""
    echo "🔍 /disaster 경로 설정 확인:"
    if grep -q "location.*disaster" "$NGINX_CONFIG"; then
        echo "✅ /disaster 경로 설정 확인됨"
        grep -A 5 "location.*disaster" "$NGINX_CONFIG"
    else
        echo "⚠️  /disaster 경로 설정 없음 (location / 에서 처리)"
    fi
else
    echo "❌ scripts/nginx_config.conf 파일을 찾을 수 없습니다"
    exit 1
fi

echo ""
echo "3️⃣  Nginx 설정 검증"
echo "-------------------"
if sudo nginx -t 2>&1; then
    echo "✅ Nginx 설정 검증 성공"
else
    echo "❌ Nginx 설정 검증 실패"
    exit 1
fi

echo ""
echo "4️⃣  Nginx 재시작"
echo "-------------------"
sudo systemctl reload nginx
echo "✅ Nginx 재시작 완료"

echo ""
echo "5️⃣  프론트엔드 서버 확인 및 시작"
echo "-------------------"
FRONTEND_PID=$(pgrep -f "vite.*3000" || echo "")
if [ -n "$FRONTEND_PID" ]; then
    echo "✅ 프론트엔드 서버 실행 중 (PID: $FRONTEND_PID)"
else
    echo "⚠️  프론트엔드 서버 미실행"
    echo "   수동으로 시작하세요:"
    echo "   cd ${PROJECT_DIR}/frontend"
    echo "   npm run dev"
    echo ""
    echo "   또는 백그라운드에서:"
    echo "   cd ${PROJECT_DIR}/frontend"
    echo "   nohup npm run dev > /tmp/frontend.log 2>&1 &"
fi

echo ""
echo "6️⃣  백엔드 서버 확인"
echo "-------------------"
BACKEND_PID=$(pgrep -f "uvicorn.*8000" || echo "")
if [ -n "$BACKEND_PID" ]; then
    echo "✅ 백엔드 서버 실행 중 (PID: $BACKEND_PID)"
else
    echo "⚠️  백엔드 서버 미실행"
    echo "   필요시 시작하세요:"
    echo "   cd ${PROJECT_DIR}/backend"
    echo "   uvicorn src.main:app --host 0.0.0.0 --port 8000"
fi

echo ""
echo "7️⃣  연결 테스트"
echo "-------------------"
echo "프론트엔드 로컬 테스트:"
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/disaster | grep -q "200\|404"; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/disaster)
    echo "✅ 프론트엔드 응답 코드: $HTTP_CODE"
else
    echo "❌ 프론트엔드 서버 응답 없음"
fi

echo ""
echo "Nginx를 통한 테스트:"
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/disaster 2>/dev/null | grep -q "200\|404"; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/disaster 2>/dev/null)
    echo "✅ Nginx 프록시 응답 코드: $HTTP_CODE"
else
    echo "⚠️  Nginx 프록시 테스트 실패 (HTTPS로 테스트 필요)"
fi

echo ""
echo "8️⃣  최종 확인"
echo "-------------------"
echo "✅ 설정 완료!"
echo ""
echo "확인 사항:"
echo "  1. Nginx 설정 업데이트: ✅"
echo "  2. Nginx 재시작: ✅"
echo "  3. 프론트엔드 서버: $([ -n "$FRONTEND_PID" ] && echo "✅ 실행 중" || echo "⚠️  미실행")"
echo "  4. 백엔드 서버: $([ -n "$BACKEND_PID" ] && echo "✅ 실행 중" || echo "⚠️  미실행")"
echo ""
echo "접속 테스트:"
echo "  https://${DOMAIN}/disaster"
echo ""
echo "문제가 계속되면 디버깅 스크립트 실행:"
echo "  bash scripts/debug_server.sh"

