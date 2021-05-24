'''
YES24 OfflineShop Parse Module by Sc0_Nep
'''
from typing import Dict, List
from bs4 import BeautifulSoup
# from collections import defaultdict

import requests
import asyncio
import json
import time

# yes24 중고몰 관련된 URL
MAIN_URL = "http://www.yes24.com/Mall/UsedStore/Main"  # 중고몰 메인페이지 URL
COMMON_URL = "http://www.yes24.com/Mall/UsedStore/Search?STORE_CODE="  # 중고몰 공통 URL

# 중고서점 고유코드 dict형태의 변수
malls: Dict = {}  # 중고서점 지점 : 중고서점 고유코드

# 중고몰 고유코드 미리 가져오는 작업
html: str = requests.get(MAIN_URL).text
soup = BeautifulSoup(html, "lxml")
get_malls: List = soup.find("ul", id="ulStoreSerchCategory").find_all("li")
for i in get_malls:
    malls.setdefault(i.text.strip(), i.find("a").attrs["value"])

# dict형태의 검색결과 저장하는 함수
search_result: Dict = {}

# 검색결과 가져오는 클래스


class Yes24:
    def __init__(self, keyword) -> None:
        # mall정보 가져오기
        mall_names: List[str] = list(malls.keys())  # 중고몰 이름
        mall_codes: List[str] = list(malls.values())  # 중고몰 코드

        # 키워드값 받는 변수
        # yes24는 ascii형태로 인코딩된 값을 파라미터에 넣는 형식임
        self.keyword = str(keyword.encode('ascii', 'backslashreplace')).upper(
        ).replace('\\\\U', '%u')[2:][:-1]

        # url조합
        url_list: List = (COMMON_URL + url + "&searchText=" +
                          self.keyword for url in mall_codes)

        # json데이터 dict로정의 (크롤링 하고 처리된 데이터들 담는 곳)
        self.data: Dict = {
            "keyword": keyword,
            "searchTotal": "",
        }

        # 검색된 책의 타이틀만 모아둔 리스트
        books: List = []

        # 검색된 책 들의 검색결과를 정리하는 리스트
        result: List = []

        # 크롤링한 결과를 임시로 저장하는 temp리스트
        temp: List = []

        # 조합된 url들 함수에 넣고 크롤링하기
        for i, url in enumerate(url_list):
            temp.append(self.__scrap_process(url, mall_names[i]))

        # print(self.books)
        # print(temp)

        # temp안에 있는 매장 개수만큼 반복
        for mall in temp:
            # 매장 데이터 안에 있는 책 결과들 만금 반복
            for item in mall['result']:

                # 검색 결과 없음 뜨는지 확인(해당 매장에 아무 결과 안뜨는 경우임)
                if item != "검색 결과 없음":

                    # 책이 books에 있는지 없는지 중복확인하고 없으면 defaultdict 생성해서 self.result 리스트에 추가
                    if item['bookname'] not in books:

                        # self.result 리스트에 넣을 dict 생성
                        # book_info: defaultdict = defaultdict(str)
                        book_info: Dict = {}
                        book_info['id'] = len(books)
                        book_info['bookName'] = item['bookname']
                        book_info['description'] = item['description']
                        book_info['imgUrl'] = item['imgurl']
                        book_info['mallCount'] = "test"
                        book_info['mall'] = []

                        result.append(book_info)

                        # books 리스트에 저장함
                        books.append(item['bookname'])

                    # 없으면 PASS
                    else:
                        pass

                    # 책이름 확인하고 어디에 넣을지 고르기
                    index: int = books.index(item['bookname'])

                    # 매장내 재고 추가 하기
                    mall_info: Dict = {}
                    mall_info['mall_id'] = len(result[index]['mall'])
                    mall_info['mallName'] = "YES24 " + item['mall']
                    mall_info['price'] = None if item['price'] == "None" else item['price'][:-1]
                    mall_info['location'] = None if item['location'] == "None" else item['location']
                    mall_info['stockCount'] = None if item['location'] == "None" else int(
                        item['stockcount'][2:-2].strip())
                    result[index]['mall'].append(mall_info)
                    result[index]['mallCount'] = len(result[index]['mall'])
                else:
                    pass

        # defaultdict 형태를 dict로 형태로 컨버팅하기
        # result = [dict(item) for item in result]
        result = [item for item in result]

        # 검색결과를 dict에 넣기
        self.data["searchTotal"] = len(result)  # 검색된 개수를 result아이템갯수로
        self.data["result"] = result  # result 리스트 통째로 넣기

    #    print(self.data)

    def __scrap_process(self, url, mall_name) -> Dict:
        source: str = requests.get(url).text
        soup = BeautifulSoup(source, "lxml")
        tag_ul = soup.find("ul", id="ulResult")
        result = []

        # 검색 결과 없는 경우도 있으니 확인
        if str(tag_ul) == "None":
            result.append("검색 결과 없음")
        else:
            tag_li: List = tag_ul.find_all("li")
            for j in tag_li:
                # 책 제목 가져오는 부분
                title: str = j.find("strong", class_="name").text.strip()

                '''
                # 책이 books에 있는지 없는지 중복확인하고 저장
                if title not in self.books:
                    self.books.append(title)
                else:
                    pass
                '''

                # 설명부분 text들 싹다 가져와서 합쳐버리기 - description 크롤링
                tag_p: str = j.find("p", class_="storeG_pubGrp")
                tag_span: List = tag_p.find_all("span")
                description: str = ""
                for k in tag_span:
                    description += k.text + " | "
                description = description[:-2].strip()

                # 이미지주소 크롤링
                tag_em: str = j.find("em", class_="img_bdr")
                imgurl: str = tag_em.find("img").attrs['src']

                # 매물 가격 및 위치 가져오기 - price, location, stockcount 크롤링
                # YES24는 매물에 가격또는 도서 위치가 없는 경우가 있음;;
                price: str = ""
                location: str = ""
                stockcount: str = ""
                try:
                    # 가격 부분 가져오기
                    price = j.find(
                        "p", class_="storeG_price").text[2:].strip()  # 가격 가져오기
                    location = j.find("dd").text.strip()  # 책 위치 가져오기
                    stockcount = j.find(
                        "em", class_="txC_blue").text.strip()  # 매장내 재고 갯수 가져오기
                except AttributeError:
                    price = "None"
                    location = "None"
                    stockcount = "None"

                # 이제 이것들을 dict로 저장시켜버리자
                item: Dict = {'bookname': title, 'description': description,
                              'price': price, 'stockcount': stockcount, 'location': location, 'imgurl': imgurl, 'mall': mall_name}
                result.append(item)
        return {'mall': mall_name, 'result': result}

    def result(self) -> Dict:
        return self.data


# test
if __name__ == "__main__":
    a = Yes24("파이썬")
