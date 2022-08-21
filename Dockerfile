# 파이썬 이미지 기반으로 이미지 생성
FROM ubuntu:18.04

# Project 가져오기
RUN apt update && apt install -y git python3-minimal python3-pip libxml2-dev libxslt-dev
RUN git clone https://github.com/dlehdgud2380/offline-used-bookmall-search
WORKDIR /offline-used-bookmall-search

# requirements 설치하기
RUN pip3 install -r requirements.txt

# PORT FORWARDING
EXPOSE 7000

# RUN API Server
CMD ["python3", "api_server.py"]
