# 통합 에너지 분석 시스템 Dockerfile

FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 추가 패키지 설치 (통합 시스템용)
RUN pip install --no-cache-dir \
    flask \
    flask-cors \
    flask-socketio \
    sqlalchemy \
    psycopg2-binary \
    redis \
    requests \
    asyncio-mqtt \
    prometheus-client \
    psutil

# 애플리케이션 코드 복사
COPY . .

# 상위 디렉토리에서 필요한 파일들 복사
COPY ../config ./config
COPY ../tools ./tools
COPY ../multi_mcp_system ./multi_mcp_system

# 디렉토리 생성
RUN mkdir -p logs data models/forecasting models/anomaly_detection

# 포트 노출
EXPOSE 5002 5003 8005

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV FLASK_APP=energy_dashboard.py
ENV FLASK_ENV=production

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/api/v1/health || exit 1

# 시작 스크립트
COPY docker/start-integrated.sh /start-integrated.sh
RUN chmod +x /start-integrated.sh

CMD ["/start-integrated.sh"]


