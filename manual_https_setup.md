# HTTPS 설정 가이드

## 1. GCP Compute Engine에서 실행할 명령어들

### SSH 접속
```bash
ssh metal@34.47.89.217
```

### 1단계: 시스템 업데이트 및 certbot 설치
```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### 2단계: nginx 중지
```bash
sudo systemctl stop nginx
```

### 3단계: Let's Encrypt SSL 인증서 발급
```bash
sudo certbot certonly --standalone -d damcp.gngmeta.com --non-interactive --agree-tos --email admin@gngmeta.com
```

### 4단계: nginx 설정 파일 생성
```bash
sudo tee /etc/nginx/nginx.conf > /dev/null << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream energy_analysis {
        server localhost:8000;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name damcp.gngmeta.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name damcp.gngmeta.com;

        # SSL configuration
        ssl_certificate /etc/letsencrypt/live/damcp.gngmeta.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/damcp.gngmeta.com/privkey.pem;
        
        # SSL security settings
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        location / {
            proxy_pass http://energy_analysis;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port $server_port;
        }

        location /health {
            proxy_pass http://energy_analysis/health;
            access_log off;
        }
    }
}
EOF
```

### 5단계: nginx 설정 테스트
```bash
sudo nginx -t
```

### 6단계: nginx 시작
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 7단계: 방화벽 확인
```bash
sudo ufw status
sudo ufw allow 443/tcp
```

## 2. GCP 콘솔에서 방화벽 규칙 설정

### 방화벽 규칙 생성
1. GCP 콘솔 → VPC 네트워크 → 방화벽
2. "방화벽 규칙 만들기" 클릭
3. 다음 설정 입력:
   - 이름: `allow-https`
   - 방향: 수신
   - 대상: 지정된 대상 태그
   - 대상 태그: `https-server`
   - 소스 IP 범위: `0.0.0.0/0`
   - 프로토콜 및 포트: TCP, 포트 443

### Compute Engine 인스턴스에 태그 추가
1. GCP 콘솔 → Compute Engine → VM 인스턴스
2. 해당 인스턴스 클릭 → 편집
3. 네트워크 태그에 `https-server` 추가

## 3. SSL 인증서 자동 갱신 설정

```bash
sudo crontab -e
```

다음 줄 추가:
```
0 12 * * * /usr/bin/certbot renew --quiet
```

## 4. 테스트

설정 완료 후 다음 URL로 접속 테스트:
- https://damcp.gngmeta.com
- http://damcp.gngmeta.com (자동으로 HTTPS로 리다이렉트)

## 5. 문제 해결

### SSL 인증서 발급 실패 시
```bash
# 도메인 확인
nslookup damcp.gngmeta.com

# 포트 80이 열려있는지 확인
sudo netstat -tlnp | grep :80
```

### nginx 시작 실패 시
```bash
# 설정 파일 문법 확인
sudo nginx -t

# 로그 확인
sudo tail -f /var/log/nginx/error.log
```

### 방화벽 문제 시
```bash
# GCP 방화벽 규칙 확인
gcloud compute firewall-rules list

# 인스턴스 태그 확인
gcloud compute instances describe INSTANCE_NAME --zone=ZONE
```
