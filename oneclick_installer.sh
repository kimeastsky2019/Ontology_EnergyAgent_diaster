#!/bin/bash
# install_realtime_dashboard.sh
# 실시간 태양광 대시보드 원클릭 설치 스크립트 (개선된 버전)

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 배너 출력
echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║   🌞 실시간 태양광 모니터링 대시보드 설치 🌞          ║"
echo "║                                                        ║"
echo "║   Version: 2.0.0 (Enhanced)                           ║"
echo "║   Author: Energy Analysis Team                         ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# 현재 디렉토리 확인
CURRENT_DIR=$(pwd)
PROJECT_NAME="energy-analysis-mcp"
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"

echo -e "${BLUE}📁 현재 디렉토리: $CURRENT_DIR${NC}"
echo ""

# 함수: 진행 상태 표시
show_progress() {
    echo -e "${PURPLE}▶ $1${NC}"
}

show_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

show_error() {
    echo -e "${RED}✗ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

show_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 함수: 포트 사용 확인
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 포트 사용 중
    else
        return 1  # 포트 사용 가능
    fi
}

# 함수: 사용자 확인
confirm() {
    local message=$1
    echo -e "${YELLOW}$message (y/N)${NC}"
    read -r response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# 함수: 백업 생성
create_backup() {
    if [ -d "$PROJECT_NAME" ]; then
        show_warning "기존 프로젝트를 백업합니다..."
        cp -r "$PROJECT_NAME" "$BACKUP_DIR"
        show_success "백업 완료: $BACKUP_DIR"
    fi
}

# 함수: 정리 작업
cleanup() {
    show_warning "정리 작업 중..."
    docker-compose down 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
    show_success "정리 완료"
}

# 함수: 에러 처리
handle_error() {
    show_error "설치 중 오류가 발생했습니다!"
    show_info "백업에서 복원하려면: cp -r $BACKUP_DIR $PROJECT_NAME"
    show_info "로그 확인: docker-compose logs"
    exit 1
}

# 에러 트랩 설정
trap handle_error ERR

# 1. 시스템 요구사항 확인
show_progress "[1/12] 시스템 요구사항 확인 중..."

# 운영체제 확인
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    show_success "Linux 시스템 감지됨"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    show_success "macOS 시스템 감지됨"
else
    show_warning "지원되지 않는 운영체제: $OSTYPE"
fi

# Docker 확인
if ! command -v docker &> /dev/null; then
    show_error "Docker가 설치되어 있지 않습니다."
    show_info "설치 방법:"
    echo "  Ubuntu/Debian: curl -fsSL https://get.docker.com | sh"
    echo "  macOS: https://docs.docker.com/desktop/mac/install/"
    echo "  또는: brew install docker"
    exit 1
fi
show_success "Docker 설치됨 ($(docker --version | cut -d' ' -f3 | cut -d',' -f1))"

# Docker 서비스 확인
if ! docker info &> /dev/null; then
    show_error "Docker 서비스가 실행되지 않았습니다."
    show_info "Docker Desktop을 시작하거나 다음 명령을 실행하세요:"
    echo "  sudo systemctl start docker"
    exit 1
fi
show_success "Docker 서비스 실행 중"

# Docker Compose 확인
if ! command -v docker-compose &> /dev/null; then
    show_error "Docker Compose가 설치되어 있지 않습니다."
    show_info "설치 방법:"
    echo "  Ubuntu/Debian: sudo apt install docker-compose"
    echo "  macOS: brew install docker-compose"
    exit 1
fi
show_success "Docker Compose 설치됨 ($(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1))"

# Git 확인
if ! command -v git &> /dev/null; then
    show_warning "Git이 설치되어 있지 않습니다. 설치 중..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update && sudo apt install -y git
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install git
    fi
fi
show_success "Git 설치됨"

# curl 확인
if ! command -v curl &> /dev/null; then
    show_warning "curl이 설치되어 있지 않습니다. 설치 중..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt install -y curl
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install curl
    fi
fi
show_success "curl 설치됨"

echo ""

# 2. 포트 확인
show_progress "[2/12] 포트 사용 확인 중..."

if check_port 80; then
    show_warning "포트 80이 이미 사용 중입니다."
    if confirm "포트 8080을 사용하시겠습니까?"; then
        FRONTEND_PORT=8080
    else
        show_error "포트 충돌로 인해 설치를 중단합니다."
        exit 1
    fi
else
    FRONTEND_PORT=80
    show_success "포트 80 사용 가능"
fi

if check_port 8000; then
    show_warning "포트 8000이 이미 사용 중입니다."
    if confirm "포트 8001을 사용하시겠습니까?"; then
        BACKEND_PORT=8001
    else
        show_error "포트 충돌로 인해 설치를 중단합니다."
        exit 1
    fi
else
    BACKEND_PORT=8000
    show_success "포트 8000 사용 가능"
fi

echo ""

# 3. 백업 생성
show_progress "[3/12] 백업 생성 중..."
create_backup
echo ""

# 4. 저장소 클론 또는 업데이트
show_progress "[4/12] 코드 가져오기..."

if [ -d "$PROJECT_NAME" ]; then
    show_warning "프로젝트 디렉토리가 이미 존재합니다."
    if confirm "기존 프로젝트를 업데이트하시겠습니까?"; then
        cd $PROJECT_NAME
        git stash 2>/dev/null || true
        git pull origin main
        cd ..
    else
        show_info "기존 프로젝트를 사용합니다."
    fi
else
    show_progress "GitHub에서 클론 중..."
    git clone https://github.com/kimeastsky2019/energy-analysis-mcp.git
fi

show_success "코드 가져오기 완료"
echo ""

# 5. 환경 변수 설정
show_progress "[5/12] 환경 변수 설정 중..."

cd $PROJECT_NAME

# .env 파일 생성
cat > .env << 'ENV_EOF'
# 실시간 대시보드 설정
FRONTEND_PORT=80
BACKEND_PORT=8000
LOG_LEVEL=INFO

# API 키 (선택사항)
OPENWEATHER_API_KEY=your_openweather_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# 보안 설정
SECRET_KEY=your_secret_key_change_in_production
ENV_EOF

# 포트 설정 업데이트
sed -i.bak "s/FRONTEND_PORT=80/FRONTEND_PORT=$FRONTEND_PORT/" .env
sed -i.bak "s/BACKEND_PORT=8000/BACKEND_PORT=$BACKEND_PORT/" .env

show_success "환경 변수 설정 완료"
echo ""

# 6. Backend 디렉토리 생성
show_progress "[6/12] Backend 설정 중..."

mkdir -p backend
cd backend

# realtime_server.py 생성 (개선된 버전)
cat > realtime_server.py << 'BACKEND_EOF'
"""
실시간 태양광 데이터 서버 (개선된 버전)
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import asyncio
import json
import os
from datetime import datetime
import math
import random
import logging
from typing import List, Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Realtime Solar API",
    version="2.0.0",
    description="실시간 태양광 모니터링 API"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.data_history: List[Dict[str, Any]] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket 연결됨. 총 연결 수: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket 연결 해제됨. 총 연결 수: {len(self.active_connections)}")
    
    async def broadcast(self, message: str):
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            for connection in disconnected:
                self.disconnect(connection)

manager = ConnectionManager()

def generate_panel_data():
    """개별 태양광 판넬 데이터 생성"""
    panels = []
    for i in range(1, 13):  # 12개 판넬
        base_output = 300 + random.uniform(0, 50)  # 300-350W
        efficiency = 85 + random.uniform(0, 10)  # 85-95%
        temperature = 25 + random.uniform(0, 15)  # 25-40°C
        
        panels.append({
            "id": f"Panel-{i:02d}",
            "position": f"Row {math.ceil(i/4)} Col {((i-1) % 4) + 1}",
            "output": round(base_output * (efficiency / 100)),
            "efficiency": round(efficiency, 1),
            "temperature": round(temperature, 1),
            "status": "Excellent" if efficiency > 90 else "Good" if efficiency > 80 else "Fair" if efficiency > 70 else "Poor",
            "lastCheck": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return panels

def generate_realistic_data():
    """현실적인 태양광 데이터 생성"""
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    # 시간대별 태양광 발전량 (6시-18시)
    if 6 <= hour <= 18:
        # 정규분포 곡선으로 일출-일몰 시뮬레이션
        peak_hour = 12
        time_from_peak = abs(hour - peak_hour)
        base_power = max(0, 4.5 * math.exp(-(time_from_peak / 3) ** 2))
        
        # 분 단위 미세 조정
        minute_factor = 1 + (math.sin(minute * math.pi / 30) * 0.1)
        base_power *= minute_factor
    else:
        base_power = 0.01  # 야간 최소값
    
    # 날씨 영향 시뮬레이션
    weather_factor = 0.7 + random.uniform(0, 0.3)  # 70-100%
    temperature_factor = 1 - (random.uniform(-0.05, 0.05))  # 온도 영향
    
    solar_power = max(0, base_power * weather_factor * temperature_factor)
    
    # 배터리 SOC (태양광 발전량에 따라 변화)
    if solar_power > 0:
        soc_change = random.uniform(0.1, 0.5)
    else:
        soc_change = random.uniform(-0.2, 0.1)
    
    battery_soc = max(0, min(100, 85 + soc_change + random.uniform(-2, 2)))
    
    # 환경 데이터
    temperature = 20 + random.uniform(0, 15) + (solar_power * 2)  # 태양광 영향
    humidity = 40 + random.uniform(0, 40) - (solar_power * 5)  # 태양광 영향
    wind_speed = random.uniform(0.5, 5.0)
    irradiance = int(solar_power * 1000) if solar_power > 0 else random.randint(0, 50)
    
    # 태양광 판넬 데이터 생성
    panels = generate_panel_data()
    
    data = {
        "timestamp": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "solarPower": round(solar_power, 3),
        "batterySOC": round(battery_soc, 1),
        "temperature": round(temperature, 1),
        "humidity": int(humidity),
        "windSpeed": round(wind_speed, 1),
        "irradiance": irradiance,
        "efficiency": round(85 + random.uniform(-5, 10), 1),
        "dailyGeneration": round(random.uniform(15, 35), 1),  # 일일 발전량
        "panels": panels,  # 개별 판넬 데이터
        "totalPanels": len(panels),
        "activePanels": len([p for p in panels if p["status"] in ["Excellent", "Good"]]),
        "systemEfficiency": round(sum(p["efficiency"] for p in panels) / len(panels), 1),
        # 새로운 필드들
        "ratedPower": 4.5,  # 정격 전력
        "currentGeneration": round(solar_power, 2),  # 현재 발전량
        "avgTemperature": round(temperature + random.uniform(-2, 2), 1),  # 평균 온도
        "avgHumidity": int(humidity + random.uniform(-5, 5)),  # 평균 습도
        "maxWindSpeed": round(wind_speed + random.uniform(0, 2), 1),  # 최대 풍속
        "solarIrradiance": irradiance,  # 태양 복사량
        "tempConsumptionCorrelation": round(0.75 + random.uniform(0, 0.1), 2),  # 온도-소비 상관관계
        "solarGenerationCorrelation": round(0.90 + random.uniform(0, 0.05), 2),  # 태양광-발전 상관관계
        "humidityEfficiencyCorrelation": round(-0.40 - random.uniform(0, 0.1), 2)  # 습도-효율 상관관계
    }
    
    # 데이터 히스토리 저장 (최근 100개)
    manager.data_history.append(data)
    if len(manager.data_history) > 100:
        manager.data_history.pop(0)
    
    return data

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>Solar API</title></head>
        <body>
            <h1>🌞 실시간 태양광 API</h1>
            <p>API 문서: <a href="/docs">/docs</a></p>
            <p>상태 확인: <a href="/health">/health</a></p>
        </body>
    </html>
    """

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "connections": len(manager.active_connections),
        "uptime": "running",
        "version": "2.0.0"
    }

@app.get("/api/current")
async def current():
    return generate_realistic_data()

@app.get("/api/history")
async def history(limit: int = 50):
    if limit > 100:
        limit = 100
    return {"data": manager.data_history[-limit:]}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # 초기 데이터 전송
        initial_data = generate_realistic_data()
        await websocket.send_text(json.dumps(initial_data))
        
        # 실시간 데이터 전송
        while True:
            await asyncio.sleep(5)
            data = generate_realistic_data()
            await websocket.send_text(json.dumps(data))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket 오류: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
BACKEND_EOF

# requirements.txt 생성 (개선된 버전)
cat > requirements.txt << 'REQ_EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
python-multipart==0.0.6
python-dotenv==1.0.0
REQ_EOF

# Dockerfile 생성 (개선된 버전)
cat > Dockerfile << 'DOCKER_EOF'
FROM python:3.11-slim

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "realtime_server:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKER_EOF

cd ..
show_success "Backend 설정 완료"
echo ""

# 7. Frontend 디렉토리 생성 (개선된 버전)
show_progress "[7/12] Frontend 설정 중..."

mkdir -p frontend
cd frontend

cat > Dockerfile << 'FRONT_DOCKER_EOF'
FROM nginx:alpine

# nginx 설정 파일 복사
COPY nginx.conf /etc/nginx/nginx.conf

# 정적 파일 복사
COPY index.html /usr/share/nginx/html/

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
FRONT_DOCKER_EOF

# nginx 설정 파일 생성
cat > nginx.conf << 'NGINX_EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 로그 설정
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # gzip 압축
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        # 정적 파일 캐싱
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # API 프록시
        location /api/ {
            proxy_pass http://backend:8000/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # WebSocket 프록시
        location /ws {
            proxy_pass http://backend:8000/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # SPA 라우팅 지원
        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
NGINX_EOF

# 개선된 HTML 대시보드 생성
cat > index.html << 'HTML_EOF'
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>실시간 태양광 모니터링</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .gradient-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
    </style>
</head>
<body class="bg-gradient-to-br from-blue-50 to-green-50 min-h-screen p-6">
    <div class="max-w-7xl mx-auto">
        <!-- 헤더 -->
        <div class="mb-6">
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-4xl font-bold text-gray-900">🌞 Energy Supply Monitoring Dashboard</h1>
                <div class="flex items-center gap-2">
                    <span class="text-sm text-gray-600">Language:</span>
                    <select id="language-selector" class="px-3 py-1 border border-gray-300 rounded-md text-sm">
                        <option value="ko">🇰🇷 한국어</option>
                        <option value="en">🇺🇸 English</option>
                        <option value="zh">🇨🇳 中文</option>
                    </select>
                </div>
            </div>
            <div class="flex items-center gap-4">
                <div id="connection-status" class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gray-100">
                    <div id="status-dot" class="w-3 h-3 rounded-full bg-gray-400"></div>
                    <span id="status-text">연결 중...</span>
                </div>
                <div class="text-sm text-gray-600">
                    마지막 업데이트: <span id="last-update">-</span>
                </div>
            </div>
        </div>

        <!-- 메인 메트릭 카드 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-yellow-400">
                <div class="text-sm text-gray-600 font-medium mb-2">☀️ 태양광 발전</div>
                <div class="text-3xl font-bold text-yellow-600" id="solar-power">0.000</div>
                <div class="text-sm text-gray-500">kW</div>
                <div class="mt-2 text-xs text-gray-400">일일: <span id="daily-generation">0.0</span> kWh</div>
            </div>
            
            <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-green-400">
                <div class="text-sm text-gray-600 font-medium mb-2">🔋 배터리 충전</div>
                <div class="text-3xl font-bold text-green-600" id="battery-soc">0.0</div>
                <div class="text-sm text-gray-500">%</div>
                <div class="mt-2">
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div id="battery-bar" class="bg-green-600 h-2 rounded-full transition-all duration-500" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-red-400">
                <div class="text-sm text-gray-600 font-medium mb-2">🌡️ 온도</div>
                <div class="text-3xl font-bold text-red-600" id="temperature">0.0</div>
                <div class="text-sm text-gray-500">°C</div>
                <div class="mt-2 text-xs text-gray-400">습도: <span id="humidity">0</span>%</div>
            </div>
            
            <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-400">
                <div class="text-sm text-gray-600 font-medium mb-2">☀️ 일사량</div>
                <div class="text-3xl font-bold text-blue-600" id="irradiance">0</div>
                <div class="text-sm text-gray-500">W/m²</div>
                <div class="mt-2 text-xs text-gray-400">풍속: <span id="wind-speed">0.0</span> m/s</div>
            </div>
        </div>

        <!-- 차트 섹션 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h3 class="text-lg font-semibold mb-4">📊 발전량 추이</h3>
                <canvas id="power-chart" height="200"></canvas>
            </div>
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h3 class="text-lg font-semibold mb-4">🔋 배터리 상태</h3>
                <canvas id="battery-chart" height="200"></canvas>
            </div>
        </div>

        <!-- Solar Energy Management System -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 class="text-lg font-semibold mb-4">☀️ Solar Energy Management System</h3>
            
            <!-- PV Module Status -->
            <div class="mb-6">
                <h4 class="text-md font-medium mb-4">PV Module Status</h4>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4" id="pv-module-status">
                    <!-- 동적으로 생성될 PV 모듈 상태 -->
                </div>
            </div>

            <!-- Power Generation Summary -->
            <div class="mb-6">
                <h4 class="text-md font-medium mb-4">Power Generation</h4>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-blue-50 p-4 rounded-lg">
                        <div class="text-sm text-blue-600 font-medium">Current</div>
                        <div class="text-2xl font-bold text-blue-800" id="current-generation">0.00 kW</div>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg">
                        <div class="text-sm text-green-600 font-medium">Rated</div>
                        <div class="text-2xl font-bold text-green-800">4.50 kW</div>
                    </div>
                    <div class="bg-purple-50 p-4 rounded-lg">
                        <div class="text-sm text-purple-600 font-medium">Today</div>
                        <div class="text-2xl font-bold text-purple-800" id="today-generation">0.0 kWh</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Power Data Analysis Platform -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 class="text-lg font-semibold mb-4">⚡ Power Data Analysis Platform</h3>
            <p class="text-gray-600 mb-4">Real-time energy data monitoring and analysis system</p>
            
            <!-- Power Metrics -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div class="text-center p-4 bg-yellow-50 rounded-lg">
                    <h4 class="text-sm font-medium text-yellow-600 mb-2">Solar Power</h4>
                    <div class="text-2xl font-bold text-yellow-800" id="solar-power-metric">0.00 kW</div>
                    <div class="text-xs text-gray-500">Current Generation</div>
                </div>
                <div class="text-center p-4 bg-green-50 rounded-lg">
                    <h4 class="text-sm font-medium text-green-600 mb-2">Battery SOC</h4>
                    <div class="text-2xl font-bold text-green-800" id="battery-soc-metric">0.0%</div>
                    <div class="text-xs text-gray-500">State of Charge</div>
                </div>
                <div class="text-center p-4 bg-red-50 rounded-lg">
                    <h4 class="text-sm font-medium text-red-600 mb-2">Temperature</h4>
                    <div class="text-2xl font-bold text-red-800" id="temperature-metric">0.0°C</div>
                    <div class="text-xs text-gray-500">Ambient Temp</div>
                </div>
                <div class="text-center p-4 bg-blue-50 rounded-lg">
                    <h4 class="text-sm font-medium text-blue-600 mb-2">Humidity</h4>
                    <div class="text-2xl font-bold text-blue-800" id="humidity-metric">0.0%</div>
                    <div class="text-xs text-gray-500">Relative Humidity</div>
                </div>
            </div>
        </div>

        <!-- 태양광 판넬 모니터링 섹션 -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 class="text-lg font-semibold mb-4">☀️ 태양광 판넬 모니터링</h3>
            
            <!-- 시스템 효율성 분석 -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div class="text-center">
                    <h4 class="text-md font-medium mb-2">System Efficiency Analysis</h4>
                    <canvas id="efficiency-chart" height="200"></canvas>
                </div>
                <div class="text-center">
                    <h4 class="text-md font-medium mb-2">Panel Performance</h4>
                    <canvas id="panel-performance-chart" height="200"></canvas>
                </div>
                <div class="text-center">
                    <h4 class="text-md font-medium mb-2">Energy Distribution</h4>
                    <canvas id="energy-distribution-chart" height="200"></canvas>
                </div>
            </div>

            <!-- 개별 판넬 상태 -->
            <div class="mb-6">
                <h4 class="text-md font-medium mb-4">🔧 개별 판넬 상태</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" id="panel-status-grid">
                    <!-- 동적으로 생성될 판넬 카드들 -->
                </div>
            </div>

            <!-- 판넬 성능 테이블 -->
            <div class="mb-6">
                <h4 class="text-md font-medium mb-4">📋 판넬 성능 상세</h4>
                <div class="overflow-x-auto">
                    <table class="min-w-full bg-white border border-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">판넬 ID</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">위치</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">출력 (W)</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">효율 (%)</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">온도 (°C)</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">상태</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">마지막 점검</th>
                            </tr>
                        </thead>
                        <tbody id="panel-detail-table" class="divide-y divide-gray-200">
                            <!-- 동적으로 생성될 테이블 행들 -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 알림 및 경고 -->
            <div class="mb-6">
                <h4 class="text-md font-medium mb-4">⚠️ 알림 및 경고</h4>
                <div id="panel-alerts" class="space-y-2">
                    <!-- 동적으로 생성될 알림들 -->
                </div>
            </div>
        </div>

        <!-- Advanced Weather Analysis -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 class="text-lg font-semibold mb-4">🌤️ Advanced Weather Analysis</h3>
            <p class="text-gray-600 mb-4">Real-time weather monitoring with interactive charts and predictions</p>
            
            <!-- Weather Metrics -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div class="text-center p-4 bg-red-50 rounded-lg">
                    <div class="text-2xl font-bold text-red-800" id="avg-temperature">0.0°C</div>
                    <div class="text-sm text-gray-600">평균 온도</div>
                </div>
                <div class="text-center p-4 bg-blue-50 rounded-lg">
                    <div class="text-2xl font-bold text-blue-800" id="avg-humidity">0%</div>
                    <div class="text-sm text-gray-600">평균 습도</div>
                </div>
                <div class="text-center p-4 bg-green-50 rounded-lg">
                    <div class="text-2xl font-bold text-green-800" id="max-wind-speed">0.0 m/s</div>
                    <div class="text-sm text-gray-600">최대 풍속</div>
                </div>
                <div class="text-center p-4 bg-yellow-50 rounded-lg">
                    <div class="text-2xl font-bold text-yellow-800" id="solar-irradiance">0 W/m²</div>
                    <div class="text-sm text-gray-600">태양 복사량</div>
                </div>
            </div>

            <!-- Weather Dashboard Links -->
            <div class="flex gap-4 mb-6">
                <button class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                    Open Weather Dashboard
                </button>
                <button class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors">
                    Legacy Weather Analysis
                </button>
            </div>

            <!-- Weather Description -->
            <div class="bg-gray-50 p-4 rounded-lg">
                <p class="text-sm text-gray-600">
                    Modern React dashboard with advanced analytics, interactive maps, and real-time updates
                </p>
            </div>
        </div>

        <!-- Energy Correlations -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 class="text-lg font-semibold mb-4">📈 에너지 상관관계</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="text-center p-4 bg-orange-50 rounded-lg">
                    <div class="text-2xl font-bold text-orange-800" id="temp-consumption-correlation">0.00</div>
                    <div class="text-sm text-gray-600">온도 vs 소비</div>
                </div>
                <div class="text-center p-4 bg-yellow-50 rounded-lg">
                    <div class="text-2xl font-bold text-yellow-800" id="solar-generation-correlation">0.00</div>
                    <div class="text-sm text-gray-600">태양광 vs 발전</div>
                </div>
                <div class="text-center p-4 bg-blue-50 rounded-lg">
                    <div class="text-2xl font-bold text-blue-800" id="humidity-efficiency-correlation">0.00</div>
                    <div class="text-sm text-gray-600">습도 vs 효율</div>
                </div>
            </div>
        </div>

        <!-- Real-time Data Table -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 class="text-lg font-semibold mb-4">📊 Real-time Data Table</h3>
            <div class="overflow-x-auto">
                <table class="min-w-full bg-white border border-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Solar Power (kW)</th>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Battery SOC (%)</th>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Temperature (°C)</th>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Humidity (%)</th>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Wind Speed (m/s)</th>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Irradiance (W/m²)</th>
                        </tr>
                    </thead>
                    <tbody id="realtime-data-table" class="divide-y divide-gray-200">
                        <tr>
                            <td colspan="7" class="px-4 py-8 text-center text-gray-500">Loading data...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 데이터 로그 -->
        <div class="bg-white rounded-lg shadow-lg p-6">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold">📊 실시간 데이터 로그</h3>
                <button id="clear-log" class="text-sm text-gray-500 hover:text-gray-700">로그 지우기</button>
            </div>
            <div id="data-log" class="space-y-2 max-h-96 overflow-y-auto font-mono text-sm"></div>
        </div>
    </div>

    <script>
        let ws;
        let reconnectInterval;
        let powerChart, batteryChart, efficiencyChart, panelPerformanceChart, energyDistributionChart;
        let powerData = [];
        let batteryData = [];
        let panelData = [];
        let totalPanels = 12; // 총 판넬 개수
        let currentLanguage = 'ko'; // 현재 언어
        let translations = {}; // 번역 데이터
        let dailyGeneration = 0; // 일일 발전량 누적

        // 차트 초기화
        function initCharts() {
            const powerCtx = document.getElementById('power-chart').getContext('2d');
            powerChart = new Chart(powerCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '발전량 (kW)',
                        data: [],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: '발전량 (kW)'
                            }
                        }
                    }
                }
            });

            const batteryCtx = document.getElementById('battery-chart').getContext('2d');
            batteryChart = new Chart(batteryCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '배터리 SOC (%)',
                        data: [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'SOC (%)'
                            }
                        }
                    }
                }
            });

            // System Efficiency Analysis 도넛 차트 (참고 사이트와 동일한 스타일)
            const efficiencyCtx = document.getElementById('efficiency-chart').getContext('2d');
            efficiencyChart = new Chart(efficiencyCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Solar Efficiency', 'Battery Efficiency', 'System Loss'],
                    datasets: [{
                        data: [85, 92, 8],
                        backgroundColor: ['#10b981', '#3b82f6', '#ef4444'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });

            // Panel Performance 차트
            const panelPerformanceCtx = document.getElementById('panel-performance-chart').getContext('2d');
            panelPerformanceChart = new Chart(panelPerformanceCtx, {
                type: 'bar',
                data: {
                    labels: ['Panel 1', 'Panel 2', 'Panel 3', 'Panel 4', 'Panel 5', 'Panel 6'],
                    datasets: [{
                        label: 'Output (W)',
                        data: [320, 315, 325, 310, 318, 322],
                        backgroundColor: 'rgba(59, 130, 246, 0.8)',
                        borderColor: '#3b82f6',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Output (W)'
                            }
                        }
                    }
                }
            });

            // Energy Distribution 차트
            const energyDistributionCtx = document.getElementById('energy-distribution-chart').getContext('2d');
            energyDistributionChart = new Chart(energyDistributionCtx, {
                type: 'pie',
                data: {
                    labels: ['Grid Export', 'Battery Charge', 'Load Consumption', 'System Loss'],
                    datasets: [{
                        data: [45, 30, 20, 5],
                        backgroundColor: ['#10b981', '#f59e0b', '#3b82f6', '#ef4444'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });
        }

        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('✓ WebSocket 연결됨');
                document.getElementById('status-dot').className = 'w-3 h-3 rounded-full bg-green-500 pulse-animation';
                document.getElementById('status-text').textContent = '실시간 연결';
                document.getElementById('connection-status').className = 'inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-100 text-green-700';
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                updateDashboard(data);
                updateCharts(data);
            };

            ws.onerror = (error) => {
                console.error('WebSocket 오류:', error);
            };

            ws.onclose = () => {
                console.log('WebSocket 연결 종료');
                document.getElementById('status-dot').className = 'w-3 h-3 rounded-full bg-red-500';
                document.getElementById('status-text').textContent = '연결 끊김';
                document.getElementById('connection-status').className = 'inline-flex items-center gap-2 px-4 py-2 rounded-full bg-red-100 text-red-700';
                
                // 3초 후 재연결 시도
                setTimeout(connect, 3000);
            };
        }

        function updateDashboard(data) {
            document.getElementById('solar-power').textContent = data.solarPower.toFixed(3);
            document.getElementById('battery-soc').textContent = data.batterySOC.toFixed(1);
            document.getElementById('temperature').textContent = data.temperature.toFixed(1);
            document.getElementById('irradiance').textContent = data.irradiance;
            document.getElementById('humidity').textContent = data.humidity;
            document.getElementById('wind-speed').textContent = data.windSpeed.toFixed(1);
            document.getElementById('daily-generation').textContent = data.dailyGeneration.toFixed(1);
            document.getElementById('last-update').textContent = data.timestamp;

            // 배터리 바 업데이트
            const batteryBar = document.getElementById('battery-bar');
            batteryBar.style.width = data.batterySOC + '%';

            // 데이터 로그 업데이트
            const log = document.getElementById('data-log');
            const entry = document.createElement('div');
            entry.className = 'text-gray-700 p-2 bg-gray-50 rounded border-l-4 border-blue-400';
            entry.innerHTML = `
                <div class="flex justify-between items-center">
                    <span class="font-semibold">[${data.timestamp}]</span>
                    <span class="text-xs text-gray-500">${data.date}</span>
                </div>
                <div class="mt-1 text-sm">
                    발전: <span class="font-semibold text-yellow-600">${data.solarPower}kW</span> | 
                    배터리: <span class="font-semibold text-green-600">${data.batterySOC}%</span> | 
                    온도: <span class="font-semibold text-red-600">${data.temperature}°C</span> |
                    효율: <span class="font-semibold text-blue-600">${data.efficiency}%</span>
                </div>
            `;
            log.insertBefore(entry, log.firstChild);
            
            // 최대 20개 로그만 유지
            if (log.children.length > 20) {
                log.removeChild(log.lastChild);
            }
        }

        // 다국어 번역 데이터
        const translationData = {
            ko: {
                'Energy Supply Monitoring Dashboard': '에너지 공급 모니터링 대시보드',
                'Solar Generation': '태양광 발전',
                'Energy Storage': '에너지 저장',
                'Weather Data': '날씨 데이터',
                'PV Module Status': 'PV 모듈 상태',
                'Power Generation': '전력 발전',
                'Current': '현재',
                'Rated': '정격',
                'Today': '오늘',
                'Power Data Analysis Platform': '전력 데이터 분석 플랫폼',
                'Real-time energy data monitoring and analysis system': '실시간 에너지 데이터 모니터링 및 분석 시스템',
                'Solar Power': '태양광 전력',
                'Battery SOC': '배터리 SOC',
                'Temperature': '온도',
                'Humidity': '습도',
                'Current Generation': '현재 발전량',
                'State of Charge': '충전 상태',
                'Ambient Temp': '주변 온도',
                'Relative Humidity': '상대 습도',
                'Advanced Weather Analysis': '고급 날씨 분석',
                'Real-time weather monitoring with interactive charts and predictions': '인터랙티브 차트와 예측을 통한 실시간 날씨 모니터링',
                '평균 온도': '평균 온도',
                '평균 습도': '평균 습도',
                '최대 풍속': '최대 풍속',
                '태양 복사량': '태양 복사량',
                'Open Weather Dashboard': '날씨 대시보드 열기',
                'Legacy Weather Analysis': '레거시 날씨 분석',
                'Modern React dashboard with advanced analytics, interactive maps, and real-time updates': '고급 분석, 인터랙티브 맵, 실시간 업데이트가 포함된 모던 React 대시보드',
                '에너지 상관관계': '에너지 상관관계',
                '온도 vs 소비': '온도 vs 소비',
                '태양광 vs 발전': '태양광 vs 발전',
                '습도 vs 효율': '습도 vs 효율',
                'Real-time Data Table': '실시간 데이터 테이블',
                'Timestamp': '타임스탬프',
                'Solar Power (kW)': '태양광 전력 (kW)',
                'Battery SOC (%)': '배터리 SOC (%)',
                'Temperature (°C)': '온도 (°C)',
                'Humidity (%)': '습도 (%)',
                'Wind Speed (m/s)': '풍속 (m/s)',
                'Irradiance (W/m²)': '일사량 (W/m²)',
                'Loading data...': '데이터 로딩 중...',
                '실시간 데이터 로그': '실시간 데이터 로그',
                '로그 지우기': '로그 지우기',
                '연결 중...': '연결 중...',
                '실시간 연결': '실시간 연결',
                '연결 끊김': '연결 끊김',
                '마지막 업데이트': '마지막 업데이트',
                'Language': '언어'
            },
            en: {
                'Energy Supply Monitoring Dashboard': 'Energy Supply Monitoring Dashboard',
                'Solar Generation': 'Solar Generation',
                'Energy Storage': 'Energy Storage',
                'Weather Data': 'Weather Data',
                'PV Module Status': 'PV Module Status',
                'Power Generation': 'Power Generation',
                'Current': 'Current',
                'Rated': 'Rated',
                'Today': 'Today',
                'Power Data Analysis Platform': 'Power Data Analysis Platform',
                'Real-time energy data monitoring and analysis system': 'Real-time energy data monitoring and analysis system',
                'Solar Power': 'Solar Power',
                'Battery SOC': 'Battery SOC',
                'Temperature': 'Temperature',
                'Humidity': 'Humidity',
                'Current Generation': 'Current Generation',
                'State of Charge': 'State of Charge',
                'Ambient Temp': 'Ambient Temp',
                'Relative Humidity': 'Relative Humidity',
                'Advanced Weather Analysis': 'Advanced Weather Analysis',
                'Real-time weather monitoring with interactive charts and predictions': 'Real-time weather monitoring with interactive charts and predictions',
                '평균 온도': 'Average Temperature',
                '평균 습도': 'Average Humidity',
                '최대 풍속': 'Max Wind Speed',
                '태양 복사량': 'Solar Irradiance',
                'Open Weather Dashboard': 'Open Weather Dashboard',
                'Legacy Weather Analysis': 'Legacy Weather Analysis',
                'Modern React dashboard with advanced analytics, interactive maps, and real-time updates': 'Modern React dashboard with advanced analytics, interactive maps, and real-time updates',
                '에너지 상관관계': 'Energy Correlations',
                '온도 vs 소비': 'Temperature vs Consumption',
                '태양광 vs 발전': 'Solar vs Generation',
                '습도 vs 효율': 'Humidity vs Efficiency',
                'Real-time Data Table': 'Real-time Data Table',
                'Timestamp': 'Timestamp',
                'Solar Power (kW)': 'Solar Power (kW)',
                'Battery SOC (%)': 'Battery SOC (%)',
                'Temperature (°C)': 'Temperature (°C)',
                'Humidity (%)': 'Humidity (%)',
                'Wind Speed (m/s)': 'Wind Speed (m/s)',
                'Irradiance (W/m²)': 'Irradiance (W/m²)',
                'Loading data...': 'Loading data...',
                '실시간 데이터 로그': 'Real-time Data Log',
                '로그 지우기': 'Clear Log',
                '연결 중...': 'Connecting...',
                '실시간 연결': 'Real-time Connected',
                '연결 끊김': 'Disconnected',
                '마지막 업데이트': 'Last Update',
                'Language': 'Language'
            },
            zh: {
                'Energy Supply Monitoring Dashboard': '能源供应监控仪表板',
                'Solar Generation': '太阳能发电',
                'Energy Storage': '能源存储',
                'Weather Data': '天气数据',
                'PV Module Status': '光伏模块状态',
                'Power Generation': '发电',
                'Current': '当前',
                'Rated': '额定',
                'Today': '今天',
                'Power Data Analysis Platform': '电力数据分析平台',
                'Real-time energy data monitoring and analysis system': '实时能源数据监控和分析系统',
                'Solar Power': '太阳能',
                'Battery SOC': '电池SOC',
                'Temperature': '温度',
                'Humidity': '湿度',
                'Current Generation': '当前发电',
                'State of Charge': '充电状态',
                'Ambient Temp': '环境温度',
                'Relative Humidity': '相对湿度',
                'Advanced Weather Analysis': '高级天气分析',
                'Real-time weather monitoring with interactive charts and predictions': '具有交互式图表和预测的实时天气监控',
                '평균 온도': '平均温度',
                '평균 습도': '平均湿度',
                '최대 풍속': '最大风速',
                '태양 복사량': '太阳辐射',
                'Open Weather Dashboard': '打开天气仪表板',
                'Legacy Weather Analysis': '传统天气分析',
                'Modern React dashboard with advanced analytics, interactive maps, and real-time updates': '具有高级分析、交互式地图和实时更新的现代React仪表板',
                '에너지 상관관계': '能源相关性',
                '온도 vs 소비': '温度 vs 消耗',
                '태양광 vs 발전': '太阳能 vs 发电',
                '습도 vs 효율': '湿度 vs 效率',
                'Real-time Data Table': '实时数据表',
                'Timestamp': '时间戳',
                'Solar Power (kW)': '太阳能 (kW)',
                'Battery SOC (%)': '电池SOC (%)',
                'Temperature (°C)': '温度 (°C)',
                'Humidity (%)': '湿度 (%)',
                'Wind Speed (m/s)': '风速 (m/s)',
                'Irradiance (W/m²)': '辐照度 (W/m²)',
                'Loading data...': '加载数据中...',
                '실시간 데이터 로그': '实时数据日志',
                '로그 지우기': '清除日志',
                '연결 중...': '连接中...',
                '실시간 연결': '实时连接',
                '연결 끊김': '连接断开',
                '마지막 업데이트': '最后更新',
                'Language': '语言'
            }
        };

        // PV Module Status 생성
        function createPVModuleStatus() {
            const container = document.getElementById('pv-module-status');
            container.innerHTML = '';
            
            const modules = [
                { id: 'Module 1', status: 'Active', color: 'green' },
                { id: 'Module 2', status: 'Active', color: 'green' },
                { id: 'Module 3', status: 'Maintenance', color: 'yellow' }
            ];
            
            modules.forEach(module => {
                const moduleDiv = document.createElement('div');
                moduleDiv.className = `p-4 border-l-4 border-${module.color}-400 bg-${module.color}-50 rounded-lg`;
                moduleDiv.innerHTML = `
                    <div class="font-semibold text-sm">${module.id}</div>
                    <div class="text-xs text-gray-600 mt-1">${module.status}</div>
                `;
                container.appendChild(moduleDiv);
            });
        }

        // 언어 변경 함수
        function changeLanguage(lang) {
            currentLanguage = lang;
            translations = translationData[lang] || translationData['ko'];
            applyTranslations();
        }

        // 번역 적용 함수
        function applyTranslations() {
            const elements = document.querySelectorAll('[data-translate]');
            elements.forEach(element => {
                const key = element.getAttribute('data-translate');
                if (translations[key]) {
                    element.textContent = translations[key];
                }
            });
        }

        // 태양광 판넬 데이터 생성
        function generatePanelData() {
            const panels = [];
            for (let i = 1; i <= totalPanels; i++) {
                const baseOutput = 300 + Math.random() * 50; // 300-350W
                const efficiency = 85 + Math.random() * 10; // 85-95%
                const temperature = 25 + Math.random() * 15; // 25-40°C
                
                panels.push({
                    id: `Panel-${i.toString().padStart(2, '0')}`,
                    position: `Row ${Math.ceil(i/4)} Col ${((i-1) % 4) + 1}`,
                    output: Math.round(baseOutput * (efficiency / 100)),
                    efficiency: Math.round(efficiency * 10) / 10,
                    temperature: Math.round(temperature * 10) / 10,
                    status: efficiency > 90 ? 'Excellent' : efficiency > 80 ? 'Good' : efficiency > 70 ? 'Fair' : 'Poor',
                    lastCheck: new Date().toLocaleString()
                });
            }
            return panels;
        }

        // 판넬 상태 카드 생성
        function createPanelStatusCards(panels) {
            const grid = document.getElementById('panel-status-grid');
            grid.innerHTML = '';
            
            panels.forEach(panel => {
                const statusColor = panel.status === 'Excellent' ? 'green' : 
                                  panel.status === 'Good' ? 'blue' : 
                                  panel.status === 'Fair' ? 'yellow' : 'red';
                
                const card = document.createElement('div');
                card.className = `bg-white border-l-4 border-${statusColor}-400 p-4 rounded-lg shadow`;
                card.innerHTML = `
                    <div class="flex justify-between items-center mb-2">
                        <h5 class="font-semibold text-sm">${panel.id}</h5>
                        <span class="px-2 py-1 text-xs rounded-full bg-${statusColor}-100 text-${statusColor}-800">${panel.status}</span>
                    </div>
                    <div class="text-xs text-gray-600 space-y-1">
                        <div>출력: <span class="font-medium">${panel.output}W</span></div>
                        <div>효율: <span class="font-medium">${panel.efficiency}%</span></div>
                        <div>온도: <span class="font-medium">${panel.temperature}°C</span></div>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        // 판넬 상세 테이블 업데이트
        function updatePanelDetailTable(panels) {
            const tbody = document.getElementById('panel-detail-table');
            tbody.innerHTML = '';
            
            panels.forEach(panel => {
                const row = document.createElement('tr');
                row.className = 'hover:bg-gray-50';
                row.innerHTML = `
                    <td class="px-4 py-2 text-sm font-medium">${panel.id}</td>
                    <td class="px-4 py-2 text-sm text-gray-600">${panel.position}</td>
                    <td class="px-4 py-2 text-sm">${panel.output}</td>
                    <td class="px-4 py-2 text-sm">${panel.efficiency}</td>
                    <td class="px-4 py-2 text-sm">${panel.temperature}</td>
                    <td class="px-4 py-2 text-sm">
                        <span class="px-2 py-1 text-xs rounded-full ${
                            panel.status === 'Excellent' ? 'bg-green-100 text-green-800' :
                            panel.status === 'Good' ? 'bg-blue-100 text-blue-800' :
                            panel.status === 'Fair' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                        }">${panel.status}</span>
                    </td>
                    <td class="px-4 py-2 text-sm text-gray-500">${panel.lastCheck}</td>
                `;
                tbody.appendChild(row);
            });
        }

        // 알림 생성
        function generatePanelAlerts(panels) {
            const alertsContainer = document.getElementById('panel-alerts');
            alertsContainer.innerHTML = '';
            
            const alerts = [];
            
            // 효율성 낮은 판넬 체크
            panels.forEach(panel => {
                if (panel.efficiency < 75) {
                    alerts.push({
                        type: 'warning',
                        message: `${panel.id} 효율성이 낮습니다 (${panel.efficiency}%)`,
                        time: new Date().toLocaleTimeString()
                    });
                }
                if (panel.temperature > 50) {
                    alerts.push({
                        type: 'error',
                        message: `${panel.id} 온도가 높습니다 (${panel.temperature}°C)`,
                        time: new Date().toLocaleTimeString()
                    });
                }
            });
            
            // 알림이 없으면 정상 메시지 표시
            if (alerts.length === 0) {
                alerts.push({
                    type: 'success',
                    message: '모든 판넬이 정상 작동 중입니다',
                    time: new Date().toLocaleTimeString()
                });
            }
            
            alerts.forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.className = `p-3 rounded-lg border-l-4 ${
                    alert.type === 'success' ? 'bg-green-50 border-green-400 text-green-700' :
                    alert.type === 'warning' ? 'bg-yellow-50 border-yellow-400 text-yellow-700' :
                    'bg-red-50 border-red-400 text-red-700'
                }`;
                alertDiv.innerHTML = `
                    <div class="flex justify-between items-center">
                        <span class="text-sm font-medium">${alert.message}</span>
                        <span class="text-xs text-gray-500">${alert.time}</span>
                    </div>
                `;
                alertsContainer.appendChild(alertDiv);
            });
        }

        // 실시간 데이터 테이블 업데이트
        function updateRealtimeDataTable(data) {
            const tbody = document.getElementById('realtime-data-table');
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';
            row.innerHTML = `
                <td class="px-4 py-2 text-sm">${data.timestamp}</td>
                <td class="px-4 py-2 text-sm">${data.solarPower.toFixed(2)}</td>
                <td class="px-4 py-2 text-sm">${data.batterySOC.toFixed(1)}</td>
                <td class="px-4 py-2 text-sm">${data.temperature.toFixed(1)}</td>
                <td class="px-4 py-2 text-sm">${data.humidity.toFixed(0)}</td>
                <td class="px-4 py-2 text-sm">${data.windSpeed.toFixed(1)}</td>
                <td class="px-4 py-2 text-sm">${data.irradiance.toFixed(0)}</td>
            `;
            tbody.insertBefore(row, tbody.firstChild);
            
            // 최대 20개 행만 유지
            while (tbody.children.length > 20) {
                tbody.removeChild(tbody.lastChild);
            }
        }

        // 에너지 상관관계 업데이트
        function updateEnergyCorrelations(data) {
            // 간단한 상관관계 계산 (실제로는 더 정교한 계산 필요)
            const tempCorrelation = (0.75 + Math.random() * 0.1).toFixed(2);
            const solarCorrelation = (0.90 + Math.random() * 0.05).toFixed(2);
            const humidityCorrelation = (-0.40 - Math.random() * 0.1).toFixed(2);
            
            document.getElementById('temp-consumption-correlation').textContent = tempCorrelation;
            document.getElementById('solar-generation-correlation').textContent = solarCorrelation;
            document.getElementById('humidity-efficiency-correlation').textContent = humidityCorrelation;
        }

        // 고급 날씨 분석 업데이트
        function updateAdvancedWeatherAnalysis(data) {
            // 평균값 계산 (실제로는 히스토리 데이터에서 계산)
            const avgTemp = (data.temperature + Math.random() * 5).toFixed(1);
            const avgHumidity = (data.humidity + Math.random() * 10).toFixed(0);
            const maxWind = (data.windSpeed + Math.random() * 2).toFixed(1);
            const solarIrradiance = data.irradiance.toFixed(0);
            
            document.getElementById('avg-temperature').textContent = avgTemp + '°C';
            document.getElementById('avg-humidity').textContent = avgHumidity + '%';
            document.getElementById('max-wind-speed').textContent = maxWind + ' m/s';
            document.getElementById('solar-irradiance').textContent = solarIrradiance + ' W/m²';
        }

        function updateCharts(data) {
            const now = new Date();
            const timeLabel = now.toLocaleTimeString();
            
            // 일일 발전량 누적
            dailyGeneration += data.solarPower * (5 / 3600); // 5초 간격을 시간으로 변환
            
            // 발전량 차트 업데이트
            powerData.push({x: timeLabel, y: data.solarPower});
            if (powerData.length > 20) powerData.shift();
            
            powerChart.data.labels = powerData.map(d => d.x);
            powerChart.data.datasets[0].data = powerData.map(d => d.y);
            powerChart.update('none');
            
            // 배터리 차트 업데이트
            batteryData.push({x: timeLabel, y: data.batterySOC});
            if (batteryData.length > 20) batteryData.shift();
            
            batteryChart.data.labels = batteryData.map(d => d.x);
            batteryChart.data.datasets[0].data = batteryData.map(d => d.y);
            batteryChart.update('none');
            
            // 태양광 판넬 데이터 업데이트
            const panels = generatePanelData();
            createPanelStatusCards(panels);
            updatePanelDetailTable(panels);
            generatePanelAlerts(panels);
            
            // 판넬 성능 차트 업데이트
            const panelOutputs = panels.slice(0, 6).map(p => p.output);
            panelPerformanceChart.data.datasets[0].data = panelOutputs;
            panelPerformanceChart.update('none');
            
            // 효율성 차트 업데이트 (동적 값)
            const avgEfficiency = panels.reduce((sum, p) => sum + p.efficiency, 0) / panels.length;
            const batteryEfficiency = 90 + Math.random() * 5; // 90-95%
            const systemLoss = 100 - avgEfficiency - batteryEfficiency + 10;
            
            efficiencyChart.data.datasets[0].data = [
                Math.round(avgEfficiency),
                Math.round(batteryEfficiency),
                Math.round(Math.max(0, systemLoss))
            ];
            efficiencyChart.update('none');
            
            // 새로운 기능들 업데이트
            updateRealtimeDataTable(data);
            updateEnergyCorrelations(data);
            updateAdvancedWeatherAnalysis(data);
            
            // Power Data Analysis Platform 메트릭 업데이트
            document.getElementById('solar-power-metric').textContent = data.solarPower.toFixed(2) + ' kW';
            document.getElementById('battery-soc-metric').textContent = data.batterySOC.toFixed(1) + '%';
            document.getElementById('temperature-metric').textContent = data.temperature.toFixed(1) + '°C';
            document.getElementById('humidity-metric').textContent = data.humidity.toFixed(0) + '%';
            
            // Solar Energy Management System 업데이트
            document.getElementById('current-generation').textContent = data.solarPower.toFixed(2) + ' kW';
            document.getElementById('today-generation').textContent = dailyGeneration.toFixed(1) + ' kWh';
        }

        // 로그 지우기 기능
        document.getElementById('clear-log').addEventListener('click', () => {
            document.getElementById('data-log').innerHTML = '';
        });

        // 페이지 로드 시 초기화
        document.addEventListener('DOMContentLoaded', () => {
            // 언어 설정 초기화
            translations = translationData[currentLanguage];
            
            // 차트 초기화
            initCharts();
            
            // PV Module Status 초기화
            createPVModuleStatus();
            
            // 언어 선택기 이벤트 리스너
            document.getElementById('language-selector').addEventListener('change', function(e) {
                changeLanguage(e.target.value);
            });
            
            // WebSocket 연결
            connect();
        });
    </script>
</body>
</html>
HTML_EOF

cd ..
show_success "Frontend 설정 완료"
echo ""

# 8. docker-compose.yml 생성 (개선된 버전)
show_progress "[8/12] Docker Compose 설정 중..."

cat > docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    container_name: solar-backend
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    environment:
      - BACKEND_PORT=${BACKEND_PORT:-8000}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - solar-network

  frontend:
    build: 
      context: ./frontend
      dockerfile: Dockerfile
    container_name: solar-frontend
    ports:
      - "${FRONTEND_PORT:-80}:80"
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - solar-network

networks:
  solar-network:
    driver: bridge

volumes:
  solar-data:
    driver: local
COMPOSE_EOF

show_success "Docker Compose 설정 완료"
echo ""

# 9. 배포 스크립트 생성 (개선된 버전)
show_progress "[9/12] 배포 스크립트 생성 중..."

cat > deploy.sh << 'DEPLOY_EOF'
#!/bin/bash
# 배포 스크립트 (개선된 버전)

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 실시간 태양광 대시보드 배포 시작...${NC}"

# 환경 변수 로드
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${YELLOW}환경 변수 로드됨${NC}"
fi

# 기존 컨테이너 정리
echo -e "${YELLOW}기존 컨테이너 정리 중...${NC}"
docker-compose down 2>/dev/null || true

# 이미지 빌드
echo -e "${YELLOW}Docker 이미지 빌드 중...${NC}"
docker-compose build --no-cache

# 컨테이너 시작
echo -e "${YELLOW}컨테이너 시작 중...${NC}"
docker-compose up -d

# 헬스체크 대기
echo -e "${YELLOW}서비스 시작 대기 중...${NC}"
sleep 10

# 상태 확인
echo -e "${GREEN}배포 완료!${NC}"
echo ""
echo "컨테이너 상태:"
docker-compose ps

echo ""
echo "접속 주소:"
echo "  Frontend: http://localhost:${FRONTEND_PORT:-80}"
echo "  Backend:  http://localhost:${BACKEND_PORT:-8000}"
echo "  API Docs: http://localhost:${BACKEND_PORT:-8000}/docs"
DEPLOY_EOF

chmod +x deploy.sh

# 관리 스크립트 생성
cat > manage.sh << 'MANAGE_EOF'
#!/bin/bash
# 관리 스크립트

case "$1" in
    "start")
        docker-compose up -d
        ;;
    "stop")
        docker-compose down
        ;;
    "restart")
        docker-compose restart
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        docker-compose ps
        ;;
    "update")
        git pull origin main
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    *)
        echo "사용법: $0 {start|stop|restart|logs|status|update}"
        exit 1
        ;;
esac
MANAGE_EOF

chmod +x manage.sh

show_success "배포 스크립트 생성 완료"
echo ""

# 10. .gitignore 업데이트
show_progress "[10/12] .gitignore 업데이트 중..."

cat >> .gitignore << 'IGNORE_EOF'

# 실시간 대시보드
backend/.env
backend/__pycache__/
backend/*.pyc
frontend/node_modules/
frontend/dist/
*.log
backup_*/
IGNORE_EOF

show_success ".gitignore 업데이트 완료"
echo ""

# 11. Docker 이미지 빌드
show_progress "[11/12] Docker 이미지 빌드 중... (시간이 걸릴 수 있습니다)"

# 환경 변수 로드
export $(cat .env | grep -v '^#' | xargs)

docker-compose build

show_success "Docker 이미지 빌드 완료"
echo ""

# 12. 컨테이너 시작 및 상태 확인
show_progress "[12/12] 컨테이너 시작 및 상태 확인 중..."

docker-compose up -d

# 서비스 시작 대기
show_info "서비스 시작 대기 중... (10초)"
sleep 10

show_success "컨테이너 시작 완료"
echo ""

# 상태 확인
echo "컨테이너 상태:"
docker-compose ps
echo ""

# 헬스체크
show_progress "헬스체크 수행 중..."

# Backend 헬스체크
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null; then
    show_success "Backend API 정상 작동 (http://localhost:$BACKEND_PORT)"
else
    show_warning "Backend API 응답 없음"
fi

# Frontend 확인
if curl -s http://localhost:$FRONTEND_PORT > /dev/null; then
    show_success "Frontend 정상 작동 (http://localhost:$FRONTEND_PORT)"
else
    show_warning "Frontend 응답 없음"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                        ║${NC}"
echo -e "${GREEN}║   ✅ 설치 완료!                                        ║${NC}"
echo -e "${GREEN}║                                                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📡 접속 주소:${NC}"
echo -e "   Frontend: ${YELLOW}http://localhost:$FRONTEND_PORT${NC}"
echo -e "   Backend:  ${YELLOW}http://localhost:$BACKEND_PORT${NC}"
echo -e "   API Docs: ${YELLOW}http://localhost:$BACKEND_PORT/docs${NC}"
echo -e "   WebSocket: ${YELLOW}ws://localhost:$BACKEND_PORT/ws${NC}"
echo ""
echo -e "${CYAN}🔧 유용한 명령어:${NC}"
echo -e "   로그 보기:    ${YELLOW}./manage.sh logs${NC}"
echo -e "   재시작:       ${YELLOW}./manage.sh restart${NC}"
echo -e "   중지:         ${YELLOW}./manage.sh stop${NC}"
echo -e "   상태 확인:    ${YELLOW}./manage.sh status${NC}"
echo -e "   업데이트:     ${YELLOW}./manage.sh update${NC}"
echo ""
echo -e "${CYAN}📚 다음 단계:${NC}"
echo "   1. 브라우저에서 http://localhost:$FRONTEND_PORT 접속"
echo "   2. 실시간 데이터가 5초마다 업데이트되는지 확인"
echo "   3. 문제 발생 시: ./manage.sh logs"
echo "   4. API 테스트: http://localhost:$BACKEND_PORT/docs"
echo ""
echo -e "${CYAN}🔄 백업 정보:${NC}"
if [ -d "$BACKUP_DIR" ]; then
    echo -e "   백업 위치: ${YELLOW}$BACKUP_DIR${NC}"
    echo -e "   복원 방법: ${YELLOW}cp -r $BACKUP_DIR $PROJECT_NAME${NC}"
fi
echo ""
echo -e "${GREEN}🎉 즐거운 모니터링 되세요! 🎉${NC}"
echo ""
