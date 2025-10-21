# GCP 콘솔에서 HTTPS 설정하기

## 1. 방화벽 규칙 설정 (GCP 콘솔)

### 단계별 가이드:

1. **GCP 콘솔 접속**
   - https://console.cloud.google.com 접속
   - 해당 프로젝트 선택

2. **방화벽 규칙 생성**
   - 왼쪽 메뉴 → "VPC 네트워크" → "방화벽"
   - "방화벽 규칙 만들기" 클릭

3. **방화벽 규칙 설정**
   ```
   이름: allow-https
   설명: Allow HTTPS traffic on port 443
   방향: 수신
   대상: 지정된 대상 태그
   대상 태그: https-server
   소스 IP 범위: 0.0.0.0/0
   프로토콜 및 포트: 
     - TCP 체크
     - 포트: 443
   ```

4. **규칙 생성 완료**

## 2. Compute Engine 인스턴스에 태그 추가

1. **VM 인스턴스 페이지로 이동**
   - 왼쪽 메뉴 → "Compute Engine" → "VM 인스턴스"

2. **인스턴스 편집**
   - IP가 34.47.89.217인 인스턴스 클릭
   - "편집" 버튼 클릭

3. **네트워크 태그 추가**
   - "네트워킹" 섹션에서
   - "네트워크 태그" 필드에 `https-server` 입력
   - "저장" 클릭

## 3. SSH로 서버 접속하여 HTTPS 설정

### SSH 접속 방법:
1. **GCP 콘솔에서 SSH 접속**
   - VM 인스턴스 페이지에서 해당 인스턴스의 "SSH" 버튼 클릭
   - 브라우저에서 터미널이 열림

2. **또는 로컬 터미널에서 접속**
   ```bash
   # SSH 키가 설정되어 있다면
   ssh metal@34.47.89.217
   ```

### 서버에서 실행할 명령어들:

```bash
# 1. 시스템 업데이트 및 certbot 설치
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. nginx 중지
sudo systemctl stop nginx

# 3. SSL 인증서 발급
sudo certbot certonly --standalone -d damcp.gngmeta.com --non-interactive --agree-tos --email admin@gngmeta.com

# 4. nginx 설정 파일 백업
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# 5. 새로운 nginx 설정 적용
sudo cp /path/to/nginx_https.conf /etc/nginx/nginx.conf

# 6. nginx 설정 테스트
sudo nginx -t

# 7. nginx 시작
sudo systemctl start nginx
sudo systemctl enable nginx

# 8. 서비스 상태 확인
sudo systemctl status nginx
```

## 4. 설정 확인

### 테스트 명령어:
```bash
# HTTP 접속 (HTTPS로 리다이렉트되는지 확인)
curl -I http://damcp.gngmeta.com

# HTTPS 접속
curl -I https://damcp.gngmeta.com

# SSL 인증서 확인
openssl s_client -connect damcp.gngmeta.com:443 -servername damcp.gngmeta.com
```

## 5. 문제 해결

### SSL 인증서 발급 실패 시:
- 도메인이 올바르게 설정되어 있는지 확인
- 포트 80이 열려있는지 확인
- DNS 설정이 올바른지 확인

### nginx 시작 실패 시:
- 설정 파일 문법 확인: `sudo nginx -t`
- 로그 확인: `sudo tail -f /var/log/nginx/error.log`
- 백업에서 복원: `sudo cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf`

### 방화벽 문제 시:
- GCP 콘솔에서 방화벽 규칙이 올바르게 생성되었는지 확인
- 인스턴스에 `https-server` 태그가 추가되었는지 확인
- 포트 443이 열려있는지 확인: `sudo netstat -tlnp | grep :443`
