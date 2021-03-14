'''
Aladin OfflineShop Parse Module by Sc0_Nep
'''

from typing import Any, Dict, Tuple, List
from bs4 import BeautifulSoup
import bs4.element
from request import url_request
import json
import time

# 알라딘 고정 URL
ALADIN_URL = 'https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=UsedStore&KeyTag=&SearchWord='
YES24_URL = "http://www.yes24.com/Mall/UsedStore/Main"

# 알라딘 검색 페이지 크롤링 클래스


class Aladin:
    '''
    알라딘 검색했을때의 필요한 데이터만 뽑아오는 클래스
    '''

    def __init__(self, keyword: str) -> None:
        # 알라딘 검색 페이지로부터 webpage를 호출하여 가져온다.
        response: Tuple = url_request(ALADIN_URL + keyword)

        # 검색결과에 대한 데이터가 dict형태로 담겨있는 리스트 변수
        self.result: List = []

        # 검색한 키워드를 저장하는 변수
        self.keyword: str = keyword

        # 크롤러 객체 할당
        self.soup = BeautifulSoup(response[0], 'lxml')

        # keyword로 검색했을때 나오는 책 결과 리스트변수
        self.items: bs4.element.ResultSet = self.soup.find_all(
            'div', class_='ss_book_box')

        # 검색 결과 수
        self.item_quantity: int = len(self.items)

        # 검색페이지 크롤링 실행 (멀티프로세싱 도입 예정)
        for i, item in enumerate(self.items):
            self.__parse_singleitem(i, item)

    # 한개의 아이템에 대한 정보를 가져오는
    def __parse_singleitem(self, index: int, bs4_element: bs4.element.Tag) -> None:

        # 책 제목 가져오기
        title = bs4_element.find('b', class_='bo3').text

        # 책 설명 가져오기
        tag_li: bs4.element.ResultSet = bs4_element.find_all('li')
        description: bs4.element.Tag = tag_li[1].text

        # 책 이미지 주소 가져오기
        imgurl = bs4_element.find('img', class_='i_cover').attrs['src']

        # 재고 있는 매장들 가져오기
        instock_shop = {}
        tag_a = bs4_element.find_all('a', class_='usedshop_off_text3')
        for j in tag_a:
            shopname = j.text
            shopurl = j.attrs['href']
            instock_shop.setdefault(shopname, shopurl)

        # dict 형태로 저장하기
        self.result.append({"id": index, "bookname": title, "description": description,
                            "imgurl": imgurl, "mall": list(instock_shop.keys())})

    def data(self):
        return self.result

class Yes24:
    


if __name__ == "__main__":
    a = Aladin("스즈미야")
    print(json.dumps(a.data(), indent=3, ensure_ascii=False))
