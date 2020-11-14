'''
Aladin OfflineShop Parse Module by Sc0_Nep
'''

from bs4 import BeautifulSoup
import requests
import json

#알라딘 고정 URL
URL = "https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=UsedStore&KeyTag=&SearchWord="

#알라딘 검색 페이지 크롤링 클래스
class Searchpage:
    def __init__(self, keyword):
        html = requests.get(URL + keyword).text
        self.soup = BeautifulSoup(html, 'html.parser')
        self.get_items = self.soup.find_all("div", class_ = "ss_book_box")
        self.item_quantity = len(self.get_items)

        #책제목, 책 설명, 재고가 있는 매장
        self.list_title = []
        self.list_description = []
        self.list_shop = []

        #검색페이지 크롤링 실행
        self.__parse_searchdata()

    # 알라딘 검색페이지 크롤링 함수
    def __parse_searchdata(self):
        for i in self.get_items:
            #책 제목 가져오기
            title = i.find("b", class_ = "bo3").text

            #책 설명 가져오기
            tag_li = i.find_all("li")
            description = tag_li[1].text

            #재고 있는 매장들 가져오기
            shop = {}
            tag_a = i.find_all("a", class_ = "usedshop_off_text3")
            for j in tag_a:
                shopname = j.text
                shopurl = j.attrs['href']
                shop.setdefault(shopname, shopurl)

            #HTML 소스코드 위에서 아래순으로 데이터들 리스트 추가
            self.list_title.append(title)
            self.list_description.append(description)
            self.list_shop.append(shop)

    #데이터들 클래스 외부로 리턴
    def return_data(self):
        return self.list_title, self.list_description, self.list_shop
    
    #데이터 잘 들어있나 확인
    def print_searchdata(self):
        for i in range(0, self.item_quantity):
            print(self.list_title[i])
            print(self.list_description[i])
            print(list(self.list_shop[i].keys()))
            print("--------------------------- \n")

#선택한 책에 대한 정보를 크롤링
class Itempage:
    def __init__(self, num, searchresult):
        self.title = searchresult[0][num]
        self.description = searchresult[1][num]
        self.target_shops = searchresult[2][num]
        self.shops_stock = []
        self.__parse_itemdata()

    #선택한 책의 매장별 가격과 위치 크롤링
    def __parse_itemdata(self):
        shopurl = self.target_shops.values()
        shopname = list(self.target_shops.keys())

        #각 각 매장에 있는 책의 정보 가져오기
        loop_count = 0
        for i in shopurl:
            html = requests.get(i).text
            self.soup = BeautifulSoup(html, 'html.parser')
            self.get_stock = self.soup.find_all("div", class_="ss_book_box") #매장에 책 재고 있는 만큼 정보 가져오기
            count_stock = len(self.get_stock)
            stock = []
            for j in self.get_stock:
                price = j.find("span", class_="ss_p2").text #매장의 책 가격
                quality = j.find("span", class_="us_f_bob").text.strip() #매장의 책 상태
                location = j.find_all("span", class_="ss_p3")[3].find("b").text[7:].strip() #책이 있는 위치
                
                #매장안에 있는 책의 정보들 json으로 저장
                item = {'가격' : price, '상태' : quality, '서적 위치' : location}
                stock.append(item)
            #매장 지점별로 책 재고 정보 저장
            self.shops_stock.append({'지점' : shopname[loop_count], '재고 수량' : count_stock, '재고 현황' : stock})
            loop_count += 1

    #하나의 책에 대한 매장별로 재고 현황 표시
    def print_data(self):
        print("책제목: " + self.title)
        print("설명: " + self.description)
        for i in range(0, len(self.shops_stock)):
            print(json.dumps(self.shops_stock[i], indent=4, ensure_ascii = False))

    def return_data(self):
        return self.shops_stock

'''
if __name__ == "__main__":
    print("알라딘 오프라인 상점 검색기\n\n")
    keyword = input("검색내용 입력: ")
    print("\n")
    a = Searchpage(keyword)
    a.print_searchdata()
    num = int(input("몇번째 아이템을 선택? : "))-1
    print("\n")
    b = Itempage(num, a.return_data())
    b.print_data()
'''