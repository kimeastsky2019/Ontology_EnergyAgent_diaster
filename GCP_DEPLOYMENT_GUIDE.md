# 🚀 GCP Compute Engine 배포 가이드

## 📋 서버 정보
- **IP**: 34.47.89.217
- **사용자**: metal
- **인증**: ppk 키 사용

## 🔧 배포 단계

### 1단계: ppk 키를 pem으로 변환 (선택사항)
```bash
# Windows에서 PuTTYgen 사용
puttygen your_key.ppk -O private-openssh -o your_key.pem

# 또는 직접 ppk 키 사용
```

### 2단계: 압축 파일 업로드
```bash
# ppk 키 사용
scp -i your_key.ppk energy-analysis-mcp-deploy.tar.gz metal@34.47.89.217:/tmp/

# pem 키 사용 (변환한 경우)
scp -i your_key.pem energy-analysis-mcp-deploy.tar.gz metal@34.47.89.217:/tmp/
```

### 3단계: 서버 접속 및 배포
```bash
# ppk 키로 접속
ssh -i your_key.ppk metal@34.47.89.217

# pem 키로 접속 (변환한 경우)
ssh -i your_key.pem metal@34.47.89.217
```

### 4단계: 서버에서 배포 명령어 실행
```bash
# 1. 압축 파일 확인
ls -la /tmp/energy-analysis-mcp-deploy.tar.gz

# 2. 기존 디렉토리 백업 및 새로 생성
cd /home/metal
mv energy-analysis-mcp energy-analysis-mcp-backup-$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
mkdir -p energy-analysis-mcp
cd energy-analysis-mcp

# 3. 압축 해제
tar -xzf /tmp/energy-analysis-mcp-deploy.tar.gz
rm /tmp/energy-analysis-mcp-deploy.tar.gz

# 4. Python 환경 설정
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. 기존 서비스 중지
sudo systemctl stop energy-analysis-mcp 2>/dev/null || true
sudo systemctl disable energy-analysis-mcp 2>/dev/null || true

# 6. systemd 서비스 파일 생성
sudo tee /etc/systemd/system/energy-analysis-mcp.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Energy Analysis MCP Service
After=network.target

[Service]
Type=simple
User=metal
WorkingDirectory=/home/metal/energy-analysis-mcp
Environment=PATH=/home/metal/energy-analysis-mcp/venv/bin
ExecStart=/home/metal/energy-analysis-mcp/venv/bin/python -m uvicorn web_interface:web_app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# 7. 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable energy-analysis-mcp
sudo systemctl start energy-analysis-mcp

# 8. 서비스 상태 확인
sudo systemctl status energy-analysis-mcp --no-pager

# 9. 방화벽 설정
sudo ufw allow 8000/tcp 2>/dev/null || true

# 10. 포트 확인
netstat -tlnp | grep :8000 || ss -tlnp | grep :8000
```

## ✅ 배포 완료 확인

### 서비스 URL
- **메인 페이지**: http://34.47.89.217:8000/?lang=ko
- **거래 페이지**: http://34.47.89.217:8000/trading?lang=ko
- **Statistics 페이지**: http://34.47.89.217:8000/statistics?lang=ko

### 서비스 관리 명령어
```bash
# 서비스 상태 확인
sudo systemctl status energy-analysis-mcp

# 서비스 시작
sudo systemctl start energy-analysis-mcp

# 서비스 중지
sudo systemctl stop energy-analysis-mcp

# 서비스 재시작
sudo systemctl restart energy-analysis-mcp

# 로그 확인
sudo journalctl -u energy-analysis-mcp -f
```

## 🔧 문제 해결

### 포트가 열리지 않는 경우
```bash
# 방화벽 상태 확인
sudo ufw status

# 포트 열기
sudo ufw allow 8000/tcp

# GCP 방화벽 규칙 확인 (GCP 콘솔에서)
# 네트워킹 > VPC 네트워크 > 방화벽 규칙
```

### 서비스가 시작되지 않는 경우
```bash
# 로그 확인
sudo journalctl -u energy-analysis-mcp -n 50

# 수동 실행 테스트
cd /home/metal/energy-analysis-mcp
source venv/bin/activate
python -m uvicorn web_interface:web_app --host 0.0.0.0 --port 8000
```

## 📊 배포된 기능

### 전력/탄소 거래 플랫폼
- P2P 전력 거래 마켓플레이스
- 탄소 크레딧 거래 시스템
- AI 수익 최적화 엔진
- 실시간 거래 피드
- 거래 통계 및 분석

### 글로벌 Demo Sites
- Finland, Sweden, Romania, Greece
- 실시간 모니터링
- 성과 지표 분석

---

**배포 완료 후**: http://34.47.89.217:8000/trading?lang=ko 에서 거래 플랫폼을 확인하세요!
