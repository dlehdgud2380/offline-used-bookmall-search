'''
Aladin OfflineShop Parse Module by Sc0_Nep
'''

from bs4 import BeautifulSoup
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor

# 알라딘 고정 URL
URL = "https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=UsedStore&KeyTag=&SearchWord="


def get_html(url):
    with ThreadPoolExecutor(max_workers=8) as executor:
        thread = executor.submit(requests.get, url)
    return thread.result().text

# 알라딘 검색 페이지 크롤링 클래스


class Searchpage:
    def __init__(self, keyword):
        html = get_html(URL + keyword)
        self.keyword = keyword
        self.soup = BeautifulSoup(html, 'lxml')
        self.get_items = self.soup.find_all("div", class_="ss_book_box")
        self.item_quantity = len(self.get_items)

        # 책제목, 책 설명, 재고가 있는 매장
        self.list_title = []
        self.list_description = []
        self.list_shop = []
        self.list_imgurl = []
        self.json_result = []

        # 검색페이지 크롤링 실행
        self.__parse_searchdata()

    # 알라딘 검색페이지 크롤링 함수
    def __parse_searchdata(self):
        index = 0
        for i in self.get_items:

            # 책 제목 가져오기
            title = i.find("b", class_="bo3").text

            # 책 설명 가져오기
            tag_li = i.find_all("li")
            description = tag_li[1].text

            # 재고 있는 매장들 가져오기
            instock_shop = {}
            tag_a = i.find_all("a", class_="usedshop_off_text3")
            for j in tag_a:
                shopname = j.text
                shopurl = j.attrs['href']
                instock_shop.setdefault(shopname, shopurl)

            # 책 이미지 주소 가져오기
            imgurl = i.find("img", class_="i_cover").attrs['src']

            # HTML 소스코드 위에서 아래순으로 데이터들 리스트 추가
            self.list_title.append(title)
            self.list_description.append(description)
            self.list_shop.append(instock_shop)
            self.list_imgurl.append(imgurl)

            # JSON으로 아이템 저장하기
            self.json_result.append({"id": index, "bookname": title, "description": description,
                                    "imgurl": imgurl, "mall": list(instock_shop.keys())})
            index += 1

    # 데이터들 클래스 외부로 리턴
    def return_data(self):
        return self.list_title, self.list_description, self.list_shop, self.list_imgurl

    # 데이터 잘 들어있나 확인
    def print_searchdata(self):
        print(json.dumps(self.json_result, indent=4, ensure_ascii=False))

# 선택한 책에 대한 정보를 크롤링


class Search_result(Searchpage):
    def __init__(self, keyword):
        start = time.time()
        print("검색키워드: " + keyword + " - Aladin크롤링시작")
        super().__init__(keyword)
        data = super().return_data()
        self.title = data[0]
        self.description = data[1]
        self.target_shops = data[2]
        self.img_urls = data[3]
        self.result = []
        self.__parse_itemdata()
        print("time :", time.time() - start)

    # 선택한 책의 매장별 가격과 위치 크롤링
    def __parse_itemdata(self):

        # 검색결과 전체적으로 돌려보자
        for i in range(0, len(self.title)):
            shopurl = self.target_shops[i].values()  # 매장 주소 가져오는 것
            shopname = list(self.target_shops[i].keys())  # 이건 매장이름들 가져오는거
            # 이건 검색결과에서 매장 어디어디 있는가 보여주는 것들
            stores = ", ".join(str(data)
                               for data in self.target_shops[i].keys())
            shops_stock = []
            for loop, data in enumerate(shopurl):
                html = get_html(data)
                self.soup = BeautifulSoup(html, 'html.parser')
                self.get_stock = self.soup.find_all(
                    "div", class_="ss_book_box")  # 매장에 책 재고 있는 만큼 정보 가져오기
                count_stock = len(self.get_stock)
                stock = []
                index = 0
                for j in self.get_stock:
                    price = j.find("span", class_="ss_p2").text  # 매장의 책 가격
                    quality = j.find(
                        "span", class_="us_f_bob").text.strip()  # 매장의 책 상태
                    location = j.find_all("span", class_="ss_p3")[
                        3].find("b").text[7:].strip()  # 책이 있는 위치
                    # 매장안에 있는 책의 정보들 json으로 저장
                    item = {'stock_id': index, 'price': price,
                            'quality': quality, 'location': location}
                    stock.append(item)
                    index += 1
                # 매장 지점별로 책 재고 정보 저장
                shops_stock.append(
                    {'mall_id': loop, 'mall': shopname[loop], 'count_stock': count_stock, 'status_stock': stock})
            self.result.append({'search_id': i, 'bookname': self.title[i], 'description': self.description[
                               i], 'stores': stores, 'imgurl': self.img_urls[i], 'result': shops_stock})

    # 하나의 책에 대한 매장별로 재고 현황 표시
    def print_data(self):
        print(json.dumps(self.result, indent=4, ensure_ascii=False))

    def return_data(self):
        return self.result


if __name__ == "__main__":
    # a = Searchpage("python")
    # a.print_searchdata()
    b = Search_result("다빈치코드")
    # b.print_data()
