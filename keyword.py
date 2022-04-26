import pandas as pd
from scraping.corpus_cleaning import to_paragraph_based

new_dfs = []
for paper in ['경향신문', '조선일보', '중앙일보', '한겨레']:
    df = pd.read_csv(f'C:/Users/oian/Documents/GitHub/A2-TeamProject/scraping/corpus/corpus_{paper}_cleaned.csv')
    if paper in ['한겨레', '중앙일보']:
        df = to_paragraph_based(df)

    df['newspaper'] = [paper] * len(df)
    new_df = df[['newspaper','title', 'body', 'written_at']]
    new_dfs.append(new_df)
    new_df.to_csv(f'C:/Users/oian/Documents/GitHub/A2-TeamProject/scraping/corpus/corpus_{paper}_cleaned_p.csv',\
        encoding='utf-8-sig', index=False)

df_total = pd.concat(new_dfs)
df_total.to_csv(f'C:/Users/oian/Documents/GitHub/A2-TeamProject/scraping/corpus/corpus_{조선&중앙&한겨레&경향}_cleaned_p.csv', encoding='utf-8-sig', index=False)
