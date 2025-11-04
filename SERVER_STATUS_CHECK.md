# 서버 상태 확인 가이드
## damcp.gngmeta.com 서버 진단

### 1. 서버 접속

```bash
cd /Users/donghokim/Documents/myworkspace/Energy_Agent/Ontology_EnergyMCP_Diaster
chmod 600 google_compute_engine.pem
ssh -F /dev/null -i google_compute_engine.pem -o "IdentitiesOnly=yes" -o "ServerAliveInterval=60" -o "StrictHostKeyChecking=no" metal@34.47.89.217
```

### 2. 서버 상태 확인 명령어

서버에 접속한 후 다음 명령어들을 실행하세요:

#### 2.1 서비스 상태 확인
```bash
# Backend 서비스 상태
sudo systemctl status energy-backend

# Frontend 서비스 상태 (있는 경우)
sudo systemctl status energy-frontend

# Nginx 서비스 상태
sudo systemctl status nginx
```

#### 2.2 포트 확인
```bash
# 리스닝 포트 확인
sudo ss -tlnp | grep -E ':(80|443|8000|3000)'
# 또는
sudo netstat -tlnp | grep -E ':(80|443|8000|3000)'
```

#### 2.3 프로세스 확인
```bash
# Python 프로세스 (Backend)
ps aux | grep -E "(uvicorn|python.*server)" | grep -v grep

# Node 프로세스 (Frontend)
ps aux | grep -E "(node|npm)" | grep -v grep

# Nginx 프로세스
ps aux | grep nginx | grep -v grep
```

#### 2.4 로컬 접속 테스트
```bash
# Backend Health Check
curl -v http://127.0.0.1:8000/health

# Frontend 접속 (있는 경우)
curl -v http://127.0.0.1:3000

# Nginx 접속
curl -v http://127.0.0.1
```

#### 2.5 로그 확인
```bash
# Backend 서비스 로그
sudo journalctl -u energy-backend -n 50 --no-pager

# Frontend 서비스 로그 (있는 경우)
sudo journalctl -u energy-frontend -n 50 --no-pager

# Nginx 에러 로그
sudo tail -50 /var/log/nginx/error.log

# Nginx 액세스 로그
sudo tail -50 /var/log/nginx/access.log
```

#### 2.6 Nginx 설정 확인
```bash
# Nginx 설정 파일 존재 여부
ls -la /etc/nginx/sites-available/damcp.gngmeta.com
ls -la /etc/nginx/sites-enabled/damcp.gngmeta.com

# Nginx 설정 검증
sudo nginx -t

# Nginx 설정 파일 내용 확인
sudo cat /etc/nginx/sites-available/damcp.gngmeta.com
```

### 3. 서버 복구 명령어

#### 3.1 서비스 시작
```bash
# Backend 서비스 시작
sudo systemctl start energy-backend
sudo systemctl enable energy-backend

# Frontend 서비스 시작 (있는 경우)
sudo systemctl start energy-frontend
sudo systemctl enable energy-frontend

# Nginx 서비스 시작
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 3.2 서비스 재시작
```bash
# 모든 서비스 재시작
sudo systemctl restart energy-backend energy-frontend nginx
```

#### 3.3 프로젝트 디렉토리 확인
```bash
# 프로젝트 디렉토리 확인
cd /home/metal/energy-platform
ls -la

# Backend 확인
cd backend
ls -la
cat requirements.txt | head -20

# Frontend 확인 (있는 경우)
cd ../frontend
ls -la
cat package.json | head -20
```

#### 3.4 Backend 수동 시작 (테스트)
```bash
cd /home/metal/energy-platform/backend
source venv/bin/activate
python server_cloud.py
# 또는
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

### 4. 일반적인 문제 해결

#### 4.1 서비스가 시작되지 않는 경우
```bash
# 1. 로그 확인
sudo journalctl -u energy-backend -n 100 --no-pager

# 2. 가상환경 확인
cd /home/metal/energy-platform/backend
ls -la venv/

# 3. 의존성 재설치
source venv/bin/activate
pip install -r requirements.txt

# 4. 서비스 파일 확인
sudo cat /etc/systemd/system/energy-backend.service
```

#### 4.2 Nginx가 502 에러를 반환하는 경우
```bash
# 1. Backend가 실행 중인지 확인
curl http://127.0.0.1:8000/health

# 2. Nginx 설정 확인
sudo nginx -t

# 3. Nginx 에러 로그 확인
sudo tail -50 /var/log/nginx/error.log
```

#### 4.3 포트가 리스닝되지 않는 경우
```bash
# 1. 포트 사용 확인
sudo lsof -i :8000
sudo lsof -i :3000
sudo lsof -i :80

# 2. 방화벽 확인
sudo ufw status
# GCP 콘솔에서도 방화벽 규칙 확인 필요
```

### 5. 빠른 복구 스크립트 실행

로컬에서 실행:
```bash
cd /Users/donghokim/Documents/myworkspace/Energy_Agent/Ontology_EnergyMCP_Diaster
bash scripts/fix_server.sh
```

### 6. 도메인 접속 테스트

로컬에서:
```bash
# HTTP 접속 테스트
curl -v http://damcp.gngmeta.com

# HTTPS 접속 테스트
curl -v -k https://damcp.gngmeta.com

# Health Check
curl http://damcp.gngmeta.com/health

# API Docs
curl http://damcp.gngmeta.com/docs
```

### 7. 문제 보고

서버 상태를 확인한 후 다음 정보를 수집하세요:
1. 서비스 상태 (systemctl status)
2. 포트 리스닝 상태
3. 최근 로그 (journalctl, nginx error log)
4. Nginx 설정 파일 내용
5. 도메인 접속 응답 코드

