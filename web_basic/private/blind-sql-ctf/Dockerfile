FROM php:8.1-apache

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    vim \
    curl \
    && docker-php-ext-install pdo_sqlite \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /var/www/html

# PHP 설정 파일 복사
COPY ctf.php /var/www/html/index.php

# 권한 설정
RUN chmod 644 /var/www/html/index.php
RUN mkdir -p /tmp && chmod 777 /tmp

# Apache 모듈 활성화
RUN a2enmod rewrite

# 포트 노출
EXPOSE 80

# Apache 실행
CMD ["apache2-foreground"]
