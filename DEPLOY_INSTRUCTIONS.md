# 서버 배포 안내

## 현재 상황
- ❌ `google_compute_engine.pem` 파일이 없음
- ✅ `google_compute_engine.ppk` 파일은 존재함
- ❌ `puttygen`이 설치되지 않음

## 해결 방법

### 방법 1: Google Cloud Console에서 .pem 키 다운로드 (권장)
1. Google Cloud Console → Compute Engine → VM 인스턴스
2. 해당 인스턴스 선택
3. SSH 키 생성/다운로드
4. 다운로드한 `.pem` 파일을 프로젝트 루트에 `google_compute_engine.pem`로 저장

### 방법 2: .ppk를 .pem으로 변환
```bash
# puttygen 설치
brew install putty

# .ppk를 .pem으로 변환
puttygen google_compute_engine.ppk -O private-openssh -o google_compute_engine.pem

# 권한 설정
chmod 600 google_compute_engine.pem
```

## 배포 실행
`.pem` 파일이 준비되면 다음 명령어로 배포:

```bash
# 권한 설정 및 서버 접속하여 배포
chmod 600 google_compute_engine.pem
ssh -i google_compute_engine.pem -o "IdentitiesOnly=yes" -o "ServerAliveInterval=60" -o "StrictHostKeyChecking=no" metal@34.47.89.217

# 또는 배포 스크립트 실행
bash scripts/deploy_with_pem.sh
```

## 배포 스크립트 내용
`scripts/deploy_with_pem.sh` 스크립트는:
1. .pem 파일 권한 설정
2. 서버 연결 테스트
3. Git repository clone/update
4. 서버 환경 설정 (Python, Node.js 설치)
5. 백엔드/프론트엔드 의존성 설치

