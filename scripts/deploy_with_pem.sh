#!/bin/bash
# PEM 키를 사용한 서버 배포 스크립트

set -e

# 서버 정보
SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/$SERVER_USER/energy-platform"
GIT_REPO_HTTPS="https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git"
PROJECT_DIR="/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"
PEM_FILE="$PROJECT_DIR/google_compute_engine.pem"

echo "🚀 PEM 키를 사용한 서버 배포 시작..."
echo "서버: ${SERVER_USER}@${SERVER_IP}"
echo "배포 경로: ${REMOTE_DIR}"
echo ""

# PEM 파일 확인
if [ ! -f "$PEM_FILE" ]; then
    echo "❌ PEM 파일을 찾을 수 없습니다: $PEM_FILE"
    echo ""
    echo "PPK 파일이 있는 경우 다음 명령으로 변환하세요:"
    echo "  brew install putty"
    echo "  puttygen google_compute_engine.ppk -O private-openssh -o google_compute_engine.pem"
    echo ""
    exit 1
fi

# PEM 파일 권한 설정
echo "🔐 PEM 파일 권한 설정 중..."
chmod 600 "$PEM_FILE"
echo "✅ 권한 설정 완료"

# SSH 옵션 설정 (config 파일 우회)
SSH_OPTS="-i $PEM_FILE -o IdentitiesOnly=yes -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -F /dev/null"

# 서버 연결 테스트
echo "🔌 서버 연결 테스트 중..."
if ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} "echo '연결 성공'" 2>/dev/null; then
    echo "✅ 서버 연결 확인"
else
    echo "❌ 서버 연결 실패"
    echo ""
    echo "다음 명령어로 수동 연결을 시도하세요:"
    echo "ssh -i $PEM_FILE -o IdentitiesOnly=yes -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -F /dev/null ${SERVER_USER}@${SERVER_IP}"
    exit 1
fi

# 서버 환경 설정
echo "📦 서버 환경 설정 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
# Git 설치 확인
if ! command -v git &> /dev/null; then
    echo "📦 Git 설치 중..."
    sudo apt-get update
    sudo apt-get install -y git
fi

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo "📦 Python3 설치 중..."
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Node.js 확인
if ! command -v node &> /dev/null; then
    echo "📦 Node.js 설치 중..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

echo "✅ 서버 환경 준비 완료"
ENDSSH

# Git repository 설정
echo "📥 Git repository 설정 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
# 디렉토리 생성
mkdir -p ${REMOTE_DIR}
cd ${REMOTE_DIR}

# 기존 Git repository 확인
if [ -d ".git" ]; then
    echo "📥 Git repository 업데이트 중..."
    git fetch origin
    git reset --hard origin/main
    git clean -fd
    echo "✅ Git 업데이트 완료"
else
    echo "📥 Git repository clone 중..."
    git clone ${GIT_REPO_HTTPS} .
    echo "✅ Git clone 완료"
fi

# 현재 브랜치 확인
echo "📍 현재 브랜치: \$(git branch --show-current)"
echo "📍 최근 커밋: \$(git log -1 --oneline)"
ENDSSH

# 서버 설정 스크립트 전송
echo "⚙️  서버 설정 스크립트 전송 중..."
scp $SSH_OPTS "$PROJECT_DIR/scripts/server_setup.sh" ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/ || {
    echo "⚠️  설정 스크립트 전송 실패 (수동 실행 필요)"
}

# 서버 설정 실행
echo "⚙️  서버 설정 실행 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
cd ${REMOTE_DIR}
if [ -f "server_setup.sh" ]; then
    chmod +x server_setup.sh
    bash server_setup.sh
else
    echo "⚠️  server_setup.sh를 찾을 수 없습니다."
    echo "수동으로 실행하세요:"
    echo "cd ${REMOTE_DIR}/backend"
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
fi
ENDSSH

echo ""
echo "🎉 배포 완료!"
echo ""
echo "서버 정보:"
echo "  접속: ssh -i $PEM_FILE -o IdentitiesOnly=yes -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -F /dev/null ${SERVER_USER}@${SERVER_IP}"
echo "  위치: ${REMOTE_DIR}"
echo ""
echo "다음 단계:"
echo "1. 서버에 접속"
echo "2. cd ${REMOTE_DIR}/backend"
echo "3. .env 파일 생성 및 설정"
echo "4. source venv/bin/activate"
echo "5. uvicorn src.main:app --host 0.0.0.0 --port 8000"
echo ""

