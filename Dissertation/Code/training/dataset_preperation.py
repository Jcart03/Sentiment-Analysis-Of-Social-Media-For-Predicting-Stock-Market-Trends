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
    
    def aggregate(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column], errors="coerce", utc=True)
        
        df['date'] = df[self.timestamp_column].dt.date
        
        def get_correct_symbol(ticker):
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
        
            if ticker in symbol_mapping:
                return symbol_mapping[ticker]
            else:
                return ticker
        
        df['ticker_symbol'] = df[self.ticker_column].apply(lambda x: re.findall(r'\$(\w+)', str(x)))
        ## will try grouping by hour first to see how that effects the dataset
        df['ticker_symbol'] = df['ticker_symbol'].apply(lambda x: [get_correct_symbol(t) for t in x])
        df = df.explode('ticker_symbol')
        df = df[df['ticker_symbol'].notna() & (df['ticker_symbol'] != '')]
        
        grouped = df.groupby(['ticker_symbol', 'date'])
        
       
        
        
        aggregated = grouped.agg(
            volume = (self.timestamp_column, lambda x: x.count()),
            negative_pct =(self.sentiment_column, lambda x:(x == 0).mean()),
            neutral_pct = (self.sentiment_column, lambda x:(x==1).mean()),
            positive_pct = (self.sentiment_column,lambda x: (x==2).mean()),
            sentiment_std = (self.sentiment_column, lambda x: x.std()),
            sentiment_avg = (self.sentiment_column, lambda x: x.mean())
            ).reset_index()
        
        aggregated = aggregated[aggregated['volume'] > 1]
        aggregated = aggregated[aggregated['ticker_symbol'] != '0X0']
        
        
        
        
        return aggregated
    
    
    def add_price_data(self, df: pd.DataFrame, timestamp_column: str):
        
        
        
        def get_price(ticker, date):
            time.sleep(random.randint(3, 7))
            try: 
                start_date = date
                end_date = date + pd.Timedelta(days= 2)
                price_data = yf.download(ticker, start=start_date, end=end_date)
                
                if not price_data.empty:
                    price_today = price_data['Close'].iloc[0]
                    price_tomorrow = price_data['Close'].iloc[1]
                    print(price_today, price_tomorrow)
                    return price_tomorrow - price_today
                else:
                    return None
            except Exception:
                print(f"Error fetching data for {ticker}")
                return None
           
        df['price_diff'] = df.apply(lambda row: get_price(row['ticker_symbol'], row[timestamp_column]), axis = 1)
        
        return df
if __name__ == "__main__":
    """
    path1 = "Dissertation/datasets/predictions/raw/111111Aggregated_Formatted_financial_tweets.csv"
    path2 = "Dissertation\datasets\predictions\clean\Aggregated_Formatted_financial_tweets.csv"
    original_dataset = pd.read_csv(path1)
    new_dataset = pd.read_csv(path2)
    
    final_dataset = new_dataset.merge(
        original_dataset[['ticker_symbol', 'date', 'price_diff']],
        on=['ticker_symbol', 'date'],
        how='left')
    """
   
    """ 
    path = "Dissertation/datasets/predictions/clean/traindataDONE.csv"
    final_dataset = pd.read_csv(path)
    final_dataset  = final_dataset[final_dataset['price_diff'].notna()]
    final_dataset['price_diff'] = final_dataset['price_diff'].apply(lambda x: re.findall(r'-?\d+\.\d+', str(x))[0] if x is not None else None)
    final_dataset.to_csv("Dissertation/datasets/predictions/clean/traindataDONE.csv", index = False)
    """
    path = "Dissertation/datasets/predictions/clean/traindataDONE.csv"
    final_dataset = pd.read_csv(path)
    
    percentage = 2
    ticker_diff_avg = final_dataset.groupby('ticker_symbol')['price_diff'].mean().abs()
    final_dataset['threshold'] = final_dataset['ticker_symbol'].map(ticker_diff_avg) * percentage
    
    final_dataset['label'] = final_dataset.apply(
        lambda row: 1 if abs(row['price_diff']) <= row['threshold'] else (2 if row['price_diff'] > 0  else 0),
        axis=1
    )
    final_dataset.to_csv("Dissertation/datasets/predictions/clean/traindataLabelled.csv", index = False)
    
    
    """
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
    
    
   
        output_path = "Dissertation/datasets/predictions/clean"
        aggregated_file_path = os.path.join(output_path, f"Aggregated_{os.path.basename(dataset_path)}")
        aggregated_df.to_csv(aggregated_file_path, index=False)
        print(aggregated_df.head())
    
    """
    