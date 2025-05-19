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
        
        
        
    def get_price_data(self, ticker:str, date: str = None)-> StockDTO:
        time.sleep(random.randint(10, 15))
        print("<<<fetching>>>")
        if not date:
            query_date = datetime.now()
        else:
            query_date = datetime.strptime(date, "%Y-%m-%d")
        
        
        print(query_date)
        
        print("<<<fetching2>>>")
        print(ticker)
        
       
        try: 
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history("7d")
            
            query_date = query_date.astimezone(hist.index.tz)
            valid_dates = hist.index[hist.index <= query_date] 
            if valid_dates.empty:
                ErrorHandler.handle_error(f"No valid trading days found before {query_date.date()} for {ticker}", 1 )
                return
           
            last_trading_day = valid_dates[-1]
            print(f"last day for {ticker}: {last_trading_day.date()}")
            start_date = last_trading_day.date()
            end_date = last_trading_day.date() + timedelta(days=1)
            
            
            hist = yf.download(tickers=ticker, start=start_date, end=end_date, interval=self.default_interval, progress=True)
            print(hist)
            if hist.empty:
                ErrorHandler().handle_error(f"No data found for: {ticker} between {end_date} and {start_date}", 1)
                return
            
        
        except Exception as e:
            ErrorHandler().handle_error(f"Failed to fetch data for {ticker}", 2)
            print(e)
            traceback.print_stack()
            return
    
        
        print("<<<fetch finished>>>")
       
        stock_data = hist.iloc[0]
        stock_dto = StockDTO(ticker=ticker, date=end_date, 
                            open_price=stock_data['Open'], 
                            high_price=stock_data['High'], 
                            low_price=stock_data['Low'], 
                            close_price=stock_data['Close'],
                            volume=stock_data['Volume'])
        
        
        
        return stock_dto
    
        