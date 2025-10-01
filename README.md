# 2025-2-Whois-CTF-Problem-production-Project

## Challenge Folder Structure

```
└── [Challenge Name]
    ├── public # 공개 문제 ( flag 없는지 크로스 체크 )
    ├── private # 비공개 문제
    ├── poc # poc.py 혹은 README.md에 POC 작성.
    └── README.md # Title, Author, Description, Level(low, mid, high)
```

다음 주의사항을 반드시 읽어 주세요!
- 바로 마스터 브랜치에 커밋하지 마세요. 반드시 브랜치 따서 쓸것. 브랜치 명은 [name]@ajou.ac.kr에서 name부분을 사용하시면 됩니다. 예) aku7777

## 문제 배포 관련

서버가 필요한 문제의 경우 **docker compose**로 배포 (필수) 
바이너리만 있는 문제의 경우 **빌드 스크립트**와 **전체 소스코드** 포함 (필수)

## challenge.yml 구조

[yaml 문법 cheatsheet](https://quickref.me/yaml.html)

레포 내 challenge.yml 파일 참조 (내용 기입 후 주석은 지워주세요.)
```yaml
name: stlchall #문제이름
category: pwn #문제 분야 (pwn, web, rev, forensic, crypto, misc, ai, blockchain)
difficulty: medium # 난이도: beginner, easy, medium, hard
port: 2222
# 포트가 여러개 일시 - 배열로 작성:
# - 2222
# - 4444
tags: # 문제 컨셉
- ROP
- ARM
description: |
./client {ip}
this is description
asdasd
flag: Whois2025{test_flag} #플래그
chall_dir: pwn-chall #문제 폴더 (최상위 폴더 기준으로 작성)
compose_file: pwn-stlchall/challenge/docker-compose.yml #문제 도커 컴포즈 파일 위치 (상대 경로로 작성)
```

## git을 잘 모르는 당신을 위해

우선, 다음을 설정합니다:
https://www.lainyzine.com/ko/article/creating-ssh-key-for-github/

다음과 같이 프로젝트를 클론합니다:

```bash
git clone git@github.com:aku7777/{레포지토리_주소}.git
```

당신의 브랜치를 생성합니다:

```bash
cd {레포지토리_주소}
git checkout -b [위에서 말한 본인 메일주소 앞 이름!!!!!! 옆에 대괄호는 지우세요.]
```

당신의 문제를 위의 설명에 맞게 셋업 합니다:

```bash
mkdir -p pwn/sample
mkdir -p pwn/sample/challenge
touch pwn/sample/README.md
...
```

당신의 문제를 인덱싱 후, 커밋합니다.

```bash
git add .
git commit -m "[add] [문제 이름] 추가."
```

당신의 브랜치를 푸쉬합니다:

```bash
git push origin [브랜치 이름. 위에서 말한 본인 메일주소 앞 이름!!!! 옆에 대괄호는 지우세요.]
```
