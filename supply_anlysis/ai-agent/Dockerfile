FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 모델 저장 디렉토리 생성
RUN mkdir -p /app/models

EXPOSE 8001

CMD ["python", "-m", "app.main"]
