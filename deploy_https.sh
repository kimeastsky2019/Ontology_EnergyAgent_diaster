#!/bin/bash

# HTTPS 자동 배포 스크립트
# GCP Compute Engine에서 실행

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 HTTPS 설정을 시작합니다..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 시스템 업데이트
log_info "시스템 패키지를 업데이트합니다..."
sudo apt update -y

# 2. 필요한 패키지 설치
log_info "필요한 패키지를 설치합니다..."
sudo apt install -y certbot python3-certbot-nginx nginx-common

# 3. 현재 nginx 상태 확인
log_info "현재 nginx 상태를 확인합니다..."
if systemctl is-active --quiet nginx; then
    log_info "nginx가 실행 중입니다. 중지합니다..."
    sudo systemctl stop nginx
else
    log_info "nginx가 중지 상태입니다."
fi

# 4. 기존 설정 백업
log_info "기존 nginx 설정을 백업합니다..."
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)

# 5. SSL 인증서 발급
log_info "SSL 인증서를 발급합니다..."
if sudo certbot certonly --standalone -d damcp.gngmeta.com --non-interactive --agree-tos --email admin@gngmeta.com; then
    log_success "SSL 인증서 발급 완료!"
else
    log_error "SSL 인증서 발급 실패!"
    exit 1
fi

# 6. nginx HTTPS 설정 생성
log_info "nginx HTTPS 설정을 생성합니다..."
sudo tee /etc/nginx/nginx.conf > /dev/null << 'EOF'
events {
    worker_connections 1024;
}

http {
    # 로그 설정
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # 기본 설정
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # MIME 타입
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    upstream energy_analysis {
        server localhost:8000;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name damcp.gngmeta.com;
        
        # Let's Encrypt 인증을 위한 경로
        location /.well-known/acme-challenge/ {
            root /var/www/html;
        }
        
        # 모든 HTTP 요청을 HTTPS로 리다이렉트
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name damcp.gngmeta.com;

        # SSL 인증서 설정
        ssl_certificate /etc/letsencrypt/live/damcp.gngmeta.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/damcp.gngmeta.com/privkey.pem;
        
        # SSL 보안 설정
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES256-SHA256;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        ssl_session_tickets off;
        
        # OCSP Stapling
        ssl_stapling on;
        ssl_stapling_verify on;
        ssl_trusted_certificate /etc/letsencrypt/live/damcp.gngmeta.com/chain.pem;
        
        # 보안 헤더
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' https://cdnjs.cloudflare.com;" always;

        # 메인 애플리케이션 프록시
        location / {
            proxy_pass http://energy_analysis;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port $server_port;
            
            # 타임아웃 설정
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # 버퍼 설정
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        # 헬스 체크 엔드포인트
        location /health {
            proxy_pass http://energy_analysis/health;
            access_log off;
        }
        
        # 정적 파일 캐싱
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            proxy_pass http://energy_analysis;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

# 7. nginx 설정 테스트
log_info "nginx 설정을 테스트합니다..."
if sudo nginx -t; then
    log_success "nginx 설정이 올바릅니다!"
else
    log_error "nginx 설정에 오류가 있습니다!"
    sudo nginx -t
    exit 1
fi

# 8. nginx 시작
log_info "nginx를 시작합니다..."
sudo systemctl start nginx
sudo systemctl enable nginx

# 9. 방화벽 설정 확인
log_info "방화벽 설정을 확인합니다..."
if command -v ufw >/dev/null 2>&1; then
    sudo ufw allow 443/tcp
    sudo ufw allow 80/tcp
    log_success "UFW 방화벽 규칙이 설정되었습니다."
else
    log_warning "UFW가 설치되지 않았습니다. GCP 방화벽 규칙을 확인하세요."
fi

# 10. 서비스 상태 확인
log_info "서비스 상태를 확인합니다..."
if systemctl is-active --quiet nginx; then
    log_success "nginx가 정상적으로 실행 중입니다!"
else
    log_error "nginx 시작에 실패했습니다!"
    sudo systemctl status nginx
    exit 1
fi

# 11. SSL 인증서 자동 갱신 설정
log_info "SSL 인증서 자동 갱신을 설정합니다..."
(crontab -l 2>/dev/null | grep -v certbot; echo "0 12 * * * /usr/bin/certbot renew --quiet --renew-hook 'systemctl reload nginx'") | crontab -

# 12. 연결 테스트
log_info "HTTPS 연결을 테스트합니다..."
sleep 5

if curl -s -I https://damcp.gngmeta.com | grep -q "HTTP/2 200\|HTTP/1.1 200"; then
    log_success "HTTPS 연결이 성공했습니다!"
elif curl -s -I https://damcp.gngmeta.com | grep -q "HTTP/2 301\|HTTP/1.1 301"; then
    log_success "HTTPS 리다이렉트가 정상 작동합니다!"
else
    log_warning "HTTPS 연결 테스트에 실패했습니다. 수동으로 확인해주세요."
fi

# 13. 최종 상태 출력
echo ""
echo "🎉 HTTPS 설정이 완료되었습니다!"
echo ""
echo "📋 설정 요약:"
echo "  ✅ SSL 인증서: Let's Encrypt"
echo "  ✅ HTTP → HTTPS 자동 리다이렉트"
echo "  ✅ 보안 헤더 설정"
echo "  ✅ 자동 인증서 갱신"
echo ""
echo "🌐 접속 URL:"
echo "  🔒 HTTPS: https://damcp.gngmeta.com"
echo "  🔄 HTTP: http://damcp.gngmeta.com (자동 리다이렉트)"
echo ""
echo "🔧 관리 명령어:"
echo "  nginx 상태 확인: sudo systemctl status nginx"
echo "  nginx 재시작: sudo systemctl restart nginx"
echo "  SSL 인증서 갱신: sudo certbot renew"
echo "  nginx 로그 확인: sudo tail -f /var/log/nginx/error.log"
echo ""
