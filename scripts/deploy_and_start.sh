#!/bin/bash
# 서버 배포 및 서버 시작 스크립트

set -e

SERVER_USER="metal"
SERVER_HOST="34.47.89.217"
PROJECT_DIR="/home/metal/energy-platform"
KEY_FILE="google_compute_engine.pem"

echo "🚀 서버 배포 및 시작"
echo "===================="
echo ""

# PEM 파일 확인
if [ ! -f "$KEY_FILE" ]; then
    echo "⚠️  $KEY_FILE 파일을 찾을 수 없습니다"
    echo ""
    echo "PPK 파일을 PEM으로 변환하거나 PEM 파일 위치를 확인하세요"
    echo ""
    echo "PPK를 PEM으로 변환 (puttygen 필요):"
    echo "  puttygen google_compute_engine.ppk -O private-openssh -o google_compute_engine.pem"
    echo ""
    echo "또는 PEM 파일이 다른 위치에 있다면 경로를 수정하세요"
    exit 1
fi

# 키 파일 권한 설정
chmod 600 "$KEY_FILE"
echo "✅ SSH 키 권한 설정 완료"

# SSH 옵션
SSH_OPTS="-i $KEY_FILE -o IdentitiesOnly=yes -o ServerAliveInterval=60 -o StrictHostKeyChecking=no"

echo ""
echo "1️⃣  서버 연결 테스트..."
if ssh $SSH_OPTS ${SERVER_USER}@${SERVER_HOST} "echo '서버 연결 성공'" 2>&1; then
    echo "✅ 서버 연결 확인"
else
    echo "❌ 서버 연결 실패"
    exit 1
fi

echo ""
echo "2️⃣  코드 업데이트..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
cd /home/metal/energy-platform
echo "현재 디렉토리: $(pwd)"
echo ""
if [ -d ".git" ]; then
    echo "Git 저장소 확인됨"
    git pull origin main || echo "⚠️  Git pull 실패 (계속 진행)"
else
    echo "⚠️  Git 저장소 없음"
fi
echo ""
ENDSSH

echo ""
echo "3️⃣  프론트엔드 서버 시작..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
cd /home/metal/energy-platform
echo "프론트엔드 서버 상태 확인 중..."

# 기존 프로세스 확인
FRONTEND_PID=$(pgrep -f "vite.*3000" || echo "")
if [ -n "$FRONTEND_PID" ]; then
    echo "✅ 프론트엔드 서버 이미 실행 중 (PID: $FRONTEND_PID)"
else
    echo "프론트엔드 서버 시작 중..."
    
    # 스크립트가 있으면 사용
    if [ -f "scripts/start_frontend.sh" ]; then
        bash scripts/start_frontend.sh dev
    else
        # 직접 시작
        cd frontend
        if [ ! -d "node_modules" ]; then
            echo "의존성 설치 중..."
            npm install
        fi
        nohup npm run dev > /tmp/frontend.log 2>&1 &
        sleep 2
        if pgrep -f "vite.*3000" > /dev/null; then
            echo "✅ 프론트엔드 서버 시작 성공"
        else
            echo "❌ 프론트엔드 서버 시작 실패"
            cat /tmp/frontend.log | tail -20
        fi
    fi
fi
ENDSSH

echo ""
echo "4️⃣  백엔드 서버 확인..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
cd /home/metal/energy-platform
BACKEND_PID=$(pgrep -f "uvicorn.*8000" || echo "")
if [ -n "$BACKEND_PID" ]; then
    echo "✅ 백엔드 서버 실행 중 (PID: $BACKEND_PID)"
else
    echo "⚠️  백엔드 서버 미실행"
    echo "   시작하려면: bash scripts/start_backend.sh"
fi
ENDSSH

echo ""
echo "5️⃣  서버 상태 확인..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
echo "포트 확인:"
echo "  프론트엔드 (3000):"
lsof -i :3000 2>/dev/null || netstat -tlnp 2>/dev/null | grep :3000 || echo "    리스닝 중인 프로세스 없음"
echo ""
echo "  백엔드 (8000):"
lsof -i :8000 2>/dev/null || netstat -tlnp 2>/dev/null | grep :8000 || echo "    리스닝 중인 프로세스 없음"
echo ""
echo "프로세스 확인:"
pgrep -f "vite.*3000" && echo "  ✅ 프론트엔드 프로세스 실행 중" || echo "  ❌ 프론트엔드 프로세스 없음"
pgrep -f "uvicorn.*8000" && echo "  ✅ 백엔드 프로세스 실행 중" || echo "  ❌ 백엔드 프로세스 없음"
ENDSSH

echo ""
echo "6️⃣  연결 테스트..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
echo "프론트엔드 로컬 테스트:"
curl -s -o /dev/null -w "HTTP 코드: %{http_code}\n" http://127.0.0.1:3000 || echo "연결 실패"
echo ""
echo "백엔드 로컬 테스트:"
curl -s -o /dev/null -w "HTTP 코드: %{http_code}\n" http://127.0.0.1:8000/health || echo "연결 실패"
ENDSSH

echo ""
echo "✅ 배포 및 시작 완료!"
echo ""
echo "확인:"
echo "  https://damcp.gngmeta.com/disaster"
echo ""
echo "서버 로그 확인:"
echo "  ssh -i $KEY_FILE ${SERVER_USER}@${SERVER_HOST} 'tail -f /tmp/frontend.log'"


