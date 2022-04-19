'''
네이버 검색 API를 사용하지 않는 버전. (출판사별 사설/오피니언 링크를 곧바로 얻을 수 있음.)
네이버 뉴스- 조선일보 코드 : news_office_checked=1023

--TO-DO:
1. 기사 중간에 삽입된 사진과 캡션 제거 필요
ref:
1. https://developers.naver.com/docs/search/blog/
2. 공식API 사용할 때 (https://ysyblog.tistory.com/49)
3. API없이 읽을 때 (https://wonhwa.tistory.com/8)
4. https://butnotforme.tistory.com/entry/python%EC%9C%BC%EB%A1%9C-%EC%97%85%EB%AC%B4-%EC%9E%90%EB%8F%99%ED%99%94%EA%B9%8C%EC%A7%80-8-requests3?category=932590
'''
import requests as req
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

headers= {
    #"User-Agent" : generate_user_agent()
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
}

def is_opinion(title):
    if title.startswith('[사설]') or title.endswith('[사설]'): #or title.startswith('&lt;<b>사설</b>&gt')
        # [사설] : 경향, 국민, 서울신문, 세계일보, 조선일보, 중앙일보, 한겨레, 한국일보, 매일경제, 한국경제, 서울경제
        return True
    return False

def read_article(url, driver):
    '''
    - title: 기사제목
    - body: 기사본문
    - written_at: 기사 업로드 일자('YYYY.MM.DD.' 형식) 
    '''
    
    driver.get(url)
    title = driver.find_element(by=By.CSS_SELECTOR, value="#articleTitle").text.strip()
    body = driver.find_element(by=By.CSS_SELECTOR, value='#articleBodyContents').text.strip()
    written_at = driver.find_element(by=By.CSS_SELECTOR, value='#main_content > div.article_header > div.article_info > div > span.t11').text.split()[0]
    #title = driver.find_element_by_css_selector("#articleTitle").text

    return title, body, written_at 

def search_opinions(publisher, start=1, since=None, to=None):
    import re
    """
    언론사별 사설을 검색하여, 이들의 네이버뉴스 링크를 리턴하는 메소드
    - publisher: 언론사
    - start: 검색 page index
    - since/to: 'YYYY.MM.DD' 검색할 기사 작성 날짜 기간. since가 to보다 이전이여야 함

    e.g.https://search.naver.com/search.naver?where=news&sm=tab_pge&query=사설&mynews=1&office_type=1&office_section_code=1&news_office_checked=1023&start=1
    """
    publisher_ids = {'경향신문':1032,'국민일보':1005,'동아일보':1020,'서울신문':1081,'세계일보':1022, '조선일보':1023, \
                    '중앙일보':1025, '한겨레':1028, '한국일보':1469, '매일경제':1009, '한국경제':1015, '서울경제':1011}
    if publisher not in publisher_ids.keys():
        raise Exception("입력한 출판사는 이용할 수 없습니다.")
    publisher_id = publisher_ids[publisher]

    if since is not None or to is not None:
        url_per_publisher = f'https://search.naver.com/search.naver?where=news&sm=tab_opt&query=사설&ds={to}&de={since}&mynews=1&office_type=1&office_section_code=1&news_office_checked={publisher_id}&start={start}&nso=so%3Ar%2Cp%3Afrom{since.replace(".","")}to{to.replace(".","")}'
        date_pattern = r'(19|20)[0-9]{2}\.[0-9]{2}\.[0-9]{2}' # 완벽하지 않음
        if re.fullmatch(date_pattern, since) and re.fullmatch(date_pattern, since).group(0) != since: 
            raise Exception("잘못된 since 날짜 형식입니다.")
        if re.fullmatch(date_pattern, to) and re.fullmatch(date_pattern, to).group(0) != to:
            raise Exception("잘못된 to 날짜 형식입니다.")
    else:
        url_per_publisher = f'https://search.naver.com/search.naver?where=news&sm=tab_pge&query=사설&mynews=1&office_type=1&office_section_code=1&news_office_checked={publisher_id}&start={start}'
    
    webpage = req.get(url_per_publisher, headers=headers)
    soup = BeautifulSoup(webpage.text, "html.parser")
    articles = soup.find_all('a', class_=["info"])
    links = []
    for a in articles:
        if len(a.get('class')) == 1: # 네이버 기사와 원신문사 기사 링크 중 네이버 기사 링크 선택
            links.append(a.get('href'))
    return links

def scraper(publishers, pages_n=1, since=None, to=None):
    '''    
    주어진 조건에 따라 해당 신문사의 사설을 모아 dataframe으로 return.
    - publishers: List. 검색할 언론사 목록
    - pages_n : 검색할 page 수
    - since/to: 'YYYY.MM.DD' 검색할 기사 작성 날짜 기간. since가 to보다 이전이여야 함
    '''
    driver = webdriver.Chrome()
    total_df = pd.DataFrame()
    for publisher in publishers:
        titles, bodies, written_ats= [],[],[]
        for idx in range(1, pages_n+1):
            links = search_opinions(publisher, start=idx, since=since, to=to)
            for link in links:
                title, body, written_at  = read_article(link, driver)
                sleep(0.2)
                if is_opinion(title):
                    titles.append(title)
                    bodies.append(body)
                    written_ats.append(written_at)
        publisher_ls = [publisher] * len(titles)
        new_df = pd.DataFrame({'newspaper': publisher_ls, 'title': titles, 'body': bodies, 'written_at': written_ats})
        total_df = pd.concat([total_df, new_df])
    driver.close()
    return total_df

newspaper = [] # 
corpus = scraper(newspaper, pages_n=100)
corpus.to_csv(f'corpus_{newspaper}.csv', encoding='utf-8-sig')