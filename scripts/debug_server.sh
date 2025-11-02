#!/bin/bash
# 서버 디버깅 스크립트

set -e

DOMAIN="damcp.gngmeta.com"
NGINX_CONFIG="/etc/nginx/sites-available/${DOMAIN}"

echo "🔍 서버 상태 디버깅"
echo "==================="
echo ""

# 서버에서 실행해야 함
if [ ! -f "$NGINX_CONFIG" ]; then
    echo "⚠️  이 스크립트는 서버(metal@34.47.89.217)에서 실행하세요"
    exit 1
fi

echo "1️⃣  Nginx 설정 확인"
echo "--------------------"
if [ -f "$NGINX_CONFIG" ]; then
    echo "✅ Nginx 설정 파일 존재: $NGINX_CONFIG"
    echo ""
    echo "📍 /disaster 경로 설정 확인:"
    if grep -q "location.*disaster" "$NGINX_CONFIG"; then
        echo "✅ /disaster 경로 설정 발견"
        grep -A 10 "location.*disaster" "$NGINX_CONFIG" | head -15
    else
        echo "❌ /disaster 경로 설정 없음"
        echo "📍 기본 location / 설정:"
        grep -A 10 "^    location / {" "$NGINX_CONFIG" | head -15
    fi
else
    echo "❌ Nginx 설정 파일 없음: $NGINX_CONFIG"
fi

echo ""
echo "2️⃣  Nginx 설정 검증"
echo "--------------------"
if sudo nginx -t 2>&1; then
    echo "✅ Nginx 설정 유효"
else
    echo "❌ Nginx 설정 오류"
fi

echo ""
echo "3️⃣  서버 프로세스 확인"
echo "--------------------"
echo "프론트엔드 (포트 3000):"
if netstat -tlnp 2>/dev/null | grep -q ":3000 " || ss -tlnp 2>/dev/null | grep -q ":3000 "; then
    echo "✅ 프론트엔드 서버 실행 중"
    netstat -tlnp 2>/dev/null | grep ":3000 " || ss -tlnp 2>/dev/null | grep ":3000 "
else
    echo "❌ 프론트엔드 서버 미실행"
fi

echo ""
echo "백엔드 (포트 8000):"
if netstat -tlnp 2>/dev/null | grep -q ":8000 " || ss -tlnp 2>/dev/null | grep -q ":8000 "; then
    echo "✅ 백엔드 서버 실행 중"
    netstat -tlnp 2>/dev/null | grep ":8000 " || ss -tlnp 2>/dev/null | grep ":8000 "
else
    echo "❌ 백엔드 서버 미실행"
fi

echo ""
echo "4️⃣  로컬 접속 테스트"
echo "--------------------"
echo "프론트엔드 로컬 테스트:"
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/disaster | grep -q "200\|404"; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/disaster)
    echo "✅ 프론트엔드 응답 코드: $HTTP_CODE"
    if [ "$HTTP_CODE" = "404" ]; then
        echo "   ⚠️  404 응답 - React Router가 처리하지 못함"
    fi
else
    echo "❌ 프론트엔드 서버 응답 없음"
fi

echo ""
echo "백엔드 로컬 테스트:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 백엔드 응답 코드: $HTTP_CODE"
else
    echo "❌ 백엔드 응답 코드: $HTTP_CODE"
fi

echo ""
echo "5️⃣  Nginx 로그 확인 (최근 10줄)"
echo "--------------------"
if [ -f "/var/log/nginx/damcp-access.log" ]; then
    echo "Access 로그:"
    sudo tail -10 /var/log/nginx/damcp-access.log | grep -E "(disaster|404|500)" || echo "관련 로그 없음"
else
    echo "⚠️  Access 로그 파일 없음"
fi

echo ""
if [ -f "/var/log/nginx/damcp-error.log" ]; then
    echo "Error 로그:"
    sudo tail -10 /var/log/nginx/damcp-error.log || echo "에러 없음"
else
    echo "⚠️  Error 로그 파일 없음"
fi

echo ""
echo "6️⃣  실제 라우팅 테스트"
echo "--------------------"
echo "백엔드 /disaster 직접 테스트:"
BACKEND_RESPONSE=$(curl -s http://127.0.0.1:8000/disaster || echo "")
if echo "$BACKEND_RESPONSE" | grep -q "Not Found\|detail"; then
    echo "❌ 백엔드가 /disaster 경로를 처리함 (잘못됨)"
    echo "   응답: $(echo "$BACKEND_RESPONSE" | head -1)"
else
    echo "✅ 백엔드가 /disaster 경로를 처리하지 않음 (정상)"
fi

echo ""
echo "프론트엔드 /disaster 직접 테스트:"
FRONTEND_RESPONSE=$(curl -s http://127.0.0.1:3000/disaster || echo "")
if echo "$FRONTEND_RESPONSE" | grep -q "html\|<!DOCTYPE"; then
    echo "✅ 프론트엔드가 /disaster 경로를 HTML로 응답 (정상)"
elif echo "$FRONTEND_RESPONSE" | grep -q "Not Found"; then
    echo "❌ 프론트엔드가 404 응답"
else
    echo "⚠️  프론트엔드 응답 확인 필요"
    echo "   응답 시작: $(echo "$FRONTEND_RESPONSE" | head -1 | cut -c1-50)"
fi

echo ""
echo "7️⃣  해결 방법"
echo "--------------------"
echo "1. Nginx 설정 업데이트:"
echo "   sudo cp /home/metal/energy-platform/scripts/nginx_config.conf $NGINX_CONFIG"
echo "   sudo nginx -t"
echo "   sudo systemctl reload nginx"
echo ""
echo "2. 프론트엔드 서버 시작:"
echo "   cd /home/metal/energy-platform/frontend"
echo "   npm run dev"
echo ""
echo "3. 백엔드 서버 시작 (필요시):"
echo "   cd /home/metal/energy-platform/backend"
echo "   uvicorn src.main:app --host 0.0.0.0 --port 8000"

