#!/bin/bash

# Energy Analysis MCP - 권한 설정 스크립트
# 사용법: ./set_permissions.sh

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

log_info "🔐 Energy Analysis MCP 권한을 설정합니다..."

# 현재 사용자 확인
CURRENT_USER=$(whoami)
log_info "현재 사용자: $CURRENT_USER"

# 스크립트 파일 실행 권한
log_info "스크립트 파일에 실행 권한을 부여합니다..."
chmod +x *.sh
chmod +x integration/*.py
chmod +x tools/*.py
chmod +x api-server/*.py
chmod +x automl/*.py

# 디렉토리 권한 설정
log_info "디렉토리 권한을 설정합니다..."
chmod 755 .
chmod 755 integration/
chmod 755 tools/
chmod 755 api-server/
chmod 755 automl/
chmod 755 i18n/
chmod 755 i18n/locales/

# 데이터 디렉토리 권한
log_info "데이터 디렉토리 권한을 설정합니다..."
mkdir -p data/cache
mkdir -p logs
chmod 755 data/
chmod 755 data/cache/
chmod 755 logs/

# 웹 파일 권한
log_info "웹 파일 권한을 설정합니다..."
chmod 644 *.html
chmod 644 *.py
chmod 644 requirements.txt
chmod 644 *.md
chmod 644 .env 2>/dev/null || true

# React 앱 권한
log_info "React 앱 권한을 설정합니다..."
chmod -R 755 react-weather-app/
chmod 644 react-weather-app/package.json
chmod 644 react-weather-app/package-lock.json

# 통합 대시보드 권한
log_info "통합 대시보드 권한을 설정합니다..."
chmod 644 integration/templates/*.html
chmod 644 integration/static/css/*
chmod 644 integration/static/js/*
chmod 644 integration/static/images/* 2>/dev/null || true

# i18n 파일 권한
log_info "다국어 파일 권한을 설정합니다..."
chmod 644 i18n/locales/*.json
chmod 644 i18n/*.js
chmod 644 i18n/*.py

# 소유자 변경 (www-data로)
log_info "파일 소유자를 www-data로 변경합니다..."
sudo chown -R www-data:www-data .
sudo chown -R $CURRENT_USER:$CURRENT_USER .git 2>/dev/null || true
sudo chown -R $CURRENT_USER:$CURRENT_USER .venv 2>/dev/null || true

# 특별한 권한 설정
log_info "특별한 권한을 설정합니다..."
# .env 파일은 소유자만 읽기 가능
chmod 600 .env 2>/dev/null || true
# 로그 파일은 쓰기 가능
chmod 666 logs/*.log 2>/dev/null || true
# 데이터베이스 파일 권한
chmod 664 data/*.db 2>/dev/null || true

# SELinux 설정 (CentOS/RHEL에서)
if command -v setsebool &> /dev/null; then
    log_info "SELinux 설정을 확인합니다..."
    sudo setsebool -P httpd_can_network_connect 1 2>/dev/null || true
fi

# 방화벽 포트 확인
log_info "방화벽 포트를 확인합니다..."
if command -v ufw &> /dev/null; then
    sudo ufw status | grep -E ':(80|443|8000)' || log_warning "방화벽 포트가 열려있지 않을 수 있습니다."
fi

# 서비스 파일 권한
log_info "서비스 파일 권한을 설정합니다..."
sudo chmod 644 /etc/systemd/system/energy-analysis-mcp.service 2>/dev/null || true
sudo chmod 644 /etc/nginx/sites-available/energy-analysis-mcp 2>/dev/null || true

# 권한 확인
log_info "설정된 권한을 확인합니다..."
echo "=== 스크립트 파일 권한 ==="
ls -la *.sh | head -5
echo ""
echo "=== 데이터 디렉토리 권한 ==="
ls -la data/
echo ""
echo "=== 웹 파일 권한 ==="
ls -la *.html *.py | head -5

log_success "🎉 권한 설정이 완료되었습니다!"
log_info "설정된 권한:"
echo "  - 스크립트 파일: 실행 가능 (755)"
echo "  - 웹 파일: 읽기 가능 (644)"
echo "  - 데이터 디렉토리: 읽기/실행 가능 (755)"
echo "  - 로그 파일: 읽기/쓰기 가능 (666)"
echo "  - 소유자: www-data"

log_warning "보안 참고사항:"
echo "  - .env 파일은 소유자만 읽기 가능 (600)"
echo "  - 데이터베이스 파일은 적절한 권한으로 설정됨"
echo "  - 정기적으로 권한을 확인하세요"
