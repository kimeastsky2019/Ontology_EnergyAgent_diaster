#!/bin/bash
echo "🚀 GCP Compute Engine 배포 스크립트"
echo "=================================="

# 서버 정보
SERVER_IP="34.47.89.217"
USER="metal"
APP_DIR="/home/metal/energy-analysis-mcp"
SERVICE_NAME="energy-analysis-mcp"

echo "1. 서버에 압축 파일 업로드..."
echo "   ppk 키를 사용하여 업로드합니다..."
echo "   scp -i your_key.ppk energy-analysis-mcp-deploy.tar.gz $USER@$SERVER_IP:/tmp/"

echo "2. 서버에서 압축 해제 및 설정..."
echo "   ssh -i your_key.ppk $USER@$SERVER_IP"
echo ""
echo "   서버에서 다음 명령어들을 실행하세요:"
echo "   ==================================="
cat << 'REMOTE_COMMANDS'
# 1. 압축 파일 확인
ls -la /tmp/energy-analysis-mcp-deploy.tar.gz

# 2. 기존 디렉토리 백업 및 새로 생성
cd /home/metal
mv energy-analysis-mcp energy-analysis-mcp-backup-$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
mkdir -p energy-analysis-mcp
cd energy-analysis-mcp

# 3. 압축 해제
tar -xzf /tmp/energy-analysis-mcp-deploy.tar.gz
rm /tmp/energy-analysis-mcp-deploy.tar.gz

# 4. Python 환경 설정
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. 기존 서비스 중지
sudo systemctl stop energy-analysis-mcp 2>/dev/null || true
sudo systemctl disable energy-analysis-mcp 2>/dev/null || true

# 6. systemd 서비스 파일 생성
sudo tee /etc/systemd/system/energy-analysis-mcp.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Energy Analysis MCP Service
After=network.target

[Service]
Type=simple
User=metal
WorkingDirectory=/home/metal/energy-analysis-mcp
Environment=PATH=/home/metal/energy-analysis-mcp/venv/bin
ExecStart=/home/metal/energy-analysis-mcp/venv/bin/python -m uvicorn web_interface:web_app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# 7. 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable energy-analysis-mcp
sudo systemctl start energy-analysis-mcp

# 8. 서비스 상태 확인
sudo systemctl status energy-analysis-mcp --no-pager

# 9. 방화벽 설정
sudo ufw allow 8000/tcp 2>/dev/null || true

# 10. 포트 확인
netstat -tlnp | grep :8000 || ss -tlnp | grep :8000

echo "✅ 배포 완료!"
echo "🌐 서비스 URL: http://34.47.89.217:8000"
echo "📊 거래 페이지: http://34.47.89.217:8000/trading?lang=ko"
echo "📈 Statistics 페이지: http://34.47.89.217:8000/statistics?lang=ko"
REMOTE_COMMANDS

echo ""
echo "📋 수동 배포 단계:"
echo "1. ppk 키로 서버 접속: ssh -i your_key.ppk metal@34.47.89.217"
echo "2. 압축 파일 업로드: scp -i your_key.ppk energy-analysis-mcp-deploy.tar.gz metal@34.47.89.217:/tmp/"
echo "3. 서버에서 위의 명령어들 실행"
echo ""
echo "📦 압축 파일: energy-analysis-mcp-deploy.tar.gz ($(ls -lh energy-analysis-mcp-deploy.tar.gz | awk '{print $5}'))"
