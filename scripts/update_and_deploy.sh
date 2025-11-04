#!/bin/bash
# 서버 업데이트 및 재배포 스크립트

set -e

# 설정
SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/$SERVER_USER/energy-platform"
PROJECT_DIR="/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"
PEM_FILE="$PROJECT_DIR/google_compute_engine.pem"

echo "🔄 서버 업데이트 및 재배포 시작..."
echo "서버: ${SERVER_USER}@${SERVER_IP}"
echo ""

# PEM 파일 확인
if [ -f "$PEM_FILE" ]; then
    chmod 600 "$PEM_FILE"
    SSH_OPTS="-i $PEM_FILE -o IdentitiesOnly=yes -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -F /dev/null"
    echo "✅ PEM 파일 사용"
else
    echo "⚠️  PEM 파일 없음. SSH 키를 사용합니다."
    SSH_OPTS="-o ServerAliveInterval=60 -o StrictHostKeyChecking=no"
fi

# 서버 연결 테스트
echo "🔌 서버 연결 테스트 중..."
if ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} "echo '연결 성공'" 2>/dev/null; then
    echo "✅ 서버 연결 확인"
else
    echo "❌ 서버 연결 실패"
    exit 1
fi

# 1. Git 업데이트
echo ""
echo "📥 코드 업데이트 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

cd ${REMOTE_DIR}

# Git 업데이트
echo "📥 Git repository 업데이트 중..."
git fetch origin > /dev/null 2>&1
git reset --hard origin/main || git reset --hard origin/master
git clean -fd

echo "✅ 코드 업데이트 완료"
ENDSSH

# 2. 백엔드 업데이트
echo ""
echo "⚙️  백엔드 업데이트 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

cd ${REMOTE_DIR}/backend

if [ -d "venv" ]; then
    source venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        echo "📦 백엔드 의존성 업데이트 중..."
        pip install --upgrade pip > /dev/null 2>&1
        pip install -r requirements.txt > /dev/null 2>&1
    fi
    
    echo "✅ 백엔드 업데이트 완료"
else
    echo "⚠️  가상환경이 없습니다. 새로 생성합니다..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
fi
ENDSSH

# 3. 프론트엔드 업데이트 및 빌드
echo ""
echo "⚙️  프론트엔드 업데이트 및 빌드 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

cd ${REMOTE_DIR}/frontend

if [ -f "package.json" ]; then
    echo "📦 프론트엔드 의존성 업데이트 중..."
    npm install > /dev/null 2>&1 || echo "⚠️  의존성 설치 경고"
    
    echo "🏗️  프론트엔드 빌드 중..."
    npm run build > /dev/null 2>&1 || {
        echo "❌ 빌드 실패. 로그 확인:"
        npm run build 2>&1 | tail -20
        exit 1
    }
    
    echo "✅ 프론트엔드 빌드 완료"
else
    echo "⚠️  package.json을 찾을 수 없습니다."
fi
ENDSSH

# 4. 서비스 재시작
echo ""
echo "🚀 서비스 재시작 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

# 백엔드 재시작
if sudo systemctl is-active --quiet energy-backend; then
    echo "🔄 백엔드 재시작 중..."
    sudo systemctl restart energy-backend
    sleep 2
    sudo systemctl status energy-backend --no-pager -l || echo "⚠️  백엔드 상태 확인 필요"
else
    echo "⚠️  백엔드 서비스가 실행 중이 아닙니다. 시작합니다..."
    sudo systemctl start energy-backend
    sudo systemctl enable energy-backend
    sleep 2
    sudo systemctl status energy-backend --no-pager -l || echo "⚠️  백엔드 상태 확인 필요"
fi

# 프론트엔드 재시작
if sudo systemctl is-active --quiet energy-frontend; then
    echo "🔄 프론트엔드 재시작 중..."
    sudo systemctl restart energy-frontend
    sleep 2
    sudo systemctl status energy-frontend --no-pager -l || echo "⚠️  프론트엔드 상태 확인 필요"
else
    echo "⚠️  프론트엔드 서비스가 실행 중이 아닙니다. 시작합니다..."
    sudo systemctl start energy-frontend
    sudo systemctl enable energy-frontend
    sleep 2
    sudo systemctl status energy-frontend --no-pager -l || echo "⚠️  프론트엔드 상태 확인 필요"
fi

# Nginx 재시작
echo "🔄 Nginx 재시작 중..."
sudo systemctl restart nginx
sudo systemctl status nginx --no-pager -l || echo "⚠️  Nginx 상태 확인 필요"

echo "✅ 서비스 재시작 완료"
ENDSSH

# 5. 상태 확인
echo ""
echo "📊 서비스 상태 확인 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
echo "=== 백엔드 상태 ==="
sudo systemctl is-active energy-backend && echo "✅ 백엔드 실행 중" || echo "❌ 백엔드 미실행"

echo ""
echo "=== 프론트엔드 상태 ==="
sudo systemctl is-active energy-frontend && echo "✅ 프론트엔드 실행 중" || echo "❌ 프론트엔드 미실행"

echo ""
echo "=== Nginx 상태 ==="
sudo systemctl is-active nginx && echo "✅ Nginx 실행 중" || echo "❌ Nginx 미실행"

echo ""
echo "=== 포트 확인 ==="
sudo netstat -tulpn | grep -E ':(8000|3000|80|443)' || echo "⚠️  포트 확인 실패"

echo ""
echo "=== 최근 로그 (백엔드) ==="
sudo journalctl -u energy-backend -n 10 --no-pager || echo "⚠️  로그 확인 실패"

echo ""
echo "=== 최근 로그 (프론트엔드) ==="
sudo journalctl -u energy-frontend -n 10 --no-pager || echo "⚠️  로그 확인 실패"
ENDSSH

echo ""
echo "🎉 업데이트 및 재배포 완료!"
echo ""
echo "🌐 접속 확인:"
echo "  https://damcp.gngmeta.com/energy-demand"
echo "  https://damcp.gngmeta.com/api/health"
echo ""
echo "📋 문제 해결:"
echo "  서비스가 실행되지 않는 경우:"
echo "    ssh ${SERVER_USER}@${SERVER_IP}"
echo "    sudo systemctl status energy-backend"
echo "    sudo systemctl status energy-frontend"
echo "    sudo journalctl -u energy-backend -f"
echo "    sudo journalctl -u energy-frontend -f"
echo ""


