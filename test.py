# 알라딘 또는 YES24 오프라인 검색기 테스트 프로그램

import multiprocessing
# import module.aladin as Aladin
from module.aladinV2 import Aladin
from module.yes24V2 import Yes24
#import module.yes24 as Yes24


class Search_Process:
    def __init__(self, word, mod):
        self.word = word
        self.mod = mod
        if mod == "0":
            self.search_aladin()
        else:
            self.search_yes24()

    def search_aladin(self):
        # search_result = Aladin.Search_result(self.word)
        # search_result.print_data()
        search = Aladin(self.word)
        print(search.result())

    def search_yes24(self):
        # search_page = Yes24.Searchpage(self.word)
        # search_page.print_data()
        search = Yes24(self.word)
        print(search.result())


if __name__ == "__main__":
    word = input("검색어를 입력하세요: ")
    searchmod = input("알라딘검색 - 0, yes24 - 1 : ")
    search = Search_Process(word, searchmod)
    print('\n')
