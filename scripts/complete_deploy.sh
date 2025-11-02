#!/bin/bash
# 완전한 Git 배포 스크립트 (HTTPS fallback 포함)

set -e

SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/$SERVER_USER/energy-platform"
GIT_REPO_HTTPS="https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git"
GIT_REPO_SSH="git@github.com:kimeastsky2019/Ontology_EnergyAgent_diaster.git"

echo "🚀 Git 배포 시작..."
echo "서버: ${SERVER_USER}@${SERVER_IP}"
echo "배포 경로: ${REMOTE_DIR}"
echo ""

# SSH 연결 방법 확인
SSH_CMD="ssh gcp-energy"
if ! ssh -o ConnectTimeout=5 gcp-energy "echo 'test'" 2>/dev/null; then
    # SSH config가 작동하지 않으면 직접 연결 시도
    SSH_KEY_FILE="/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster/google_compute_engine.ppk"
    if [ -f "$SSH_KEY_FILE" ]; then
        SSH_CMD="ssh -o StrictHostKeyChecking=no -i $SSH_KEY_FILE ${SERVER_USER}@${SERVER_IP}"
        echo "⚠️  SSH config 사용 불가. 직접 키 사용: $SSH_KEY_FILE"
    else
        echo "❌ SSH 연결 불가. SSH 키를 확인하세요."
        exit 1
    fi
fi

# 서버 연결 테스트
echo "🔌 서버 연결 테스트..."
if $SSH_CMD "echo '연결 확인'" 2>/dev/null; then
    echo "✅ 서버 연결 성공"
else
    echo "❌ 서버 연결 실패"
    echo ""
    echo "다음 명령어로 수동 연결을 시도하세요:"
    echo "ssh gcp-energy"
    echo "또는"
    echo "ssh -i google_compute_engine.ppk metal@34.47.89.217"
    exit 1
fi

# 서버에 필요한 도구 설치
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

# 기존 Git repository 확인
if [ -d ".git" ]; then
    echo "📥 Git repository 업데이트 중..."
    git fetch origin
    git reset --hard origin/main
    git clean -fd
    echo "✅ Git 업데이트 완료"
else
    echo "📥 Git repository clone 중..."
    
    # HTTPS로 clone (SSH 키 없이도 가능)
    if git clone ${GIT_REPO_HTTPS} . 2>/dev/null; then
        echo "✅ Git clone 완료 (HTTPS)"
    else
        echo "❌ Git clone 실패"
        exit 1
    fi
fi

# 현재 브랜치 확인
echo "📍 현재 브랜치: \$(git branch --show-current)"
echo "📍 최근 커밋: \$(git log -1 --oneline)"
ENDSSH

# 서버 설정 스크립트 전송 및 실행
echo "⚙️  서버 설정 스크립트 전송 중..."
scp -o StrictHostKeyChecking=no scripts/server_setup.sh gcp-energy:${REMOTE_DIR}/ 2>/dev/null || \
    scp -o StrictHostKeyChecking=no -i google_compute_engine.ppk scripts/server_setup.sh metal@34.47.89.217:${REMOTE_DIR}/ 2>/dev/null || {
    echo "⚠️  설정 스크립트 전송 실패 (수동 전송 필요)"
}

echo "⚙️  서버 설정 실행 중..."
$SSH_CMD << ENDSSH
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
echo "✅ Git 배포 완료!"
echo ""
echo "서버 정보:"
echo "  접속: ssh gcp-energy (또는 직접 ssh 명령어)"
echo "  위치: ${REMOTE_DIR}"
echo ""
echo "다음 단계:"
echo "1. ssh gcp-energy"
echo "2. cd ${REMOTE_DIR}/backend"
echo "3. cp .env.example .env && nano .env"
echo "4. source venv/bin/activate"
echo "5. uvicorn src.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "업데이트 방법:"
echo "  cd ${REMOTE_DIR} && git pull"

