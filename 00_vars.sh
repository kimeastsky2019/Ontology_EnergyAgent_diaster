#!/usr/bin/env bash
# 공통 환경 변수 (모든 스크립트에서 source하여 사용)
set -euo pipefail

# 프로젝트 메타
export APP_NAME="energy-analysis-mcp"
export REPO_URL="https://github.com/kimeastsky2019/energy-analysis-mcp.git"
export APP_USER="metal"                    # GCP 서버 사용자
export BASE_DIR="/home/${APP_USER}/${APP_NAME}"
export RELEASES_DIR="${BASE_DIR}/releases"
export SHARED_DIR="${BASE_DIR}/shared"
export CURRENT_DIR="${BASE_DIR}/current"
export LOG_DIR="${SHARED_DIR}/logs"
export ENV_FILE="${SHARED_DIR}/.env"       # 서비스 런타임 환경
export NODE_VERSION="20"                   # LTS 권장
export APP_PORT="5002"                     # 웹 인터페이스 포트
export SERVER_NAME="damcp.gngmeta.com"     # Nginx server_name

# 기능 플래그/알림 임계치(예시)
export REALTIME_POLL_MS="5000"             # 5초 업데이트
export SUPPORTED_LOCALES="ko,en,zh"
export EFF_WARN="80"   # 효율 경고 임계치(%)
export EFF_CRIT="60"   # 효율 심각 임계치(%)
export TEMP_WARN="70"  # 온도 경고(°C)
export TEMP_CRIT="85"  # 온도 심각(°C)

# 헬스체크
export HEALTHCHECK_URL="http://127.0.0.1:${APP_PORT}/health"
export PUBLIC_CHECK_URL="https://${SERVER_NAME}/data-collection?lang=ko"

# 타임스탬프 릴리스 폴더
export TS=$(date +"%Y%m%d%H%M%S")
export NEW_RELEASE_DIR="${RELEASES_DIR}/${TS}"

# 유틸리티
msg() { echo -e "\033[1;32m[INFO]\033[0m $*"; }
warn() { echo -e "\033[1;33m[WARN]\033[0m $*"; }
err() { echo -e "\033[1;31m[ERR ]\033[0m $*"; }
need_root() { [[ $EUID -eq 0 ]] || { err "root로 실행하세요"; exit 1; }; }

