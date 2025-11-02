#!/bin/bash
# 서버 배포 스크립트

set -e

SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/$SERVER_USER/energy-platform"
PROJECT_DIR="/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"

echo "🚀 GCP Compute Engine 배포 시작..."
echo "서버: ${SERVER_USER}@${SERVER_IP}"
echo "배포 경로: ${REMOTE_DIR}"
echo ""

# 프로젝트 디렉토리로 이동
cd "$PROJECT_DIR"

# 임시 압축 파일 생성 (제외 파일 제외)
echo "📦 프로젝트 파일 압축 중..."
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='.env' \
    --exclude='*.ppk' \
    --exclude='.DS_Store' \
    --exclude='*.log' \
    -czf /tmp/energy-platform-deploy.tar.gz .

echo "✅ 압축 완료: /tmp/energy-platform-deploy.tar.gz"

# 서버에 압축 파일 전송
echo "📤 서버로 파일 전송 중..."
echo "⚠️  SSH 키 인증이 필요합니다."
echo ""

# SSH를 통한 배포 (수동 실행 필요)
echo "다음 명령어를 실행하세요:"
echo ""
echo "# 1. 서버에 디렉토리 생성"
echo "ssh ${SERVER_USER}@${SERVER_IP} 'mkdir -p ${REMOTE_DIR}'"
echo ""
echo "# 2. 압축 파일 전송"
echo "scp /tmp/energy-platform-deploy.tar.gz ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"
echo ""
echo "# 3. 서버에서 압축 해제 및 설정"
echo "ssh ${SERVER_USER}@${SERVER_IP} 'cd ${REMOTE_DIR} && tar -xzf energy-platform-deploy.tar.gz && rm energy-platform-deploy.tar.gz'"
echo ""
echo "# 4. 서버 설정 스크립트 실행"
echo "scp scripts/server_setup.sh ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"
echo "ssh ${SERVER_USER}@${SERVER_IP} 'cd ${REMOTE_DIR} && chmod +x server_setup.sh && bash server_setup.sh'"
echo ""

# 자동 배포 시도 (키가 설정된 경우)
if [ -f "google_compute_engine.ppk" ]; then
    echo "자동 배포 시도 중..."
    
    # 서버 디렉토리 생성
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
        ${SERVER_USER}@${SERVER_IP} \
        "mkdir -p ${REMOTE_DIR}" 2>&1 || {
        echo "❌ 자동 배포 실패. 위의 수동 명령어를 사용하세요."
        echo ""
        echo "SSH 키 설정이 필요한 경우:"
        echo "1. PPK 파일을 OpenSSH 형식으로 변환"
        echo "2. ~/.ssh/config 파일에 설정 추가"
        exit 1
    }
    
    # 압축 파일 전송
    scp -o StrictHostKeyChecking=no \
        /tmp/energy-platform-deploy.tar.gz \
        ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/ 2>&1 || {
        echo "❌ 파일 전송 실패. 수동으로 전송하세요."
        exit 1
    }
    
    # 서버에서 압축 해제
    ssh -o StrictHostKeyChecking=no \
        ${SERVER_USER}@${SERVER_IP} \
        "cd ${REMOTE_DIR} && tar -xzf energy-platform-deploy.tar.gz && rm energy-platform-deploy.tar.gz" 2>&1 || {
        echo "❌ 압축 해제 실패"
        exit 1
    }
    
    # 설정 스크립트 전송 및 실행
    scp -o StrictHostKeyChecking=no \
        scripts/server_setup.sh \
        ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/ 2>&1 || echo "설정 스크립트 전송 실패 (수동 실행 필요)"
    
    echo "✅ 배포 완료!"
    echo ""
    echo "서버 접속: ssh ${SERVER_USER}@${SERVER_IP}"
    echo "프로젝트 위치: ${REMOTE_DIR}"
else
    echo "⚠️  SSH 키 파일을 찾을 수 없습니다."
fi

