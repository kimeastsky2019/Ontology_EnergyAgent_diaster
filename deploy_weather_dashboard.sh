#!/bin/bash

echo "🚀 Weather Dashboard 배포 시작..."

# 서버 정보
SERVER_IP="34.47.89.217"
SERVER_USER="metal"
SSH_KEY="google_compute_engine.pem"

# 로컬 파일들을 서버에 업로드
echo "📁 파일 업로드 중..."

# Weather Dashboard HTML 파일 업로드
scp -i $SSH_KEY weather_dashboard.html $SERVER_USER@$SERVER_IP:/home/$SERVER_USER/energy-analysis-mcp/

# React Weather Server 파일 업로드
scp -i $SSH_KEY react_weather_server.py $SERVER_USER@$SERVER_IP:/home/$SERVER_USER/energy-analysis-mcp/

echo "✅ 파일 업로드 완료"

# 서버에서 Weather Dashboard 서버 시작
echo "🔄 서버에서 Weather Dashboard 시작 중..."

ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP << 'EOF'
cd energy-analysis-mcp

# 기존 Weather Dashboard 서버 종료
pkill -f react_weather_server.py
sleep 3

# 가상환경 활성화 및 서버 시작
source venv/bin/activate
python react_weather_server.py &
echo "Weather Dashboard 서버 시작됨 (포트 3000)"

# 서버 상태 확인
sleep 5
curl -s http://localhost:3000/health || echo "서버 시작 중..."
EOF

echo "✅ Weather Dashboard 배포 완료!"
echo "🌐 접속 URL: http://$SERVER_IP:3000/react-weather"
echo "📊 API 엔드포인트: http://$SERVER_IP:3000/api/weather/current"

