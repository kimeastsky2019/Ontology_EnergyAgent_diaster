# Multi-MCP Time Series Analysis System Dockerfile

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
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 추가 패키지 설치 (웹 서비스용)
RUN pip install --no-cache-dir \
    flask \
    flask-cors \
    flask-socketio \
    sqlalchemy \
    psycopg2-binary

# 애플리케이션 코드 복사
COPY . .

# 디렉토리 생성
RUN mkdir -p logs data models/forecasting models/anomaly_detection

# 포트 노출
EXPOSE 5000 5001 8001 8002 8003

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV FLASK_APP=web_service/app.py
ENV FLASK_ENV=production

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 시작 스크립트
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]


