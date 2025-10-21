#!/bin/bash

# GCP 방화벽 규칙 설정 스크립트
# 로컬에서 gcloud CLI로 실행

echo "=== GCP 방화벽 규칙 설정 ==="

# 프로젝트 ID 확인 (실제 프로젝트 ID로 변경 필요)
PROJECT_ID="your-project-id"

# HTTPS 트래픽을 위한 방화벽 규칙 생성
echo "포트 443 (HTTPS) 방화벽 규칙 생성 중..."

gcloud compute firewall-rules create allow-https \
    --project=$PROJECT_ID \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:443 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=https-server

echo "방화벽 규칙이 생성되었습니다."

# Compute Engine 인스턴스에 태그 추가
echo "Compute Engine 인스턴스에 태그 추가 중..."

# 인스턴스 이름 확인 (실제 인스턴스 이름으로 변경 필요)
INSTANCE_NAME="your-instance-name"
ZONE="your-zone"

gcloud compute instances add-tags $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --tags=https-server

echo "인스턴스에 https-server 태그가 추가되었습니다."

# 현재 방화벽 규칙 확인
echo "=== 현재 방화벽 규칙 ==="
gcloud compute firewall-rules list --project=$PROJECT_ID

echo "=== 설정 완료 ==="
echo "이제 HTTPS 트래픽이 허용됩니다."
