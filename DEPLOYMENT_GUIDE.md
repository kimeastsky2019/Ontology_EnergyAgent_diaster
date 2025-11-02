# 서버 배포 가이드

**GCP Compute Engine 배포**

서버 정보:
- IP: 34.47.89.217
- 사용자: metal
- 배포 경로: /home/metal/energy-platform

---

## 1. SSH 키 설정

PPK 파일을 OpenSSH 형식으로 변환:

### 방법 1: puttygen 사용 (Windows/Mac)

```bash
# puttygen 설치 (Homebrew)
brew install putty

# PPK를 OpenSSH 형식으로 변환
puttygen google_compute_engine.ppk -O private-openssh -o google_compute_engine_key

# 키 권한 설정
chmod 600 google_compute_engine_key
```

### 방법 2: SSH Config 파일 설정 (Mac/Linux)

`~/.ssh/config` 파일에 추가:

```
Host gcp-energy
    HostName 34.47.89.217
    User metal
    IdentityFile /Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster/google_compute_engine_key
    StrictHostKeyChecking no
```

그 다음:
```bash
ssh gcp-energy
```

---

## 2. 자동 배포 (SSH 키 설정 후)

```bash
cd "/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"
bash scripts/deploy_to_server.sh
```

---

## 3. 수동 배포

### 3.1 프로젝트 파일 압축

```bash
cd "/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"

tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='.env' \
    --exclude='*.ppk' \
    --exclude='.DS_Store' \
    --exclude='*.log' \
    -czf /tmp/energy-platform-deploy.tar.gz .
```

### 3.2 서버에 디렉토리 생성

```bash
ssh metal@34.47.89.217 "mkdir -p /home/metal/energy-platform"
```

### 3.3 압축 파일 전송

```bash
scp /tmp/energy-platform-deploy.tar.gz metal@34.47.89.217:/home/metal/energy-platform/
```

### 3.4 서버에서 압축 해제

```bash
ssh metal@34.47.89.217 "cd /home/metal/energy-platform && tar -xzf energy-platform-deploy.tar.gz && rm energy-platform-deploy.tar.gz"
```

### 3.5 설정 스크립트 전송 및 실행

```bash
scp scripts/server_setup.sh metal@34.47.89.217:/home/metal/energy-platform/
ssh metal@34.47.89.217 "cd /home/metal/energy-platform && chmod +x server_setup.sh && bash server_setup.sh"
```

---

## 4. 서버 설정

### 4.1 환경 변수 설정

```bash
ssh metal@34.47.89.217
cd /home/metal/energy-platform/backend
cp .env.example .env
nano .env  # 또는 vi .env
```

필수 설정:
- `DATABASE_URL`: PostgreSQL 연결 정보
- `SECRET_KEY`: 랜덤 시크릿 키
- `CORS_ORIGINS`: 프론트엔드 URL

### 4.2 백엔드 설정

```bash
cd /home/metal/energy-platform/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 프론트엔드 설정

```bash
cd /home/metal/energy-platform/frontend
npm install
npm run build
```

---

## 5. 서비스 실행

### 5.1 백엔드 실행 (개발 모드)

```bash
cd /home/metal/energy-platform/backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5.2 백엔드 실행 (프로덕션 모드 - systemd)

`/etc/systemd/system/energy-backend.service` 파일 생성:

```ini
[Unit]
Description=Energy Platform Backend
After=network.target

[Service]
Type=simple
User=metal
WorkingDirectory=/home/metal/energy-platform/backend
Environment="PATH=/home/metal/energy-platform/backend/venv/bin"
ExecStart=/home/metal/energy-platform/backend/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

시작:
```bash
sudo systemctl daemon-reload
sudo systemctl enable energy-backend
sudo systemctl start energy-backend
sudo systemctl status energy-backend
```

### 5.3 프론트엔드 실행

```bash
cd /home/metal/energy-platform/frontend
npm run preview  # 빌드된 파일 서빙
```

또는 Nginx 설정 (프로덕션)

---

## 6. 방화벽 설정

GCP 콘솔에서 다음 포트 열기:
- 8000: Backend API
- 3000: Frontend (개발)
- 80/443: Nginx (프로덕션)

---

## 7. 데이터베이스 설정

PostgreSQL이 설치되어 있지 않다면:

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

데이터베이스 생성:
```bash
sudo -u postgres psql
CREATE DATABASE energy_db;
CREATE USER energy_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE energy_db TO energy_user;
\q
```

---

## 8. 확인

서비스 확인:
```bash
# Backend
curl http://localhost:8000/health

# 또는 브라우저에서
http://34.47.89.217:8000/docs
```

---

## 문제 해결

### SSH 연결 실패
1. PPK 키를 OpenSSH 형식으로 변환
2. 키 권한 확인: `chmod 600 google_compute_engine_key`
3. SSH config 파일 설정 확인

### 포트 접근 불가
1. GCP 콘솔에서 방화벽 규칙 확인
2. 서버 내부 방화벽 확인: `sudo ufw status`

### 서비스 실행 오류
1. 로그 확인: `journalctl -u energy-backend -f`
2. 가상환경 활성화 확인
3. 의존성 설치 확인

