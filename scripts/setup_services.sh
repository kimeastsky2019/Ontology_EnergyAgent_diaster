#!/bin/bash
# Systemd 서비스 설정 스크립트

set -e

PROJECT_DIR="/home/metal/energy-platform"
SYSTEMD_DIR="/etc/systemd/system"

echo "⚙️  Systemd 서비스 설정"
echo "======================"
echo ""

# 서버에서 실행해야 함
if [ "$USER" != "metal" ]; then
    echo "⚠️  이 스크립트는 서버(metal@34.47.89.217)에서 실행하세요"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

# 프론트엔드 서비스 설정
echo "1️⃣  프론트엔드 서비스 설정..."
if [ -f "scripts/systemd/frontend.service" ]; then
    sudo cp scripts/systemd/frontend.service "$SYSTEMD_DIR/"
    echo "✅ 프론트엔드 서비스 파일 복사 완료"
else
    echo "❌ 프론트엔드 서비스 파일을 찾을 수 없습니다"
fi

# 백엔드 서비스 설정
echo ""
echo "2️⃣  백엔드 서비스 설정..."
if [ -f "scripts/systemd/backend.service" ]; then
    sudo cp scripts/systemd/backend.service "$SYSTEMD_DIR/"
    echo "✅ 백엔드 서비스 파일 복사 완료"
else
    echo "❌ 백엔드 서비스 파일을 찾을 수 없습니다"
fi

# Systemd 재로드
echo ""
echo "3️⃣  Systemd 재로드..."
sudo systemctl daemon-reload
echo "✅ Systemd 재로드 완료"

echo ""
echo "📝 서비스 관리 명령어:"
echo ""
echo "프론트엔드 서비스:"
echo "  시작: sudo systemctl start frontend"
echo "  중지: sudo systemctl stop frontend"
echo "  재시작: sudo systemctl restart frontend"
echo "  상태: sudo systemctl status frontend"
echo "  로그: sudo journalctl -u frontend -f"
echo "  자동 시작: sudo systemctl enable frontend"
echo ""
echo "백엔드 서비스:"
echo "  시작: sudo systemctl start backend"
echo "  중지: sudo systemctl stop backend"
echo "  재시작: sudo systemctl restart backend"
echo "  상태: sudo systemctl status backend"
echo "  로그: sudo journalctl -u backend -f"
echo "  자동 시작: sudo systemctl enable backend"
echo ""
echo "⚠️  주의: 서비스 파일의 경로와 설정을 확인하세요"
echo "   - frontend.service: WorkingDirectory, ExecStart 경로 확인"
echo "   - backend.service: venv 경로 및 uvicorn 경로 확인"


