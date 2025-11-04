# GitHub 토큰 인증 문제 해결

현재 403 에러가 발생하고 있습니다. 다음 단계를 따라 해결하세요.

## 문제 진단

현재 에러: `Permission denied (403)`

이는 다음 중 하나일 수 있습니다:
1. 토큰에 `repo` 권한이 없음
2. 토큰이 만료됨
3. 저장소 접근 권한 문제

## 해결 방법

### 방법 1: 새로운 토큰 생성 (권장)

1. **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**

2. **"Generate new token (classic)" 클릭**

3. **다음 권한을 체크하세요:**
   - ✅ `repo` (전체 저장소 접근)
   - ✅ `workflow` (GitHub Actions 사용 시)

4. **토큰 생성 후 복사**

5. **다음 명령어로 푸시:**
```bash
cd "/Users/donghokim/Documents/myworkspace/Energy Agent/Ontology_EnergyMCP_Diaster"

# 원격 저장소 URL 업데이트 (새 토큰 사용)
git remote set-url origin https://YOUR_USERNAME:YOUR_NEW_TOKEN@github.com/kimeastsky2019/Ontology_EnergyAgent_diaster.git

# 푸시
git push -u origin main
```

### 방법 2: SSH 키 사용 (더 안전)

```bash
# SSH 키 생성 (없다면)
ssh-keygen -t ed25519 -C "your_email@example.com"

# 공개 키 확인
cat ~/.ssh/id_ed25519.pub

# GitHub → Settings → SSH and GPG keys → New SSH key에 추가

# 원격 저장소 URL을 SSH로 변경
git remote set-url origin git@github.com:kimeastsky2019/Ontology_EnergyAgent_diaster.git

# 푸시
git push -u origin main
```

### 방법 3: GitHub CLI 사용

```bash
# GitHub CLI 설치 (Homebrew 사용)
brew install gh

# 로그인
gh auth login

# 푸시
git push -u origin main
```

## 저장소 확인

저장소가 존재하는지 확인:
- https://github.com/kimeastsky2019/Ontology_EnergyAgent_diaster

저장소가 없다면:
1. GitHub에서 새 저장소 생성
2. 이름: `Ontology_EnergyAgent_diaster`
3. Public 또는 Private 선택

## 현재 상태 확인

다음 명령어로 현재 설정 확인:

```bash
# 원격 저장소 확인
git remote -v

# 브랜치 확인
git branch

# 커밋 확인
git log --oneline

# 원격 저장소 연결 테스트
git ls-remote origin
```

## 보안 주의사항

⚠️ **토큰이 노출되지 않도록 주의하세요:**
- `.git-credentials` 파일은 절대 커밋하지 마세요
- `.gitignore`에 이미 포함되어 있습니다
- 토큰을 URL에 포함시키면 Git 히스토리에 남을 수 있습니다

## 권장 방법

가장 안전한 방법은 **SSH 키 사용**입니다:

```bash
# 1. SSH 키 생성
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. SSH agent 시작
eval "$(ssh-agent -s)"

# 3. SSH 키 추가
ssh-add ~/.ssh/id_ed25519

# 4. 공개 키 확인 및 GitHub에 추가
cat ~/.ssh/id_ed25519.pub

# 5. 원격 저장소 URL 변경
git remote set-url origin git@github.com:kimeastsky2019/Ontology_EnergyAgent_diaster.git

# 6. 푸시
git push -u origin main
```

## 추가 도움말

- [GitHub Personal Access Tokens 문서](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub SSH 키 설정](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)


