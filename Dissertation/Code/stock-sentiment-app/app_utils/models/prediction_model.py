
from app_utils.handlers.error_handler import ErrorHandler
from DTOs.Prediction import PredictionDTO
import os
import xgboost as xgb
import pandas as pd
class PredictionModel:
    
    def __init__(self, model_path = "Dissertation/Code/stock-sentiment-app/app_utils/models/Model_files/prediction_model.xgb"):
        self._model_path = model_path
        self._features = [
            "price",
            "volume",
            "negative_pct",
            "neutral_pct",
            "positive_pct",
            "sentiment_std",
            "avg_sentiment"
        ]
        
        
        self._result:PredictionDTO = None
        
    def load_model(self):
        print("loading model")
        if not os.path.exists(self._model_path):
            ErrorHandler().handle_error("Failed to Load Prediction model (File Not Found)", 2)
            return
        
        self.model = xgb.XGBClassifier()
        try:
            self.model.load_model(self._model_path)
        except Exception:
            ErrorHandler().handle_error("Failed to Load Prediction model (File Not Found)", 4)
            
        
    def predict(self, df: pd.DataFrame):
        try: 
            target = df[self.features]
            prediction = self.model.predict(target)
            probs = self.model.predict_proba(target)
        except Exception as e:
            print(e)
            ErrorHandler().handle_error("Prediction Failed (have you checked the dataset?)", 3)
            return
        
        predicted_value = int(prediction[0])
        probabilities = probs[0].tolist()
        
        self._result = PredictionDTO.from_prediction(predicted_value, probabilities)
        
        
    @property
    def result(self):return self._result
    @property
    def features(self):return self._features
    @features.setter
    def features(self, features:list)->None: self._features=features
    @property
    def model_path(self):return self._model_path
    @model_path.setter
    def model_path(self, model_path:str)->None:self._model_path=model_path