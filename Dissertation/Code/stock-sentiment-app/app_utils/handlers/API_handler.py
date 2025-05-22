from DTOs.Comment import CommentBatchDTO, CommentDTO
from DTOs.Stock import StockDTO
from DTOs.Sentiment import SentimentBatchDTO


from app_utils.handlers.error_handler import ErrorHandler
from app_utils.api_housing.scraper_api import ScraperAPI
from app_utils.api_housing.finance_api import FinanceAPI
import json
from datetime import datetime, timezone
class APIHandler:
    def __init__(self):
        self._scraper_api = ScraperAPI( "<REDACTED>", 	"<REDACTED>",  "<REDACTED>")
        self._finance_api = FinanceAPI()
        self._comments: CommentBatchDTO 
        self._stocks:StockDTO
        
        
        
    def fetch_comments(self, ticker:str):
        print("fetching Comments")
        with open("Dissertation/Code/stock-sentiment-app/app_utils/config/company_names.json", "r") as f:
           company_names_cfg =  json.load(f)
           print(company_names_cfg)
        with open("Dissertation/Code/stock-sentiment-app/app_utils/config/subreddits.json", "r") as q:
            subreddit_names_cfg = json.load(q)
            print(subreddit_names_cfg)
        company_names = company_names_cfg[ticker]['company_names']
        subreddits = subreddit_names_cfg['subreddits']
        
        print(f"Fetching comments for: {subreddits}, {company_names}, {ticker}")
        try: 
            self._scraper_api.get_recent_comments(subreddits, company_names, ticker)
        except Exception: 
            ErrorHandler().handle_error("failed to fetch reddit data. try again......")
        
        
        print("Comments Fetched!")
        self._comments =  self._scraper_api.filtered_comments
        
    def get_finance_data(self, ticker, date):
        self._stocks = self._finance_api.get_price_data(ticker, date)
    

       
       
    