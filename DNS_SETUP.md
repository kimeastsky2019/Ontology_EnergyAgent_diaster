# DNS 설정 가이드

**도메인**: damcp.gngmeta.com  
**서버 IP**: 34.47.89.217

---

## 📋 DNS 레코드 설정

### 도메인 관리자 패널에서 설정

다음 DNS 레코드를 추가하세요:

#### A 레코드

```
Type: A
Name: damcp (또는 @ 또는 damcp.gngmeta.com)
Value: 34.47.89.217
TTL: 3600 (또는 기본값)
Priority: (없음)
```

#### 예시 (도메인 제공자별)

**Cloudflare:**
- DNS → Records → Add Record
- Type: A
- Name: damcp
- IPv4 address: 34.47.89.217
- Proxy status: (DNS만 - Proxied 비활성화 권장)
- TTL: Auto

**AWS Route 53:**
- Hosted Zone 선택 → Create Record
- Record type: A
- Record name: damcp
- Value: 34.47.89.217
- TTL: 300

**Google Domains:**
- DNS → Custom resource records
- Name: damcp
- Type: A
- Data: 34.47.89.217
- TTL: 3600

---

## ✅ DNS 전파 확인

### 명령어로 확인

```bash
# nslookup 사용
nslookup damcp.gngmeta.com

# dig 사용
dig damcp.gngmeta.com

# 여러 DNS 서버 확인
dig @8.8.8.8 damcp.gngmeta.com        # Google DNS
dig @1.1.1.1 damcp.gngmeta.com        # Cloudflare DNS
dig @208.67.222.222 damcp.gngmeta.com # OpenDNS
```

**예상 결과:**
```
damcp.gngmeta.com.    IN    A    34.47.89.217
```

### 온라인 도구

- https://dnschecker.org/#A/damcp.gngmeta.com
- https://www.whatsmydns.net/#A/damcp.gngmeta.com

---

## ⏱️ DNS 전파 시간

- **일반적으로**: 5분 ~ 2시간
- **최대**: 24-48시간
- **즉시 확인**: `dig @8.8.8.8` (Google DNS 캐시 직접 확인)

---

## 🔧 문제 해결

### DNS가 전파되지 않는 경우

1. **도메인 설정 확인**
   - 레코드 이름이 올바른지 확인
   - IP 주소가 정확한지 확인
   - TTL 설정 확인

2. **캐시 클리어**
   ```bash
   # 로컬 DNS 캐시 클리어 (Mac)
   sudo dscacheutil -flushcache
   sudo killall -HUP mDNSResponder
   
   # 로컬 DNS 캐시 클리어 (Linux)
   sudo systemd-resolve --flush-caches
   ```

3. **여러 DNS 서버로 확인**
   ```bash
   # 여러 서버에서 확인하여 전파 상태 파악
   for dns in 8.8.8.8 1.1.1.1 208.67.222.222; do
       echo "=== $dns ==="
       dig @$dns damcp.gngmeta.com +short
   done
   ```

---

## ✅ DNS 설정 후 다음 단계

DNS 전파가 완료되면:

1. **서버에 접속**
   ```bash
   ssh metal@34.47.89.217
   ```

2. **Nginx 설정**
   ```bash
   cd /home/metal/energy-platform
   bash scripts/setup_domain.sh
   ```

3. **SSL 인증서 발급**
   ```bash
   sudo certbot --nginx -d damcp.gngmeta.com
   ```

---

## 📝 확인 체크리스트

- [ ] DNS A 레코드 설정 완료
- [ ] DNS 전파 확인 (여러 DNS 서버에서 확인)
- [ ] 서버 접속 가능
- [ ] Nginx 설치 완료
- [ ] Nginx 설정 완료
- [ ] SSL 인증서 발급 완료
- [ ] 도메인 접속 확인

