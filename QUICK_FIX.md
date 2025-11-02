# /disaster 경로 문제 빠른 해결

## 문제
`https://damcp.gngmeta.com/disaster` 접속 시 `{"detail":"Not Found"}` 오류 발생

## 원인
**3000번 포트에서 리스닝 중인 프론트엔드 서버가 없음**

## 즉시 해결 (서버에서 실행)

```bash
ssh metal@34.47.89.217
cd /home/metal/energy-platform

# 방법 1: 자동 해결 스크립트 (권장)
bash scripts/fix_disaster_complete.sh

# 또는 방법 2: 프론트엔드 서버만 시작
bash scripts/start_frontend.sh

# 또는 방법 3: 모든 서버 시작
bash scripts/start_all.sh
```

## 수동 해결

```bash
# 1. 서버 접속
ssh metal@34.47.89.217
cd /home/metal/energy-platform

# 2. 코드 업데이트
git pull origin main

# 3. 프론트엔드 서버 시작
cd frontend
npm run dev

# 또는 백그라운드:
nohup npm run dev > /tmp/frontend.log 2>&1 &
```

## 확인

서버 시작 후 확인:

```bash
# 포트 확인
lsof -i :3000
# 또는
netstat -tlnp | grep 3000

# 로컬 테스트
curl http://127.0.0.1:3000/disaster

# 도메인 테스트
curl https://damcp.gngmeta.com/disaster
```

## 서버 재시작 시 자동 시작 설정

### PM2 사용 (권장)

```bash
# PM2 설치
npm install -g pm2

# 프론트엔드 시작
cd /home/metal/energy-platform/frontend
pm2 start npm --name "frontend" -- run dev

# 백엔드 시작
cd /home/metal/energy-platform/backend
pm2 start "uvicorn src.main:app --host 0.0.0.0 --port 8000" --name "backend"

# 자동 시작 설정
pm2 save
pm2 startup
```

### Systemd 사용

```bash
# 서비스 설정
bash scripts/setup_services.sh

# 서비스 시작
sudo systemctl start frontend
sudo systemctl enable frontend
sudo systemctl start backend
sudo systemctl enable backend
```

## 문제 해결 체크리스트

- [x] 프론트엔드 서버 미실행 확인 (3000번 포트)
- [ ] 프론트엔드 서버 시작 (`bash scripts/start_frontend.sh`)
- [ ] Nginx 설정 업데이트 확인
- [ ] 도메인 접속 테스트

