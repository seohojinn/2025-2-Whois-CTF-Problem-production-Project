#!/bin/bash
echo "CTF 환경 정리 중..."

# 컨테이너 중지 및 삭제
docker-compose down -v

# 이미지 삭제
docker rmi blind-sql-ctf 2>/dev/null || true

# 로그 파일 정리
rm -rf logs/

echo "정리 완료!"
