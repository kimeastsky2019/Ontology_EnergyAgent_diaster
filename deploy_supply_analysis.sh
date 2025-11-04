#!/bin/bash

# Supply Analysis 배포 스크립트
# 도메인: damcp.gngmeta.com/s_an

set -e

echo "🚀 Supply Analysis 배포 시작..."
echo "================================"

# 서버 정보
SERVER_IP="34.47.89.217"
SERVER_USER="metal"
REMOTE_DIR="/home/metal/supply_anlysis"

# SSH 키 파일 찾기 (PEM 우선, PPK는 변환 필요)
SSH_KEY=""
if [ -f "google_compute_engine.pem" ]; then
    SSH_KEY="google_compute_engine.pem"
elif [ -f "google_compute_engine.ppk" ]; then
    echo "⚠️  PPK 파일을 찾았습니다. PEM 파일이 필요합니다."
    echo "PPK를 PEM으로 변환하려면:"
    echo "  puttygen google_compute_engine.ppk -O private-openssh -o google_compute_engine.pem"
    echo ""
    echo "또는 SSH config를 사용하세요."
    SSH_KEY=""
fi

# SSH 옵션 설정
if [ -n "$SSH_KEY" ] && [ -f "$SSH_KEY" ]; then
    chmod 600 "$SSH_KEY"
    SSH_OPTS="-F /dev/null -i $SSH_KEY -o IdentitiesOnly=yes -o ServerAliveInterval=60 -o StrictHostKeyChecking=no"
    echo "✅ SSH 키 파일 사용: $SSH_KEY"
elif [ -f ~/.ssh/config ] && grep -q "34.47.89.217\|gcp-energy" ~/.ssh/config; then
    # SSH config 사용 (config 파일에 오류가 있을 수 있으므로 무시)
    SSH_OPTS="-F /dev/null -o StrictHostKeyChecking=no"
    SERVER_HOST="${SERVER_USER}@${SERVER_IP}"
    echo "⚠️  SSH config에 오류가 있어 우회합니다"
else
    SSH_OPTS="-F /dev/null -o StrictHostKeyChecking=no"
    SERVER_HOST="${SERVER_USER}@${SERVER_IP}"
    echo "⚠️  SSH 키 없이 진행 (인증 필요할 수 있음)"
fi

echo ""
echo "1️⃣  서버 연결 테스트..."
if [ -n "$SERVER_HOST" ] && [ "$SERVER_HOST" != "gcp-energy" ]; then
    SERVER_TARGET="${SERVER_USER}@${SERVER_IP}"
else
    SERVER_TARGET="${SERVER_HOST:-${SERVER_USER}@${SERVER_IP}}"
fi

if ssh $SSH_OPTS $SERVER_TARGET "echo '연결 성공'" 2>/dev/null; then
    echo "✅ 서버 연결 확인"
else
    echo "❌ 서버 연결 실패"
    echo ""
    echo "SSH 키 설정 방법:"
    echo "1. PPK를 PEM으로 변환:"
    echo "   puttygen google_compute_engine.ppk -O private-openssh -o google_compute_engine.pem"
    echo ""
    echo "2. 또는 ~/.ssh/config에 추가:"
    echo "   Host gcp-energy"
    echo "       HostName 34.47.89.217"
    echo "       User metal"
    echo "       IdentityFile /path/to/key"
    echo ""
    exit 1
fi

echo ""
echo "2️⃣  supply_anlysis 폴더 압축..."
cd "/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='node_modules' \
    --exclude='.env' \
    --exclude='.DS_Store' \
    --exclude='*.log' \
    -czf /tmp/supply_anlysis.tar.gz supply_anlysis/

echo "✅ 압축 완료"

echo ""
echo "3️⃣  서버에 파일 업로드..."
scp $SSH_OPTS /tmp/supply_anlysis.tar.gz $SERVER_TARGET:/tmp/
echo "✅ 업로드 완료"

echo ""
echo "4️⃣  서버에서 배포 실행..."
ssh $SSH_OPTS $SERVER_TARGET << 'ENDSSH'
    echo "📋 서버에서 배포 작업 시작..."
    
    # 기존 디렉토리 백업
    if [ -d "/home/metal/supply_anlysis" ]; then
        echo "📦 기존 디렉토리 백업 중..."
        mv /home/metal/supply_anlysis /home/metal/supply_anlysis_backup_$(date +%Y%m%d_%H%M%S)
    fi
    
    # 디렉토리 생성
    mkdir -p /home/metal/supply_anlysis
    cd /home/metal/supply_anlysis
    
    # 압축 해제
    echo "📂 압축 해제 중..."
    tar -xzf /tmp/supply_anlysis.tar.gz --strip-components=1
    rm /tmp/supply_anlysis.tar.gz
    echo "✅ 압축 해제 완료"
    
    # Docker 및 Docker Compose 확인
    if ! command -v docker &> /dev/null; then
        echo "🐳 Docker 설치 중..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "🐳 Docker Compose 설치 중..."
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    # docker-compose.yml 포트 수정 (기존 서비스와 충돌 방지)
    echo "⚙️  docker-compose.yml 포트 설정 수정 중..."
    if [ -f "docker-compose.yml" ]; then
        # 포트 변경: frontend 3000 -> 3001, backend 8000 -> 8002, ai-agent 8001 -> 8003
        # PostgreSQL과 Redis 포트는 내부 네트워크만 사용하므로 외부 포트만 변경
        sed -i 's/- "3000:3000"/- "3001:3000"/g' docker-compose.yml
        sed -i 's/- "8000:8000"/- "8002:8000"/g' docker-compose.yml
        sed -i 's/- "8001:8001"/- "8003:8001"/g' docker-compose.yml
        sed -i 's/- "5432:5432"/- "5433:5432"/g' docker-compose.yml
        sed -i 's/- "6379:6379"/- "6380:6379"/g' docker-compose.yml
        
        # Frontend 환경 변수 수정 (상대 경로 사용)
        sed -i 's|REACT_APP_API_URL: http://localhost:8000|REACT_APP_API_URL: /s_an/api|g' docker-compose.yml
        sed -i 's|REACT_APP_AI_API_URL: http://localhost:8001|REACT_APP_AI_API_URL: /s_an/ai|g' docker-compose.yml
        
        echo "✅ 포트 설정 수정 완료"
        echo "   Frontend: 3001"
        echo "   Backend: 8002"
        echo "   AI Agent: 8003"
        echo "   PostgreSQL: 5433"
        echo "   Redis: 6380"
    fi
    
    # .env 파일 생성 (없는 경우)
    if [ ! -f ".env" ]; then
        echo "📝 .env 파일 생성 중..."
        cat > .env << 'ENVEOF'
WEATHER_API_KEY=demo_key
ENVIRONMENT=production
LOG_LEVEL=info
ENVEOF
        echo "✅ .env 파일 생성 완료"
    fi
    
    # 기존 컨테이너 중지 및 제거
    echo "🛑 기존 컨테이너 중지 중..."
    docker-compose down 2>/dev/null || true
    
    # Docker 이미지 빌드 및 시작
    echo "🐳 Docker 컨테이너 빌드 및 시작 중..."
    docker-compose up -d --build
    
    # 컨테이너 상태 확인
    echo ""
    echo "📊 컨테이너 상태 확인 중..."
    sleep 5
    docker-compose ps
    
    echo ""
    echo "✅ Docker 컨테이너 시작 완료"
ENDSSH

echo ""
echo "5️⃣  Nginx 설정 업데이트..."
ssh $SSH_OPTS $SERVER_TARGET << 'ENDSSH'
    echo "🌐 Nginx 설정 업데이트 중..."
    
    # 기존 nginx 설정 백업
    if [ -f "/etc/nginx/sites-available/damcp.gngmeta.com" ]; then
        sudo cp /etc/nginx/sites-available/damcp.gngmeta.com /etc/nginx/sites-available/damcp.gngmeta.com.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    # /s_an 경로 추가를 위한 설정
    NGINX_CONFIG="/etc/nginx/sites-available/damcp.gngmeta.com"
    
        # /s_an 경로가 이미 있는지 확인
    if ! grep -q "location /s_an" "$NGINX_CONFIG" 2>/dev/null; then
        echo "➕ /s_an 경로 추가 중..."
        
        # /s_an 경로를 위한 nginx 설정 추가 (API 경로 다음에)
        # Python 스크립트로 설정 파일 수정
        sudo python3 << 'PYTHON_EOF'
import re

nginx_file = "/etc/nginx/sites-available/damcp.gngmeta.com"

with open(nginx_file, 'r') as f:
    content = f.read()

# /api location 블록 다음에 /s_an 경로 추가
s_an_config = '''
    # Supply Analysis Frontend (/s_an 경로)
    location /s_an {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        rewrite ^/s_an/(.*) /$1 break;
        rewrite ^/s_an$ / break;
    }

    # Supply Analysis Backend API
    location /s_an/api {
        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        rewrite ^/s_an/api/(.*) /api/$1 break;
        rewrite ^/s_an/api$ /api break;
    }

    # Supply Analysis AI Agent API
    location /s_an/ai {
        proxy_pass http://127.0.0.1:8003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        rewrite ^/s_an/ai/(.*) /$1 break;
        rewrite ^/s_an/ai$ / break;
    }
'''

# /api location 블록 다음에 추가
pattern = r'(location /api \{.*?\n\s*\})'
match = re.search(pattern, content, re.DOTALL)
if match:
    # /api 블록 다음에 추가
    insert_pos = match.end()
    content = content[:insert_pos] + s_an_config + content[insert_pos:]
else:
    # /api 블록을 찾지 못하면 Health check 블록 다음에 추가
    pattern = r'(location /health \{.*?\n\s*\})'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + s_an_config + content[insert_pos:]

with open(nginx_file, 'w') as f:
    f.write(content)
PYTHON_EOF
        
        echo "✅ /s_an 경로 추가 완료"
    else
        echo "ℹ️  /s_an 경로가 이미 설정되어 있습니다."
    fi
    
    # Nginx 설정 테스트
    echo "🔍 Nginx 설정 테스트 중..."
    if sudo nginx -t; then
        echo "✅ Nginx 설정 검증 완료"
        sudo systemctl reload nginx
        echo "✅ Nginx 재시작 완료"
    else
        echo "❌ Nginx 설정 오류"
        echo "백업 파일에서 복원하세요:"
        echo "  sudo cp /etc/nginx/sites-available/damcp.gngmeta.com.backup.* /etc/nginx/sites-available/damcp.gngmeta.com"
        exit 1
    fi
ENDSSH

echo ""
echo "6️⃣  배포 확인..."
ssh $SSH_OPTS $SERVER_TARGET << 'ENDSSH'
    echo "🔍 서비스 상태 확인 중..."
    
    # Docker 컨테이너 상태
    echo ""
    echo "📦 Docker 컨테이너 상태:"
    cd /home/metal/supply_anlysis
    docker-compose ps
    
    # 포트 확인
    echo ""
    echo "🔌 포트 확인:"
    echo "  Frontend (3001):"
    netstat -tlnp 2>/dev/null | grep :3001 || ss -tlnp 2>/dev/null | grep :3001 || echo "    리스닝 중인 프로세스 없음"
    echo "  Backend (8002):"
    netstat -tlnp 2>/dev/null | grep :8002 || ss -tlnp 2>/dev/null | grep :8002 || echo "    리스닝 중인 프로세스 없음"
    echo "  AI Agent (8003):"
    netstat -tlnp 2>/dev/null | grep :8003 || ss -tlnp 2>/dev/null | grep :8003 || echo "    리스닝 중인 프로세스 없음"
    
    # 로컬 연결 테스트
    echo ""
    echo "🌐 로컬 연결 테스트:"
    echo "  Frontend:"
    curl -s -o /dev/null -w "HTTP 코드: %{http_code}\n" http://127.0.0.1:3001 || echo "연결 실패"
    echo "  Backend:"
    curl -s -o /dev/null -w "HTTP 코드: %{http_code}\n" http://127.0.0.1:8002/health || echo "연결 실패"
ENDSSH

echo ""
echo "✅ 배포 완료!"
echo ""
echo "🌐 접속 주소:"
echo "  https://damcp.gngmeta.com/s_an"
echo ""
echo "📊 서비스 상태 확인:"
echo "  ssh $SERVER_TARGET 'cd /home/metal/supply_anlysis && docker-compose ps'"
echo ""
echo "📝 로그 확인:"
echo "  ssh $SERVER_TARGET 'cd /home/metal/supply_anlysis && docker-compose logs -f'"
echo ""

