#!/bin/bash
# 서버 초기 설정 스크립트 (서버에서 실행)

set -e

PROJECT_DIR="/home/metal/energy-platform"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "🚀 서버 설정 시작..."

# Python 가상환경 생성 및 백엔드 의존성 설치
if [ -d "$BACKEND_DIR" ]; then
    echo "📦 백엔드 설정 중..."
    cd "$BACKEND_DIR"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ 백엔드 의존성 설치 완료"
fi

# Frontend 의존성 설치
if [ -d "$FRONTEND_DIR" ]; then
    echo "📦 프론트엔드 설정 중..."
    cd "$FRONTEND_DIR"
    
    if [ -f "package.json" ]; then
        npm install
        echo "✅ 프론트엔드 의존성 설치 완료"
    fi
fi

# .env 파일이 없으면 템플릿 생성
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "📝 .env 파일 템플릿 생성..."
    cat > "$BACKEND_DIR/.env.example" << 'EOF'
# Application Settings
APP_NAME=Energy Orchestrator Platform
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/energy_db
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=CHANGE_THIS_TO_RANDOM_SECRET_KEY_IN_PRODUCTION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://34.47.89.217:3000","http://localhost:3000"]

# External APIs
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
WEATHER_API_KEY=
EOF
    echo "⚠️  .env 파일을 생성하고 필요한 값을 설정하세요: $BACKEND_DIR/.env"
fi

echo ""
echo "✅ 서버 설정 완료!"
echo ""
echo "다음 단계:"
echo "1. cd $BACKEND_DIR && source venv/bin/activate"
echo "2. .env 파일 생성 및 설정"
echo "3. uvicorn src.main:app --host 0.0.0.0 --port 8000"

