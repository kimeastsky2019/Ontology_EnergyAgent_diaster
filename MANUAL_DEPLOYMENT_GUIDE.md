# 🚀 GCP Compute Engine 수동 배포 가이드

## 📋 서버 정보
- **IP**: 34.47.89.217
- **사용자**: metal
- **인증**: ppk 키 필요

## 🔧 배포 단계

### 1단계: ppk 키 준비
```bash
# Windows에서 PuTTYgen 사용하여 ppk 키 생성 또는 기존 키 사용
# 또는 기존 SSH 키를 ppk로 변환
```

### 2단계: PuTTY 또는 WinSCP로 서버 접속
```bash
# PuTTY 설정
Host: 34.47.89.217
Port: 22
Username: metal
Authentication: ppk 키 파일 선택
```

### 3단계: 압축 파일 업로드
```bash
# WinSCP 또는 FileZilla 사용
# 로컬 파일: energy-analysis-mcp-deploy.tar.gz
# 원격 경로: /tmp/energy-analysis-mcp-deploy.tar.gz
```

### 4단계: 서버에서 배포 명령어 실행
```bash
# 1. 압축 파일 확인
ls -la /tmp/energy-analysis-mcp-deploy.tar.gz

# 2. 기존 디렉토리 백업
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

echo "✅ 배포 완료!"
echo "🌐 서비스 URL: http://34.47.89.217:8000"
echo "📊 거래 페이지: http://34.47.89.217:8000/trading?lang=ko"
echo "📈 Statistics 페이지: http://34.47.89.217:8000/statistics?lang=ko"
```

## 🌐 배포 완료 후 접속 URL
- **메인 페이지**: http://34.47.89.217:8000/?lang=ko
- **거래 페이지**: http://34.47.89.217:8000/trading?lang=ko
- **Statistics 페이지**: http://34.47.89.217:8000/statistics?lang=ko

## 🔧 문제 해결

### 포트가 열리지 않는 경우
```bash
# GCP 콘솔에서 방화벽 규칙 추가
# 네트워킹 > VPC 네트워크 > 방화벽 규칙
# 방향: 수신
# 대상: 모든 인스턴스
# 소스 IP 범위: 0.0.0.0/0
# 프로토콜 및 포트: TCP, 8000
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
- 전력/탄소 거래 플랫폼
- P2P 전력 거래 마켓플레이스
- 탄소 크레딧 거래 시스템
- AI 수익 최적화 엔진
- 글로벌 Demo Sites 모니터링
