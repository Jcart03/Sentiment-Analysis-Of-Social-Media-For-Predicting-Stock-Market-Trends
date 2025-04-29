from error_handler import ErrorHandler
from app_utils.models.prediction_model import PredictionModel
from app_utils.models.sentiment_model import SentimentModel
from datasets import Dataset
import numpy as np
import pandas as pd

class ModelHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelHandler, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self._sentiment_model:SentimentModel = None
        self._prediction_model:PredictionModel = None
        self._error_handler = ErrorHandler()
        self._ticker = None
        self._sentiment_scores = []
        self._confidence_scores = []
        self._result = None
        self._single_result = None
        self._probs = None
        self._prediction = None
        
    
    @property
    def sentiment_scores(self):return self._sentiment_scores
    @property
    def confidence_scores(self):return self._confidence_scores
    @property
    def probs(self):return self._probs
    @property
    def prediction(self):return self._prediction
    @property
    def result(self): return self._result
    @property
    def single_result(self):return self._single_result

    # Connects to loaders/modelLoader for model download during runtime
    def load_model_sentiment(self):
        self.sentiment_model=""

    def load_model_predict(self):
        self.prediction_model=""

    def sentiment_single(self, text: str):
        if not self._sentiment_model:
            self._error_handler.handle_error("Sentiment model is not loaded", 6)
        sentiment_result = self._sentiment_model.analyze(text)
        
        sentiment_score = self._sentiment_model.score(sentiment_result)
        sentiment_label = self._sentiment_model.human_sentiment(sentiment_result)
        
        self._single_result =  {
            'sentiment': sentiment_label,
            'sentiment_score': sentiment_score
        }

    def sentiment_bulk(self, df: Dataset, text_column_name: str):
        if not self._sentiment_model:
            self._error_handler.handle_error("Sentiment model is not loaded", 7)
        sentiment_scores: list = []
        confidence_scores: list = []
        sentiment_label: str = ""
        confidence_label: str = ""

        for _, row in df.iterrows():
            text = row[text_column_name]
            self._sentiment_model.analyze(text)
            sentiment_score = self._sentiment_model.score()
            sentiment_numeric = self._sentiment_model.numeric_sentiment()
            
            confidence_scores.append(sentiment_score)
            sentiment_scores.append(sentiment_numeric)
       
        # Return if no inputs are delivered
        if len(df) == 0:
            self._result= {
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
            return
            
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
        
        # Dictionary mapping for sentiment and confidence labels (cleaner than elif statements)
        sentiment_label = {
            'positive': (avg_sentiment >= 1.3),
            'negative': (avg_sentiment <= 0.7),
            'neutral': (0.7 < avg_sentiment < 1.3),
        }
        
        confidence_label = {
            'high': (avg_confidence >= 0.8),
            'medium': (0.5 <= avg_confidence < 0.8),
            'low': (avg_confidence < 0.5),
        }
        
        # Mapping based on conditions listed above
        sentiment_label = next(label for label, condition in sentiment_label.items() if condition)
        confidence_label = next(label for label, condition in confidence_label.items() if condition)
        
        self._result = {
            "avg_confidence": avg_confidence,
            "confidence_label": confidence_label,
            "avg_sentiment": avg_sentiment,
            "sentiment_label": sentiment_label,
            "positive_pct": positive_pct,
            "neutral_pct": neutral_pct,
            "negative_pct": negative_pct,
            "sentiment_std": sentiment_std,
            "confidence_std": confidence_std,
            "volume": volume
        }

         

    # Prediction logic for movement
    def predict_movement(self):
        if not self._prediction_model:
            self._error_handler.handle_error("Prediction model is not loaded", 8)
        
        avg_confidence = self._result["avg_confidence"]
        avg_sentiment = self._result["avg_sentiment"]
        positive_pct = self._result["positive_pct"]
        neutral_pct = self._result["neutral_pct"]
        negative_pct = self._result["negative_pct"]
        sentiment_std = self._result["sentiment_std"]
        confidence_std = self._result["confidence_std"]
        volume = self._result["volume"]
        
        
        features_data = {
            "avg_confidence" : [avg_confidence],
            "avg_sentiment": [avg_sentiment],
            "positive_pct": [positive_pct],
            "neutral_pct": [neutral_pct],
            "negative_pct":[negative_pct],
            "sentiment_std":[sentiment_std],
            "confidence_std":[confidence_std],
            "volume":[volume]
         }
         
        df = pd.DataFrame(features_data)
        self._prediction_model.predict(df)
        
        
        self.probs = self._prediction_model.probs
        self.prediction = self._prediction_model.result
        
