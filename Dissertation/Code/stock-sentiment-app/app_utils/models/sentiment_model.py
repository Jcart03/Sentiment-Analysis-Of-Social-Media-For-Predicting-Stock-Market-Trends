import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from ..handlers.error_handler import ErrorHandler
import torch.nn.functional as F


class SentimentModel:
    """ 
    class for housing the sentiment model
    
    Attributes:
        model_path(str): path to model
        mapping_path(str): path to sentiment label mappings
        
        Methods:
            analyze(text:str) -> dict: returns sentiment for the text as a dictionary
            
    
    """
    def __init__(self, model_path = "Dissertation/Code/stock-sentiment-app/app_utils/models/Model_files", mapping_path = "Dissertation/Code/stock-sentiment-app/app_utils/config/label_mappings.json"):
        self._error_handler = ErrorHandler()
        self._model_path = model_path
        self._mapping_path = mapping_path
        self._score:float = 0
        self._result:dict = {}
        self._human_sentiment:str = ""
        self._raw_sentiment:int = 0
        
        self.tokenizer = None
        self.model = None
        self.label_mapping = None
        
        
    def load_model(self):
        print("[Sentiment_Model] Loading Sentiment...")
        if not self._model_path or not self._mapping_path:
            self._error_handler.handle_error("SET MAPPING AND MODEL PATH FIRST", 5)
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self._model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self._model_path)
            
            
            with open(self._mapping_path, "r") as f:
                self.label_mapping = json.load(f)
        except Exception as e:
            self._error_handler.handle_error(f"Error loading model or tokenizer...", 400)
            
            
            
    def analyze(self, text: str) -> dict:
        if not self.model or not self.tokenizer:
            self._error_handler.handle_error("Sentiment model loaded incorrectly", 401)
            return {}
        inputs = self.tokenizer(text, return_tensors="pt", truncation = True, padding = "max_length", max_length = 128)
        
        with torch.no_grad():
            outputs = self.model(**inputs).logits

        predicted_index = outputs.argmax(dim=-1).item()
        labels = self.model.config.id2label
        label = labels[predicted_index]
        
        
        self._result =  {
            "label": label,
            "text": self.label_mapping[label]['text'],
            "numeric": self.label_mapping[label]['numeric']  
        }
        self._human_sentiment = self.label_mapping[label]['text']
        self._raw_sentiment = self.label_mapping[label]['numeric']
        
    
    @property
    def model_path(self)->str:return self._model_path
    @model_path.setter
    def model_path(self, model_path:str)->None:self._model_path=model_path
    @property
    def mapping_path(self)->str:return self._mapping_path
    @mapping_path.setter
    def mapping_path(self, mapping_path:str)->None:self._mapping_path=mapping_path
    @property
    def result(self)->dict:return self._result
    @property
    def human_sentiment(self)->str:return self._human_sentiment
    @property
    def score(self)->float:return self._score
    @property
    def raw_sentiment(self)->int:return self._raw_sentiment