# Node.js 18 LTS 이미지 사용
FROM node:18-alpine

# Chromium 및 필요한 패키지 설치
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont

# Puppeteer를 위한 환경 변수 설정
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser \
    CHROMIUM_PATH=/usr/bin/chromium-browser

# 작업 디렉토리 설정
WORKDIR /app

# package.json 복사 및 의존성 설치
COPY package*.json ./
RUN npm install --production

# 애플리케이션 파일 복사
COPY . .

# 데이터 디렉토리 생성
RUN mkdir -p /app/data

# 포트 노출
EXPOSE 8000

# 환경 변수 설정
ENV NODE_ENV=production \
    PORT=8000 \
    FLAG=Whois2025{XSS_1n_A1rl1n3_R3s3rv4t10n_Syst3m_2025}

# 애플리케이션 실행
CMD ["node", "server.js"]