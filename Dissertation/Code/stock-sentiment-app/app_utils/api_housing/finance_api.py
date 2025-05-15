import yfinance as yf
from app_utils.handlers.error_handler import ErrorHandler
from DTOs.Stock import StockDTO
from datetime import datetime, timedelta
import time
import random
import traceback

class FinanceAPI:
    def __init__(self, default_interval: str = "1d" ):
        self.default_interval = default_interval
        self.error_handler =ErrorHandler()
        
        
    def get_price_data(self, ticker:str, date: str = None)-> StockDTO:
        time.sleep(random.randint(10, 15))
        print("<<<fetching>>>")
        if not date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d")
        
        
        print(end_date)
        
        print("<<<fetching2>>>")
        print(ticker)
        
        start_date = end_date - timedelta(days=1)
        print(start_date)
        try: 
           
            hist = yf.download(tickers=ticker, start=start_date, end=end_date, interval=self.default_interval, progress=True)
            print(hist)
            if hist.empty:
                self.error_handler.handle_error(f"No data found for: {ticker} between {end_date} and {start_date}", 1)
                return
            
        
        except Exception as e:
            self.error_handler.handle_error(f"Failed to fetch data for {ticker}", 2)
            print(e)
            traceback.print_stack()
    
        
        print("<<<fetch finished>>>")
       
        stock_data = hist.iloc[0]
        stock_dto = StockDTO(ticker=ticker, date=end_date.date(), 
                            open_price=stock_data['Open'], 
                            high_price=stock_data['High'], 
                            low_price=stock_data['Low'], 
                            close_price=stock_data['Close'],
                            volume=stock_data['Volume'])
        
        
        
        return stock_dto
    
        