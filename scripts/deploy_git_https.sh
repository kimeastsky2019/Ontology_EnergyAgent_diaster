#!/bin/bash
# Git HTTPS 배포 스크립트 (SSH 키 불필요)

set -e

SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/$SERVER_USER/energy-platform"
GIT_REPO="https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git"

echo "🚀 Git 배포 시작 (HTTPS 방식)..."
echo "서버: ${SERVER_USER}@${SERVER_IP}"
echo "배포 경로: ${REMOTE_DIR}"
echo ""

# SSH 연결 방법 선택
echo "🔌 서버 연결 방법 선택..."
SSH_CMD=""

# 방법 1: SSH config 사용
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no gcp-energy "echo 'test'" 2>/dev/null; then
    SSH_CMD="ssh -o StrictHostKeyChecking=no gcp-energy"
    echo "✅ SSH config 사용"
# 방법 2: 직접 키 사용
elif [ -f "google_compute_engine.ppk" ]; then
    # PPK 파일을 직접 사용하려면 putty를 통해 변환 필요
    SSH_CMD="ssh -o StrictHostKeyChecking=no -o PubkeyAcceptedKeyTypes=+ssh-rsa -i google_compute_engine.ppk ${SERVER_USER}@${SERVER_IP}"
    echo "⚠️  PPK 파일 사용 시도 (OpenSSH 형식 변환 권장)"
else
    echo "❌ SSH 연결 방법을 찾을 수 없습니다."
    echo ""
    echo "수동 배포 방법:"
    echo "1. 서버에 수동으로 접속: ssh ${SERVER_USER}@${SERVER_IP}"
    echo "2. 다음 명령어를 서버에서 실행:"
    echo "   mkdir -p ${REMOTE_DIR}"
    echo "   cd ${REMOTE_DIR}"
    echo "   git clone ${GIT_REPO} ."
    exit 1
fi

# 서버 연결 테스트
echo "🔌 서버 연결 테스트..."
if $SSH_CMD "echo '연결 확인'" 2>/dev/null; then
    echo "✅ 서버 연결 성공"
else
    echo "❌ 서버 연결 실패"
    echo ""
    echo "수동 배포 방법:"
    echo "1. 서버에 수동으로 접속하세요"
    echo "2. 다음 명령어를 서버에서 실행:"
    echo "   mkdir -p ${REMOTE_DIR}"
    echo "   cd ${REMOTE_DIR}"
    echo "   git clone ${GIT_REPO} ."
    echo "   bash <(curl -sL scripts/server_setup.sh)"
    exit 1
fi

# 서버 환경 설정
echo "📦 서버 환경 설정 중..."
$SSH_CMD << 'ENDSSH'
# Git 설치
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
$SSH_CMD << ENDSSH
# 디렉토리 생성
mkdir -p ${REMOTE_DIR}
cd ${REMOTE_DIR}

# 기존 Git repository 확인 및 업데이트
if [ -d ".git" ]; then
    echo "📥 Git repository 업데이트 중..."
    git fetch origin
    git reset --hard origin/main
    git clean -fd
    echo "✅ Git 업데이트 완료"
else
    echo "📥 Git repository clone 중..."
    
    # 기존 파일이 있으면 백업
    if [ "$(ls -A . 2>/dev/null)" ]; then
        echo "⚠️  기존 파일 백업 중..."
        mkdir -p ../energy-platform-backup-$(date +%Y%m%d-%H%M%S)
        mv * .[^.]* ../energy-platform-backup-$(date +%Y%m%d-%H%M%S)/ 2>/dev/null || true
    fi
    
    # HTTPS로 clone
    git clone ${GIT_REPO} .
    echo "✅ Git clone 완료"
fi

# 현재 상태 확인
echo ""
echo "📍 현재 브랜치: \$(git branch --show-current)"
echo "📍 최근 커밋: \$(git log -1 --oneline)"
echo "📍 커밋 해시: \$(git rev-parse HEAD)"
ENDSSH

# 서버 설정 스크립트 전송 및 실행
echo "⚙️  서버 설정 스크립트 실행 중..."

# 스크립트를 직접 실행
$SSH_CMD << 'ENDSSH'
cd /home/metal/energy-platform/backend

# Python 가상환경 생성 및 의존성 설치
if [ ! -d "venv" ]; then
    echo "📦 Python 가상환경 생성 중..."
    python3 -m venv venv
fi

echo "📦 백엔드 의존성 설치 중..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Frontend 의존성 설치
cd ../frontend
if [ -f "package.json" ]; then
    echo "📦 프론트엔드 의존성 설치 중..."
    npm install
fi

echo "✅ 서버 설정 완료"
ENDSSH

echo ""
echo "✅ Git 배포 완료!"
echo ""
echo "서버 정보:"
echo "  접속: $SSH_CMD"
echo "  위치: ${REMOTE_DIR}"
echo ""
echo "다음 단계:"
echo "1. 서버 접속: $SSH_CMD"
echo "2. cd ${REMOTE_DIR}/backend"
echo "3. cp .env.example .env && nano .env"
echo "4. source venv/bin/activate"
echo "5. uvicorn src.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "업데이트 방법:"
echo "  cd ${REMOTE_DIR} && git pull && cd backend && source venv/bin/activate && pip install -r requirements.txt"

