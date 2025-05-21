from app_utils.handlers.error_handler import ErrorHandler
from app_utils.models.prediction_model import PredictionModel
from app_utils.models.sentiment_model import SentimentModel
from DTOs.Sentiment import SentimentBatchDTO
from DTOs.Features import FeaturesDTO
from DTOs.Prediction import PredictionDTO
from datasets import Dataset
import numpy as np
import pandas as pd
from app_utils.loaders.modelLoader import ModelLoader as ml

class ModelHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelHandler, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self._sentiment_model = SentimentModel()
        self._prediction_model = PredictionModel()
        self._error_handler = ErrorHandler()
        self._model_loader= ml("Dissertation/Code/stock-sentiment-app/app_utils/config/sentimentmodeluploader-c6108fd9e6d7.json", "Dissertation/Code/stock-sentiment-app/app_utils/models/Model_files")
        self._ticker = None
        self._sentiments: SentimentBatchDTO = None
        self._prediction: PredictionDTO = None
        
    
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
    
    def download_models(self, progress_callback=None):
        self._model_loader.download_and_extract("1bG1Ben0PoMNm7adPMVjzpksB1WUESqO0", progress_callback=progress_callback)
    
    def load_model_sentiment(self):
        print("[Model_Handler] Loading Sentiment")
        self._sentiment_model.load_model()
    
    def load_model_predict(self):
        print("[Model_Handler] Loading Predict")
        self._prediction_model.load_model()

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
        sentiments = SentimentBatchDTO()
        for _, row in df.iterrows():
            text = row[text_column_name]
            self._sentiment_model.analyze(text)
            result = self._sentiment_model._result
            sentiments.add_sentiment(result)
            
       
        # Return if no inputs are delivered
        if len(df) == 0:
            ErrorHandler().handle_error("No Comments Given To Sentiment Model...", 45)
            return
        
        
        self._sentiments = sentiments
        
      
        
        

         

    # Prediction logic for movement
    def predict_movement(self, features: FeaturesDTO):
        if not self._prediction_model:
            self._error_handler.handle_error("Prediction model is not loaded", 8)
            return
        sentiments = features.sentiments
        stock = features.stock
        distro = sentiments.sentiment_distribution()
        avg_sentiment = sentiments.average_sentiment()
        positive_pct = distro["positive_pct"]
        neutral_pct = distro["neutral_pct"]
        negative_pct = distro["negative_pct"]
        sentiment_std = sentiments.sentiment_standard_deviation()
        volume = sentiments.len()
        close_price = stock.close_price
        close_price = float(close_price.iloc[0])
        
        features_vector = {
            "avg_sentiment": [avg_sentiment],
            "positive_pct": [positive_pct],
            "neutral_pct": [neutral_pct],
            "negative_pct":[negative_pct],
            "sentiment_std":[sentiment_std],
            "volume":[volume],
            "price": [close_price]
         }
         
        df = pd.DataFrame(features_vector)
        print(df)
        self._prediction_model.predict(df)
        
        
        self._probs = self._prediction_model.result.probabilities
        self._prediction = self._prediction_model.result.readable_value
        print(self._probs)
        print(self._prediction)
        
