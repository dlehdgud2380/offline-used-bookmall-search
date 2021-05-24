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
