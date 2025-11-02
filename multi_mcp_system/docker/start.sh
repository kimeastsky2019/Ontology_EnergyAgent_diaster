#!/bin/bash

# Multi-MCP Time Series Analysis System 시작 스크립트

echo "🌟 Multi-MCP Time Series Analysis System Starting..."
echo "=================================================="

# 환경 변수 설정
export PYTHONPATH=/app
export DATABASE_URL=${DATABASE_URL:-"sqlite:///mcp_analysis.db"}
export REDIS_URL=${REDIS_URL:-"redis://localhost:6379"}

# 로그 디렉토리 생성
mkdir -p /app/logs
mkdir -p /app/data
mkdir -p /app/models/forecasting
mkdir -p /app/models/anomaly_detection

# 데이터베이스 초기화
echo "📊 Initializing database..."
python -c "
from web_service.models.database import init_database
init_database()
print('Database initialized successfully')
"

# 서비스 시작
case "${1:-all}" in
    "forecasting")
        echo "🚀 Starting Forecasting MCP Server..."
        python forecasting_mcp_server.py
        ;;
    "anomaly")
        echo "🔍 Starting Anomaly Detection MCP Server..."
        python anomaly_mcp_server.py
        ;;
    "coordinator")
        echo "🤝 Starting Coordinator MCP Server..."
        python coordinator_mcp_server.py
        ;;
    "web")
        echo "🌐 Starting Web Dashboard..."
        python web_service/app.py
        ;;
    "api")
        echo "🔌 Starting REST API Service..."
        python web_service/api/rest_api.py
        ;;
    "all")
        echo "🚀 Starting all services..."
        
        # 백그라운드에서 MCP 서버들 시작
        echo "Starting Forecasting MCP Server..."
        python forecasting_mcp_server.py &
        FORECASTING_PID=$!
        
        echo "Starting Anomaly Detection MCP Server..."
        python anomaly_mcp_server.py &
        ANOMALY_PID=$!
        
        echo "Starting Coordinator MCP Server..."
        python coordinator_mcp_server.py &
        COORDINATOR_PID=$!
        
        # 잠시 대기
        sleep 5
        
        echo "Starting Web Dashboard..."
        python web_service/app.py &
        WEB_PID=$!
        
        echo "Starting REST API Service..."
        python web_service/api/rest_api.py &
        API_PID=$!
        
        echo "✅ All services started!"
        echo "Forecasting MCP Server PID: $FORECASTING_PID"
        echo "Anomaly Detection MCP Server PID: $ANOMALY_PID"
        echo "Coordinator MCP Server PID: $COORDINATOR_PID"
        echo "Web Dashboard PID: $WEB_PID"
        echo "REST API Service PID: $API_PID"
        echo ""
        echo "🌐 Web Dashboard: http://localhost:5000"
        echo "🔌 REST API: http://localhost:5001"
        echo "📊 Forecasting MCP: http://localhost:8001"
        echo "🔍 Anomaly MCP: http://localhost:8002"
        echo "🤝 Coordinator MCP: http://localhost:8003"
        echo ""
        echo "Press Ctrl+C to stop all services"
        
        # 신호 처리
        trap 'echo "Stopping all services..."; kill $FORECASTING_PID $ANOMALY_PID $COORDINATOR_PID $WEB_PID $API_PID; exit 0' INT TERM
        
        # 모든 프로세스가 종료될 때까지 대기
        wait
        ;;
    *)
        echo "Usage: $0 {forecasting|anomaly|coordinator|web|api|all}"
        echo "  forecasting: Start only Forecasting MCP Server"
        echo "  anomaly: Start only Anomaly Detection MCP Server"
        echo "  coordinator: Start only Coordinator MCP Server"
        echo "  web: Start only Web Dashboard"
        echo "  api: Start only REST API Service"
        echo "  all: Start all services (default)"
        exit 1
        ;;
esac


