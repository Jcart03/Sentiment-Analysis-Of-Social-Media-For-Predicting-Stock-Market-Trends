from models.sentiment_model import SentimentModel
from models.prediction_model import PredictionModel
from datasets import Dataset
import numpy as np

def load_model_sentiment():
    return "Sentiment Model Loaded"

def load_model_predict():
    return "Prediction Model Loaded"

def sentiment_single(text: str, sentiment_model: SentimentModel):
    
    load_model_sentiment()
    sentiment_result = sentiment_model.analyze(text)
    
    sentiment_score = sentiment_model.score(sentiment_result)
    
    sentiment_label = sentiment_model.human_sentiment(sentiment_result)
    
    return {
        'sentiment': sentiment_label,
        'sentiment_score': sentiment_score
    }
    
def sentiment_bulk(df: Dataset, sentiment_model: SentimentModel, text_column_name: str) -> dict:
    load_model_sentiment()
    result: dict = {}
    sentiment_scores: list = []
    confidence_scores: list = []
    sentiment_label: str = ""
    confidence_label: str = ""
    
    for _, row, in df.iterrows():
        text = row[text_column_name]
        
        sentiment_result = sentiment_model.analyze(text)
        
        sentiment_score = sentiment_model.score(sentiment_result)
        sentiment_numeric = sentiment_model.numeric_sentiment(sentiment_result)
        
        confidence_scores.append(sentiment_score)
        sentiment_scores.append(sentiment_numeric)
   
   #### return if no inputs delivered
    if len(df) == 0:
        return {
            "avg_confidence": 0.0,
            "confidence_label": "low",
            "avg_sentiment": "1.0",
            "sentiment_label": "neutral",
            "positive_pct": 0.0,
            "neutral_pct": 0.0,
            "negative_pct": 0.0,
            "sentiment_std": 0.0,
            "confidence_std": 0.0,
            "tweet_volume": 0
        }
        
    sentiment_scores_np = np.array(sentiment_scores)
    confidence_scores_np = np.array(confidence_scores)
    
    avg_confidence: float = confidence_scores_np.mean()
    avg_sentiment: float = sentiment_scores_np.mean()
    
    sentiment_std = sentiment_scores_np.std()
    confidence_std = confidence_scores_np.std()
    
    volume = len(sentiment_scores)
    positive_pct = sentiment_scores.count(2) / volume
    neutral_pct = sentiment_scores.count(1) / volume
    negative_pct = sentiment_scores.count(0) / volume
    
    
    ### python needs a switch case statement I hate elif if statements - edit changed to dictionary mapping so it looks nicer
    
    
    sentiment_label = {
        'positive': (avg_sentiment >= 1.3),
        'negative': (avg_sentiment <=0.7),
        'neutral': (0.7> avg_sentiment < 1.3),
    }
    
    confidence_label = {
        'high': (avg_confidence >= 0.8),
        'medium': (0.5<= avg_confidence < 0.8),
        'low': (avg_confidence < 0.5),
    }
   
   
   ##dictionary ,mapping based on conditions listed above (looks cleaner than an elif statement)
    sentiment_label = next(label for label, condition in sentiment_label.items() if condition)
    confidence_label = next(label for label, condition in confidence_label.items() if condition)
    
    result = {
        "avg_confidence": avg_confidence,
        "confidence_label": confidence_label,
        "avg_sentiment": avg_sentiment,
        "sentiment_label": sentiment_label,
        "positive_pct": positive_pct,
        "neutral_pct": neutral_pct,
        "negative_pct": negative_pct,
        "sentiment_std": sentiment_std,
        "confidence_std": confidence_std,
        "tweet_volume": volume
    }
    return result


## essentially pseudo code for the missing piece that is the predicitons
def predict_movement(results: dict, predict_model : PredictionModel, ticker: str):
    load_model_predict()
    avg_sentiment = results["avg_sentiment"]
    avg_confidence = results["avg_confidence"]
    positive_pct = results["positive_pct"]
    neutral_pct = results["neutral_pct"]
    negative_pct = results["negative_pct"]
    
    prediction = predict_model.predict(avg_sentiment, avg_confidence, positive_pct, neutral_pct, negative_pct, ticker)
    
    return {
        "predicted movement": prediction
    }