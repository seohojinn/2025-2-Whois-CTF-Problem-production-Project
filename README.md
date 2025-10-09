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


## Docker 사용법 기초

Docker 이론 : 
https://velog.io/@gyumin_2/Docker%EB%9E%80-%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80%EA%B0%80-%EB%AC%B4%EC%97%87%EC%9D%B8%EC%A7%80-%EB%AA%A8%EB%A5%B4%EA%B2%A0%EB%8B%A4

CTF & WARGAME에서 PWN 문제 파일을 보면 아래와 같이 Dockerfile이 주어지게 됩니다. (단순 Binary & Libc File만 제공되는 경우도 있지만, 실제 문제 서버는 Docker로 돌아갑니다.)

```bash
➜  pwn-d9d284884e7d28835f666769c53d1298 ls
Dockerfile    chall.elf.i64
```

Dockerfile 내용 및 의미는 아래와 같습니다.
```Dockerfile
# 기반 이미지 설정: Ubuntu 22.04를 사용하는데, 보안성과 일관성을 위해 SHA256 digest로 이미지 버전을 고정함.
FROM ubuntu:22.04@sha256:3d1556a8a18cf5307b121e0a98e93f1ddf1f3f8e092f1fddfd941254785b95d7

# 환경 변수 설정
#   user: 사용자 이름을 pwn으로 설정.
#   prob_port: 서비스가 열릴 포트를 1004로 설정 (나중에 EXPOSE와 socat에서 사용됨).
ENV user pwn
ENV prob_port 1004

# 패키지 설치
#   apt-get update: 패키지 인덱스를 갱신.
#   socat: 네트워크 ↔ 프로세스 연결을 위한 도구 설치 (이 컨테이너에서 /prob 실행에 사용됨).
RUN apt-get update
RUN apt-get -y install socat

# 사용자 생성: UID 1337로 $user (pwn) 유저를 생성함. 
RUN adduser -u 1337 $user

# 파일 복사
#   현재 디렉토리의 flag 파일을 컨테이너의 /flag에 복사.
#   prob 바이너리를 유저의 홈 디렉토리로 복사.
ADD ./flag /flag
ADD ./prob /home/$user/prob

# 소유권 변경
#   /flag와 /home/pwn/prob 파일의 그룹을 $user로 변경하고, 소유자는 root로 유지.
RUN chown root:$user /flag
RUN chown root:$user /home/$user/prob

# 권한 설정
#   prob 바이너리에 실행 권한 부여
#   flag 파일은 읽기 권한만 부여 (root와 그룹에게만 r--).
RUN chmod +x /home/$user/prob
RUN chmod 440 /flag

# 작업 디렉토리 설정: 이후의 명령은 /home/pwn 디렉토리 기준으로 실행됨.
WORKDIR /home/$user

# 유저 전환: 이후 모든 명령은 $user (pwn) 권한으로 실행됨.
USER $user

# 포트 노출: 컨테이너 외부에서 $prob_port(=1004) 포트를 접근할 수 있도록 함.
EXPOSE $prob_port

# 시작 명령
#   socat을 사용해 TCP 포트 1004를 열고, 접속이 들어오면 ./prob 바이너리를 실행시킴.
#   fork 옵션으로 여러 클라이언트 동시 처리 가능.
CMD socat TCP-L:1004,reuseaddr,fork, EXEC:"./prob"
```
