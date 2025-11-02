# /disaster 경로 문제 해결 가이드

## 문제
`https://damcp.gngmeta.com/disaster` 접속 시 `{"detail":"Not Found"}` 오류 발생

## 원인
1. Nginx 설정이 `/disaster`를 백엔드로 라우팅
2. 프론트엔드 서버(포트 3000) 미실행
3. React Router SPA 라우팅 미처리

## 해결 방법

### 1. 서버에 접속
```bash
ssh metal@34.47.89.217
cd /home/metal/energy-platform
```

### 2. 코드 업데이트
```bash
git pull origin main
```

### 3. Nginx 설정 업데이트
```bash
sudo cp scripts/nginx_config.conf /etc/nginx/sites-available/damcp.gngmeta.com
sudo nginx -t
sudo systemctl reload nginx
```

### 4. 프론트엔드 서버 실행 확인
```bash
# 프론트엔드 서버가 실행 중인지 확인
curl http://127.0.0.1:3000

# 실행되지 않은 경우 시작
cd frontend
npm install  # 필요한 경우
npm run dev  # 또는 pm2, systemd 등으로 관리
```

### 5. 백엔드 서버 실행 확인
```bash
# 백엔드 서버가 실행 중인지 확인
curl http://127.0.0.1:8000/health

# 실행되지 않은 경우 시작
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 6. 자동 스크립트 사용
```bash
bash scripts/fix_disaster_route.sh
```

## 설정 확인

### Nginx 로그 확인
```bash
sudo tail -f /var/log/nginx/damcp-access.log
sudo tail -f /var/log/nginx/damcp-error.log
```

### 서버 상태 확인
```bash
# 포트 확인
sudo netstat -tlnp | grep -E ':(3000|8000)'

# 프로세스 확인
ps aux | grep -E '(node|vite|uvicorn|python)'
```

### 접속 테스트
```bash
# 로컬 테스트
curl http://127.0.0.1:3000/disaster

# 원격 테스트
curl https://damcp.gngmeta.com/disaster
```

## 예상 동작

1. `https://damcp.gngmeta.com/disaster` 접속
2. Nginx가 `/disaster`를 `/` location 블록에 의해 프론트엔드(포트 3000)로 프록시
3. Vite 개발 서버가 `/disaster` 경로를 `index.html`로 서빙
4. React Router가 클라이언트 사이드에서 `/disaster` 경로를 `Disaster` 컴포넌트로 라우팅

## 추가 문제 해결

### 프론트엔드가 HTML 대신 JSON 반환
- Vite 설정 확인: `frontend/vite.config.ts`
- 빌드된 파일이 있으면 `npm run build` 후 `npm run preview` 실행

### 여전히 백엔드로 라우팅됨
- Nginx 설정 파일 확인: `/etc/nginx/sites-available/damcp.gngmeta.com`
- `/disaster` location 블록이 있는지 확인 (있으면 제거)
- Nginx 재시작: `sudo systemctl restart nginx`

### CORS 오류
- 백엔드 CORS 설정 확인: `backend/src/config.py`
- `damcp.gngmeta.com`이 `CORS_ORIGINS`에 포함되어 있는지 확인

