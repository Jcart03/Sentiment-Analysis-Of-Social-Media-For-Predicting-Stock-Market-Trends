from DTOs.Comment import CommentBatchDTO, CommentDTO
from DTOs.Stock import StockDTO



from api_housing.scraper_api import ScraperAPI
from api_housing.finance_api import FinanceAPI
import json
from datetime import datetime, timezone
class APIHandler:
    def __init__(self):
        self._scraper_api = ScraperAPI()
        self._finance_api = FinanceAPI()
        
        
    def fetch_comments(self, subreddit:str, ticker:str):
        with open("Dissertation/Code/stock-sentiment-app/app_utils/config/company_names.json", "r") as f:
           company_names_cfg =  json.load(f)
        
        company_names = company_names_cfg[ticker]
        self._scraper_api.get_recent_comments(subreddit, ticker, company_names)
        self._comments = self._scraper_api.filtered_comments()
        
        
        
    def get_finance_data(self, ):
        self._finance_api.get_price_data(ticker, date)
    