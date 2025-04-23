from utils.dataset_utils import TwitterDataScraper
import pandas as pd
from datetime import datetime, timedelta
import requests
import certifi
import urllib3





def create_tweet_dataset(tickers, start_date, end_date, file_path = "Dissertation/datasets/predictions/raw"):
    scraper = TwitterDataScraper(tickers, start_date, end_date=end_date)
    tweet_data = scraper.scrape_tweets()
    
    tweet_df = pd.DataFrame(tweet_data)
    tweet_df.to_csv(file_path)
    print(f"saved to {file_path}")
    
    



if __name__ == "__main__":
    
    import os
    import ssl                                        
    openssl_dir, openssl_cafile = os.path.split(      
    ssl.get_default_verify_paths().openssl_cafile)
    # no content in this folder
    os.listdir(openssl_dir)
    # non existent file
    print(os.path.exists(os.path.join(openssl_dir, openssl_cafile))) #I couldnt get this to work - will be pushed to experimental
    print(f"OpenSSL Dir: {openssl_dir}")
    print(f"OpenSSL CA File: {openssl_cafile}")
    print(os.listdir(openssl_dir))
    
    session = requests.Session()
    session.verify = certifi.where()
    response = session.get('https://x.com/search?...')
    popular_tickers = [
    "AAPL", "TSLA", "NVDA", "AMD", "AMZN",
    "GOOG", "MSFT", "META", "NFLX", "INTC",
    "PLTR", "BA", "GE", "VZ", "ORCL",
    "F", "PYPL", "CRM", "DIS", "UBER"
    ]
    end_date = datetime.today()
    start_date = end_date - timedelta(days=1)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    create_tweet_dataset(popular_tickers, start_date_str, end_date_str)
