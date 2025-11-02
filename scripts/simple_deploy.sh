#!/bin/bash
# 간단한 배포 스크립트 - 수동으로 키를 지정해야 함

set -e

SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/$SERVER_USER/energy-platform"
PROJECT_DIR="/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"

echo "🚀 배포 시작..."
echo "⚠️  SSH 키 인증이 필요합니다."
echo ""

# 서버에 디렉토리 생성 (수동 SSH 접속 필요)
echo "📁 서버에 디렉토리를 생성합니다..."
echo "다음 명령어를 서버에서 실행하세요:"
echo "ssh ${SERVER_USER}@${SERVER_IP}"
echo ""
echo "서버 접속 후 실행:"
echo "mkdir -p ${REMOTE_DIR}"
echo "cd ${REMOTE_DIR}"
echo ""

# 파일 전송 준비
echo "📤 파일 전송 준비..."
cd "$PROJECT_DIR"

# 전송할 파일 목록
echo "전송할 파일:"
find . -type f \
    ! -path './.git/*' \
    ! -path '*/__pycache__/*' \
    ! -path '*/venv/*' \
    ! -path '*/node_modules/*' \
    ! -path '*.pyc' \
    ! -name '.env' \
    ! -name '*.ppk' \
    ! -name '.DS_Store' | head -20

echo ""
echo "✅ 배포 스크립트 준비 완료"
echo ""
echo "다음 단계:"
echo "1. SSH 키를 사용하여 서버에 접속:"
echo "   ssh -i google_compute_engine.ppk ${SERVER_USER}@${SERVER_IP}"
echo ""
echo "2. 또는 수동으로 다음 명령어 실행:"
echo "   rsync -avz --exclude='.git' --exclude='venv' --exclude='node_modules' \\"
echo "     -e 'ssh -i google_compute_engine.ppk' \\"
echo "     ./ ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"

