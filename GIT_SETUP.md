# GitHub 저장소 설정 가이드

이 문서는 프로젝트를 GitHub 저장소에 업로드하고 관리하는 방법을 안내합니다.

## GitHub 저장소 정보

- **저장소 URL**: https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git
- **저장소 이름**: Ontology_EnergyAgent_diaster

## 방법 1: 자동 설정 스크립트 사용 (권장)

```bash
# 스크립트에 실행 권한 부여
chmod +x setup_git.sh

# 스크립트 실행
./setup_git.sh

# GitHub에 푸시
git push -u origin main
```

## 방법 2: 수동 설정

### 1. Git 저장소 초기화

```bash
cd "/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"

# Git 저장소 초기화 (아직 안 했다면)
git init

# 브랜치를 main으로 설정
git branch -M main
```

### 2. 원격 저장소 추가

```bash
# 원격 저장소 추가
git remote add origin https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git

# 또는 이미 추가되어 있다면 업데이트
git remote set-url origin https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git

# 원격 저장소 확인
git remote -v
```

### 3. 파일 스테이징 및 커밋

```bash
# 모든 파일 스테이징 (제외: .env, node_modules, __pycache__ 등)
git add .

# 커밋
git commit -m "Initial commit: AI 재난 대응형 에너지 공유 플랫폼

- Backend: FastAPI 기반 REST API
- Frontend: React + TypeScript
- AI Agents: DisasterAnalyzer, EnergyAnalyzer
- Infrastructure: Docker Compose 설정
- Database: PostgreSQL + TimescaleDB
- Monitoring: Prometheus + Grafana"
```

### 4. GitHub에 푸시

```bash
# 첫 푸시 (upstream 설정)
git push -u origin main

# 이후 푸시
git push origin main
```

## GitHub 인증 방법

### Personal Access Token 사용 (HTTPS)

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" 클릭
3. 권한 선택: `repo` (전체 저장소 접근)
4. 토큰 생성 후 복사
5. 푸시 시 비밀번호 대신 토큰 사용

```bash
# 사용자 이름: GitHub 사용자명
# 비밀번호: Personal Access Token
git push -u origin main
```

### SSH 키 사용 (권장)

1. SSH 키 생성 (없다면)
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. SSH 키를 GitHub에 추가
```bash
# 공개 키 복사
cat ~/.ssh/id_ed25519.pub

# GitHub → Settings → SSH and GPG keys → New SSH key에 추가
```

3. 원격 저장소 URL을 SSH로 변경
```bash
git remote set-url origin git@github.com:kimeastsky2019/Ontology_EnergyAgent_diaster.git
```

4. 푸시
```bash
git push -u origin main
```

## .gitignore 확인

다음 파일들은 자동으로 제외됩니다:

- `.env` - 환경 변수 (민감한 정보)
- `node_modules/` - Node.js 의존성
- `__pycache__/` - Python 캐시
- `*.pyc` - Python 컴파일 파일
- `venv/` - Python 가상환경
- `.DS_Store` - macOS 시스템 파일
- `dist/`, `build/` - 빌드 결과물

## 일반적인 Git 명령어

```bash
# 상태 확인
git status

# 변경사항 확인
git diff

# 브랜치 확인
git branch

# 원격 저장소 확인
git remote -v

# 최신 변경사항 가져오기
git pull origin main

# 변경사항 푸시
git push origin main

# 커밋 로그 확인
git log --oneline

# 특정 파일만 커밋
git add path/to/file
git commit -m "커밋 메시지"
git push origin main
```

## 주의사항

1. **.env 파일**: 절대 커밋하지 마세요! 환경 변수에는 민감한 정보가 포함될 수 있습니다.
2. **대용량 파일**: 데이터베이스 덤프나 대용량 모델 파일은 Git LFS를 사용하세요.
3. **의존성 파일**: `requirements.txt`, `package.json`은 커밋하되, 실제 의존성 폴더(`node_modules`, `venv`)는 제외됩니다.

## 문제 해결

### 인증 오류
```bash
# GitHub 인증 문제 시 Personal Access Token 사용
git remote set-url origin https://YOUR_TOKEN@github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git
```

### 충돌 해결
```bash
# 최신 변경사항 가져오기
git pull origin main

# 충돌 수정 후
git add .
git commit -m "충돌 해결"
git push origin main
```

### 저장소 URL 변경
```bash
git remote set-url origin NEW_URL
```

## 추가 리소스

- [GitHub Docs](https://docs.github.com/)
- [Git 공식 문서](https://git-scm.com/doc)
- [GitHub CLI](https://cli.github.com/) - 명령줄에서 GitHub 사용


