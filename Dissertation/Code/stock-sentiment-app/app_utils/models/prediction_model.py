from xml.sax.handler import property_declaration_handler
from handlers.error_handler import ErrorHandler
import os
import xgboost as xgb
import pandas as pd
class PredictionModel:
    
    def __init__(self, model_path:str):
        self._error_handler = ErrorHandler()
        self._model_path = ""
        self._features = [
            "avg_confidence",
            "avg_sentiment",
            "positive_pct",
            "neutral_pct",
            "negative_pct",
            "sentiment_std",
            "confidence_std",
            "volume"
        ]
        self._probs=None
        self._result=None
    def load_model(self):
        if not os.path.exists(self._model_path):
            self._error_handler.handle_error("Failed to Load Prediction model (File Not Found)", 2)
            return
        
        self.model = xgb.XGBClassifier()
        try:
            self.model.load_model(self._model_path)
        except Exception:
            self._error_handler.handle_error("Failed to Load Prediction model (File Not Found)", 4)
            return
            
        
    def predict(self, df: pd.DataFrame):
        try: 
            target = df[self.features]
            prediction = self.model.predict(target)
            probs = self.model.predict_proba(target)
        except Exception:
            self._error_handler.handle_error("Prediction Failed (have you checked the dataset?)", 3)
            return
        self._result = prediction
        self._probs = probs
        
    @property
    def probs(self):return self._probs
    @property
    def result(self):return self._result
    @property
    def features(self):return self._features
    @features.setter
    def features(self, features:list)->list: self._features=features
    @property
    def model_path(self):return self._model_path
    @model_path.setter
    def model_path(self, model_path:str)->None:self._model_path=model_path