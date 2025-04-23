import snscrape.modules.twitter as snstwitter
import yfinance as yf
import pandas as pd
import datetime
import datasets as Dataset
import numpy as np
import ssl
import time

ssl._create_default_https_context = ssl._create_unverified_context
class TwitterDataScraper:
    def __init__(self, tickers, start_date, end_date):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        
    def scrape_tweets(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        tweet_data = []
        for ticker in self.tickers:
            query = f"#{ticker} since:{self.start_date} until:{self.end_date}"
            print(f"Scraping tweets for {ticker} from {self.start_date} to {self.end_date}")
            retries = 5
            while retries > 0:
                try:
                    for tweet in snstwitter.TwitterSearchScraper(query).get_items():
                        print(ticker)
                        tweet_data.append({
                            'ticker': ticker,
                            'date': tweet.date,
                            'content': tweet.content,
                            'sentiment': None
                            })
                    break
                except Exception:
                    print(f"Error {retries} attempts left.")
                    retries -= 1
                    time.sleep(5)
            if retries == 0:
                print("Failed to scrape for {ticker}")
        return tweet_data
    
class StockPriceData:
    def __init__(self, tickers, start_date, end_date):
        self.tickers = tickers
        self.start_date =  start_date
        self.end_date = end_date
        
    def fetch_stock_prices(self):
        stock_data = {}
        for ticker in self.tickers:
            stock = yf.download(ticker, start=self.start_date, end=self.end_date, interval = "1h")
            stock_data[ticker] = stock[['Close']]