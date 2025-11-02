# 하얀 페이지 문제 디버깅 가이드

## 서버 측 확인 결과

### ✅ 정상 작동 중인 것들
1. **HTML 페이지**: 정상적으로 로드됨 (HTTP 200)
2. **JavaScript 파일**: `/src/main.tsx` 정상 로드 (HTTP 200)
3. **Vite 클라이언트**: `/@vite/client` 정상 로드 (HTTP 200)
4. **프론트엔드 서버**: 정상 실행 중 (포트 3000)
5. **백엔드 서버**: 정상 실행 중 (포트 8000)

### ❌ 문제 발견
1. **의존성 파일 로드 실패**: `/node_modules/.vite/deps/*.js` 파일들이 404 반환
   - `/node_modules/.vite/deps/react.js` → 404
   - `/node_modules/.vite/deps/react-redux.js` → 404
   - `/node_modules/.vite/deps/@mui_material.js` → 404
   - `/node_modules/.vite/deps/react_jsx-dev-runtime.js` → 404

2. **Nginx 권한 문제**: 
   ```
   open() "/var/lib/nginx/proxy/1/00/0000000001" failed (13: Permission denied)
   ```

3. **React 앱 초기화 실패**: JavaScript 의존성 파일을 로드하지 못해 React 앱이 초기화되지 않음

## 브라우저에서 확인할 사항

### 1. 개발자 도구 열기 (F12)
- **Console 탭**에서 JavaScript 에러 확인
- **Network 탭**에서 실패한 파일 확인

### 2. Console 탭 확인
다음과 같은 에러들이 표시될 가능성이 높습니다:
```
Failed to load module script: Expected a JavaScript or WebAssembly module
Uncaught SyntaxError: Unexpected token
Failed to resolve module specifier "/node_modules/.vite/deps/react.js"
```

### 3. Network 탭 확인
다음 파일들이 404 또는 빨간색으로 표시될 것입니다:
- `/node_modules/.vite/deps/react.js?v=...`
- `/node_modules/.vite/deps/react-redux.js?v=...`
- `/node_modules/.vite/deps/@mui_material.js?v=...`
- `/node_modules/.vite/deps/react_jsx-dev-runtime.js?v=...`

### 4. 실제 로드되는 파일 확인
Network 탭에서 다음 파일들은 정상적으로 로드될 것입니다:
- ✅ `/disaster` (HTML)
- ✅ `/src/main.tsx` (JavaScript)
- ✅ `/@vite/client` (Vite 클라이언트)
- ❌ `/node_modules/.vite/deps/*.js` (의존성 파일들 - 404)

## 문제 원인

1. **Nginx 설정 문제**: `/node_modules` 경로가 프론트엔드로 프록시되지 않음
2. **Location 블록 우선순위**: `/location /` 블록이 `/node_modules`를 가로채고 있을 가능성
3. **Nginx 버퍼링 권한 문제**: Proxy 버퍼 파일 쓰기 권한 문제

## 임시 해결 방법

브라우저 개발자 도구에서 확인한 실제 에러 메시지를 알려주시면 더 정확한 해결 방법을 제시할 수 있습니다.

## 다음 단계

1. **브라우저 Console 탭**에서 에러 메시지 확인
2. **Network 탭**에서 실패한 파일들의 정확한 URL 확인
3. **에러 메시지 또는 스크린샷** 공유
4. **서버 측 로그** 추가 확인 필요 시 요청

## 참고 사항

- `/disaster` 경로는 인증 없이 접근 가능하도록 설정됨
- API URL은 상대 경로(`/api`)로 설정되어 HTTPS와 호환됨
- 프론트엔드 서버는 정상 실행 중이며, 직접 접속 시 모든 파일이 정상 로드됨

