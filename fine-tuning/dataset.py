 #-*- coding: utf-8 -*- 
import torch
import pandas as pd
import numpy as np
from torch.utils.data import DataLoader

batch_size= 16

class ArticleDataset(torch.utils.data.Dataset):
    def __init__(self, dataframe):
        df = dataframe
        self.publisher = df.loc[:, 'publisher'].values
        self.text = df.loc[:, 'paragraph_form'].values

    def __getitem__(self, idx):
        return self.publisher[idx] + ':' +self.text[idx]
    
    def __len__(self):
        return len(self.publisher)

train_percent = 0.8
df1 = pd.read_csv("/home/ubuntu/kogpt_article/data/NWRW2100000003.csv", encoding='utf-8') ## csv file
df2 = pd.read_csv("/home/ubuntu/kogpt_article/data/NWRW2100000004.csv", encoding='utf-8')

df = pd.concat([df1, df2], axis=0)
df= df[df.topic == '정치']
df['split'] = np.random.randn(df.shape[0], 1)
msk = np.random.rand(len(df)) <= train_percent

train_df = df.iloc[msk, :]
test_df = df.iloc[~msk, :]

print(f'train dataset: {len(train_df)} & test dataset: {len(test_df)}')

train_dataset = ArticleDataset(train_df)
test_dataset = ArticleDataset(test_df)

train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=batch_size)
test_dataloader = DataLoader(test_dataset, batch_size=batch_size)
