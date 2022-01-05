# Python 기반의 크롤러 개발환경 구축하기 

# ubuntu:최신 버전 이미지 기반으로 이미지 생성
FROM ubuntu:latest

# apt를 이용하여 패키지 설치
RUN apt update
RUN apt install -y python3 && apt install -y python3-pip
RUN apt install -y nano

# pip3를 이용하여 파이썬 라이브러리 설치
RUN pip3 install requests bs4 selenium

# /workspace 라는 디렉터리 만들기
RUN mkdir /workspace

# 작업환경 디렉터리를 /workspace 디렉터리로 설정하기
WORKDIR /workspace