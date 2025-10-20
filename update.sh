#!/bin/bash

# Energy Analysis MCP - 업데이트 스크립트
# 사용법: ./update.sh

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

log_info "🔄 Energy Analysis MCP 업데이트를 시작합니다..."

# 백업 생성
log_info "현재 설정을 백업합니다..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r .venv "$BACKUP_DIR/" 2>/dev/null || true
cp .env "$BACKUP_DIR/" 2>/dev/null || true
cp -r data "$BACKUP_DIR/" 2>/dev/null || true
log_success "백업이 생성되었습니다: $BACKUP_DIR"

# Git 업데이트
log_info "Git 저장소를 업데이트합니다..."
git fetch origin
git pull origin main

# 가상환경 활성화
source .venv/bin/activate

# Python 의존성 업데이트
log_info "Python 의존성을 업데이트합니다..."
pip install --upgrade pip
pip install -r requirements.txt

# Node.js 의존성 업데이트 (React 앱)
log_info "React 앱을 업데이트합니다..."
cd react-weather-app
npm install
npm run build
cd ..

# 데이터베이스 마이그레이션 (필요한 경우)
log_info "데이터베이스를 확인합니다..."
python -c "
import sqlite3
import os
os.makedirs('data', exist_ok=True)
conn = sqlite3.connect('data/external_data.db')
# 여기에 필요한 마이그레이션 로직 추가
conn.close()
print('데이터베이스 확인 완료')
"

# 서비스 재시작
log_info "서비스를 재시작합니다..."
sudo systemctl restart energy-analysis-mcp

# 서비스 상태 확인
sleep 5
if sudo systemctl is-active --quiet energy-analysis-mcp; then
    log_success "서비스가 성공적으로 재시작되었습니다!"
else
    log_error "서비스 재시작에 실패했습니다."
    sudo systemctl status energy-analysis-mcp
    exit 1
fi

# 헬스체크
log_info "헬스체크를 수행합니다..."
for i in {1..5}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "헬스체크 성공!"
        break
    else
        log_warning "헬스체크 시도 $i/5..."
        sleep 2
    fi
done

# Nginx 재시작
log_info "Nginx를 재시작합니다..."
sudo systemctl reload nginx

# 로그 정리 (선택사항)
read -p "오래된 로그 파일을 정리하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "로그 파일을 정리합니다..."
    find logs/ -name "*.log" -mtime +30 -delete 2>/dev/null || true
    sudo journalctl --vacuum-time=30d
fi

log_success "🎉 업데이트가 완료되었습니다!"
log_info "서비스 상태:"
echo "  - 메인 서비스: $(sudo systemctl is-active energy-analysis-mcp)"
echo "  - Nginx: $(sudo systemctl is-active nginx)"
echo "  - 접속 URL: http://localhost:8000"

log_info "업데이트된 기능:"
echo "  - 다국어 지원 (10개 언어)"
echo "  - RTL 언어 지원 (아랍어, 히브리어)"
echo "  - 개선된 사용자 인터페이스"
echo "  - 자동화된 배포 스크립트"
