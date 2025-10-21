# 서버에서 HTTPS 설정하기

## 🖥️ GCP Compute Engine 서버 접속 방법

### 방법 1: GCP 콘솔 브라우저 SSH (권장)
1. https://console.cloud.google.com 접속
2. **"Compute Engine"** → **"VM 인스턴스"**
3. **IP가 34.47.89.217인 인스턴스** 클릭
4. **"SSH"** 버튼 클릭 (브라우저에서 터미널 열림)

### 방법 2: 로컬 터미널 (SSH 키 설정된 경우)
```bash
ssh metal@34.47.89.217
```

## 🚀 HTTPS 설정 실행

### 1단계: 스크립트 다운로드
```bash
# 스크립트를 서버에 업로드하거나 직접 생성
wget https://raw.githubusercontent.com/your-repo/deploy_https.sh
# 또는 직접 생성
```

### 2단계: 스크립트 실행
```bash
chmod +x deploy_https.sh
./deploy_https.sh
```

### 3단계: 수동 설정 (스크립트 사용 불가능한 경우)

#### 시스템 업데이트
```bash
sudo apt update -y
sudo apt install -y certbot python3-certbot-nginx nginx-common
```

#### nginx 중지
```bash
sudo systemctl stop nginx
```

#### SSL 인증서 발급
```bash
sudo certbot certonly --standalone -d damcp.gngmeta.com --non-interactive --agree-tos --email admin@gngmeta.com
```

#### nginx 설정 업데이트
```bash
# 기존 설정 백업
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# 새 설정 적용 (deploy_https.sh의 nginx 설정 부분 복사)
sudo nano /etc/nginx/nginx.conf
```

#### nginx 시작
```bash
sudo nginx -t  # 설정 테스트
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 방화벽 설정
```bash
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp
```

## 🔍 설정 확인

### 서비스 상태 확인
```bash
sudo systemctl status nginx
```

### HTTPS 연결 테스트
```bash
curl -I https://damcp.gngmeta.com
```

### SSL 인증서 확인
```bash
openssl s_client -connect damcp.gngmeta.com:443 -servername damcp.gngmeta.com
```

## 🛠️ 문제 해결

### SSL 인증서 발급 실패
```bash
# 도메인 확인
nslookup damcp.gngmeta.com

# 포트 80 확인
sudo netstat -tlnp | grep :80
```

### nginx 시작 실패
```bash
# 설정 파일 문법 확인
sudo nginx -t

# 로그 확인
sudo tail -f /var/log/nginx/error.log
```

### 방화벽 문제
```bash
# 포트 443 확인
sudo netstat -tlnp | grep :443

# UFW 상태 확인
sudo ufw status
```

## ✅ 완료 확인

설정 완료 후 다음 URL로 접속 테스트:
- 🔒 **HTTPS**: https://damcp.gngmeta.com
- 🔄 **HTTP**: http://damcp.gngmeta.com (자동 리다이렉트)

브라우저에서 자물쇠 아이콘이 표시되면 성공입니다! 🎉
