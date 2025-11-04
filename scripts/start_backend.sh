#!/bin/bash
# 백엔드 서버 시작 스크립트

set -e

PROJECT_DIR="/home/metal/energy-platform"
BACKEND_DIR="${PROJECT_DIR}/backend"
LOG_FILE="/tmp/backend.log"

echo "🚀 백엔드 서버 시작"
echo "=================="
echo ""

# 서버에서 실행해야 함
if [ ! -d "$BACKEND_DIR" ]; then
    echo "⚠️  백엔드 디렉토리를 찾을 수 없습니다: $BACKEND_DIR"
    echo "이 스크립트는 서버(metal@34.47.89.217)에서 실행하세요"
    exit 1
fi

cd "$BACKEND_DIR" || exit 1

# 기존 프로세스 확인
EXISTING_PID=$(pgrep -f "uvicorn.*8000" || echo "")
if [ -n "$EXISTING_PID" ]; then
    echo "⚠️  백엔드 서버가 이미 실행 중입니다 (PID: $EXISTING_PID)"
    echo "   종료하려면: pkill -f 'uvicorn.*8000'"
    exit 0
fi

# 가상환경 확인
if [ -d "venv" ]; then
    echo "🐍 가상환경 활성화 중..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🐍 가상환경 활성화 중..."
    source .venv/bin/activate
else
    echo "⚠️  가상환경을 찾을 수 없습니다"
    echo "   가상환경이 필요할 수 있습니다"
fi

# 의존성 확인
if ! command -v uvicorn &> /dev/null; then
    echo "❌ uvicorn이 설치되어 있지 않습니다"
    echo "   설치: pip install -r requirements.txt"
    exit 1
fi

echo "✅ 환경 확인 완료"
echo ""

# 서버 시작 옵션
MODE="${1:-dev}"

case "$MODE" in
    dev)
        echo "🔧 개발 모드로 시작 중..."
        echo "   로그: $LOG_FILE"
        echo ""
        nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > "$LOG_FILE" 2>&1 &
        BACKEND_PID=$!
        sleep 2
        
        if ps -p $BACKEND_PID > /dev/null; then
            echo "✅ 백엔드 서버 시작 성공 (PID: $BACKEND_PID)"
            echo "   포트: 8000"
            echo "   로그 확인: tail -f $LOG_FILE"
            echo ""
            echo "프로세스 확인:"
            ps aux | grep -E "uvicorn.*8000" | grep -v grep || echo "   프로세스 확인 중..."
        else
            echo "❌ 백엔드 서버 시작 실패"
            echo "   로그 확인: cat $LOG_FILE"
            exit 1
        fi
        ;;
    background)
        echo "🔧 백그라운드 모드로 시작 중..."
        echo "   로그: $LOG_FILE"
        nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 > "$LOG_FILE" 2>&1 &
        BACKEND_PID=$!
        echo "✅ 백엔드 서버 시작 (PID: $BACKEND_PID)"
        echo "   로그: tail -f $LOG_FILE"
        ;;
    pm2)
        if ! command -v pm2 &> /dev/null; then
            echo "⚠️  PM2가 설치되어 있지 않습니다"
            echo "   설치: npm install -g pm2"
            echo "   또는 'dev' 모드 사용: bash scripts/start_backend.sh dev"
            exit 1
        fi
        
        echo "🔧 PM2로 시작 중..."
        pm2 start "uvicorn src.main:app --host 0.0.0.0 --port 8000" --name "backend"
        echo "✅ PM2로 백엔드 서버 시작 완료"
        echo "   상태 확인: pm2 status"
        echo "   로그 확인: pm2 logs backend"
        ;;
    *)
        echo "사용법: $0 [dev|background|pm2]"
        echo "  dev: 개발 모드 (기본값, --reload 포함)"
        echo "  background: 백그라운드 모드"
        echo "  pm2: PM2로 관리"
        exit 1
        ;;
esac

echo ""
echo "🔍 연결 테스트:"
sleep 1
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health | grep -q "200"; then
    echo "✅ 백엔드 서버 응답 코드: 200"
else
    echo "⚠️  백엔드 서버 응답 확인 중..."
fi

echo ""
echo "📝 다음 단계:"
echo "  1. 백엔드 서버 상태 확인: curl http://127.0.0.1:8000/health"
echo "  2. API 문서 확인: curl http://127.0.0.1:8000/docs"


