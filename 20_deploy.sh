#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_vars.sh"

msg "릴리스 디렉터리 생성: ${NEW_RELEASE_DIR}"
mkdir -p ${NEW_RELEASE_DIR}
chown -R ${APP_USER}:${APP_USER} ${RELEASES_DIR}

msg "리포지토리 클론"
sudo -u ${APP_USER} git clone --depth=1 ${REPO_URL} ${NEW_RELEASE_DIR}

msg "Python 의존성 설치"
pushd ${NEW_RELEASE_DIR}
  sudo -u ${APP_USER} python3 -m venv venv
  sudo -u ${APP_USER} bash -c "source venv/bin/activate && pip install --upgrade pip && pip install fastapi uvicorn"
popd

msg ".env 연결 및 공유 리소스 연결"
ln -sf ${ENV_FILE} ${NEW_RELEASE_DIR}/.env
mkdir -p ${NEW_RELEASE_DIR}/logs
ln -snf ${LOG_DIR} ${NEW_RELEASE_DIR}/logs/shared

msg "현재→이전 백업 및 심볼릭 스위치"
if [[ -L ${CURRENT_DIR} ]]; then
  export PREV_RELEASE=$(readlink -f ${CURRENT_DIR} || true)
  msg "이전 릴리스: ${PREV_RELEASE:-없음}"
fi
ln -sfn ${NEW_RELEASE_DIR} ${CURRENT_DIR}

msg "기존 프로세스 종료"
pkill -f "python.*web_interface.py" || true
sleep 2

msg "새 버전 시작"
cd ${CURRENT_DIR}
sudo -u ${APP_USER} bash -c "source venv/bin/activate && nohup python -c 'import uvicorn; from web_interface import web_app; uvicorn.run(web_app, host=\"0.0.0.0\", port=${APP_PORT})' > web_interface.log 2>&1 &"

msg "헬스체크: ${HEALTHCHECK_URL}"
for i in {1..20}; do
  if curl -fsSL "${HEALTHCHECK_URL}" >/dev/null 2>&1; then
    msg "헬스체크 통과"
    OK=1; break
  fi
  sleep 1
done

if [[ "${OK:-0}" -ne 1 ]]; then
  warn "헬스체크 실패 → 롤백 수행"
  bash "$(dirname "$0")/50_rollback.sh" || true
  exit 1
fi

sudo systemctl reload nginx || true
msg "배포 완료: ${PUBLIC_CHECK_URL}"

