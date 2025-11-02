FROM ubuntu:22.04

RUN apt-get update && apt-get install -y socat qemu-user-static gcc-arm-linux-gnu

RUN useradd -mU pwn

COPY ./prob /home/pwn/prob
COPY ./flag /home/pwn/flag
COPY ./run.sh /home/pwn/run.sh

RUN chown -R root:pwn /home/pwn
RUN chmod -R 750 /home/pwn

WORKDIR /home/pwn
CMD socat -T 300 TCP-LISTEN:1004,reuseaddr,fork EXEC:/home/pwn/run.sh,su=pwn
EXPOSE 1004
