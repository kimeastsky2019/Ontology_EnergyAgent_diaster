#!/bin/bash

# GitHub 저장소 설정 스크립트
# 사용법: ./setup_git.sh

cd "$(dirname "$0")"

echo "🚀 GitHub 저장소 설정 시작..."

# Git 저장소 초기화 (이미 있으면 스킵)
if [ ! -d ".git" ]; then
    echo "📦 Git 저장소 초기화 중..."
    git init
else
    echo "✅ Git 저장소가 이미 초기화되어 있습니다."
fi

# .gitignore 확인
if [ ! -f ".gitignore" ]; then
    echo "⚠️  .gitignore 파일이 없습니다. 생성 중..."
fi

# 원격 저장소 확인 및 추가
REMOTE_URL="https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git"

if git remote | grep -q "origin"; then
    echo "📝 원격 저장소 업데이트 중..."
    git remote set-url origin "$REMOTE_URL"
else
    echo "➕ 원격 저장소 추가 중..."
    git remote add origin "$REMOTE_URL"
fi

echo "✅ 원격 저장소 설정 완료: $REMOTE_URL"

# 브랜치 설정 (main)
echo "🌿 브랜치를 'main'으로 설정 중..."
git branch -M main

# 파일 스테이징
echo "📋 변경사항 스테이징 중..."
git add .

# 커밋 메시지
COMMIT_MSG="Initial commit: AI 재난 대응형 에너지 공유 플랫폼

- Backend: FastAPI 기반 REST API
- Frontend: React + TypeScript
- AI Agents: DisasterAnalyzer, EnergyAnalyzer
- Infrastructure: Docker Compose 설정
- Database: PostgreSQL + TimescaleDB
- Monitoring: Prometheus + Grafana"

echo "💾 커밋 중..."
git commit -m "$COMMIT_MSG" || {
    echo "⚠️  변경사항이 없거나 이미 커밋되어 있습니다."
}

echo ""
echo "✨ 설정 완료!"
echo ""
echo "다음 단계:"
echo "1. git push -u origin main  # 첫 푸시"
echo "2. 또는: git push origin main"
echo ""
echo "⚠️  GitHub 인증이 필요할 수 있습니다."
echo "   Personal Access Token을 사용하거나 SSH 키를 설정하세요."


