# 도메인 설정 가이드

**도메인**: damcp.gngmeta.com  
**서버 IP**: 34.47.89.217

---

## 📋 설정 단계

### 1. DNS 설정

도메인 관리자 패널에서 DNS 레코드를 설정하세요:

```
Type: A
Name: damcp (또는 @)
Value: 34.47.89.217
TTL: 3600 (또는 기본값)
```

**확인 방법:**
```bash
nslookup damcp.gngmeta.com
# 또는
dig damcp.gngmeta.com
```

---

### 2. 서버 접속 및 Nginx 설치

```bash
# 서버 접속
ssh metal@34.47.89.217

# Nginx 및 Certbot 설치
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

---

### 3. Nginx 설정

#### 3.1 설정 파일 생성

```bash
sudo nano /etc/nginx/sites-available/damcp.gngmeta.com
```

다음 내용 입력 (또는 `scripts/nginx_config.conf` 파일 참조):

```nginx
# HTTP 서버 (SSL 인증서 발급 전)
server {
    listen 80;
    server_name damcp.gngmeta.com;

    # Let's Encrypt 인증용
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # API 프록시
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
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # API 문서
    location /docs {
        proxy_pass http://127.0.0.1:8000;
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
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### 3.2 설정 활성화

```bash
# 심볼릭 링크 생성
sudo ln -sf /etc/nginx/sites-available/damcp.gngmeta.com /etc/nginx/sites-enabled/

# 기본 사이트 비활성화 (선택사항)
sudo rm -f /etc/nginx/sites-enabled/default

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

### 4. SSL 인증서 발급 (Let's Encrypt)

```bash
# SSL 인증서 발급 및 자동 설정
sudo certbot --nginx -d damcp.gngmeta.com \
    --non-interactive \
    --agree-tos \
    --email admin@gngmeta.com \
    --redirect
```

**또는 대화형 모드:**
```bash
sudo certbot --nginx -d damcp.gngmeta.com
```

---

### 5. 방화벽 설정 (GCP)

GCP 콘솔에서 다음 포트를 열어야 합니다:

1. **GCP Console → Compute Engine → VM 인스턴스**
2. **네트워크 태그 확인**
3. **VPC 네트워크 → 방화벽 규칙**

**필요한 규칙:**
- HTTP (80): 모든 IP 허용
- HTTPS (443): 모든 IP 허용

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

### 6. 서비스 실행

#### 백엔드 실행

```bash
cd /home/metal/energy-platform/backend
source venv/bin/activate
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

**프로덕션 모드 (systemd):**
```bash
# systemd 서비스 파일 생성
sudo nano /etc/systemd/system/energy-backend.service
```

#### 프론트엔드 실행

```bash
cd /home/metal/energy-platform/frontend
npm run build
npm run preview -- --host 127.0.0.1 --port 3000
```

---

## ✅ 확인

### 도메인 접속 확인

```bash
# HTTP
curl http://damcp.gngmeta.com/health

# HTTPS (SSL 인증서 발급 후)
curl https://damcp.gngmeta.com/health
```

### 브라우저에서 확인

- http://damcp.gngmeta.com
- https://damcp.gngmeta.com (SSL 발급 후)
- https://damcp.gngmeta.com/docs
- https://damcp.gngmeta.com/api/health

---

## 🔧 문제 해결

### DNS 설정 확인

```bash
# DNS 전파 확인
nslookup damcp.gngmeta.com
dig damcp.gngmeta.com

# 여러 DNS 서버 확인
dig @8.8.8.8 damcp.gngmeta.com
dig @1.1.1.1 damcp.gngmeta.com
```

### Nginx 상태 확인

```bash
# Nginx 상태
sudo systemctl status nginx

# Nginx 로그
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### SSL 인증서 확인

```bash
# 인증서 정보
sudo certbot certificates

# 인증서 갱신 테스트
sudo certbot renew --dry-run
```

---

## 🔄 자동 배포 스크립트

### 방법 1: 원격 실행

```bash
cd "/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"
bash scripts/remote_setup_domain.sh
```

### 방법 2: 서버에서 직접 실행

```bash
ssh metal@34.47.89.217
cd /home/metal/energy-platform
bash scripts/setup_domain.sh
```

---

## 📝 참고 사항

- DNS 전파는 최대 24-48시간 소요될 수 있습니다
- SSL 인증서는 90일마다 자동 갱신됩니다
- Nginx 재시작 후 설정이 적용됩니다

