#!/bin/bash

# HTTPS 설정 스크립트
# GCP Compute Engine에서 실행

echo "=== HTTPS 설정 시작 ==="

# 1. 시스템 업데이트
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. nginx 중지 (certbot이 설정을 수정할 수 있도록)
sudo systemctl stop nginx

# 3. Let's Encrypt SSL 인증서 발급
sudo certbot certonly --standalone -d damcp.gngmeta.com --non-interactive --agree-tos --email admin@gngmeta.com

# 4. nginx HTTPS 설정 파일 생성
sudo tee /etc/nginx/sites-available/damcp-https > /dev/null << 'EOF'
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

# 5. 기존 nginx 설정 백업 및 새 설정 적용
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
sudo cp /etc/nginx/sites-available/damcp-https /etc/nginx/nginx.conf

# 6. nginx 설정 테스트
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "nginx 설정이 올바릅니다."
    
    # 7. nginx 시작
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    # 8. 방화벽 규칙 확인 (포트 443 열기)
    echo "방화벽 규칙 확인 중..."
    sudo ufw status
    
    # 9. 서비스 상태 확인
    echo "=== 서비스 상태 확인 ==="
    sudo systemctl status nginx --no-pager
    sudo systemctl status python3 --no-pager || echo "Python 서비스가 실행되지 않음"
    
    echo "=== HTTPS 설정 완료 ==="
    echo "이제 https://damcp.gngmeta.com 으로 접속할 수 있습니다."
    
else
    echo "nginx 설정에 오류가 있습니다. 백업에서 복원합니다."
    sudo cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf
    sudo systemctl start nginx
fi

# 10. SSL 인증서 자동 갱신 설정
echo "SSL 인증서 자동 갱신 설정..."
sudo crontab -l 2>/dev/null | grep -v certbot > /tmp/crontab_backup
echo "0 12 * * * /usr/bin/certbot renew --quiet" >> /tmp/crontab_backup
sudo crontab /tmp/crontab_backup
rm /tmp/crontab_backup

echo "=== 설정 완료 ==="
