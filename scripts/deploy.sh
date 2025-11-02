#!/bin/bash
# GCP Compute Engine 배포 스크립트

set -e

# 서버 정보
SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/$SERVER_USER/energy-platform"
PROJECT_DIR="/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"

echo "🚀 배포 시작..."

# SSH 키 확인
if [ ! -f "$PROJECT_DIR/google_compute_engine.ppk" ]; then
    echo "❌ SSH 키 파일을 찾을 수 없습니다: google_compute_engine.ppk"
    exit 1
fi

# PPK를 OpenSSH 형식으로 변환 시도
SSH_KEY="$PROJECT_DIR/google_compute_engine_key"
if [ ! -f "$SSH_KEY" ]; then
    echo "📝 SSH 키 변환 중..."
    # puttygen이 있으면 변환
    if command -v puttygen &> /dev/null; then
        puttygen "$PROJECT_DIR/google_compute_engine.ppk" -O private-openssh -o "$SSH_KEY"
        chmod 600 "$SSH_KEY"
    else
        # OpenSSH 형식 키가 이미 있을 수도 있음
        echo "⚠️  puttygen이 없습니다. 직접 키를 사용합니다."
        SSH_KEY="$PROJECT_DIR/google_compute_engine.ppk"
    fi
fi

# SSH 옵션 설정
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
if [ -f "$SSH_KEY" ] && [ "$SSH_KEY" != "$PROJECT_DIR/google_compute_engine.ppk" ]; then
    SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
fi

# 서버 연결 테스트
echo "🔌 서버 연결 테스트..."
if ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} "echo '연결 성공'" 2>/dev/null; then
    echo "✅ 서버 연결 확인"
else
    echo "❌ 서버 연결 실패. 키 인증이 필요할 수 있습니다."
    echo "다음 명령어로 수동 연결을 시도하세요:"
    echo "ssh ${SERVER_USER}@${SERVER_IP}"
    exit 1
fi

# 서버에 디렉토리 생성
echo "📁 서버 디렉토리 생성..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
mkdir -p /home/metal/energy-platform
cd /home/metal/energy-platform
mkdir -p backend frontend infrastructure scripts
echo "✅ 디렉토리 생성 완료"
ENDSSH

# 프로젝트 파일 전송 (rsync 사용)
echo "📤 프로젝트 파일 전송 중..."
cd "$PROJECT_DIR"

# .gitignore에 추가할 파일들 제외하고 전송
rsync -avz --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='*.ppk' \
    --exclude='.DS_Store' \
    $SSH_OPTS \
    ./ ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/

echo "✅ 파일 전송 완료"

# 서버에서 초기 설정 실행
echo "⚙️  서버에서 초기 설정 중..."
ssh $SSH_OPTS ${SERVER_USER}@${SERVER_IP} << ENDSSH
cd ${REMOTE_DIR}

# Python 확인 및 설치
if ! command -v python3 &> /dev/null; then
    echo "📦 Python3 설치 중..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Node.js 확인 및 설치
if ! command -v node &> /dev/null; then
    echo "📦 Node.js 설치 중..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Docker 확인 및 설치
if ! command -v docker &> /dev/null; then
    echo "📦 Docker 설치 중..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# PostgreSQL 클라이언트 설치
if ! command -v psql &> /dev/null; then
    echo "📦 PostgreSQL 클라이언트 설치 중..."
    sudo apt-get install -y postgresql-client
fi

echo "✅ 시스템 준비 완료"
ENDSSH

echo ""
echo "🎉 배포 완료!"
echo ""
echo "서버 접속: ssh ${SERVER_USER}@${SERVER_IP}"
echo "프로젝트 위치: ${REMOTE_DIR}"
echo ""
echo "다음 단계:"
echo "1. 서버에 접속하여 .env 파일 설정"
echo "2. backend/ 디렉토리에서 python3 -m venv venv && source venv/bin/activate"
echo "3. pip install -r requirements.txt"
echo "4. frontend/ 디렉토리에서 npm install"
echo "5. uvicorn src.main:app --host 0.0.0.0 --port 8000 (백엔드 실행)"

