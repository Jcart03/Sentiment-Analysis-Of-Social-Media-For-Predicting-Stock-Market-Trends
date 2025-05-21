from dataclasses import dataclass, field
from typing import List
import statistics


@dataclass
class SentimentDTO:
    sentiment_numeric: int
    sentiment_label: str
    
    
    def format_sentiment(self)->str:
        return f"Sentiment: {self.sentiment_label}, Numeric: {self.sentiment_numeric}"
    
@dataclass   
class SentimentBatchDTO:
    sentiments: List[SentimentDTO] = field(default_factory=list)
    
    
    def add_sentiment(self, sentiment: SentimentDTO):
        self.sentiments.append(sentiment)
    
    def average_sentiment(self) -> float:
        if not self.sentiments:
            return 0.0
        return sum([sentiment.sentiment_numeric for sentiment in self.sentiments]) / len(self.sentiments)
    
    def sentiment_distribution(self)-> dict:
        total_sentiments = len(self.sentiments)
        if total_sentiments == 0:
            return {"positive_pct": 0.0, "negative_pct": 0.0, "neutral_pct": 0.0}
        
        distribution = {"positive_pct": 0.0, "neutral_pct": 0.0, "negative_pct": 0.0}
        for sentiment in self.sentiments:
            if sentiment.sentiment_label == "positive":
                distribution["positive_pct"]+= 1
            elif sentiment.sentiment_label == "neutral":
                distribution["neutral_pct"]+=1
            elif sentiment.sentiment_label == "negative": 
                distribution["negative_pct"]+=1
        distribution_percentage = {label: (count / total_sentiments) for label, count in distribution.items() }
        
        return distribution_percentage
    
    def sentiment_standard_deviation(self)-> float:
        sentiment_values = [sentiment.sentiment_numeric for sentiment in self.sentiments]
        if len(sentiment_values) > 1:
            return statistics.stdev(sentiment_values)
        return 0.0
    
    def len(self) -> int:
        return len(self.sentiments)
    