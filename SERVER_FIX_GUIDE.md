# 서버 /disaster 경로 문제 해결 가이드

## 문제
`https://damcp.gngmeta.com/disaster` 접속 시 `{"detail":"Not Found"}` 오류 발생

## 즉시 해결 방법

### 방법 1: 자동 스크립트 (권장)

서버에 접속하여 다음 명령어 실행:

```bash
ssh metal@34.47.89.217
cd /home/metal/energy-platform
bash scripts/fix_disaster_complete.sh
```

이 스크립트가 자동으로:
- 코드 업데이트
- Nginx 설정 업데이트
- 서버 상태 확인
- 연결 테스트

### 방법 2: 수동 실행

```bash
# 1. 서버 접속
ssh metal@34.47.89.217
cd /home/metal/energy-platform

# 2. 코드 업데이트
git pull origin main

# 3. Nginx 설정 업데이트
sudo cp scripts/nginx_config.conf /etc/nginx/sites-available/damcp.gngmeta.com
sudo nginx -t
sudo systemctl reload nginx

# 4. 프론트엔드 서버 시작 (미실행 시)
cd frontend
npm run dev
# 또는 백그라운드:
# nohup npm run dev > /tmp/frontend.log 2>&1 &
```

## 문제 진단

### 디버깅 스크립트 실행

```bash
bash scripts/debug_server.sh
```

이 스크립트는 다음을 확인합니다:
- Nginx 설정 상태
- 프론트엔드/백엔드 서버 실행 상태
- 로컬 연결 테스트
- Nginx 로그 확인

### 수동 진단

```bash
# 1. 프론트엔드 서버 확인
curl http://127.0.0.1:3000/disaster

# 2. 백엔드 서버 확인
curl http://127.0.0.1:8000/health

# 3. Nginx 설정 확인
sudo cat /etc/nginx/sites-available/damcp.gngmeta.com | grep -A 5 "disaster"

# 4. Nginx 로그 확인
sudo tail -f /var/log/nginx/damcp-error.log
```

## 예상 동작

정상 작동 시:
1. `https://damcp.gngmeta.com/disaster` 접속
2. Nginx가 요청을 프론트엔드(포트 3000)로 프록시
3. Vite 개발 서버가 HTML 응답 (React Router가 처리)
4. 브라우저에서 React Router가 `/disaster` 경로를 `Disaster` 컴포넌트로 라우팅

## 자주 발생하는 문제

### 1. 프론트엔드 서버 미실행

**증상**: `{"detail":"Not Found"}` 또는 연결 오류

**해결**:
```bash
cd /home/metal/energy-platform/frontend
npm run dev
```

### 2. Nginx 설정 미업데이트

**증상**: 여전히 백엔드로 라우팅

**해결**:
```bash
sudo cp /home/metal/energy-platform/scripts/nginx_config.conf \
        /etc/nginx/sites-available/damcp.gngmeta.com
sudo nginx -t
sudo systemctl reload nginx
```

### 3. 포트 충돌

**증상**: 서버 시작 실패

**해결**:
```bash
# 포트 확인
sudo netstat -tlnp | grep -E ':(3000|8000)'

# 기존 프로세스 종료
pkill -f "vite.*3000"
pkill -f "uvicorn.*8000"
```

### 4. 방화벽 문제

**증상**: 외부에서 접속 불가

**해결**:
```bash
# GCP 콘솔에서 방화벽 규칙 확인
# - 80 (HTTP)
# - 443 (HTTPS)
```

## 프로세스 관리

### PM2 사용 (권장)

```bash
# 프론트엔드
cd /home/metal/energy-platform/frontend
pm2 start npm --name "frontend" -- run dev

# 백엔드
cd /home/metal/energy-platform/backend
pm2 start "uvicorn src.main:app --host 0.0.0.0 --port 8000" --name "backend"

# 상태 확인
pm2 status
pm2 logs
```

### Systemd 서비스 (프로덕션)

```bash
# 프론트엔드 서비스 생성
sudo nano /etc/systemd/system/frontend.service

# 백엔드 서비스 생성
sudo nano /etc/systemd/system/backend.service

# 서비스 시작
sudo systemctl start frontend
sudo systemctl start backend
sudo systemctl enable frontend
sudo systemctl enable backend
```

## 확인 체크리스트

- [ ] 코드가 최신 버전인가? (`git pull`)
- [ ] Nginx 설정이 업데이트되었는가?
- [ ] Nginx가 재시작되었는가?
- [ ] 프론트엔드 서버가 실행 중인가? (포트 3000)
- [ ] 백엔드 서버가 실행 중인가? (포트 8000)
- [ ] 로컬에서 프론트엔드 접속이 가능한가? (`curl http://127.0.0.1:3000/disaster`)
- [ ] Nginx 로그에 오류가 없는가?

## 추가 지원

문제가 계속되면:
1. `bash scripts/debug_server.sh` 실행
2. 출력 결과 확인
3. Nginx 로그 확인: `sudo tail -f /var/log/nginx/damcp-error.log`

