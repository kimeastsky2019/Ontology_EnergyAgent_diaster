#!/bin/bash
# Git을 사용한 서버 배포 스크립트

set -e

SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/$SERVER_USER/energy-platform"
GIT_REPO="git@github.com:kimeastsky2019/Ontology_EnergyAgent_diaster.git"
PROJECT_DIR="/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"

echo "🚀 Git 배포 시작..."
echo "서버: ${SERVER_USER}@${SERVER_IP}"
echo "배포 경로: ${REMOTE_DIR}"
echo ""

# SSH 연결 테스트
echo "🔌 서버 연결 테스트..."
if ssh -o ConnectTimeout=5 gcp-energy "echo '연결 확인'" 2>/dev/null; then
    echo "✅ 서버 연결 성공"
else
    echo "❌ 서버 연결 실패"
    echo "먼저 SSH 키 설정을 실행하세요: bash scripts/setup_ssh_key.sh"
    exit 1
fi

# 서버에 Git 설치 확인 및 설치
echo "📦 서버에 Git 설치 확인 중..."
ssh gcp-energy << 'ENDSSH'
if ! command -v git &> /dev/null; then
    echo "📦 Git 설치 중..."
    sudo apt-get update
    sudo apt-get install -y git
else
    echo "✅ Git 이미 설치됨: $(git --version)"
fi
ENDSSH

# 서버에 디렉토리 생성 및 Git 설정
echo "📁 서버 디렉토리 설정 중..."
ssh gcp-energy << ENDSSH
# 디렉토리 생성
mkdir -p ${REMOTE_DIR}
cd ${REMOTE_DIR}

# 이미 Git repository가 있으면 pull, 없으면 clone
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
        echo "⚠️  기존 파일이 있습니다. 백업 중..."
        mv * .[^.]* ../energy-platform-backup-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true
    fi
    
    # GitHub SSH 키가 서버에 있는지 확인 필요
    # 만약 없다면 HTTPS로 clone하거나 SSH 키를 서버에 추가해야 함
    if ssh -o ConnectTimeout=5 -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "✅ GitHub SSH 인증 확인"
        git clone ${GIT_REPO} .
    else
        echo "⚠️  GitHub SSH 인증 실패. HTTPS로 clone합니다."
        git clone https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git .
    fi
    echo "✅ Git clone 완료"
fi
ENDSSH

# 서버 설정 스크립트 전송 및 실행
echo "⚙️  서버 설정 중..."
scp scripts/server_setup.sh gcp-energy:${REMOTE_DIR}/

ssh gcp-energy << ENDSSH
cd ${REMOTE_DIR}
chmod +x server_setup.sh
bash server_setup.sh
ENDSSH

echo ""
echo "✅ Git 배포 완료!"
echo ""
echo "서버 정보:"
echo "  접속: ssh gcp-energy"
echo "  위치: ${REMOTE_DIR}"
echo ""
echo "다음 단계:"
echo "1. ssh gcp-energy"
echo "2. cd ${REMOTE_DIR}/backend"
echo "3. cp .env.example .env && nano .env"
echo "4. source venv/bin/activate"
echo "5. uvicorn src.main:app --host 0.0.0.0 --port 8000"

