import pandas as pd
import os
from datasets import Dataset



def map(raw_path, delimiter, label, map, clean_path):
    ds = pd.read_csv(raw_path, delimiter = delimiter) #delimiter is dependant on csv file
    ds[label] = ds[label].map(map)
    ds[label] = ds[label].fillna(0)
    ds[label] = ds[label].astype(int)
    ds.to_csv(os.path.join(clean_path, f"Formatted_{os.path.basename(raw_path)}"), index=False)
    print(ds.head())
    
    
    
    
map("Dissertation/datasets/berTweet/raw/scored_tweets_total.csv", ',', 'Sentiment', map={-1:0, 0:1, 1:2}, clean_path='Dissertation/datasets/berTweet/clean')
map("Dissertation/datasets/berTweet/raw/tweets_labelled_09042020_16072020.csv", ';', 'sentiment', map={'negative':0, 'neutral':1, 'positive':2}, clean_path='Dissertation/datasets/berTweet/clean')
map("Dissertation/datasets/berTweet/raw/Twitter_Data.csv", ',', 'category', map={-1:0, 0:1, 1:2}, clean_path='Dissertation/datasets/berTweet/clean')