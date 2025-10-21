# GCP 방화벽 규칙 설정 가이드

## 🚨 중요: 먼저 GCP 콘솔에서 방화벽 규칙을 설정해야 합니다!

### 1단계: GCP 콘솔 접속
1. https://console.cloud.google.com 접속
2. 해당 프로젝트 선택

### 2단계: 방화벽 규칙 생성
1. **왼쪽 메뉴** → **"VPC 네트워크"** → **"방화벽"**
2. **"방화벽 규칙 만들기"** 클릭

### 3단계: 방화벽 규칙 설정
```
이름: allow-https-traffic
설명: Allow HTTPS traffic on port 443 for damcp.gngmeta.com
방향: 수신
대상: 지정된 대상 태그
대상 태그: https-server
소스 IP 범위: 0.0.0.0/0
프로토콜 및 포트: 
  ✅ TCP 체크
  포트: 443
```

### 4단계: HTTP 방화벽 규칙도 생성 (Let's Encrypt용)
```
이름: allow-http-letsencrypt
설명: Allow HTTP traffic on port 80 for Let's Encrypt
방향: 수신
대상: 지정된 대상 태그
대상 태그: https-server
소스 IP 범위: 0.0.0.0/0
프로토콜 및 포트: 
  ✅ TCP 체크
  포트: 80
```

### 5단계: Compute Engine 인스턴스에 태그 추가
1. **왼쪽 메뉴** → **"Compute Engine"** → **"VM 인스턴스"**
2. **IP가 34.47.89.217인 인스턴스** 클릭
3. **"편집"** 버튼 클릭
4. **"네트워킹"** 섹션에서
5. **"네트워크 태그"** 필드에 `https-server` 입력
6. **"저장"** 클릭

### 6단계: 설정 확인
방화벽 규칙이 올바르게 생성되었는지 확인:
- `allow-https-traffic` (포트 443)
- `allow-http-letsencrypt` (포트 80)

인스턴스에 `https-server` 태그가 추가되었는지 확인

## ✅ 방화벽 설정 완료 후 서버 설정 진행
