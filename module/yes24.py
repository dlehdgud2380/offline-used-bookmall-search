'''
YES24 OfflineShop Parse Module by Sc0_Nep
'''
from bs4 import BeautifulSoup
import requests
import json

#중고몰메인페이지에서 매장 어디어디 있는지 가져옴
MAIN_URL = "http://www.yes24.com/Mall/UsedStore/Main"
html = requests.get(MAIN_URL).text
soup = BeautifulSoup(html, "html.parser")
get_malls = soup.find("ul", id="ulStoreSerchCategory").find_all("li")
malls = {} #중고서점 지점 : 중고서점 고유코드
for i in get_malls:
    malls.setdefault(i.text.strip(), i.find("a").attrs["value"])

class Searchpage:
    def __init__(self, keyword):
        self.keyword = str(keyword.encode('ascii', 'backslashreplace')).upper().replace('\\\\U', '%u')[2:][:-1]
        #매장별 검색결과 리스트
        self.search_result = []
        self.__parse_searchdata()
    
    def __parse_searchdata(self):
        COMMON_URL = "http://www.yes24.com/Mall/UsedStore/Search?STORE_CODE="
        mall_name = list(malls.keys())
        mall_codes = list(malls.values())
        for i in range(0, len(mall_name)):
            source = requests.get(COMMON_URL + mall_codes[i] + "&searchText=" + self.keyword).text
            soup = BeautifulSoup(source, "html.parser")
            tag_ul = soup.find("ul", id = "ulResult")
            result = []

            #검색 결과 없는 경우도 있으니 확인
            if str(tag_ul) == "None":
                result.append("검색 결과 없음")
            else:
                tag_li = tag_ul.find_all("li")
                for j in tag_li:
                    #책 제목 가져오는 거
                    title = j.find("strong", class_ = "name").text.strip()

                    #설명부분 text들 싹다 가져와서 합쳐버리기 - description 크롤링
                    tag_p = j.find("p", class_ = "storeG_pubGrp")
                    tag_span = tag_p.find_all("span")
                    description = "| "
                    for k in tag_span:
                        description += k.text + " | "

                    #YES24는 매물에 가격또는 도서 위치가 없는 경우가 있음;;
                    price = ""
                    location = ""
                    try:
                        price = j.find("p", class_ = "storeG_price").text[2:].strip() #가격 부분 가져오기
                        location = j.find("dd").text.strip() #책 위치 가져오기
                    except AttributeError:
                        price = "가격정보 없음"
                        location = "위치정보 없음"

                    #이제 이것들을 json 파일로 저장시켜버리자
                    item = {'책 제목' : title, '설명' : description, '가격' : price, '서적 위치' : location}
                    result.append(item)
            self.search_result.append({'매장' : mall_name[i], '검색 결과' : result})

    def print_data(self):
        for i in range(0, len(self.search_result)):
            print(json.dumps(self.search_result[i], indent=4, ensure_ascii = False))

'''
if __name__ == "__main__":
    a = Searchpage("시스템")
    a.print_data()
''' 