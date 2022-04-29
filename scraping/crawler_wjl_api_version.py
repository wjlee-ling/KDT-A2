'''
공식 네이버 검색 API 사용하는 코드 
그러나 출판사 지정 못하고, '사설' 검색 결과를 리턴하기 때문에 후처리가 많이 필요함

네이버 뉴스- 조선일보 코드 : news_office_checked=1023

ref:
1. https://developers.naver.com/docs/search/blog/
2. 공식API 사용할 때 (https://ysyblog.tistory.com/49)
3. 네이버 공식 api doc (https://developers.naver.com/docs/serviceapi/search/news/news.md#%EB%89%B4%EC%8A%A4)
4. https://butnotforme.tistory.com/entry/python%EC%9C%BC%EB%A1%9C-%EC%97%85%EB%AC%B4-%EC%9E%90%EB%8F%99%ED%99%94%EA%B9%8C%EC%A7%80-8-requests3?category=932590
'''
import requests as req
import pandas as pd
import time
from bs4 import BeautifulSoup
from wjl_personal import naver_id, naver_pwd

headers= {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
    "X-Naver-Client-Id": naver_id,
    "X-Naver-Client-Secret": naver_pwd
}

def read_article(url):
    headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36"}
    webpage = req.get(url, headers)
    soup = BeautifulSoup(webpage.text, "html.parser")
    title = soup.select_one("#articleTitle").text.strip()
    body = soup.select_one('#articleBodyContents').text.strip()
    written_at = soup.select_one('#main_content > div.article_header > div.article_info > div > span.t11').text.split()[0]
    return title, body, written_at

def is_editorial(title):
    if title.startswith('[<b>사설</b>]') or title.endswith('[<b>사설</b>]'): #or title.startswith('&lt;<b>사설</b>&gt')
        # [사설] : 경향, 국민, 서울신문, 세계일보, 조선일보, 중앙일보, 한겨레, 한국일보, 매일경제, 한국경제, 서울경제
        return True
    return False

def search_opinions(publisher='default', start=1, display=100):
    """
    네이버 검색 API를 사용하여 기사들 link 추출
    - publisher: 신문사
    - start: 검색 page index
    - display: 노출 갯수

    연예/스포츠 섹션 뉴스는 제외
    """
    publisher_ids = {'경향신문':1032,'국민일보':1005,'동아일보':1020,'서울신문':1081,'세계일보':1022, '조선일보':1023, \
                    '중앙일보':1025, '한겨레':1028, '한국일보':1469, '매일경제':1009, '한국경제':1015, '서울경제':1011}
    #publisher_id = publisher_ids[publisher]

    naver_search_url = f"https://openapi.naver.com/v1/search/news.json?query=사설&start={start}&display={display}"
    res = req.get(naver_search_url, headers=headers)
    news_links = []
    if res.status_code == 200:
        res = res.json()
        items = res['items']
        for item in items:
            link = item['link']
            title = item['title']
            if 'news.naver.com' in link and is_editorial(title):
                news_links.append(link)
        time.sleep(0.15)
    else:
        print(res.status_code)

    return news_links

links = search_opinions()
print(links)

for link in links:
    title, body, written_at = read_article(link)
    print(title)
