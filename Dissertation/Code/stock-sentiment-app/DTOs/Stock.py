from dataclasses import dataclass, field
from typing import List

@dataclass
class StockDTO:
    ticker: str
    open_price: float
    close_price: float
    high: float
    low: float
    volume: int
    date: str

def format_stock_data(self)->str:
    return f"Stock: {self.ticker}, Open: {self.open_price}, Close: {self.close_price}, High: {self.high}, Low, {self.low}, Volume:{self.volume}, Date{self.date}"

@dataclass
class StockBatchDTO:
    sotcks: List[StockDTO] = field(default_factory=list)
    
    def add_stock(self, stock: StockDTO):
        self.stocks.append(stock)
        
    def get_stocks(self)-> List[StockDTO]:
        return self.stocks
    
    def format_all_stocks(self)-> str:
        return "\n".join([stock.format_stock_data() for stock in self.stocks])