from dataclasses import dataclass
from DTOs.Sentiment import SentimentBatchDTO
from DTOs.Stock import StockDTO

@dataclass
class FeaturesDTO:
    sentiments: SentimentBatchDTO
    stock: StockDTO
    
    
    def construct_results(self) -> dict:
        sentiments = self.sentiments
        stock = self.stock
        distro = sentiments.sentiment_distribution()
        avg_sentiment = sentiments.average_sentiment()
        if avg_sentiment > 1.3:
            sentiment_label = "Positive"
        elif avg_sentiment < 0.7:
            sentiment_label = "Negative"
        else: 
            sentiment_label = "Neutral"
        return {
            "avg_sentiment": avg_sentiment,
            "sentiment_std": sentiments.sentiment_standard_deviation(),
            "volume": sentiments.len(),
            "positive_pct": distro["positive_pct"],
            "neutral_pct": distro["neutral_pct"],
            "negative_pct": distro["negative_pct"],
            "ticker": stock.ticker,
            "close_price": float(stock.close_price.iloc[0]),
            "sentiment_label": sentiment_label
        }