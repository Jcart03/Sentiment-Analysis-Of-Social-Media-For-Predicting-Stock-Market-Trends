#### VERY MESSY, quick script and fix to train my prediction model until i can get the scraping sorted

import os
import pandas as pd
from datetime import datetime, timedelta


class TweetPreProcessor:
    def __init__(self, text_column, ticker_column, timestamp_column, sentiment_column, is_ticker_list: bool = False):
        self.text_column = text_column
        self.ticker_column = ticker_column
        self.time_stamp_column = timestamp_column
        self.sentiment_column = sentiment_column
        self.is_ticker_list = is_ticker_list

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[[self.text_column, self.ticker_column, self.time_stamp_column, self.sentiment_column]]
        if self.is_ticker_list:
            df = df.explode(self.ticker_column).dropna(subset=[self.ticker_column])
            
            
        return df
    
## Groups tweet on a by date basis or by hour basis haven't decided yet (writing this before doing it)
class TweetAggregator:
    def __init__(self, ticker_column, sentiment_column, timestamp_column):
        self.ticker_column = ticker_column
        self.sentiment_column = sentiment_column
        self.timestamp_column = timestamp_column
    
    def aggregate(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column], errors="coerce", utc=True)
        df['date'] = df[self.timestamp_column].dt.date
        df['hour'] = df[self.timestamp_column].dt.floor('H')
        ## will try grouping by hour first to see how that effects the dataset
        grouped = df.groupby([self.ticker_column, 'hour'])
        
        aggregated = grouped.agg(
            volume = (self.timestamp_column, lambda x: x.count()),
            average_sentiment = (self.sentiment_column, lambda x: x.mean()),
            start_time=(self.timestamp_column, lambda x: x.min()),
            end_time=(self.timestamp_column, lambda x: x.max())
            ).reset_index()
        
        return aggregated
    
    


if __name__ == "__main__":
    dataset_path = "Dissertation/datasets/predictions/raw/Formatted_financial_tweets.csv"
    df = pd.read_csv(dataset_path)
    
    preprocessor = TweetPreProcessor(
        text_column="description",
        ticker_column="financial_info",
        sentiment_column="labels",
        timestamp_column="timestamp",
        is_ticker_list=True
        )
    
    processed_df = preprocessor.preprocess(df)
    
    aggregator = TweetAggregator(
        ticker_column="financial_info",
        sentiment_column="labels",
        timestamp_column="timestamp"
    )
    
    aggregated_df = aggregator.aggregate(processed_df)
    print(aggregated_df.head())
    
    output_path = "Dissertation/datasets/predictions/clean"
    aggregated_file_path = os.path.join(output_path, f"Aggregated_{os.path.basename(dataset_path)}")
    aggregated_df.to_csv(aggregated_file_path, index=False)
    print(aggregated_df.head())
    
    
    