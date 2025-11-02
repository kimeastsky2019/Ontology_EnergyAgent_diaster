#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_vars.sh"

if [[ ! -L ${CURRENT_DIR} ]]; then
  err "CURRENT 심볼릭 링크가 없습니다"; exit 1
fi

CURR=$(readlink -f ${CURRENT_DIR})
PREV=$(ls -1dt ${RELEASES_DIR}/* | grep -v "${CURR}$" | head -n1 || true)

if [[ -z "${PREV}" ]]; then
  err "롤백할 이전 릴리스가 없습니다"; exit 2
fi

msg "롤백: ${CURR} → ${PREV}"
ln -sfn "${PREV}" "${CURRENT_DIR}"

msg "기존 프로세스 종료"
pkill -f "python.*web_interface.py" || true
sleep 2

msg "이전 버전 시작"
cd ${CURRENT_DIR}
sudo -u ${APP_USER} bash -c "source venv/bin/activate && nohup python -c 'import uvicorn; from web_interface import web_app; uvicorn.run(web_app, host=\"0.0.0.0\", port=${APP_PORT})' > web_interface.log 2>&1 &"

sudo systemctl reload nginx || true
msg "롤백 완료"

