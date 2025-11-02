#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_vars.sh"

# 최신 5개 릴리스만 유지
KEEP=5
msg "오래된 릴리스 정리 (최신 ${KEEP}개 유지)"
ls -1dt ${RELEASES_DIR}/* | tail -n +$((KEEP+1)) | xargs -r rm -rf
msg "정리 완료"

