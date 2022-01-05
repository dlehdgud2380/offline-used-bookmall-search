# Backend
yes24, 알라딘 오프라인 중고 서점 크롤링 모듈

## Spec
* Python 3.8
* requests 2.25.1
* Flask 1.1.2
* beautifulsoup4 4.9.3
* lxml 4.6.2
* Flask-RESTful 0.3.8

## Getting Start
1. pip install -r requirements.txt
2. python api_server.py

## 서버킨후 주소형식
http://{서버주소}:{포트}/search?word={검색어}&mode={검색모드}
### 예시
http://sc0nep.iptime.org:7000/search?word=스즈미야하루히의우울&mode=0

## 검색모드
0: 알라딘
1: yes24

## Dockerfile을 이용하여 이미지 생성 후 컨테이너 만들기
1. Dockerfile을 다운로드
2. Dockerfile이 위치한 디렉터리로 이동
3. docker build -t imagename:version .
4. docker run -p 7000:7000 imagename:version

## 백엔드&프론트엔드 통합 검색엔진 관련 저장소
https://github.com/cappstone/offline_oldbook_searchengine
