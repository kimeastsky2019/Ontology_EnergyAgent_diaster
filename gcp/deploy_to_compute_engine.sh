#!/bin/bash

# GCP Compute Engine 배포 스크립트
# IP: 34.47.89.217
# User: metal

set -e

echo "🚀 GCP Compute Engine 배포 시작..."

# 서버 정보
SERVER_IP="34.47.89.217"
SERVER_USER="metal"
PROJECT_DIR="/home/metal/energy-analysis-mcp"
GITHUB_REPO="https://github.com/kimeastsky2019/energy-analysis-mcp.git"

# SSH 키 설정 (필요시)
# ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# ssh-copy-id $SERVER_USER@$SERVER_IP

echo "📋 서버에 연결 중..."

# 서버에 연결하여 배포 실행
ssh $SERVER_USER@$SERVER_IP << 'EOF'
    echo "🔧 서버 환경 설정 중..."
    
    # 시스템 업데이트
    sudo apt update && sudo apt upgrade -y
    
    # Python 3.11 설치
    sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
    
    # Git 설치
    sudo apt install -y git
    
    # 필요한 시스템 패키지 설치
    sudo apt install -y build-essential curl wget
    
    # 프로젝트 디렉토리로 이동
    cd /home/metal
    
    # 기존 프로젝트 삭제 (있다면)
    if [ -d "energy-analysis-mcp" ]; then
        echo "🗑️ 기존 프로젝트 삭제 중..."
        rm -rf energy-analysis-mcp
    fi
    
    # GitHub에서 프로젝트 클론
    echo "📥 GitHub에서 프로젝트 클론 중..."
    git clone https://github.com/kimeastsky2019/energy-analysis-mcp.git
    
    cd energy-analysis-mcp
    
    # Python 가상환경 생성
    echo "🐍 Python 가상환경 생성 중..."
    python3.11 -m venv venv
    source venv/bin/activate
    
    # pip 업그레이드
    pip install --upgrade pip
    
    # 의존성 설치
    echo "📦 의존성 설치 중..."
    pip install -r requirements.txt
    
    # 환경 변수 설정
    echo "🔧 환경 변수 설정 중..."
    cat > .env << 'ENVEOF'
ENVIRONMENT=production
LOG_LEVEL=info
PORT=8000
OPENWEATHER_API_KEY=your_api_key_here
ENERGY_MCP_PORT=8000
ENVEOF
    
    # systemd 서비스 파일 생성
    echo "⚙️ systemd 서비스 설정 중..."
    sudo tee /etc/systemd/system/energy-analysis.service > /dev/null << 'SERVICEEOF'
[Unit]
Description=Energy Analysis MCP Server
After=network.target

[Service]
Type=simple
User=metal
WorkingDirectory=/home/metal/energy-analysis-mcp
Environment=PATH=/home/metal/energy-analysis-mcp/venv/bin
ExecStart=/home/metal/energy-analysis-mcp/venv/bin/python server_cloud.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF
    
    # 서비스 활성화 및 시작
    echo "🚀 서비스 시작 중..."
    sudo systemctl daemon-reload
    sudo systemctl enable energy-analysis
    sudo systemctl start energy-analysis
    
    # 서비스 상태 확인
    echo "📊 서비스 상태 확인..."
    sudo systemctl status energy-analysis --no-pager
    
    # 방화벽 설정 (필요시)
    echo "🔥 방화벽 설정 중..."
    sudo ufw allow 8000/tcp
    sudo ufw allow 22/tcp
    sudo ufw --force enable
    
    echo "✅ 배포 완료!"
    echo "🌍 서비스 URL: http://34.47.89.217:8000"
    echo "📊 API 문서: http://34.47.89.217:8000/docs"
    echo "❤️ 헬스 체크: http://34.47.89.217:8000/health"
EOF

echo "🎉 GCP Compute Engine 배포 완료!"
echo "🌍 서비스 URL: http://34.47.89.217:8000"

