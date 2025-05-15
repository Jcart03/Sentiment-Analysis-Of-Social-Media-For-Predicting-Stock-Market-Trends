#### VERY MESSY, quick script and fix to train my prediction model until i can get the scraping sorted
import re
import os
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import time
import random


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
    
    def _get_correct_symbol(self, ticker):
            ######### found a list of some of the stock tickers that require a -USD suffix on yahoo finance
            symbol_mapping = {
                'BTC': 'BTC-USD',
                'ETH': 'ETH-USD',
                'AVAX': 'AVAX-USD',
                'ADA': 'ADA-USD',
                'SOL': 'SOL-USD',
                'DOGE': 'DOGE-USD',
                'XRP': 'XRP-USD',
                'LTC': 'LTC-USD',
                'BCH': 'BCH-USD',
                'MATIC': 'MATIC-USD',
                'DOT': 'DOT-USD',
                'UNI': 'UNI-USD',
                'TRX': 'TRX-USD',
                'LINK': 'LINK-USD',
                'FIL': 'FIL-USD',
                'VET': 'VET-USD',
                'STX': 'STX-USD',
                'EOS': 'EOS-USD',
                'SHIB': 'SHIB-USD',
                'XLM': 'XLM-USD',
                'FTM': 'FTM-USD',
                'ZEC': 'ZEC-USD',
                'ICP': 'ICP-USD',
                'CRO': 'CRO-USD',
                'GRT': 'GRT-USD',
                'YFI': 'YFI-USD',
                'BTT': 'BTT-USD',
                'MKR': 'MKR-USD',
                'AAVE': 'AAVE-USD',
                'SUSHI': 'SUSHI-USD',
                'COMP': 'COMP-USD',
                'BAL': 'BAL-USD',
                'SNX': 'SNX-USD',
                'MASK': 'MASK-USD',
                'NDX': '^NDX'
            }
            return symbol_mapping.get(ticker, ticker)
                
    
    def aggregate(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column], errors="coerce", utc=True)
        
        df['date'] = df[self.timestamp_column].dt.date
        
        df['ticker_symbol'] = df[self.ticker_column].apply(lambda x: re.findall(r'\$(\w+)', str(x)))
        ## will try grouping by hour first to see how that effects the dataset
        df['ticker_symbol'] = df['ticker_symbol'].apply(lambda x: [self._get_correct_symbol(t) for t in x])
        df = df.explode('ticker_symbol')
        df = df[df['ticker_symbol'].notna() & (df['ticker_symbol'] != '')]
        
        grouped = df.groupby(['ticker_symbol', 'date'])
        
       
        
        
        aggregated = grouped.agg(
            volume = ('timestamp', 'count'),
            negative_pct =(self.sentiment_column, lambda x:(x == 0).mean()),
            neutral_pct = (self.sentiment_column, lambda x:(x==1).mean()),
            positive_pct = (self.sentiment_column,lambda x: (x==2).mean()),
            sentiment_std = (self.sentiment_column,lambda x: x.std()),
            sentiment_avg = (self.sentiment_column, lambda x: x.mean())
            ).reset_index()
        
        return aggregated[(aggregated['volume'] > 1) & (aggregated['ticker_symbol'] != '0X0')]

        
        
        

    
    
    def get_price_data(self, ticker, date):
        time.sleep(random.randint(3, 7))
        
        try:
            start_date = pd.to_datetime(date)
            end_date = start_date + pd.Timedelta(days=2)
            price_data = yf.download(ticker, start=start_date, end=end_date)
            return price_data[['Close']].reset_index()
        except Exception:
            print(f"Error fetching data for {ticker}") 
                
            return pd.DataFrame()
        
        
    def calculate_price_features(self, df: pd.DataFrame)-> pd.DataFrame:
        def compute_features(row):
            price_data = self.get_price_data(row['ticker_symbol'], row['date'])
            if len(price_data) >= 2:
                prev_close = price_data['Close'].iloc[0]
                next_close = price_data['Close'].iloc[1]
                price_change_pct_1d = ((next_close - prev_close) / prev_close) * 100
                return pd.Series([prev_close, price_change_pct_1d])
            return pd.Series([None, None])
        df[['prev_close', 'price_change_pct_1d']] = df.apply(compute_features, axis=1)
        return df
    
    
    def run_pipeline(self, raw_path:str, output_path:str, threshold:float=0.75):
        df = pd.read_csv(raw_path)
        
        preprocessor = TweetPreProcessor(
            text_column="description",
            ticker_column="financial_info",
            sentiment_column="labels",
            timestamp_column="timestamp",
            is_ticker_list=True
        )
        processed_df = preprocessor.preprocess(df)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        processed_df.to_csv(output_path, index=False)
        aggregated_df = self.aggregate(processed_df)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        aggregated_df.to_csv(output_path, index=False)
        aggregated_df = self.calculate_price_features(aggregated_df)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        aggregated_df.to_csv(output_path, index=False)
        aggregated_df["prev_close"] = aggregated_df["prev_close"].apply(self.extract_val)
        aggregated_df["price_change_pct_1d"] = aggregated_df["price_change_pct_1d"].apply(self.extract_val)
        labelled_df = self.add_label_column(aggregated_df, threshold = threshold)
        labelled_df.to_csv(output_path, index=False)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        labelled_df.to_csv(output_path, index=False)
def label_price_change( price_change_pct_1d, threshold: float= 2.0):
        if pd.notnull(price_change_pct_1d):
            if abs(price_change_pct_1d) <= threshold:
                return 1
            elif price_change_pct_1d > 0:
                return 2
            else:
                return 0
        return None
def add_label_column(df: pd.DataFrame, threshold: float=0.75)-> pd.DataFrame:
    df['label'] = df['price_change_pct_1d'].apply(label_price_change, threshold=threshold)
    return df
    
    
def extract_val(val):
    if pd.isna(val):
        return None
    match = re.search(r"(-?\d+\.?\d*)", str(val))
    return float(match.group(1)) if match else None
    
   
        
        
        
    
if __name__ == "__main__":
    """raw_path = "Dissertation/datasets/predictions/raw/Formatted_financial_tweets.csv"
    output_path = "Dissertation/datasets/predictions/clean/prediction_dataset.csv"
    
    aggregator = TweetAggregator(
        ticker_column="financial_info",
        sentiment_column="labels",
        timestamp_column="timestamp"
    )
    aggregator.run_pipeline(raw_path, output_path)
    """
    output_path = "Dissertation/datasets/predictions/raw/prediction_datasetsafe.csv"
    df = pd.read_csv(output_path)
    df["prev_close"] = df["prev_close"].apply(extract_val)
    df["price_change_pct_1d"] = df["price_change_pct_1d"].apply(extract_val)
    final_df = add_label_column(df, 0.75)
    final_df = final_df.dropna()
    final_df = final_df.drop(columns = ["price_change_pct_1d", "date", "ticker_symbol"])
    final_df = final_df[final_df["volume"] >= 4]
    final_df.to_csv("prediction_dataset.csv", index=False)
    