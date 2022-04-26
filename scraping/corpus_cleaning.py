import pandas as pd
import re


def get_paragraphs(body):
    '''
    본문을 paragraph 단위로 잘라 기사당 하나의 리스트로 리턴
    '''
    body = body.strip()
    body = body.strip("'")
    body = re.sub('\n{2,}', '\n', body) # 2개 '이상'의 연속\n이 있는 경우 \n으로 변경
    return body.split('\n')

def valid_row_general(title, body):
    '''
    general하게 모든 언론사 코퍼스에 적용할 수 있는 클리닝 코드
    TO-DO:
        1. 제목에서 [사설] 제거
        2. 제목 또는 본문에서 전체 둘러싸는 따옴표 제거
        3. 본문내 이미지 캡션 제거
        4. 본문 앞뒤로 신문사 이름 / 카피라이트 문구 / 기타 기사 추천 등 제거
        5. (한자) 제거
    '''

    # 제목 처리
    title = title.replace('[사설]', '').strip()

    ## 본문 처리
    # (한자) 제거
    hanja_in_paren = r'\([一-龥]+\)' # e.g. 일(一) -> 일 
    if re.search(hanja_in_paren, body):
        body = re.sub(hanja_in_paren, '', body)

    # 실제 기사 아닌 내용 제거
    if len(body.split('.')) <= 1:
    # 문단내 '.'으로 끝나는 문장이 하나거나 없을 때
        return title, None
    return title, body

def valid_row_kh(row):
    '''
    각 열(문단)이 본문 내용인지 판별하는 코드
    '''
    row = row.strip()
    noises = ('[경향신문]', '〈경향', '-', '▶', '경향신문 \'' '모바일 경향')
    if row.startswith(noises):
        # 예시: 공식 SNS 계정 [경향 트위터] [미투데이] [페이스북] [세상과 경향의 소통 Khross]
        # 예시: 경향신문 ‘오늘의 핫뉴스’
        # 예시: ▶ 시험 닥치면 훔치고, 싸우고, 아프고 ‘돌변하는 아이들
        return None
    return row

def valid_row_chosun(row):
    row = row.strip()
    noises = ('영문으로 이 기사', '▶', '-')
    if row.startswith(noises):
        return None
    return row

def to_paragraph_based(df):
    '''
    한 열당 기사 하나인 코퍼스를 한 열당 문단 하나로 바꾸는 코드
    '''
    title_ls, body_ls, written_ls = df['title'].values, df['body'].values, df['written_at'].values
    new_title_ls, new_body_ls, new_written_ls = [], [], []
    for t, b, wr in zip(title_ls, body_ls, written_ls):
        t, b, wr = map(lambda x: x.strip(), [t,b,wr])
        ## body to a list of paragraph
        b = get_paragraphs(b) #  문단 리스트
        for p in b:
            new_title_ls.append(t)
            new_body_ls.append(p)
            new_written_ls.append(wr)
        new_df = pd.DataFrame({'title': new_title_ls, 'body': new_body_ls, 'written_at':new_written_ls})
    return new_df

def cleaning(df, publisher):
    titles, bodies, written_ats = df['title'].values, df['body'].values, df['written_at'].values
    cleaned_t, cleaned_b, new_written_at= [], [], []
    for t, b, wr in zip(titles, bodies, written_ats):
        title, body = valid_row_general(t,b)
        if body is None:
            continue
        if publisher == '경향신문':
            body = valid_row_kh(body)
            if body is None:
                continue
        elif publisher == '조선일보':
            body = valid_row_chosun(body)
            if body is None:
                continue

        # if valid body:
        cleaned_t.append(title)
        cleaned_b.append(body)
        new_written_at.append(wr)
    new_df = pd.DataFrame({'title': cleaned_t, 'body': cleaned_b, 'written_at' : new_written_at})
    
    # 중복 제거
    new_df.drop_duplicates(subset='body', keep='first', inplace=True)
    new_df.reset_index(inplace=True)
    return new_df

## 조선일보
# chosun_mine = pd.read_csv('corpus_조선일보_20180701부터.csv')
# chosun_mine = to_paragraph_based(chosun_mine)
# chosun_rest = pd.read_csv('corpus_조선일보20180630까지.csv')
# chosun_total = chosun_mine.append(chosun_rest, ignore_index=True)
# chosun_cleaned = cleaning(chosun_total, '조선일보')
# chosun_cleaned.to_csv('corpus/corpus_조선일보_cleaned.csv', encoding='utf-8-sig', index=False)

# ## 경향
# kh_df = pd.read_csv('corpus_경향신문.csv')
# kh_df_para_based = to_paragraph_based(kh_df) 
# kh_df_cleaned = cleaning(kh_df_para_based, '경향신문')
# kh_df_cleaned.to_csv('corpus/corpus_경향신문_cleaned.csv', encoding='utf-8-sig', index=False)



