#!/bin/bash

echo "🔋 에너지 모니터링 대시보드 설치 시작..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker가 설치되어 있지 않습니다. Docker를 먼저 설치해주세요.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose가 설치되어 있지 않습니다. Docker Compose를 먼저 설치해주세요.${NC}"
    exit 1
fi

# .env 파일 생성
if [ ! -f .env ]; then
    echo -e "${GREEN}환경 변수 파일 생성 중...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env 파일이 생성되었습니다. 필요한 경우 수정해주세요.${NC}"
fi

# 필요한 디렉토리 생성
echo -e "${GREEN}필요한 디렉토리 생성 중...${NC}"
mkdir -p ai-agent/models
mkdir -p logs
mkdir -p data

# Docker 컨테이너 빌드 및 실행
echo -e "${GREEN}Docker 컨테이너 빌드 및 실행 중...${NC}"
docker-compose up -d --build

# 컨테이너 상태 확인
echo ""
echo -e "${GREEN}컨테이너 상태 확인 중...${NC}"
sleep 5
docker-compose ps

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✨ 설치가 완료되었습니다!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "📱 프론트엔드: ${YELLOW}http://localhost:3000${NC}"
echo -e "🔌 백엔드 API: ${YELLOW}http://localhost:8000${NC}"
echo -e "📚 API 문서: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "🤖 AI Agent API: ${YELLOW}http://localhost:8001${NC}"
echo ""
echo -e "컨테이너 로그 확인: ${YELLOW}docker-compose logs -f${NC}"
echo -e "컨테이너 중지: ${YELLOW}docker-compose down${NC}"
echo ""
