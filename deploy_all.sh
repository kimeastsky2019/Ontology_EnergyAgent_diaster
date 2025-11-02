#!/bin/bash

# Energy Analysis MCP - 전체 배포 스크립트
# 사용법: ./deploy_all.sh [production|development]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 환경 설정
ENVIRONMENT=${1:-development}

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

log_info "🚀 Energy Analysis MCP 배포를 시작합니다 (환경: $ENVIRONMENT)..."

# 가상환경 활성화
source .venv/bin/activate

# 서비스 중지
log_info "기존 서비스를 중지합니다..."
sudo systemctl stop energy-analysis-mcp 2>/dev/null || true

# React 앱 빌드
log_info "React 앱을 빌드합니다..."
cd react-weather-app
npm run build
cd ..

# Python 의존성 업데이트
log_info "Python 의존성을 업데이트합니다..."
pip install --upgrade pip
pip install -r requirements.txt

# 데이터베이스 초기화
log_info "데이터베이스를 초기화합니다..."
python -c "
import sqlite3
import os
os.makedirs('data', exist_ok=True)
conn = sqlite3.connect('data/external_data.db')
conn.close()
print('데이터베이스 초기화 완료')
"

# 환경별 설정
if [ "$ENVIRONMENT" = "production" ]; then
    log_info "프로덕션 환경 설정을 적용합니다..."
    export DEBUG=False
    export HOST=0.0.0.0
    export PORT=8000
else
    log_info "개발 환경 설정을 적용합니다..."
    export DEBUG=True
    export HOST=127.0.0.1
    export PORT=8000
fi

# 서비스 시작
log_info "서비스를 시작합니다..."
sudo systemctl daemon-reload
sudo systemctl enable energy-analysis-mcp
sudo systemctl start energy-analysis-mcp

# 서비스 상태 확인
sleep 5
if sudo systemctl is-active --quiet energy-analysis-mcp; then
    log_success "서비스가 성공적으로 시작되었습니다!"
else
    log_error "서비스 시작에 실패했습니다."
    sudo systemctl status energy-analysis-mcp
    exit 1
fi

# 헬스체크
log_info "헬스체크를 수행합니다..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "헬스체크 성공!"
        break
    else
        log_warning "헬스체크 시도 $i/10..."
        sleep 2
    fi
done

# Nginx 재시작
log_info "Nginx를 재시작합니다..."
sudo systemctl reload nginx

# 포트 확인
log_info "사용 중인 포트를 확인합니다..."
netstat -tlnp | grep -E ':(80|8000|443)'

log_success "🎉 배포가 완료되었습니다!"
log_info "접속 URL:"
echo "  - 메인 대시보드: http://localhost:8000"
echo "  - React 앱: http://localhost:8000/weather"
echo "  - 통합 대시보드: http://localhost:8000/integration"
echo "  - 정적 대시보드: http://localhost:8000/static/weather_dashboard.html"

log_info "서비스 관리 명령어:"
echo "  - 상태 확인: sudo systemctl status energy-analysis-mcp"
echo "  - 로그 확인: sudo journalctl -u energy-analysis-mcp -f"
echo "  - 서비스 중지: sudo systemctl stop energy-analysis-mcp"
echo "  - 서비스 시작: sudo systemctl start energy-analysis-mcp"
