# Git 배포 가이드 (GCP Compute Engine)

**서버 정보:**
- IP: 34.47.89.217
- 사용자: metal
- 배포 경로: /home/metal/energy-platform

---

## 📋 배포 방법

### 방법 1: 수동 배포 (권장 - SSH 키 문제 시)

#### 1단계: 서버 접속

```bash
# PPK 키를 사용하여 접속
ssh -i google_compute_engine.ppk metal@34.47.89.217

# 또는 SSH config 사용
ssh gcp-energy
```

#### 2단계: 서버에서 Git 설정 및 Clone

```bash
# 서버에 접속한 후 실행

# 1. 디렉토리 생성
mkdir -p /home/metal/energy-platform
cd /home/metal/energy-platform

# 2. Git 설치 확인 (필요시 설치)
sudo apt-get update
sudo apt-get install -y git

# 3. Git repository clone
git clone https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git .

# 4. 브랜치 확인
git branch
git status
```

#### 3단계: 서버 환경 설정

```bash
cd /home/metal/energy-platform

# Python 설치 (필요시)
sudo apt-get install -y python3 python3-pip python3-venv

# Node.js 설치 (필요시)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 백엔드 설정
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 프론트엔드 설정
cd ../frontend
npm install
```

#### 4단계: 환경 변수 설정

```bash
cd /home/metal/energy-platform/backend

# .env 파일 생성
cp .env.example .env
nano .env  # 또는 vi .env
```

필수 설정:
- `DATABASE_URL`: PostgreSQL 연결 정보
- `SECRET_KEY`: 랜덤 시크릿 키 생성
- `CORS_ORIGINS`: 프론트엔드 URL (`["http://34.47.89.217:3000"]`)

#### 5단계: 서비스 실행

```bash
cd /home/metal/energy-platform/backend
source venv/bin/activate

# 개발 모드
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 프로덕션 모드 (백그라운드)
nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
```

---

### 방법 2: SSH 키 설정 후 자동 배포

#### 1단계: PPK를 OpenSSH 형식으로 변환

**Mac에서:**
```bash
# putty 설치
brew install putty

# 변환
puttygen google_compute_engine.ppk -O private-openssh -o google_compute_engine_key
chmod 600 google_compute_engine_key
```

**Windows에서:**
1. PuTTY Gen 실행
2. Load → google_compute_engine.ppk 선택
3. Conversions → Export OpenSSH key
4. google_compute_engine_key로 저장

#### 2단계: SSH Config 설정

`~/.ssh/config` 파일에 추가:

```
Host gcp-energy
    HostName 34.47.89.217
    User metal
    IdentityFile /Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster/google_compute_engine_key
    StrictHostKeyChecking no
```

#### 3단계: 자동 배포 실행

```bash
cd "/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"
bash scripts/deploy_git_https.sh
```

---

## 🔄 업데이트 방법

### 서버에서 코드 업데이트

```bash
cd /home/metal/energy-platform

# 최신 코드 가져오기
git fetch origin
git pull origin main

# 백엔드 의존성 업데이트 (필요시)
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 프론트엔드 의존성 업데이트 (필요시)
cd ../frontend
npm install
npm run build  # 프로덕션 빌드

# 서비스 재시작
# 백엔드 프로세스 확인 및 재시작
```

---

## 🔧 서비스 관리

### systemd 서비스 설정 (프로덕션)

`/etc/systemd/system/energy-backend.service` 파일 생성:

```ini
[Unit]
Description=Energy Platform Backend
After=network.target postgresql.service

[Service]
Type=simple
User=metal
WorkingDirectory=/home/metal/energy-platform/backend
Environment="PATH=/home/metal/energy-platform/backend/venv/bin"
ExecStart=/home/metal/energy-platform/backend/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

서비스 시작:
```bash
sudo systemctl daemon-reload
sudo systemctl enable energy-backend
sudo systemctl start energy-backend
sudo systemctl status energy-backend
```

---

## 📊 확인

### 서비스 상태 확인

```bash
# 백엔드 API 확인
curl http://localhost:8000/health

# 또는 브라우저에서
http://34.47.89.217:8000/docs
http://34.47.89.217:8000/health
```

### 로그 확인

```bash
# systemd 서비스 로그
sudo journalctl -u energy-backend -f

# 또는 nohup 로그
tail -f /tmp/backend.log
```

---

## 🛠️ 문제 해결

### SSH 연결 실패

1. PPK 키를 OpenSSH 형식으로 변환
2. 키 권한 확인: `chmod 600 google_compute_engine_key`
3. SSH config 확인

### Git Clone 실패

1. HTTPS 사용 (SSH 키 없이도 가능)
2. 서버에서 인터넷 연결 확인
3. GitHub 접근 가능 확인

### 서비스 실행 오류

1. 가상환경 활성화 확인
2. 의존성 설치 확인: `pip list`
3. 포트 사용 확인: `netstat -tulpn | grep 8000`

---

## ✅ 배포 체크리스트

- [ ] 서버 접속 성공
- [ ] Git repository clone 완료
- [ ] Python 가상환경 생성
- [ ] 백엔드 의존성 설치
- [ ] 프론트엔드 의존성 설치
- [ ] .env 파일 설정
- [ ] 데이터베이스 연결 확인
- [ ] 서비스 실행 확인
- [ ] 방화벽 포트 오픈 확인

