# 🚀 Energy Analysis MCP 배포 가이드

이 가이드는 Energy Analysis MCP 시스템을 다양한 환경에 배포하는 방법을 설명합니다.

## 📋 목차

- [시스템 요구사항](#시스템-요구사항)
- [빠른 시작](#빠른-시작)
- [수동 설치](#수동-설치)
- [Docker 배포](#docker-배포)
- [Nginx 설정](#nginx-설정)
- [SSL 인증서 설정](#ssl-인증서-설정)
- [모니터링 및 유지보수](#모니터링-및-유지보수)
- [문제 해결](#문제-해결)

## 🖥️ 시스템 요구사항

### 최소 요구사항
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB
- **Network**: 인터넷 연결

### 권장 사양
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **Network**: 안정적인 인터넷 연결

## ⚡ 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/kimeastsky2019/energy-analysis-mcp.git
cd energy-analysis-mcp
```

### 2. 실행 권한 부여
```bash
chmod +x *.sh
```

### 3. 자동 설치
```bash
./install.sh
```

### 4. 환경 변수 설정
```bash
nano .env
```

다음 내용을 입력하세요:
```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Database
DATABASE_URL=sqlite:///data/external_data.db

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Language Settings
DEFAULT_LANGUAGE=ko
SUPPORTED_LANGUAGES=ko,en,ja,zh,ar,he,es,fr,de,ru
```

### 5. 배포 시작
```bash
./deploy_all.sh production
```

### 6. Nginx 설정
```bash
sudo ./setup_nginx.sh your-domain.com
```

### 7. SSL 인증서 설치
```bash
sudo certbot --nginx -d your-domain.com
```

## 🔧 수동 설치

### 1. 시스템 패키지 설치
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx git curl wget unzip
```

### 2. Python 가상환경 설정
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Node.js 의존성 설치
```bash
cd react-weather-app
npm install
npm run build
cd ..
```

### 4. 서비스 파일 생성
```bash
sudo cp energy-analysis-mcp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable energy-analysis-mcp
sudo systemctl start energy-analysis-mcp
```

## 🐳 Docker 배포

### 1. Docker 설치
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Docker Compose 설치
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Docker 배포 실행
```bash
./deploy_docker.sh production
```

## 🌐 Nginx 설정

### 1. 기본 설정
```bash
sudo ./setup_nginx.sh your-domain.com
```

### 2. SSL 인증서 설치
```bash
sudo certbot --nginx -d your-domain.com
```

### 3. 자동 갱신 설정
```bash
sudo crontab -e
```

다음 줄을 추가하세요:
```cron
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 모니터링 및 유지보수

### 서비스 상태 확인
```bash
# 서비스 상태
sudo systemctl status energy-analysis-mcp

# 로그 확인
sudo journalctl -u energy-analysis-mcp -f

# 포트 확인
netstat -tlnp | grep -E ':(80|8000|443)'
```

### 업데이트
```bash
# 자동 업데이트
./update.sh

# 수동 업데이트
git pull origin main
sudo systemctl restart energy-analysis-mcp
```

### 백업
```bash
# 데이터 백업
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz data/ logs/ .env

# 설정 백업
sudo tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz /etc/nginx/sites-available/energy-analysis-mcp /etc/systemd/system/energy-analysis-mcp.service
```

## 🔍 문제 해결

### 일반적인 문제

#### 1. 서비스가 시작되지 않음
```bash
# 로그 확인
sudo journalctl -u energy-analysis-mcp -n 50

# 포트 확인
sudo netstat -tlnp | grep 8000

# 권한 확인
ls -la .venv/bin/python
```

#### 2. Nginx 502 오류
```bash
# 백엔드 서비스 확인
curl http://localhost:8000/health

# Nginx 로그 확인
sudo tail -f /var/log/nginx/error.log

# 프록시 설정 확인
sudo nginx -t
```

#### 3. SSL 인증서 문제
```bash
# 인증서 상태 확인
sudo certbot certificates

# 수동 갱신
sudo certbot renew --dry-run

# Nginx 재시작
sudo systemctl reload nginx
```

### 로그 파일 위치
- **애플리케이션 로그**: `logs/`
- **시스템 로그**: `sudo journalctl -u energy-analysis-mcp`
- **Nginx 로그**: `/var/log/nginx/`
- **Docker 로그**: `docker-compose logs`

## 🌍 다국어 지원

### 지원 언어
- 🇰🇷 한국어 (Korean)
- 🇺🇸 영어 (English)
- 🇯🇵 일본어 (Japanese)
- 🇨🇳 중국어 (Chinese)
- 🇸🇦 아랍어 (Arabic) - RTL 지원
- 🇮🇱 히브리어 (Hebrew) - RTL 지원
- 🇪🇸 스페인어 (Spanish)
- 🇫🇷 프랑스어 (French)
- 🇩🇪 독일어 (German)
- 🇷🇺 러시아어 (Russian)

### 언어 설정
```bash
# 환경 변수에서 기본 언어 설정
DEFAULT_LANGUAGE=ko

# 지원 언어 목록
SUPPORTED_LANGUAGES=ko,en,ja,zh,ar,he,es,fr,de,ru
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. **로그 파일** 확인
2. **서비스 상태** 확인
3. **포트 사용** 확인
4. **권한 설정** 확인
5. **네트워크 연결** 확인

추가 도움이 필요하면 GitHub Issues에 문의하세요.

---

**🎉 배포 완료!** 이제 Energy Analysis MCP 시스템을 사용할 수 있습니다.
