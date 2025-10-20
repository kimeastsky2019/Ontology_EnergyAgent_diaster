#!/bin/bash

# Energy Analysis MCP - 서버 중지 스크립트
# 사용법: ./stop_servers.sh

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

log_info "🛑 Energy Analysis MCP 서버들을 중지합니다..."

# 메인 서비스 중지
log_info "메인 서비스를 중지합니다..."
sudo systemctl stop energy-analysis-mcp 2>/dev/null || log_warning "메인 서비스가 실행 중이 아닙니다."

# Nginx 중지 (선택사항)
read -p "Nginx도 중지하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Nginx를 중지합니다..."
    sudo systemctl stop nginx
fi

# 실행 중인 Python 프로세스 확인 및 종료
log_info "실행 중인 Python 프로세스를 확인합니다..."
PYTHON_PIDS=$(pgrep -f "python.*server" || true)
if [ ! -z "$PYTHON_PIDS" ]; then
    log_warning "실행 중인 Python 서버 프로세스를 발견했습니다: $PYTHON_PIDS"
    read -p "이 프로세스들을 종료하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo $PYTHON_PIDS | xargs kill -TERM
        sleep 2
        # 강제 종료가 필요한 경우
        REMAINING_PIDS=$(pgrep -f "python.*server" || true)
        if [ ! -z "$REMAINING_PIDS" ]; then
            echo $REMAINING_PIDS | xargs kill -KILL
        fi
        log_success "Python 프로세스들을 종료했습니다."
    fi
fi

# 포트 사용 확인
log_info "사용 중인 포트를 확인합니다..."
USED_PORTS=$(netstat -tlnp | grep -E ':(80|8000|443)' || true)
if [ ! -z "$USED_PORTS" ]; then
    log_warning "아직 사용 중인 포트가 있습니다:"
    echo "$USED_PORTS"
else
    log_success "모든 포트가 해제되었습니다."
fi

# 서비스 상태 확인
log_info "서비스 상태를 확인합니다..."
if sudo systemctl is-active --quiet energy-analysis-mcp; then
    log_warning "메인 서비스가 여전히 실행 중입니다."
else
    log_success "메인 서비스가 중지되었습니다."
fi

log_success "🎉 서버 중지가 완료되었습니다!"
log_info "서비스를 다시 시작하려면:"
echo "  - ./deploy_all.sh production"
echo "  - sudo systemctl start energy-analysis-mcp"
