#!/bin/bash
# SSH 키 설정 스크립트

set -e

PROJECT_DIR="/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"
PPK_FILE="$PROJECT_DIR/google_compute_engine.ppk"
SSH_KEY="$PROJECT_DIR/google_compute_engine_key"
SSH_DIR="$HOME/.ssh"
CONFIG_FILE="$SSH_DIR/config"

echo "🔐 SSH 키 설정 시작..."

# .ssh 디렉토리 생성
mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"

# PPK 파일 확인
if [ ! -f "$PPK_FILE" ]; then
    echo "❌ PPK 파일을 찾을 수 없습니다: $PPK_FILE"
    exit 1
fi

# puttygen이 있으면 변환
if command -v puttygen &> /dev/null; then
    echo "📝 PPK를 OpenSSH 형식으로 변환 중..."
    puttygen "$PPK_FILE" -O private-openssh -o "$SSH_KEY"
    chmod 600 "$SSH_KEY"
    echo "✅ 변환 완료: $SSH_KEY"
elif command -v putty &> /dev/null; then
    echo "⚠️  puttygen이 없습니다. putty 설치가 필요합니다."
    echo "설치: brew install putty"
    exit 1
else
    echo "⚠️  puttygen이 없습니다."
    echo ""
    echo "수동 변환 방법:"
    echo "1. PuTTY Gen 사용 (Windows/Mac)"
    echo "2. 또는 다음 명령어로 설치: brew install putty"
    echo ""
    echo "임시로 PPK 파일을 그대로 사용할 수도 있습니다."
    SSH_KEY="$PPK_FILE"
fi

# SSH config 파일에 설정 추가
echo "📝 SSH config 설정 중..."

# config 파일이 없으면 생성
if [ ! -f "$CONFIG_FILE" ]; then
    touch "$CONFIG_FILE"
    chmod 600 "$CONFIG_FILE"
fi

# 이미 설정이 있는지 확인
if grep -q "Host gcp-energy" "$CONFIG_FILE" 2>/dev/null; then
    echo "⚠️  SSH config에 이미 설정이 있습니다."
    echo "수동으로 확인하세요: $CONFIG_FILE"
else
    # 설정 추가
    cat >> "$CONFIG_FILE" << EOF

# GCP Energy Platform Server
Host gcp-energy
    HostName 34.47.89.217
    User metal
    IdentityFile $SSH_KEY
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF
    echo "✅ SSH config 설정 완료"
fi

# 연결 테스트
echo "🔌 서버 연결 테스트 중..."
if ssh -o ConnectTimeout=5 gcp-energy "echo '연결 성공'" 2>/dev/null; then
    echo "✅ SSH 연결 성공!"
else
    echo "⚠️  자동 연결 실패. 다음 명령어로 수동 연결을 시도하세요:"
    echo "ssh gcp-energy"
    echo ""
    echo "또는 직접:"
    echo "ssh -i $SSH_KEY metal@34.47.89.217"
fi

echo ""
echo "✅ SSH 키 설정 완료!"
echo ""
echo "사용법:"
echo "  ssh gcp-energy"
echo "또는"
echo "  ssh -i $SSH_KEY metal@34.47.89.217"

