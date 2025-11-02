#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_vars.sh"

msg "백엔드 헬스체크"
if curl -fsSL "${HEALTHCHECK_URL}" >/dev/null; then
  msg "OK: ${HEALTHCHECK_URL}"
else
  err "FAIL: ${HEALTHCHECK_URL}"; exit 1
fi

msg "공개 URL 확인"
HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}" "${PUBLIC_CHECK_URL}")
if [[ "${HTTP_CODE}" == "200" ]]; then
  msg "OK: ${PUBLIC_CHECK_URL}"
else
  warn "HTTP ${HTTP_CODE}: ${PUBLIC_CHECK_URL}"
fi

msg "System Efficiency Analysis 기능 확인"
if curl -s "${PUBLIC_CHECK_URL}" | grep -q "System Efficiency Analysis"; then
  msg "OK: System Efficiency Analysis 기능 확인됨"
else
  warn "System Efficiency Analysis 기능이 감지되지 않음"
fi

msg "태양광 판넬 모니터링 기능 확인"
if curl -s "${PUBLIC_CHECK_URL}" | grep -q "Individual Panel Status"; then
  msg "OK: 태양광 판넬 모니터링 기능 확인됨"
else
  warn "태양광 판넬 모니터링 기능이 감지되지 않음"
fi

