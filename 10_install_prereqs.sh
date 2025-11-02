#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_vars.sh"

msg "필수 패키지 설치"
sudo apt-get update -y
sudo apt-get install -y git curl ca-certificates build-essential nginx python3 python3-pip python3-venv

msg "Python 가상환경 설정"
cd ${BASE_DIR}
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn

msg "디렉터리 구성"
mkdir -p ${RELEASES_DIR} ${SHARED_DIR} ${LOG_DIR}
chown -R ${APP_USER}:${APP_USER} ${BASE_DIR}

if [[ ! -f ${ENV_FILE} ]]; then
  msg "기본 .env 템플릿 생성 (${ENV_FILE})"
  cat > ${ENV_FILE} <<EOF
# 런타임 환경 (.env)
PORT=${APP_PORT}
REALTIME_POLL_MS=${REALTIME_POLL_MS}
SUPPORTED_LOCALES=${SUPPORTED_LOCALES}
ALERT_EFF_WARN=${EFF_WARN}
ALERT_EFF_CRIT=${EFF_CRIT}
ALERT_TEMP_WARN=${TEMP_WARN}
ALERT_TEMP_CRIT=${TEMP_CRIT}
NODE_ENV=production
EOF
  chown ${APP_USER}:${APP_USER} ${ENV_FILE}
  chmod 640 ${ENV_FILE}
fi

msg "Nginx 기본 설정 적용"
sudo tee /etc/nginx/sites-available/${APP_NAME}.conf > /dev/null <<NGX
server {
    listen 80;
    server_name ${SERVER_NAME};

    location / {
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$host;
        proxy_pass http://127.0.0.1:${APP_PORT};
        proxy_read_timeout 120s;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript application/xml image/svg+xml;
}
NGX

sudo ln -sf /etc/nginx/sites-available/${APP_NAME}.conf /etc/nginx/sites-enabled/${APP_NAME}.conf
sudo nginx -t && sudo systemctl reload nginx

msg "사전 준비 완료"

