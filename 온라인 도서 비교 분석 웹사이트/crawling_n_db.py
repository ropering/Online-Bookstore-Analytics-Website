#-*- coding:utf-8 -*-
'''
oracle_db_wallet 경로는 자신의 wallet 위치에 맞게 경로를 설정해야 합니vbfgcdsz
'''
# keyword = input("크롤링할 키워드를 검색하세요")
# keyword = parse.quote(keyword.encode("EUC-KR"))
# keyword

from bs4 import BeautifulSoup
from selenium import webdriver
from pprint import pprint
import cx_Oracle
import urllib
from urllib import parse

def crawling_yes24():
    keyword = input("YES24에서 크롤링할 키워드를 검색하세요")
    keyword = parse.quote(keyword.encode("EUC-KR"))

    dr  = webdriver.Chrome()
    dr.get(f"http://www.yes24.com/searchcorner/Search?keywordAd=&query={keyword}")
    html_source = dr.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    products = soup.select('div.goodsList_list p.goods_name > a')
    # pprint(products)
    prod_cd = [[product['href'], product.find('strong')] for product in products]

    global names, prices, dates, companys, reviews, ratings, bookstores, serials, sales, pages, isbn_13
    names = []      # 도서명 / VARCHAR(50)
    prices = []     # 가격 / INT
    dates = []      # 출판일 / DATE
    companys = []   # 출판사 / VARCHAR(45)
    reviews = []    # 리뷰 수 / INT
    ratings = []    # 별점 / FLOAT
    bookstores = [] # 온라인 서점 명 / VARCHAR(20)
    serials = []    # 일련번호 / INT
    sales = []      # 판매 지수 / INT
    pages = []      # 쪽 수 / INT
    isbn_13 = []    # ISBN / CHAR(13)
    # 각 도서 페이지 접속 → 필요한 데이터 수집
    for i, prod in enumerate(prod_cd): # prod[0] : url 웹 주소  /  prod[1] : 교재 명
        if "http" in prod[0]: # 중고책 목록을 만나면 /
            break
        dr.get(f"https://www.yes24.com/{prod[0]}")
        html_source = dr.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        dr.implicitly_wait(10) # 화면이 다 보일 때 까지 10초 동안 기다린다

        try:
            if 'PDF' in soup.select_one('#spanGdKeynote > span.iconC.ePub > em').get_text(): # ebook을 만나면
                print("ebook은 크롤링하지 않습니다 다음으로 넘어갑니다")
                continue
        except Exception as e: # 종이 책이라면 정상적으로 진행
            pass
        try:
            if '문구' in soup.select_one('#yDetailTopWrap > div.topColRgt > div.gd_infoTop > div > strong > em').get_text():
                print("문구는 크롤링하지 않습니다 다음으로 넘어갑니다")
                continue
        except Exception as e:
            pass
        names.append(soup.select_one('.gd_name').get_text())
        prices.append(int(soup.select_one('.yes_m').get_text()[:-1].replace(',','')))
        dates.append(soup.select_one('.gd_date').get_text().replace('년 ', '-').replace('월 ', '-').replace('일', ''))
        companys.append(soup.select_one('.gd_pub').get_text())

        try:
            if "고객" in soup.select_one('div.infoSetCont_wrap > div > table > tbody > tr:nth-child(3) > td').get_text(): # ISBN13 값이 없다면
                print(soup.select_one('div.infoSetCont_wrap > div > table > tbody > tr:nth-child(3) > td').get_text())
                isbn_13.append("NULL") # ISBN13 값이 없는 경우
            else:
                isbn_13.append(soup.select_one('div.infoSetCont_wrap > div > table > tbody > tr:nth-child(3) > td').get_text())
        except Exception as e:   pass

        try:
            if "크레마" in soup.select_one('div.infoSetCont_wrap > div > table > tbody > tr:nth-child(3) > td').get_text(): # ISBN13 값이 없다면
                isbn_13.append("NULL") # ISBN13 값이 없는 경우
            else: pass
        except Exception as e:    pass

        try:
            pages.append(int(soup.select_one('div.infoSetCont_wrap > div > table > tbody > tr:nth-child(2) > td').get_text().split(' ')[0][:-1].replace(',', '')))
        except ValueError as e:
            pages.append("NULL")

        try:
            reviews.append(soup.select_one('span.gd_reviewCount .txC_blue').get_text()) # int
        except Exception as e:
            reviews.append('NULL')

        try:
            ratings.append(soup.select_one('#spanGdRating a.gd_lnkRate em.yes_b').get_text())
        except Exception as e:
            ratings.append('NULL')

        try:
            sales.append(int(soup.select_one('.gd_sellNum').get_text()[23:-7].strip().replace(',', '')))
        except Exception as e:
            sales.append('NULL')

        bookstores.append(soup.select_one('.txt_copyright').get_text()[12:17])

def yes24_insert_to_db_bookinfo():
    global names, prices, dates, companys, reviews, ratings, bookstores, serials, sales, pages, isbn_13
    try:
        cx_Oracle.init_oracle_client(config_dir=r"C:/Users/user/Desktop/work_space/Oracle_Wallet_edudb_OracleCloud")
    except Exception as e:
        pass
    con = cx_Oracle.connect(user="roper", password='UTgUGzj_9sHg47', dsn='edudb_high')
    cur = con.cursor()

    brands = ['건기원', '길벗', '영진닷컴']
    brand = ''

    for i in range(len(isbn_13)):
        if companys[i] in brands:
            if companys[i] == '건기원':
                brand = '수제비'
            if companys[i] == '길벗':
                brand = '시나공'
            if companys[i] == '영진닷컴':
                brand = '이기적'
        else:
            brand = '기타'
        cur.execute(f"INSERT INTO bookinfo VALUES ('{isbn_13[i]}', '{names[i]}', '{companys[i]}', '{dates[i]}', {pages[i]}, {prices[i]}, '{brand}')")
    con.commit()
    con.close()

def yes24_insert_to_db_onlinestore():
    global names, prices, dates, companys, reviews, ratings, bookstores, serials, sales, pages, isbn_13
    try:
        cx_Oracle.init_oracle_client(config_dir=r"C:/Users/user/Desktop/work_space/Oracle_Wallet_edudb_OracleCloud")
    except Exception as e:
        pass
    con = cx_Oracle.connect(user="roper", password='UTgUGzj_9sHg47', dsn='edudb_high')
    cur = con.cursor()

    for i in range(len(names)):
        cur.execute(f"INSERT INTO onlinestore VALUES ({i+1}, '{isbn_13[i]}', '{bookstores[i]}', {ratings[i]}, {reviews[i]}, {sales[i]})")
    con.commit()
    con.close()

def crawling_kyobo():
    keyword = input("교보문고에서 크롤링할 키워드를 검색하세요")
    keyword = parse.quote(keyword)
    dr = webdriver.Chrome()
    dr.get(f"https://search.kyobobook.co.kr/web/search?vPstrKeyWord={keyword}")
    html_source = dr.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    products = soup.select('td.detail div.title > a')
    prod_cd = [product['href'] for product in products]

    global names, prices, dates, companys, reviews, ratings, bookstores, serials, sales, pages, isbn_13
    names = []      # 도서명 / VARCHAR(50)
    prices = []     # 가격 / INT
    dates = []      # 출판일 / DATE
    companys = []   # 출판사 / VARCHAR(45)
    reviews = []    # 리뷰 수 / INT
    ratings = []    # 별점 / FLOAT
    bookstores = [] # 온라인 서점 명 / VARCHAR(20)
    serials = []    # 일련번호 / INT
    sales = []      # 판매 지수 / INT
    pages = []      # 쪽 수 / INT
    isbn_13 = []    # ISBN / CHAR(13)

    for prod in prod_cd:     # 교보문고 / 리뷰 수, 판매 지수 X
        if "used" in prod: # 중고책 목록을 만나면
            break
        dr.get(str(prod))
        html_source = dr.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        dr.implicitly_wait(10)
        try:
            ratings.append(soup.select_one('div.review > div.review_klover > div.popup_load em').get_text())
        except Exception as e :
            ratings.append('NULL')
        bookstores.append(soup.select_one('.mark_isms p').get_text()[11:15])
        isbn_13.append(soup.select_one('.table_simple2.table_opened.margin_top10 tr td span').get_text())
        reviews.append('NULL')
        sales.append('NULL')

def kyobo_insert_to_db_onlinestore():
    global names, prices, dates, companys, reviews, ratings, bookstores, serials, sales, pages, isbn_13
    try:
        cx_Oracle.init_oracle_client(config_dir=r"C:/Users/user/Desktop/work_space/Oracle_Wallet_edudb_OracleCloud")
    except Exception as e:
        pass
    con = cx_Oracle.connect(user="roper", password='UTgUGzj_9sHg47', dsn='edudb_high')
    cur = con.cursor()

    for i in range(len(isbn_13)):
        cur.execute(f"INSERT INTO onlinestore VALUES ({i+1}, '{isbn_13[i]}', '{bookstores[i]}', {ratings[i]}, {reviews[i]}, {sales[i]})")
    con.commit()
    con.close()

def crawling_aladin():
    keyword = input("알라딘에서 크롤링할 키워드를 검색하세요")
    keyword = parse.quote(keyword)

    dr = webdriver.Chrome()
    dr.get(f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=Book&SearchWord={keyword}")
    html_source = dr.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    products = soup.select('a.bo3')
    prod_cd = [product['href'] for product in products]

    global names, prices, dates, companys, reviews, ratings, bookstores, serials, sales, pages, isbn_13
    names = []      # 도서명 / VARCHAR(50)
    prices = []     # 가격 / INT
    dates = []      # 출판일 / DATE
    companys = []   # 출판사 / VARCHAR(45)
    reviews = []    # 리뷰 수 / INT
    ratings = []    # 별점 / FLOAT
    pages = []      # 쪽 수 / INT
    isbn_13 = []    # ISBN / CHAR(13)
    serials = []    # 일련번호 / INT
    sales = []      # 판매 지수 / INT
    bookstores = [] # 온라인 서점 명 / VARCHAR(20)

    for prod in prod_cd:
        container = dict()
        dr.get(str(prod))
        html_source = dr.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        dr.implicitly_wait(10)

        products = soup.select('.conts_info_list1 li')
        pages.append((int(products[0].text[:-1]))) # 페이지 수
        isbn_13.append((products[3].text[-13:])) # ISBN 값 # ISBN 값
        sales.append(int(soup.select_one('.Ere_fs15.Ere_ht18 >div strong').get_text().replace(',', '')))#판매지수
        bookstores.append(soup.select_one('.corp_info1 > h3').get_text()[3:6])#서점
        reviews.append(int(soup.select_one('.info_list.Ere_fs15.Ere_ht18 > a:nth-child(5)').get_text()[6:-1])) #리뷰건수 최종 완성본
        ratings.append(float(soup.select_one('.Ere_sub_pink.Ere_fs16.Ere_str').get_text()[:-1]))

def aladin_insert_to_db_onlinestore():
    global names, prices, dates, companys, reviews, ratings, bookstores, serials, sales, pages, isbn_13

    try:
        cx_Oracle.init_oracle_client(config_dir=r"C:/Users/user/Desktop/work_space/Oracle_Wallet_edudb_OracleCloud")
    except Exception as e:
        pass

    con = cx_Oracle.connect(user="roper", password='UTgUGzj_9sHg47', dsn='edudb_high')
    cur = con.cursor()

    for i in range(len(isbn_13)):
        cur.execute(f"INSERT INTO onlinestore VALUES ({i+1}, '{isbn_13[i]}', '{bookstores[i]}', {ratings[i]}, {reviews[i]}, {sales[i]})")
    con.commit()
    con.close()

def select_from_onlinestore_db():
    try:
        cx_Oracle.init_oracle_client(config_dir=r"C:/Users/user/Desktop/work_space/Oracle_Wallet_edudb_OracleCloud")
    except Exception as e:
        pass

    con = cx_Oracle.connect(user="roper", password='UTgUGzj_9sHg47', dsn='edudb_high')
    cur = con.cursor()

    cur.execute("SELECT * FROM onlinestore")
    return(cur.fetchall())

def select_from_bookinfo_db():
    try:
        cx_Oracle.init_oracle_client(config_dir=r"C:/Users/user/Desktop/work_space/Oracle_Wallet_edudb_OracleCloud")
    except Exception as e:
        pass

    con = cx_Oracle.connect(user="roper", password='UTgUGzj_9sHg47', dsn='edudb_high')
    cur = con.cursor()

    cur.execute("SELECT * FROM bookinfo")
    return(cur.fetchall())

def select_from_user_search(name):
    try:
        cx_Oracle.init_oracle_client(config_dir=r"C:/Users/user/Desktop/work_space/Oracle_Wallet_edudb_OracleCloud")
    except Exception as e:
        pass

    con = cx_Oracle.connect(user="roper", password='UTgUGzj_9sHg47', dsn='edudb_high')
    cur = con.cursor()

    cur.execute(f"SELECT B.ISBN13, B.NAME, B.PUBLISHER, B.DATE_PUB, B.PAGE, B.PRICE, B.BRAND, \
                S.BOOKSTORE, S.RATING, S.REVIEW, S.SALES \
                FROM BOOKINFO B FULL OUTER JOIN ONLINESTORE S ON B.ISBN13 = S.ISBN13 \
                WHERE NAME LIKE '%{name}%' ORDER BY S.SALES DESC NULLS LAST")
    return(cur.fetchall())


# f"SELECT B.ISBN13, B.NAME, B.PUBLISHER, B.DATE_PUB, B.PAGE, B.PRICE, B.BRAND, \
#             S.BOOKSTORE, S.RATING, S.REVIEW, S.SALES \
#             FROM BOOKINFO B FULL OUTER JOIN ONLINESTORE S ON B.ISBN13 = S.ISBN13 \
#             WHERE NAME LIKE '%'{name}'%'
#             ORDER BY SALES DESC




# 같은 변수명을 공유하고 있기 때문에 각 출판사 별로 함수를 실행해야 함! (yes24함수 끼리 실행)
if __name__ == "__main__":
    crawling_yes24()
    # yes24_insert_to_db_bookinfo()
    # yes24_insert_to_db_onlinestore()
    #
    crawling_kyobo()
    # kyobo_insert_to_db_onlinestore()
    #
    crawling_aladin()
    # aladin_insert_to_db_onlinestore()
    #
    select_from_onlinestore_db()
    select_from_bookinfo_db()
    #
    select_from_user_search()






#
# con.commit()
#
# cur.execute("SELECT * FROM BOOKINFO")
# cur.execute("SELECT * FROM onlinestore")
# cur.fetchall()
# con.close()
#
#
# len(isbn_13)
# len(bookstores)
# len(ratings)
# len(reviews)
# len(sales)
# len()
# len()
# len()
# len()
# len()
# len()
# len()
#
# int('123')

names = []      # 도서명 / VARCHAR(50)
prices = []     # 가격 / INT
dates = []      # 출판일 / DATE
companys = []   # 출판사 / VARCHAR(45)
reviews = []    # 리뷰 수 / INT
ratings = []    # 별점 / FLOAT
bookstores = [] # 온라인 서점 명 / VARCHAR(20)
serials = []    # 일련번호 / INT
sales = []      # 판매 지수 / INT
pages = []      # 쪽 수 / INT
isbn_13 = []

len(names)
len(prices)
len(dates)
len(companys)
len(reviews)
len(ratings)
len(bookstores)
len(sales)
len(pages)
len(isbn_13)

names
prices
dates
companys
reviews
ratings
bookstores
serials
sales
pages
isbn_13
