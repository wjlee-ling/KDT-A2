'''
네이버에서 조선일보의 사설 긁는 web crawler
네이버 뉴스- 조선일보 코드 : news_office_checked=1023

ref:
1. https://developers.naver.com/docs/search/blog/
2. 공식API 사용할 때 (https://ysyblog.tistory.com/49)
3. API없이 읽을 때 (https://wonhwa.tistory.com/8)
4. https://butnotforme.tistory.com/entry/python%EC%9C%BC%EB%A1%9C-%EC%97%85%EB%AC%B4-%EC%9E%90%EB%8F%99%ED%99%94%EA%B9%8C%EC%A7%80-8-requests3?category=932590
'''
import requests as req
import pandas as pd
from bs4 import BeautifulSoup
from wjl_personal import naver_id, naver_pwd

headers= {
    #"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Naver-Client-Id": naver_id,
    "X-Naver-Client-Secret": naver_pwd
}

def read_article(url):
    webpage = req.get(url, headers)
    soup = BeautifulSoup(webpage.text, "html.parser")
    title = soup.select_one("#articleTitle").text.strip()
    body = soup.select_one('#articleBodyContents').text.strip()
    written_at = soup.select_one('#main_content > div.article_header > div.article_info > div > span.t11').text.split()[0]
    return title, body, written_at

def search_opinions(publisher, start=1):
    """
    출판사별 사설을 검색하여, 이들의 네이버뉴스 링크를 리턴하는 메소드
    - publisher: 출판사
    - start: 검색 page index
    """
    publisher_ids = {'조선일보': 1023}
    publisher_id = publisher_ids[publisher]
    url_per_publisher = f'https://search.naver.com/search.naver?where=news&sm=tab_pge&query=사설&mynews=1&office_type=1&office_section_code=1&news_office_checked={publisher_id}&start={start}'
    webpage = req.get(url_per_publisher, headers=headers)
    soup = BeautifulSoup(webpage.text, "html.parser")
    articles = soup.find_all('a', class_=["info"])
    results = []
    for a in articles:
        if len(a.get('class')) == 1:
            results.append(a.get('href'))
    return results

articles = search_opinions('조선일보')
print(articles)