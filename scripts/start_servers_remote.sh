#!/bin/bash
# 원격 서버에서 서버 시작 스크립트

# 사용자가 제공한 SSH 명령어 사용
SSH_CMD='ssh -i google_compute_engine.pem -o "IdentitiesOnly=yes" -o "ServerAliveInterval=60" -o "StrictHostKeyChecking=no" metal@34.47.89.217'

echo "🚀 원격 서버에서 서버 시작"
echo "========================="
echo ""

# 서버에 접속하여 실행
$SSH_CMD << 'ENDSSH'
cd /home/metal/energy-platform || exit 1

echo "📂 현재 디렉토리: $(pwd)"
echo ""

# 1. 코드 업데이트
echo "1️⃣  코드 업데이트 중..."
if [ -d ".git" ]; then
    git pull origin main || echo "⚠️  Git pull 실패 (계속 진행)"
else
    echo "⚠️  Git 저장소 없음"
fi

echo ""
echo "2️⃣  프론트엔드 서버 시작..."
cd /home/metal/energy-platform

# 기존 프로세스 확인
FRONTEND_PID=$(pgrep -f "vite.*3000" || echo "")
if [ -n "$FRONTEND_PID" ]; then
    echo "✅ 프론트엔드 서버 이미 실행 중 (PID: $FRONTEND_PID)"
else
    echo "프론트엔드 서버 시작 중..."
    
    if [ -f "scripts/start_frontend.sh" ]; then
        echo "스크립트 사용: scripts/start_frontend.sh"
        bash scripts/start_frontend.sh dev
    else
        echo "직접 시작..."
        cd frontend
        if [ ! -d "node_modules" ]; then
            echo "의존성 설치 중..."
            npm install
        fi
        nohup npm run dev > /tmp/frontend.log 2>&1 &
        sleep 3
        cd ..
    fi
    
    # 시작 확인
    sleep 2
    FRONTEND_PID=$(pgrep -f "vite.*3000" || echo "")
    if [ -n "$FRONTEND_PID" ]; then
        echo "✅ 프론트엔드 서버 시작 성공 (PID: $FRONTEND_PID)"
    else
        echo "❌ 프론트엔드 서버 시작 실패"
        echo "로그 확인:"
        tail -20 /tmp/frontend.log 2>/dev/null || echo "로그 파일 없음"
    fi
fi

echo ""
echo "3️⃣  백엔드 서버 확인..."
BACKEND_PID=$(pgrep -f "uvicorn.*8000" || echo "")
if [ -n "$BACKEND_PID" ]; then
    echo "✅ 백엔드 서버 실행 중 (PID: $BACKEND_PID)"
else
    echo "⚠️  백엔드 서버 미실행"
    if [ -f "scripts/start_backend.sh" ]; then
        echo "백엔드 서버 시작하려면: bash scripts/start_backend.sh"
    fi
fi

echo ""
echo "4️⃣  서버 상태 확인..."
echo "포트 확인:"
echo "  프론트엔드 (3000):"
lsof -i :3000 2>/dev/null | head -3 || netstat -tlnp 2>/dev/null | grep :3000 || echo "    리스닝 중인 프로세스 없음"
echo ""
echo "  백엔드 (8000):"
lsof -i :8000 2>/dev/null | head -3 || netstat -tlnp 2>/dev/null | grep :8000 || echo "    리스닝 중인 프로세스 없음"

echo ""
echo "5️⃣  연결 테스트..."
echo "프론트엔드:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000 || echo "000")
echo "  HTTP 코드: $HTTP_CODE"
[ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ] && echo "  ✅ 프론트엔드 서버 응답 중" || echo "  ❌ 프론트엔드 서버 응답 없음"

echo ""
echo "백엔드:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health || echo "000")
echo "  HTTP 코드: $HTTP_CODE"
[ "$HTTP_CODE" = "200" ] && echo "  ✅ 백엔드 서버 응답 중" || echo "  ⚠️  백엔드 서버 응답 없음"

echo ""
echo "✅ 완료!"
echo ""
echo "확인:"
echo "  https://damcp.gngmeta.com/disaster"
ENDSSH

