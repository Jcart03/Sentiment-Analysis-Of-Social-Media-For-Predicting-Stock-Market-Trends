import yfinance as yf
from app_utils.handlers.error_handler import ErrorHandler
from DTOs.Stock import StockDTO
import datetime
class FinanceAPI:
    def __init__(self, default_interval: str = "1d" ):
        self.default_interval = default_interval
        self.error_handler =ErrorHandler()
        
        
    def get_price_data(self, ticker:str, date: str = None)-> StockDTO:
        if not date:
            date = datetime.now()
        
        
        stock = yf.Ticker(ticker)
        
        
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - datetime.timedelta(days=1)
        hist = stock.history(start=start_date.strftime("%Y-%m-%d"),
                            end=end_date.strftime("%Y-%m-%d",
                            interval=self.default_interval))
        
        if hist.empty:
            self.error_handler.handle_error(f"No data found for: {ticker} between {end_date} and {start_date}", 1)
            return
        stock_data = hist.iloc[0]
        stock_dto = StockDTO(ticker=ticker, date=end_date.date(), 
                             open_price=stock_data['Open'], 
                             high_price=stock_data['High'], 
                             low_price=stock_data['Low'], 
                             close_price=stock_data['Close'],
                             volume=stock_data['Volume'])
        
        
        return stock_dto
    
        