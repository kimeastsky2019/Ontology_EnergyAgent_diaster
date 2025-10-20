#!/bin/bash

# Energy Analysis MCP - Nginx 설정 스크립트
# 사용법: ./setup_nginx.sh your-domain.com

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 도메인 확인
DOMAIN=${1:-damcp.gngmeta.com}

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

log_info "🌐 Nginx 설정을 시작합니다 (도메인: $DOMAIN)..."

# Nginx 설치 확인
if ! command -v nginx &> /dev/null; then
    log_error "Nginx가 설치되지 않았습니다. 먼저 ./install.sh을 실행하세요."
    exit 1
fi

# 현재 디렉토리 경로
CURRENT_DIR=$(pwd)

# Nginx 설정 파일 생성
log_info "Nginx 설정 파일을 생성합니다..."
sudo tee /etc/nginx/sites-available/energy-analysis-mcp > /dev/null << EOF
# Energy Analysis MCP - Nginx Configuration
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # 보안 헤더
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;
    
    # 메인 애플리케이션
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # React 앱 (정적 파일)
    location /weather {
        alias $CURRENT_DIR/react-weather-app/build;
        try_files \$uri \$uri/ /index.html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 통합 대시보드
    location /integration {
        proxy_pass http://127.0.0.1:8000/integration;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 정적 파일
    location /static/ {
        alias $CURRENT_DIR/integration/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API 엔드포인트
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 헬스체크
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
    
    # 로그 설정
    access_log /var/log/nginx/energy-analysis-mcp.access.log;
    error_log /var/log/nginx/energy-analysis-mcp.error.log;
}
EOF

# 사이트 활성화
log_info "Nginx 사이트를 활성화합니다..."
sudo ln -sf /etc/nginx/sites-available/energy-analysis-mcp /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx 설정 테스트
log_info "Nginx 설정을 테스트합니다..."
if sudo nginx -t; then
    log_success "Nginx 설정이 유효합니다."
else
    log_error "Nginx 설정에 오류가 있습니다."
    exit 1
fi

# Nginx 재시작
log_info "Nginx를 재시작합니다..."
sudo systemctl restart nginx

# 방화벽 설정 (UFW 사용 시)
if command -v ufw &> /dev/null; then
    log_info "방화벽을 설정합니다..."
    sudo ufw allow 'Nginx Full'
    sudo ufw allow OpenSSH
    sudo ufw --force enable
fi

# 서비스 상태 확인
log_info "서비스 상태를 확인합니다..."
if sudo systemctl is-active --quiet nginx; then
    log_success "Nginx가 성공적으로 실행 중입니다."
else
    log_error "Nginx 시작에 실패했습니다."
    sudo systemctl status nginx
    exit 1
fi

# 포트 확인
log_info "사용 중인 포트를 확인합니다..."
netstat -tlnp | grep -E ':(80|443)'

log_success "🎉 Nginx 설정이 완료되었습니다!"
log_info "다음 단계:"
echo "1. 도메인 DNS가 이 서버를 가리키는지 확인하세요"
echo "2. SSL 인증서를 설치하세요:"
echo "   sudo certbot --nginx -d $DOMAIN"
echo "3. 웹사이트에 접속하세요:"
echo "   http://$DOMAIN"
echo "   https://$DOMAIN (SSL 설치 후)"
