#!/bin/bash

# Energy Analysis MCP - 자동 설치 스크립트
# 사용법: ./install.sh

set -e

echo "🚀 Energy Analysis MCP 설치를 시작합니다..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 시스템 업데이트
log_info "시스템 패키지를 업데이트합니다..."
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
log_info "필수 패키지를 설치합니다..."
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx git curl wget unzip

# Python 가상환경 생성
log_info "Python 가상환경을 생성합니다..."
python3 -m venv .venv
source .venv/bin/activate

# Python 의존성 설치
log_info "Python 의존성을 설치합니다..."
pip install --upgrade pip
pip install -r requirements.txt

# Node.js 의존성 설치 (React 앱)
log_info "React 앱 의존성을 설치합니다..."
cd react-weather-app
npm install
npm run build
cd ..

# 권한 설정
log_info "실행 권한을 설정합니다..."
chmod +x *.sh
chmod +x integration/*.py
chmod +x tools/*.py

# 환경 변수 파일 생성
if [ ! -f .env ]; then
    log_info ".env 파일을 생성합니다..."
    cat > .env << EOF
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Database
DATABASE_URL=sqlite:///data/external_data.db

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Language Settings
DEFAULT_LANGUAGE=ko
SUPPORTED_LANGUAGES=ko,en,ja,zh,ar,he,es,fr,de,ru
EOF
    log_warning ".env 파일이 생성되었습니다. API 키를 설정해주세요."
fi

# 데이터 디렉토리 생성
log_info "데이터 디렉토리를 생성합니다..."
mkdir -p data/cache
mkdir -p logs

# 서비스 파일 생성
log_info "시스템 서비스 파일을 생성합니다..."
sudo tee /etc/systemd/system/energy-analysis-mcp.service > /dev/null << EOF
[Unit]
Description=Energy Analysis MCP Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/.venv/bin
ExecStart=$(pwd)/.venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Nginx 설정 파일 생성
log_info "Nginx 설정 파일을 생성합니다..."
sudo tee /etc/nginx/sites-available/energy-analysis-mcp > /dev/null << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static/ {
        alias $(pwd)/integration/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Nginx 사이트 활성화
sudo ln -sf /etc/nginx/sites-available/energy-analysis-mcp /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx 설정 테스트 및 재시작
sudo nginx -t
sudo systemctl reload nginx

log_success "설치가 완료되었습니다!"
log_info "다음 단계:"
echo "1. .env 파일에 API 키를 설정하세요"
echo "2. ./deploy_all.sh production 을 실행하세요"
echo "3. sudo ./setup_nginx.sh your-domain.com 을 실행하세요"
