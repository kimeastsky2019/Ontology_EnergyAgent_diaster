#!/bin/bash
# 서버 상태 확인 스크립트 (로컬에서 실행)
# damcp.gngmeta.com 서버 상태 진단

set -e

# 설정
SERVER_IP="34.47.89.217"
SERVER_USER="metal"
PEM_FILE="google_compute_engine.pem"
DOMAIN="damcp.gngmeta.com"

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

# PEM 파일 확인 및 SSH 옵션 설정
if [ -f "$PEM_FILE" ]; then
    chmod 600 "$PEM_FILE"
    SSH_OPTS="-i $PEM_FILE -o IdentitiesOnly=yes -o ServerAliveInterval=60 -o StrictHostKeyChecking=no"
    log_info "PEM 파일 사용: $PEM_FILE"
else
    SSH_OPTS="-o ServerAliveInterval=60 -o StrictHostKeyChecking=no"
    log_warning "PEM 파일 없음. 기본 SSH 키 사용"
fi

echo ""
echo "=========================================="
echo "🔍 서버 상태 진단: ${DOMAIN}"
echo "=========================================="
echo ""

# 1. 서버 연결 테스트
log_info "1️⃣ 서버 연결 테스트..."
if ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} "echo '연결 성공'" 2>/dev/null; then
    log_success "서버 연결 성공"
else
    log_error "서버 연결 실패"
    exit 1
fi

# 2. Systemd 서비스 상태 확인
echo ""
log_info "2️⃣ Systemd 서비스 상태 확인..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo "=== Backend 서비스 (energy-backend) ==="
if systemctl is-active --quiet energy-backend 2>/dev/null; then
    echo "✅ 실행 중"
else
    echo "❌ 중지됨"
fi
systemctl status energy-backend --no-pager -l | head -5

echo ""
echo "=== Frontend 서비스 (energy-frontend) ==="
if systemctl is-active --quiet energy-frontend 2>/dev/null; then
    echo "✅ 실행 중"
else
    echo "❌ 중지됨"
fi
systemctl status energy-frontend --no-pager -l | head -5

echo ""
echo "=== Nginx 서비스 ==="
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "✅ 실행 중"
else
    echo "❌ 중지됨"
fi
systemctl status nginx --no-pager -l | head -5
ENDSSH

# 3. 포트 확인
echo ""
log_info "3️⃣ 포트 상태 확인..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo "=== 포트 8000 (Backend) ==="
if ss -tlnp 2>/dev/null | grep -q ":8000 " || netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
    echo "✅ 포트 8000 리스닝 중"
    ss -tlnp 2>/dev/null | grep ":8000 " || netstat -tlnp 2>/dev/null | grep ":8000 "
else
    echo "❌ 포트 8000 리스닝 안됨"
fi

echo ""
echo "=== 포트 3000 (Frontend) ==="
if ss -tlnp 2>/dev/null | grep -q ":3000 " || netstat -tlnp 2>/dev/null | grep -q ":3000 "; then
    echo "✅ 포트 3000 리스닝 중"
    ss -tlnp 2>/dev/null | grep ":3000 " || netstat -tlnp 2>/dev/null | grep ":3000 "
else
    echo "❌ 포트 3000 리스닝 안됨"
fi

echo ""
echo "=== 포트 80 (Nginx HTTP) ==="
if ss -tlnp 2>/dev/null | grep -q ":80 " || netstat -tlnp 2>/dev/null | grep -q ":80 "; then
    echo "✅ 포트 80 리스닝 중"
    ss -tlnp 2>/dev/null | grep ":80 " || netstat -tlnp 2>/dev/null | grep ":80 "
else
    echo "❌ 포트 80 리스닝 안됨"
fi

echo ""
echo "=== 포트 443 (Nginx HTTPS) ==="
if ss -tlnp 2>/dev/null | grep -q ":443 " || netstat -tlnp 2>/dev/null | grep -q ":443 "; then
    echo "✅ 포트 443 리스닝 중"
    ss -tlnp 2>/dev/null | grep ":443 " || netstat -tlnp 2>/dev/null | grep ":443 "
else
    echo "⚠️  포트 443 리스닝 안됨 (SSL 미설정 가능)"
fi
ENDSSH

# 4. 프로세스 확인
echo ""
log_info "4️⃣ 프로세스 상태 확인..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo "=== Python 프로세스 (Backend) ==="
ps aux | grep -E "(uvicorn|python.*server)" | grep -v grep || echo "❌ 백엔드 프로세스 없음"

echo ""
echo "=== Node 프로세스 (Frontend) ==="
ps aux | grep -E "(node|npm)" | grep -v grep || echo "❌ 프론트엔드 프로세스 없음"

echo ""
echo "=== Nginx 프로세스 ==="
ps aux | grep nginx | grep -v grep || echo "❌ Nginx 프로세스 없음"
ENDSSH

# 5. 로컬 접속 테스트
echo ""
log_info "5️⃣ 로컬 접속 테스트..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo "=== Backend Health Check (localhost:8000/health) ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Backend 응답: $HTTP_CODE"
    curl -s http://127.0.0.1:8000/health | head -3
else
    echo "❌ Backend 응답 코드: $HTTP_CODE"
fi

echo ""
echo "=== Frontend 접속 테스트 (localhost:3000) ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Frontend 응답: $HTTP_CODE"
else
    echo "❌ Frontend 응답 코드: $HTTP_CODE"
fi

echo ""
echo "=== Nginx 접속 테스트 (localhost:80) ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1 2>/dev/null || echo "000")
echo "응답 코드: $HTTP_CODE"
ENDSSH

# 6. Nginx 설정 확인
echo ""
log_info "6️⃣ Nginx 설정 확인..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo "=== Nginx 설정 파일 존재 여부 ==="
if [ -f "/etc/nginx/sites-available/damcp.gngmeta.com" ]; then
    echo "✅ 설정 파일 존재"
else
    echo "❌ 설정 파일 없음"
fi

echo ""
echo "=== Nginx 설정 활성화 여부 ==="
if [ -L "/etc/nginx/sites-enabled/damcp.gngmeta.com" ]; then
    echo "✅ 사이트 활성화됨"
else
    echo "❌ 사이트 비활성화됨"
fi

echo ""
echo "=== Nginx 설정 검증 ==="
if sudo nginx -t 2>&1 | grep -q "successful"; then
    echo "✅ Nginx 설정 유효"
else
    echo "❌ Nginx 설정 오류"
    sudo nginx -t 2>&1 | tail -5
fi
ENDSSH

# 7. 최근 로그 확인
echo ""
log_info "7️⃣ 최근 로그 확인..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
echo "=== Backend 서비스 로그 (최근 5줄) ==="
sudo journalctl -u energy-backend -n 5 --no-pager 2>/dev/null || echo "로그 없음"

echo ""
echo "=== Frontend 서비스 로그 (최근 5줄) ==="
sudo journalctl -u energy-frontend -n 5 --no-pager 2>/dev/null || echo "로그 없음"

echo ""
echo "=== Nginx 에러 로그 (최근 5줄) ==="
sudo tail -5 /var/log/nginx/error.log 2>/dev/null || echo "로그 없음"
ENDSSH

# 8. 도메인 접속 테스트
echo ""
log_info "8️⃣ 도메인 접속 테스트..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${DOMAIN} 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    log_success "도메인 응답 코드: $HTTP_CODE"
else
    log_error "도메인 응답 코드: $HTTP_CODE"
fi

HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" -k https://${DOMAIN} 2>/dev/null || echo "000")
if [ "$HTTPS_CODE" = "200" ]; then
    log_success "HTTPS 도메인 응답 코드: $HTTPS_CODE"
else
    log_warning "HTTPS 도메인 응답 코드: $HTTPS_CODE (SSL 미설정 가능)"
fi

# 9. 요약 및 해결 방법
echo ""
echo "=========================================="
log_info "📋 진단 완료"
echo "=========================================="
echo ""
echo "🔧 일반적인 해결 방법:"
echo ""
echo "1. 서비스 시작:"
echo "   ssh ${SERVER_USER}@${SERVER_IP}"
echo "   sudo systemctl start energy-backend"
echo "   sudo systemctl start energy-frontend"
echo "   sudo systemctl start nginx"
echo ""
echo "2. 서비스 재시작:"
echo "   sudo systemctl restart energy-backend energy-frontend nginx"
echo ""
echo "3. 서비스 상태 확인:"
echo "   sudo systemctl status energy-backend"
echo "   sudo systemctl status energy-frontend"
echo "   sudo systemctl status nginx"
echo ""
echo "4. 로그 확인:"
echo "   sudo journalctl -u energy-backend -f"
echo "   sudo journalctl -u energy-frontend -f"
echo "   sudo tail -f /var/log/nginx/error.log"
echo ""

