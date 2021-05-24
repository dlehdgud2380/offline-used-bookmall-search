'''
Aladin OfflineShop Parse Module by Sc0_Nep
'''

from concurrent import futures
from typing import Tuple, List, Dict
from asyncio.tasks import gather

from bs4 import BeautifulSoup
import bs4.element
from .url_request import request
import requests
import json
import time
import asyncio

# 알라딘 고정 URL
URL = 'https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=UsedStore&KeyTag=&SearchWord='


class Aladin:
    """
    알라딘 검색 페이지를 크롤링하는 메인 클래스
    """

    # 검색결과 저장하는 클래스 변수
    search_result: Dict = None

    def __init__(self, keyword: str) -> None:
        starttime = time.time()
        print("검색키워드: " + keyword + " - AladinV2 크롤링시작")

        # 알라딘 검색 페이지로부터 webpage를 호출하여 가져온다.
        self.response: Tuple[str, bool, Dict] = request(URL + keyword)

        if self.response[1] is False:
            # print(self.response[2])
            self.error_return()
        else:
            html: str = self.response[0]

            # 검색한 키워드를 저장하는 변수
            self.keyword: str = keyword

            # 크롤러 객체 할당
            self.soup = BeautifulSoup(html, 'lxml')

            # keyword로 검색했을때 나오는 책 결과 리스트변수
            self.items: bs4.element.ResultSet = self.soup.find_all(
                'div', class_='ss_book_box')

            # 검색 결과 수
            self.item_quantity: int = len(self.items)

            # 검색결과에 대한 데이터가 dict형태로 담겨있는 리스트 변수
            result: List[Dict] = []

            # 검색페이지 크롤링 실행 --> 병렬 처리할 수 있게 처리 예정
            for i, item in enumerate(self.items):
                parsed_item = self.__searchresult(item)
                parsed_item['id'] = i
                result.append(parsed_item)

            # 검색결과에 대해서 dict타입의 형태로 작성하기
            Aladin.search_result = {
                "keyword": keyword,
                "searchTotal": len(result),
                "result": result
            }

            print("time :", time.time() - starttime)

    # 크롤링하다가 문제가 발생한 경우에 대해서 에러로그를 리턴해서 프론트엔드쪽으로 전달해주기

    def error_return(self) -> Dict:
        return self.response[2]

    # 검색페이지에 뜨는 아이템들 싹다 크롤링 해오는 함수
    def __searchresult(self, bs4_element) -> Dict:
        # 책 제목 가져오기
        title: bs4.element.Tag = bs4_element.find('b', class_='bo3').text

        # 책 설명 가져오기
        tag_li: bs4.element.ResultSet = bs4_element.find_all('li')
        description: str = tag_li[1].text

        # 책 이미지 주소 가져오기
        imgurl: bs4.element.Tag = bs4_element.find(
            'img', class_='i_cover').attrs['src']

        # 재고 있는 매장들 크롤링 해오는 로직
        instock_shop: Dict = {}
        tag_a: bs4.element.ResultSet = bs4_element.find_all(
            'a', class_='usedshop_off_text3')
        for item in tag_a:
            shopname: str = item.text
            shopurl: str = item.attrs['href']
            instock_shop.setdefault(shopname, shopurl)

        # item["bookname"] = title
        # item['description'] = description
        # item['imgurl'] = imgurl
        # item['mall'] = list(instock_shop.keys())

        # temp = Aladin.Item(instock_shop.items()).stock_info()
        # print(temp)

        # 한개의 아이템에 대한 dict형태
        item: Dict = {
            "id": "",  # index
            "bookName": title,  # 책이름
            "description": description,  # 책설명
            "imgUrl": imgurl,  # 책 이미지 주소
            "mallCount": len(list(instock_shop.keys())),  # 재고가 있는 매장 개수
            "mall": Aladin.Item(instock_shop.items()).stock_info()  # 재고있는 매장의 목록
            # "mall": list(instock_shop.keys()),  # 재고있는 매장의 목록
            # 매장별로 저장한 재고데이터 (이중 리스트타입 변수)
            # "stock": Aladin.Item(instock_shop.items()).stock_info()
        }

        return item

    def result(self) -> Dict:
        return Aladin.search_result

    # 검색결과 아이템에 재고가 존재하는 중고매장의 재고정보를 가져오는 서브클래스
    class Item:
        def __init__(self, mall_list: Tuple) -> None:
            self.mall_list: Tuple = mall_list

            # 비동기 크롤링 실행
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.stock_info_list: List = self.loop.run_until_complete(
                self.__scrap_processing())
            self.loop.close()

        # __stock_info코루틴 함수 관리하는 비동기 코루틴 함수
        async def __scrap_processing(self, divide_loop: int = 5) -> Tuple:
            stock_list: List = []  # 데이터 처리가 완료된 재고 목록들 저장하는 리스트
            task_list: List[List[str]] = []  # 크롤링 할 mall 목록이 담겨 있는 리스트 타입 변수
            # 요청할 mall url의 개수가 담긴 변수
            mall_list_count: int = len(self.mall_list)-1
            extra_mall_count: int = mall_list_count % divide_loop  # 요청하고 남은 mall url의 개수가 담긴 변수

            # 한개의 아이템에 대한 mall주소로 요청을 보낼때 나눠서 요청하기 위한 로직
            temp: List[List[str]] = []  # 임시로 호출할 url 리스트들을 담는 리스트타입 로직

            # 한개의 아이템의 요청할수 있는 총 mall_url 갯수만큼 반복
            for index, mall_url in enumerate(self.mall_list):
                temp.append(mall_url)

                # 현재까지 반복한 횟수 나눴을때 0으로 나눠 떨어질때
                if index % divide_loop == 0:
                    task_list.extend([list(temp)])
                    temp.clear()

                # 반복할 횟수가 얼마 안남은 경우
                elif index >= mall_list_count - extra_mall_count:
                    if index == mall_list_count:
                        task_list.extend([list(temp)])
                        temp.clear()

            result: List[List[Dict]] = []
            """
            result 리스트 변수 구조
            [
                [n번째 매장의 재고 리스트],
                [n번째 매장의 재고 리스트],
                ...
            ]
            """
            for tasks in task_list:
                futures = [asyncio.ensure_future(
                    self.__stock_info_scrap(mall[1])) for mall in tasks]
                crauwl_result: List = await asyncio.gather(*futures)
                result.extend(crauwl_result)

            # dict형태로 데이터 재정의
            for i, mall in enumerate(self.mall_list):

                # 중고 매장 재고 정보를 dict형태의 변수로 저장
                mall_data: Dict = {
                    "mall_id": i,  # 몇번쨰 중고매장인지
                    "mallName": "알라딘-" + mall[0],  # 중고 매장 이름
                    "stockCount": len(result[i]),  # 재고수
                    "stock": result[i]  # 재고 데이터가 담긴 리스트 타입변수
                }

                stock_list.append(mall_data)
            return stock_list

        # 매장에 있는 데이터들을 싹다 가져와서 반영함

        async def __stock_info_scrap(self, url: str) -> Tuple:
            # 재고가 있는 매장의 데이터를 요청해서 가져옴
            # response: Tuple[str, bool, Dict] = request(url)
            response: str = await self.loop.run_in_executor(None, requests.get, url)

            # 재고 리스트 타입 변수
            stock: List[Dict] = []  # 내가 검색하는 아이템의 매장재고 정보를 보관하는 리스트

            # html: str = response[0]

            # 재고가 있는 매장 주소로 html 형태의 데이터 요청
            html: str = response.text
            soup = await self.loop.run_in_executor(None, BeautifulSoup, html, "lxml")

            # 매장에 책 재고 있는 만큼 정보 가져오기
            get_stock: bs4.element.ResultSet = soup.find_all(
                "div", class_="ss_book_box")

            # 매장재고수 만큼 가져와서 반복해서 담음
            for index, stock_item in enumerate(get_stock):

                price: bs4.element.Tag = stock_item.find(  # 매장의 책 가격 크롤링
                    "span", class_="ss_p2").text
                quality: bs4.element.Tag = stock_item.find(  # 매장의 책 상태
                    "span", class_="us_f_bob").text.strip()
                location: bs4.element.Tag = stock_item.find_all("span", class_="ss_p3")[
                    3].find("b").text[7:].strip()  # 책이 있는 위치 크롤링

                # 매장안에 있는 책의 정보들 json으로 저장
                item: Dict = {
                    "stock_id": index,  # 몇번째 책 인지?
                    "price": price[:-1],  # 이 책의 가격은?
                    "quality": quality,  # 이책의 상태는?
                    "location": location  # 책의 위치가 있는 곳
                }
                stock.append(item)
            return stock

        def stock_info(self) -> List:
            return self.stock_info_list


"""
if __name__ == "__main__":
    a = Aladin("다빈치코드")
"""
