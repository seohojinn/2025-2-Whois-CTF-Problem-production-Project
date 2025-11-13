FROM python:3.11-slim

# 필요한 패키지를 모두 한 번에 설치합니다. (시스템 도구 + Playwright 종속성)
# 이전의 오류 패키지(libgconf-2-4, libjpeg-turbo8)는 제거 및 대체되었습니다.
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    # Playwright/Chromium 필수 종속성 목록 (Debian Trixie 호환):
    libasound2 \
    libatk-bridge2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm-dev \
    libgbm-dev \
    libgtk-3-0 \
    libnss3 \
    libxss1 \
    libu2f-udev \
    fonts-liberation \
    fonts-unifont \
    libgbm1 \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 브라우저 바이너리 설치 (★★★ 이 명령어가 필요합니다 ★★★)
# 시스템 종속성은 이미 위에서 설치했으므로, 순수하게 브라우저만 설치합니다.
RUN playwright install chromium

COPY app/ ./

# Create temp directory for browser data
RUN mkdir -p /tmp/admin_browser

EXPOSE 80

CMD ["python", "bot.py"]