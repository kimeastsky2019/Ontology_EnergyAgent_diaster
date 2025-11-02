#!/bin/bash
# 빠른 배포 스크립트 - SSH 키가 이미 설정된 경우

SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/$SERVER_USER/energy-platform"
TAR_FILE="/tmp/energy-platform-deploy.tar.gz"

echo "🚀 빠른 배포 시작..."

# 1. 프로젝트 압축
echo "📦 프로젝트 압축 중..."
cd "$(dirname "$0")/.."
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='.env' \
    --exclude='*.ppk' \
    --exclude='.DS_Store' \
    --exclude='*.log' \
    -czf "$TAR_FILE" .

echo "✅ 압축 완료: $(du -h "$TAR_FILE" | cut -f1)"

# 2. 서버에 디렉토리 생성
echo "📁 서버 디렉토리 생성 중..."
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} \
    "mkdir -p ${REMOTE_DIR}" || {
    echo "❌ 서버 디렉토리 생성 실패"
    exit 1
}

# 3. 파일 전송
echo "📤 파일 전송 중..."
scp -o StrictHostKeyChecking=no "$TAR_FILE" \
    ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/ || {
    echo "❌ 파일 전송 실패"
    echo "수동 전송 명령어:"
    echo "scp $TAR_FILE ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"
    exit 1
}

# 4. 서버에서 압축 해제
echo "📦 서버에서 압축 해제 중..."
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} \
    "cd ${REMOTE_DIR} && tar -xzf energy-platform-deploy.tar.gz && rm energy-platform-deploy.tar.gz" || {
    echo "❌ 압축 해제 실패"
    exit 1
}

# 5. 설정 스크립트 전송
echo "⚙️  설정 스크립트 전송 중..."
scp -o StrictHostKeyChecking=no scripts/server_setup.sh \
    ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/ || {
    echo "⚠️  설정 스크립트 전송 실패 (수동 실행 필요)"
}

# 6. 로컬 압축 파일 삭제
rm -f "$TAR_FILE"

echo ""
echo "✅ 배포 완료!"
echo ""
echo "서버 접속: ssh ${SERVER_USER}@${SERVER_IP}"
echo "프로젝트 위치: ${REMOTE_DIR}"
echo ""
echo "다음 단계:"
echo "1. ssh ${SERVER_USER}@${SERVER_IP}"
echo "2. cd ${REMOTE_DIR}"
echo "3. bash server_setup.sh"
echo "4. cd backend && source venv/bin/activate"
echo "5. uvicorn src.main:app --host 0.0.0.0 --port 8000"

