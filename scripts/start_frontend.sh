#!/bin/bash
# 프론트엔드 서버 시작 스크립트

set -e

PROJECT_DIR="/home/metal/energy-platform"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
LOG_FILE="/tmp/frontend.log"

echo "🚀 프론트엔드 서버 시작"
echo "======================"
echo ""

# 서버에서 실행해야 함
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "⚠️  프론트엔드 디렉토리를 찾을 수 없습니다: $FRONTEND_DIR"
    echo "이 스크립트는 서버(metal@34.47.89.217)에서 실행하세요"
    exit 1
fi

cd "$FRONTEND_DIR" || exit 1

# 기존 프로세스 확인
EXISTING_PID=$(pgrep -f "vite.*3000" || echo "")
if [ -n "$EXISTING_PID" ]; then
    echo "⚠️  프론트엔드 서버가 이미 실행 중입니다 (PID: $EXISTING_PID)"
    echo "   종료하려면: pkill -f 'vite.*3000'"
    exit 0
fi

# 의존성 확인
if [ ! -d "node_modules" ]; then
    echo "📦 의존성 설치 중..."
    npm install
fi

# 환경 확인
if ! command -v npm &> /dev/null; then
    echo "❌ npm이 설치되어 있지 않습니다"
    echo "   Node.js와 npm을 설치하세요"
    exit 1
fi

echo "✅ 의존성 확인 완료"
echo ""

# 서버 시작 옵션
MODE="${1:-dev}"

case "$MODE" in
    dev)
        echo "🔧 개발 모드로 시작 중..."
        echo "   로그: $LOG_FILE"
        echo ""
        nohup npm run dev > "$LOG_FILE" 2>&1 &
        FRONTEND_PID=$!
        sleep 2
        
        if ps -p $FRONTEND_PID > /dev/null; then
            echo "✅ 프론트엔드 서버 시작 성공 (PID: $FRONTEND_PID)"
            echo "   포트: 3000"
            echo "   로그 확인: tail -f $LOG_FILE"
            echo ""
            echo "프로세스 확인:"
            ps aux | grep -E "vite.*3000" | grep -v grep || echo "   프로세스 확인 중..."
        else
            echo "❌ 프론트엔드 서버 시작 실패"
            echo "   로그 확인: cat $LOG_FILE"
            exit 1
        fi
        ;;
    background)
        echo "🔧 백그라운드 모드로 시작 중..."
        echo "   로그: $LOG_FILE"
        nohup npm run dev > "$LOG_FILE" 2>&1 &
        FRONTEND_PID=$!
        echo "✅ 프론트엔드 서버 시작 (PID: $FRONTEND_PID)"
        echo "   로그: tail -f $LOG_FILE"
        ;;
    pm2)
        if ! command -v pm2 &> /dev/null; then
            echo "⚠️  PM2가 설치되어 있지 않습니다"
            echo "   설치: npm install -g pm2"
            echo "   또는 'dev' 모드 사용: bash scripts/start_frontend.sh dev"
            exit 1
        fi
        
        echo "🔧 PM2로 시작 중..."
        pm2 start npm --name "frontend" -- run dev
        echo "✅ PM2로 프론트엔드 서버 시작 완료"
        echo "   상태 확인: pm2 status"
        echo "   로그 확인: pm2 logs frontend"
        ;;
    *)
        echo "사용법: $0 [dev|background|pm2]"
        echo "  dev: 개발 모드 (기본값)"
        echo "  background: 백그라운드 모드"
        echo "  pm2: PM2로 관리"
        exit 1
        ;;
esac

echo ""
echo "🔍 연결 테스트:"
sleep 1
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000 | grep -q "200\|404"; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000)
    echo "✅ 프론트엔드 서버 응답 코드: $HTTP_CODE"
else
    echo "⚠️  프론트엔드 서버 응답 확인 중..."
fi

echo ""
echo "📝 다음 단계:"
echo "  1. 프론트엔드 서버 상태 확인: curl http://127.0.0.1:3000"
echo "  2. Nginx 테스트: curl http://127.0.0.1/disaster"
echo "  3. 도메인 테스트: curl https://damcp.gngmeta.com/disaster"


