#!/bin/bash
# 원상복귀 스크립트

echo "🔄 원상복귀 스크립트 실행 중..."

# 서버에서 기존 웹 인터페이스로 복원
ssh -i google_compute_engine.pem metal@34.47.89.217 "cd energy-analysis-mcp && pkill -9 -f web_interface && sleep 3 && source venv/bin/activate && python web_interface.py &"

echo "✅ 원상복귀 완료!"
echo "🌐 웹사이트: https://damcp.gngmeta.com/"
echo "📊 데이터 수집: https://damcp.gngmeta.com/data-collection?lang=ko"

