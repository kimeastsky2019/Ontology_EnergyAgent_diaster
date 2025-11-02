# Railway 직접 배포 가이드

## 방법 1: Railway CLI 사용

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 초기화
railway init

# 배포
railway up
```

## 방법 2: Railway 웹사이트에서 직접 업로드

1. https://railway.app 방문
2. "New Project" 클릭
3. "Deploy from folder" 선택
4. 프로젝트 폴더 압축 후 업로드

## 방법 3: GitHub 저장소 생성 후 배포

1. GitHub에서 저장소 생성
2. 로컬 코드 푸시
3. Railway에서 GitHub 연결
4. 자동 배포

## 도메인 설정

배포 완료 후:
1. Railway 대시보드 → Settings → Domains
2. Custom Domain 추가: damcp.gngmeta.com
3. DNS 설정에서 CNAME 레코드 추가
