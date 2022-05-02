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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

headers= {
    "X-Naver-Client-Id": "LFDIwR9DMgVRcfm0fCSh",
    "X-Naver-Client-Secret": "4yvFIBoLrh"
}

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
    category = driver.find_element(by=By.CSS_SELECTOR, value=".media_end_categorize_item").text.strip()
    #title = driver.find_element_by_css_selector("#articleTitle").text
    article = {'title':title, 'body':body, 'written_at':written_at, 'category':category}
    return article


def search_editorials(start=1, display=100):
    """
    네이버 검색 API를 사용하여 기사들 link 추출
    - publisher: 신문사
    - start: 노출되는 기사 index로 display의 값에 따라 page_index가 달라짐. display=10이면 start=21 일 떼, page_index가 2
    - display: 노출되는 수 
    연예/스포츠 섹션 뉴스는 제외
    """
    naver_search_url = f"https://openapi.naver.com/v1/search/news.json?query=사설&start={start}&sort=sim&display={display}"
    res = req.get(naver_search_url, headers=headers)
    news_links = []
    #news_titles= []
    publishers = []
    if res.status_code == 200:
        res = res.json()
        items = res['items']
        for item in items:
            naver_link = item['link']
            original_link = item['originallink']
            title = item['title']
            if 'news.naver.com' in naver_link and '[<b>사설</b>]' in title:
                news_links.append(naver_link)
                #news_titles.append(title)
                if 'chosun' in original_link:
                    publisher = '조선일보'
                elif 'donga' in original_link:
                    publisher = '동아일보'
                elif 'hani' in original_link:
                    publisher = '한겨레'
                elif 'joongang' in original_link:
                    publisher = '중앙일보'
                elif 'khan' in original_link:
                    publisher = '경향신문'
                else:
                    publisher = ''
                publishers.append(publisher)
        time.sleep(0.15)
    else:
        print(res.status_code)

    return news_links, publishers

def create_train_data():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    news_links, publishers = search_editorials()
    bodies, newspapers= [], []
    for link, source in zip(news_links, publishers):
        article = read_article(link, driver)
        if article['category'] == '오피니언':
            bodies.append(article['body'])
            newspapers.append(source)
    df = pd.DataFrame({'body': bodies, 'newspaper':newspapers})
    driver.close()
    return df

df = create_train_data()
print(df.head())