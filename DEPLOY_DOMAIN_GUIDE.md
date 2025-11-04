# damcp.gngmeta.com 도메인 배포 가이드

## 🚀 빠른 시작

### 1. DNS 설정 확인

도메인 관리자 패널에서 DNS A 레코드를 설정하세요:

```
Type: A
Name: damcp (또는 @)
Value: 34.47.89.217
TTL: 3600 (또는 기본값)
```

**DNS 설정 확인:**
```bash
nslookup damcp.gngmeta.com
# 또는
dig damcp.gngmeta.com
```

DNS가 올바르게 설정되었는지 확인한 후 배포를 진행하세요.

---

### 2. 배포 실행

프로젝트 루트 디렉토리에서 다음 명령을 실행하세요:

```bash
cd "/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"
bash deploy_domain.sh
```

이 스크립트는 다음을 자동으로 수행합니다:

1. ✅ 서버 환경 설정 (Python, Node.js, Nginx 설치)
2. ✅ 코드 배포 (Git clone/update)
3. ✅ Nginx 설정 (도메인 설정)
4. ✅ 백엔드 설정 (의존성 설치, 가상환경)
5. ✅ 프론트엔드 설정 (의존성 설치, 빌드)
6. ✅ SSL 인증서 발급 (Let's Encrypt)
7. ✅ 서비스 자동 시작 (systemd)

---

### 3. 수동 배포 (스크립트 사용 불가 시)

#### 3.1 서버 접속

```bash
# PEM 파일이 있는 경우
ssh -i google_compute_engine.pem -o IdentitiesOnly=yes metal@34.47.89.217

# 또는 일반 SSH 키 사용
ssh metal@34.47.89.217
```

#### 3.2 필수 패키지 설치

```bash
sudo apt-get update
sudo apt-get install -y git python3 python3-pip python3-venv curl nginx certbot python3-certbot-nginx

# Node.js 설치
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 3.3 코드 배포

```bash
cd /home/metal
mkdir -p energy-platform
cd energy-platform

# Git clone 또는 update
if [ -d ".git" ]; then
    git fetch origin
    git reset --hard origin/main
else
    git clone https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git .
fi
```

#### 3.4 백엔드 설정

```bash
cd backend

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3.5 프론트엔드 설정

```bash
cd ../frontend

# 의존성 설치
npm install

# 빌드
npm run build
```

#### 3.6 Nginx 설정

```bash
# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/damcp.gngmeta.com
```

다음 내용 입력:

```nginx
server {
    listen 80;
    server_name damcp.gngmeta.com;

    # Let's Encrypt 인증용
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        access_log off;
    }

    # API 문서
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

설정 활성화:

```bash
sudo ln -sf /etc/nginx/sites-available/damcp.gngmeta.com /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### 3.7 SSL 인증서 발급

```bash
sudo certbot --nginx -d damcp.gngmeta.com \
    --non-interactive \
    --agree-tos \
    --email admin@gngmeta.com \
    --redirect
```

#### 3.8 서비스 시작

**백엔드:**

```bash
cd /home/metal/energy-platform/backend
source venv/bin/activate
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

**프론트엔드:**

```bash
cd /home/metal/energy-platform/frontend
npm run preview -- --host 127.0.0.1 --port 3000
```

---

## ✅ 배포 확인

### 도메인 접속 확인

```bash
# HTTP
curl http://damcp.gngmeta.com/health

# HTTPS (SSL 인증서 발급 후)
curl https://damcp.gngmeta.com/health
curl https://damcp.gngmeta.com/api/health
```

### 브라우저에서 확인

- https://damcp.gngmeta.com
- https://damcp.gngmeta.com/api/health
- https://damcp.gngmeta.com/docs
- https://damcp.gngmeta.com/disaster
- https://damcp.gngmeta.com/energy-demand

---

## 🔧 서비스 관리

### 서비스 상태 확인

```bash
ssh metal@34.47.89.217

# 백엔드 상태
sudo systemctl status energy-backend

# 프론트엔드 상태
sudo systemctl status energy-frontend

# Nginx 상태
sudo systemctl status nginx
```

### 서비스 재시작

```bash
# 백엔드 재시작
sudo systemctl restart energy-backend

# 프론트엔드 재시작
sudo systemctl restart energy-frontend

# Nginx 재시작
sudo systemctl restart nginx
```

### 로그 확인

```bash
# 백엔드 로그
sudo journalctl -u energy-backend -f

# 프론트엔드 로그
sudo journalctl -u energy-frontend -f

# Nginx 로그
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔒 SSL 인증서 관리

### 인증서 확인

```bash
sudo certbot certificates
```

### 인증서 갱신 테스트

```bash
sudo certbot renew --dry-run
```

### 인증서 수동 갱신

```bash
sudo certbot renew
```

Let's Encrypt 인증서는 90일마다 자동으로 갱신됩니다.

---

## 🌐 GCP 방화벽 설정

GCP 콘솔에서 다음 포트를 열어야 합니다:

1. **GCP Console → Compute Engine → VM 인스턴스**
2. **VPC 네트워크 → 방화벽 규칙**

**필요한 규칙:**

- **HTTP (80)**: 모든 IP 허용
- **HTTPS (443)**: 모든 IP 허용

**또는 gcloud CLI 사용:**

```bash
# HTTP
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server

# HTTPS
gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags https-server
```

---

## 🐛 문제 해결

### DNS 설정 확인

```bash
# DNS 전파 확인
nslookup damcp.gngmeta.com
dig damcp.gngmeta.com

# 여러 DNS 서버 확인
dig @8.8.8.8 damcp.gngmeta.com
dig @1.1.1.1 damcp.gngmeta.com
```

### Nginx 설정 확인

```bash
# 설정 테스트
sudo nginx -t

# 설정 파일 확인
cat /etc/nginx/sites-available/damcp.gngmeta.com

# Nginx 로그 확인
sudo tail -f /var/log/nginx/error.log
```

### 서비스 연결 확인

```bash
# 백엔드 확인
curl http://127.0.0.1:8000/health

# 프론트엔드 확인
curl http://127.0.0.1:3000

# 포트 확인
sudo netstat -tulpn | grep -E ':(8000|3000|80|443)'
```

### SSL 인증서 발급 실패 시

```bash
# DNS 설정 확인
dig damcp.gngmeta.com

# 수동 발급
sudo certbot --nginx -d damcp.gngmeta.com

# 인증서 상태 확인
sudo certbot certificates
```

---

## 📝 참고 사항

- DNS 전파에는 최대 24-48시간이 소요될 수 있습니다
- SSL 인증서는 90일마다 자동 갱신됩니다
- 서비스는 systemd로 자동 시작됩니다
- 백엔드와 프론트엔드는 자동 재시작됩니다

---

## 🔄 업데이트 배포

코드가 업데이트된 경우:

```bash
cd "/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"
bash deploy_domain.sh
```

또는 서버에서 직접:

```bash
ssh metal@34.47.89.217
cd /home/metal/energy-platform
git fetch origin
git reset --hard origin/main
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && npm install && npm run build
sudo systemctl restart energy-backend energy-frontend
```

---

## 📞 지원

문제가 발생하면:

1. 로그 확인: `sudo journalctl -u energy-backend -f`
2. Nginx 로그 확인: `sudo tail -f /var/log/nginx/error.log`
3. 서비스 상태 확인: `sudo systemctl status energy-backend`


