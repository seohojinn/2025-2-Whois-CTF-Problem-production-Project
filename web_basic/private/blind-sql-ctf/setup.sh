#!/bin/bash
echo "블라인드 SQL 인젝션 CTF 환경 설정 중..."

# 기존 컨테이너 정리
docker-compose down 2>/dev/null || true

# 이미지 빌드
echo "Docker 이미지 빌드 중..."
docker-compose build

# 컨테이너 실행
echo "컨테이너 실행 중..."
docker-compose up -d

# 상태 확인
echo "환경 설정 완료!"
echo "========================================="
echo "CTF 접속 URL: http://localhost:8080"
echo "========================================="
echo ""
echo "테스트 계정:"
echo "- admin / super_secret_password_123!@#"
echo "- user1 / password123"
echo ""
echo "컨테이너 상태 확인: docker-compose ps"
echo "로그 확인: docker-compose logs -f"
echo "중지: docker-compose down"
