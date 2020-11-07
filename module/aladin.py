'''
Aladin OfflineShop Parse Module by Sc0_Nep
'''

from bs4 import BeautifulSoup
import requests

URL = "https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=UsedStore&KeyTag=&SearchWord="

class Searchpage:
    def __init__(self, keyword):
        html = requests.get(URL + keyword).text
        self.soup = BeautifulSoup(html, 'html.parser')
        self.get_items = self.soup.find_all("div", class_ = "ss_book_box")
        self.item_quantity = len(self.get_items)

        #Essential lists
        self.list_title = []
        self.list_description = []
        self.list_shop = []

        #Parse & arrange data
        self.__parse_data()

    def __parse_data(self):
        for i in self.get_items:
            #Get Title
            title = i.find("b", class_ = "bo3").text

            #Get Description
            tag_li = i.find_all("li")
            description = tag_li[1].text

            #Get Shopinfo
            shop = {}
            tag_a = i.find_all("a", class_ = "usedshop_off_text3")
            for j in tag_a:
                shopname = j.text
                shopurl = j.attrs['href']
                shop.setdefault(shopname, shopurl)
            self.list_title.append(title)
            self.list_description.append(description)
            self.list_shop.append(shop)
    
    def print_data(self):
        for i in range(0, self.item_quantity):
            print(self.list_title[i])
            print(self.list_description[i])
            print(self.list_shop[i])
            print("--------------------------- \n")

#Get singleitem info
class itempage(Searchpage):
    def __init__(self, keyword, num):
        super().__init__(keyword)
        self.title = self.list_title[num]
        self.description = self.list_description[num]
        self.target_shops = self.list_shop[num]
        self.shops_stock = []
        self.__parse_itemdata()   

    def __parse_itemdata(self):
        shopurl = self.target_shops.values()
        for i in shopurl:
            html = requests.get(i).text
            self.soup = BeautifulSoup(html, 'html.parser')
            self.get_stock = self.soup.find_all("div", class_="ss_book_box")
            stock = []
            for j in self.get_stock:
                info = []
                price = j.find("span", class_="ss_p2").text
                quality = j.find("span", class_="us_f_bob").text
                location = j.find_all("span", class_="ss_p3")[3].find("b").text[7:].strip()
                info.append(price)
                info.append(quality)
                info.append(location)
                stock.append(info)
            self.shops_stock.append(stock)
    
    def print_data(self):
        print(self.title)
        print(self.description)
        print(self.target_shops.keys())
        print(self.shops_stock)

if __name__ == "__main__":
    a = itempage("컴퓨터구조", 4)
    a.print_data()

    



        