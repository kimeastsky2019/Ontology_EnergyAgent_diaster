# 📜 Energy Analysis MCP 스크립트 가이드

이 문서는 Energy Analysis MCP 프로젝트의 모든 스크립트 파일들의 사용법과 기능을 설명합니다.

## 📋 스크립트 목록

| 스크립트 | 기능 | 사용법 |
|---------|------|--------|
| `install.sh` | 자동 설치 | `./install.sh` |
| `deploy_all.sh` | 전체 배포 | `./deploy_all.sh [production\|development]` |
| `stop_servers.sh` | 서버 중지 | `./stop_servers.sh` |
| `setup_nginx.sh` | Nginx 설정 | `sudo ./setup_nginx.sh your-domain.com` |
| `deploy_docker.sh` | Docker 배포 | `./deploy_docker.sh [production\|development]` |
| `update.sh` | 시스템 업데이트 | `./update.sh` |
| `set_permissions.sh` | 권한 설정 | `./set_permissions.sh` |

## 🚀 설치 스크립트

### `install.sh`
시스템에 Energy Analysis MCP를 자동으로 설치합니다.

**기능:**
- 시스템 패키지 업데이트
- 필수 패키지 설치 (Python, Node.js, Nginx, Certbot)
- Python 가상환경 생성 및 의존성 설치
- Node.js 의존성 설치 및 React 앱 빌드
- 실행 권한 설정
- 환경 변수 파일 (.env) 생성
- 시스템 서비스 파일 생성
- Nginx 설정 파일 생성

**사용법:**
```bash
chmod +x install.sh
./install.sh
```

**주의사항:**
- sudo 권한이 필요합니다
- 인터넷 연결이 필요합니다
- 기존 서비스와 충돌할 수 있습니다

## 🚀 배포 스크립트

### `deploy_all.sh`
전체 시스템을 배포하고 시작합니다.

**기능:**
- 기존 서비스 중지
- React 앱 빌드
- Python 의존성 업데이트
- 데이터베이스 초기화
- 환경별 설정 적용
- 서비스 시작 및 활성화
- 헬스체크 수행
- Nginx 재시작

**사용법:**
```bash
# 프로덕션 환경
./deploy_all.sh production

# 개발 환경
./deploy_all.sh development
```

**환경별 차이점:**
- **Production**: DEBUG=False, HOST=0.0.0.0
- **Development**: DEBUG=True, HOST=127.0.0.1

### `deploy_docker.sh`
Docker를 사용하여 시스템을 배포합니다.

**기능:**
- Docker 및 Docker Compose 설치 확인
- Docker Compose 파일 생성
- Dockerfile 생성
- React 앱 Dockerfile 생성
- 기존 컨테이너 정리
- 이미지 빌드
- 컨테이너 시작
- 헬스체크 수행

**사용법:**
```bash
# 프로덕션 환경
./deploy_docker.sh production

# 개발 환경
./deploy_docker.sh development
```

**Docker 서비스:**
- `energy-analysis-mcp`: 메인 애플리케이션
- `nginx`: 웹 서버
- `react-app`: React 애플리케이션

## 🛑 관리 스크립트

### `stop_servers.sh`
실행 중인 모든 서버를 안전하게 중지합니다.

**기능:**
- 메인 서비스 중지
- Nginx 중지 (선택사항)
- Python 프로세스 확인 및 종료
- 포트 사용 확인
- 서비스 상태 확인

**사용법:**
```bash
./stop_servers.sh
```

**안전 기능:**
- 실행 중인 프로세스 확인
- 사용자 확인 후 종료
- 강제 종료 방지

### `update.sh`
시스템을 최신 버전으로 업데이트합니다.

**기능:**
- 현재 설정 백업
- Git 저장소 업데이트
- Python 의존성 업데이트
- Node.js 의존성 업데이트
- 데이터베이스 마이그레이션
- 서비스 재시작
- 헬스체크 수행
- 로그 정리 (선택사항)

**사용법:**
```bash
./update.sh
```

**백업:**
- 자동으로 `backup_YYYYMMDD_HHMMSS/` 디렉토리에 백업 생성
- 가상환경, 환경변수, 데이터 파일 포함

## ⚙️ 설정 스크립트

### `setup_nginx.sh`
Nginx 웹 서버를 설정합니다.

**기능:**
- Nginx 설치 확인
- 도메인별 설정 파일 생성
- 보안 헤더 설정
- Gzip 압축 설정
- 프록시 설정
- 정적 파일 서빙 설정
- 사이트 활성화
- 설정 테스트
- Nginx 재시작
- 방화벽 설정

**사용법:**
```bash
sudo ./setup_nginx.sh your-domain.com
```

**설정 내용:**
- 메인 애플리케이션 프록시
- React 앱 정적 파일 서빙
- 통합 대시보드 프록시
- API 엔드포인트 프록시
- 헬스체크 엔드포인트
- 보안 헤더 및 압축

### `set_permissions.sh`
파일 및 디렉토리 권한을 적절히 설정합니다.

**기능:**
- 스크립트 파일 실행 권한 부여
- 디렉토리 권한 설정
- 데이터 디렉토리 권한 설정
- 웹 파일 권한 설정
- React 앱 권한 설정
- 통합 대시보드 권한 설정
- 다국어 파일 권한 설정
- 소유자 변경 (www-data)
- 특별한 권한 설정
- SELinux 설정 (CentOS/RHEL)
- 방화벽 포트 확인

**사용법:**
```bash
./set_permissions.sh
```

**권한 설정:**
- 스크립트 파일: 755 (실행 가능)
- 웹 파일: 644 (읽기 가능)
- 데이터 디렉토리: 755 (읽기/실행 가능)
- 로그 파일: 666 (읽기/쓰기 가능)
- .env 파일: 600 (소유자만 읽기 가능)

## 🔧 고급 사용법

### 스크립트 조합 사용
```bash
# 전체 설치 및 배포
./install.sh
nano .env  # API 키 설정
./deploy_all.sh production
sudo ./setup_nginx.sh your-domain.com
sudo certbot --nginx -d your-domain.com
```

### Docker 환경에서 사용
```bash
# Docker로 배포
./deploy_docker.sh production

# Docker 컨테이너 관리
docker-compose ps
docker-compose logs -f
docker-compose down
docker-compose up -d
```

### 업데이트 및 유지보수
```bash
# 정기 업데이트
./update.sh

# 서비스 중지
./stop_servers.sh

# 권한 재설정
./set_permissions.sh
```

## 🚨 주의사항

### 보안
- `.env` 파일에는 민감한 정보가 포함되어 있습니다
- 프로덕션 환경에서는 반드시 강력한 비밀번호를 사용하세요
- 정기적으로 시스템을 업데이트하세요

### 백업
- 중요한 데이터는 정기적으로 백업하세요
- 업데이트 전에는 항상 백업을 생성합니다
- 설정 파일도 별도로 백업하세요

### 모니터링
- 서비스 상태를 정기적으로 확인하세요
- 로그 파일을 모니터링하세요
- 디스크 공간을 확인하세요

## 📞 문제 해결

### 일반적인 문제
1. **권한 오류**: `./set_permissions.sh` 실행
2. **포트 충돌**: `./stop_servers.sh` 실행 후 재시작
3. **의존성 오류**: `./install.sh` 재실행
4. **서비스 시작 실패**: 로그 확인 후 설정 수정

### 로그 확인
```bash
# 시스템 로그
sudo journalctl -u energy-analysis-mcp -f

# 애플리케이션 로그
tail -f logs/*.log

# Nginx 로그
sudo tail -f /var/log/nginx/error.log
```

---

**💡 팁**: 모든 스크립트는 `--help` 옵션을 지원하지 않으므로, 이 문서를 참고하여 사용하세요.
