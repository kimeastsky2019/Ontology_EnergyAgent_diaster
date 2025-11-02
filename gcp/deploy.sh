#!/bin/bash

# Google Cloud 배포 스크립트
# 도메인: https://damcp.gngmeta.com

set -e

echo "🚀 Google Cloud 배포 시작..."

# 환경 변수 설정
PROJECT_ID="energy-analysis-mcp"
SERVICE_NAME="energy-analysis-api"
REGION="asia-northeast3"  # 서울 리전
DOMAIN="damcp.gngmeta.com"

# Google Cloud 프로젝트 설정
echo "📋 Google Cloud 프로젝트 설정..."
gcloud config set project $PROJECT_ID

# 필요한 API 활성화
echo "🔧 필요한 API 활성화..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable dns.googleapis.com

# Docker 이미지 빌드 및 푸시
echo "🐳 Docker 이미지 빌드 및 푸시..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME .

# Cloud Run 서비스 배포
echo "☁️ Cloud Run 서비스 배포..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=info"

# 도메인 매핑
echo "🌐 도메인 매핑..."
gcloud run domain-mappings create \
  --service $SERVICE_NAME \
  --domain $DOMAIN \
  --region $REGION

echo "✅ 배포 완료!"
echo "🌍 서비스 URL: https://$DOMAIN"
echo "📊 Cloud Run 콘솔: https://console.cloud.google.com/run"
