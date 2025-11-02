#!/bin/bash
# 모든 서버 시작 스크립트

set -e

PROJECT_DIR="/home/metal/energy-platform"

echo "🚀 모든 서버 시작"
echo "=================="
echo ""

cd "$PROJECT_DIR" || exit 1

echo "1️⃣  백엔드 서버 시작..."
bash scripts/start_backend.sh "$1" || echo "⚠️  백엔드 서버 시작 실패"

echo ""
echo "2️⃣  프론트엔드 서버 시작..."
bash scripts/start_frontend.sh "$1" || echo "⚠️  프론트엔드 서버 시작 실패"

echo ""
echo "✅ 모든 서버 시작 완료"
echo ""
echo "📊 서버 상태 확인:"
echo "   프론트엔드: curl http://127.0.0.1:3000"
echo "   백엔드: curl http://127.0.0.1:8000/health"
echo ""
echo "🌐 도메인 테스트:"
echo "   https://damcp.gngmeta.com/disaster"

