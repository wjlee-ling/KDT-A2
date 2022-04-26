'''
네이버 검색 API를 사용하지 않는 버전. (출판사별 사설/오피니언 링크를 곧바로 얻을 수 있음.)
네이버 뉴스- 조선일보 코드 : news_office_checked=1023
네이버 검색은 최상의 검색결과 품질을 위해 뉴스 검색결과를 4,000건까지 제공합니다.
--Updates:
1. 원하는 결과물 갯수와 입력한 검색기간이 충돌할 때 검색기간을 우선시
2. (특히 짧은 기간으로 검색할 시) start에 따라 이미 수집한 기사가 여러번 반복되어 검색될시 검색 중지
3. 검색기간 입력 방식 바꿈
4. 검색기간 유효(get_earlier) 확인하는 코드 삽입

--TO-DO:

ref:
1. https://developers.naver.com/docs/search/blog/
2. 공식API 사용할 때 (https://ysyblog.tistory.com/49)
3. API없이 읽을 때 (https://wonhwa.tistory.com/8)
4. https://butnotforme.tistory.com/entry/python%EC%9C%BC%EB%A1%9C-%EC%97%85%EB%AC%B4-%EC%9E%90%EB%8F%99%ED%99%94%EA%B9%8C%EC%A7%80-8-requests3?category=932590
'''
import re

from torch import nonzero
from tqdm import tqdm
import requests as req
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

headers= {
    #"User-Agent" : generate_user_agent()
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
}

def is_editorial(title, publisher=None):
    if '[사설]' in title: #or title.startswith('&lt;<b>사설</b>&gt')
        # [사설] : 경향, 국민, 서울신문, 세계일보, 조선일보, 중앙일보, 한겨레, 한국일보, 매일경제, 한국경제, 서울경제
        return True
    else:
        # [사설] 대신 다른 키워드로 사설을 붙인 경우가 몇몇 있음.
        if publisher:
            if publisher == '한겨레':
                if '[한겨레 사설]' in title: 
                    return True

    return False

def read_article(url, driver):
    '''
    - title: 기사제목
    - body: 기사본문
    - written_at: 기사 업로드 일자('YYYY.MM.DD.' 형식) 
    '''
    
    driver.get(url)
    title = driver.find_element(by=By.CSS_SELECTOR, value=".media_end_head_headline").text.strip() # "#articleTitle"
    body = driver.find_element(by=By.CSS_SELECTOR, value="._article_body").text.strip() #'#articleBodyContents' 
    try:
        caption = driver.find_element(by=By.CSS_SELECTOR, value='.img_desc').text
        body = body.replace(caption, '').strip() # removing image captions
    except:
        body = body.strip()
        
    written_at = driver.find_element(by=By.CSS_SELECTOR, value="#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span").text.split()[0] #'#main_content > div.article_header > div.article_info > div > span.t11'
    #title = driver.find_element_by_css_selector("#articleTitle").text

    return title, body, written_at 

def search_editorials(publisher, start=1, since=None, to=None):
    """
    언론사별 사설을 검색하여, 이들의 네이버뉴스 링크를 리턴하는 메소드. 네이버는 키워드당 최대 4000개만 제공. 
    가장 최신일자 사설부터 제공. since와 to는 둘다 없거나 있어야 함.
    - publisher: 언론사
    - start: 검색 page index (display=1 일때 기준임. default가 10이므로 url상 2페이지는 21, 3페이지는 31로 )
    - since: 'YYYY.MM.DD' 검색 기간 시작점.
    - to: 'YYYY.MM.DD' 지정하지 않을 시 검색하는 날짜로 지정됨.

    e.g.https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%EC%82%AC%EC%84%A4&pd=0&ds=&de=&mynews=1&office_type=1&office_section_code=1&news_office_checked=1023&start=3001
    e.g. https://search.naver.com/search.naver?where=news&sm=tab_opt&query=사설&ds=20210419&de=20200419&mynews=1&office_type=1&office_section_code=1&news_office_checked=1023&start=1&nso=so%3Ar%2Cp%3Afrom20200419to20210419   
    """
    publisher_ids = {'경향신문':1032,'국민일보':1005,'동아일보':1020,'서울신문':1081,'세계일보':1022, '조선일보':1023, \
                    '중앙일보':1025, '한겨레':1028, '한국일보':1469, '매일경제':1009, '한국경제':1015, '서울경제':1011}
    if publisher not in publisher_ids.keys():
        raise Exception("입력한 언론사는 이용할 수 없습니다.")
    publisher_id = publisher_ids[publisher]

    if since is not None and to is not None:
        date_pattern = r'(19|20)[0-9]{2}\.[0-9]{2}\.[0-9]{2}' # 완벽하지 않음
        if not re.fullmatch(date_pattern, since): 
            raise Exception("잘못된 since 날짜 형식입니다.")
        if not re.fullmatch(date_pattern, to):
            raise Exception("잘못된 to 날짜 형식입니다.")
        url_per_publisher = f'https://search.naver.com/search.naver?where=news&sm=tab_opt&query=사설&ds={to}&de={since}&mynews=1&office_type=1&office_section_code=1&news_office_checked={publisher_id}&start={start}&nso=so%3Ar%2Cp%3Afrom{since.replace(".","")}to{to.replace(".","")}'
    else:
        url_per_publisher = f'https://search.naver.com/search.naver?where=news&sm=tab_pge&query=사설&mynews=1&office_type=1&office_section_code=1&news_office_checked={publisher_id}&start={start}'
    webpage = req.get(url_per_publisher, headers=headers)
    soup = BeautifulSoup(webpage.text, "html.parser")
    articles = soup.find_all('a', class_=["info"])
    links = []
    for a in articles:
        if len(a.get('class')) == 1 : # 네이버 기사와 원신문사 기사 링크 중 네이버 기사 링크 선택 
            href = a.get('href')
            if 'news.naver.com' in href: # 연예/스포츠 기사 제거
                links.append(a.get('href'))

    return links

def early_stop(len_links, non_editorials=None, duplicates=None):
    '''
    수집 중 조기에 중단할지 결정하는 함수.
    조기 중단 경우
        - 검색 결과가 아예 없을 때 -> 검색 기간 조정 후 재시도
        - 검색 페이지상 사설이 아닌 기사가 5개 이상일 때
    '''
    if len_links == 0:
        return True
    if non_editorials:
        if len_links == 10 and non_editorials >= 5 : # 검색 페이지상 사설이 아닌 기사가 5개 이상일 때 멈춤
            return True
        elif len_links < 10 and non_editorials == len_links:
            return True
    if duplicates:
        if duplicates == len_links:
            # 검색 page내 모든 기사들이 이미 추가한 기사일때
            return True
    return False

def get_earlier(date1, date2):
    '''
    날짜를 나타내는 두 string('YYYY.MM.DD' 형식)의 선후관계를 파악.
    이전의 시점을 return함.

    '''
    date1_ls = date1.split('.')
    date2_ls = date2.split('.')
    
    date1_score, date2_score = 0, 0
    decimal_point = [100, 10, 1]
    for p, d1, d2 in zip(decimal_point, date1_ls, date2_ls):
        d1, d2 = map(int, [d1, d2])
        if d1 < d2 :
            date2_score += p
        elif d1 > d2 :
            date1_score += p
    earlier = '.'.join(date1_ls) if date1_score < date2_score else '.'.join(date2_ls)
    if date1_score == date2_score:
        return 'same'
    return earlier

def scraper(publishers, n=1, search_range=None):
    '''    
    주어진 조건에 따라 네이버에서 해당 신문사의 사설을 모아 dataframe으로 return.
    - publishers: List. 검색할 언론사 목록
    - n : 수집할 기사 갯수
    - search_range: 검색 기간. [시작 시점, 마무리 시점]으로 각 시점은 'YYYY.MM.DD' 꼴 이여야 함.
    '''
    driver = webdriver.Chrome()
    dfs = []
    
    for publisher in publishers:
        if isinstance(search_range, list):
            since, to = search_range[0], search_range[1]
            if get_earlier(since, to) == to:
                raise Exception('Check the given range: [earlier, later]')
            input_since = since
        else:
            since, to = None, None

        titles, bodies, written_ats, naver_links = [],[],[],[]
        last_editorial_date = '0000.00.00' # first_search
        len_links, non_editorials = 10, 0
        with tqdm(total=n) as pbar:
            while len(titles) < n:
                if early_stop(len_links, non_editorials):
                    break
                # 입력한 시작 시점보다 이른 날짜로 재검색을 시도할 때 멈춤.
                if since is not None and get_earlier(since, input_since) == since:
                    print('지정한 날짜 이전으로 검색 안함')
                    break
                # 현재 검색 기간에서 주어진 n을 못 채웠을 때 재검색
                if last_editorial_date != '0000.00.00':
                    print('New search in different time ranges.')
                for idx in range(1, 401):
                    non_editorials = 0 # [사설]이 없는데, n을 채우기 위해 link를 수집하는 행위를 막기 위함.
                    duplicates = 0 # page_index가 달라질 때마다 이미 수집한 기사를 또 제공할 때 loop을 막기 위함.
                    if len(titles) >= n:
                        break
                    page_idx = 10*(idx-1) + 1 # url상 검색 1페이지는 1, 2페이지는 11, 3페이지는 21,.. 10페이지는 91, 11페이지는, 101 
                    links = search_editorials(publisher, start=page_idx, since=since, to=to)
                    len_links = len(links)
                    if early_stop(len_links):
                        # 검색 결과가 없으면 중단
                        break
                    for link in links:
                        if len(titles) >= n:
                            len_links = 0
                            break
                        try:
                            title, body, written_at  = read_article(link, driver)
                            sleep(0.13)
                        except:
                            print(f'Error occurs when reading the following article: {link}\n')
                            continue
                        if is_editorial(title):
                            if title in titles:
                                # 검색 기간을 달리 추가 검색할 때 사설 중복 수집 방지
                                duplicates += 1
                                continue
                            titles.append(title)
                            bodies.append(body)
                            written_ats.append(written_at)
                            naver_links.append(link)
                            last_editorial_date = written_at[:-1] # 마지막으로 저장된 사설 작성일
                            pbar.update(1)
                        else:
                            non_editorials+=1
                    if early_stop(len_links, non_editorials, duplicates):
                        # 사설이 아닌 결과가 5개 이상이거나, 모든 검색결과가 이미 수집한 기사일때 page-index-loop 중단
                        break

                # 지금까지 수집한 사설 수가 필요한 갯수보다 적을 때 검색 기간을 달리해 새로 수집
                year, month, date = last_editorial_date.split('.')
                year = int(year)
                since = f'{year-10}.{month}.{date}'
                to = f'{year}.{month}.{date}'
                print(f'new_since {since} :: new_to {to}')

        publisher_ls = [publisher] * len(titles)
        new_df = pd.DataFrame({'newspaper': publisher_ls, 'title': titles, 'body': bodies, 'written_at': written_ats, 'naver_link':naver_links})
        dfs.append(new_df)
        print(f'Scraping for {publisher} is done.')

    driver.close()
    return dfs

newspapers = ['동아일보']
#time_range = ['2015.03.23', '2015.03.23']
## csv형식으로 corpus 만들기
corpora =scraper(newspapers, n=10000, search_range=None)
for paper, corpus in zip(newspapers, corpora]:
    corpus.to_csv(r"C:\Users\oian\Documents\GitHub\A2-TeamProject\scraping\corpus\corpus_{paper}_raw.csv", encoding='utf-8-sig', index=False)