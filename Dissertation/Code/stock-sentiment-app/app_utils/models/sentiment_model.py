import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from handlers.error_handler import ErrorHandler


class SentimentModel:
    """ 
    class for housing the sentiment model
    
    Attributes:
        model_path(str): path to model
        mapping_path(str): path to sentiment label mappings
        
        Methods:
            analyze(text:str) -> dict: returns sentiment for the text as a dictionary
            
    
    """
    def __init__(self, model_path:str, mapping_path:str):
        self._error_handler = ErrorHandler()
        self._model_path = model_path
        self._mapping_path = mapping_path
        self._score:float = 0
        self._result:dict = {}
        self._human_sentiment:str = ""
        self._raw_sentiment:int = 0
        
        if model_path and mapping_path:
            self.load_model()
        
        
    def load_model(self):
        if not self._model_path or not self.mapping_path:
            self._error_handler.handle_error("SET MAPPING AND MODEL PATH FIRST", 5)
        self.tokenizer = AutoTokenizer(self._model_path)
        self.model = AutoModelForSequenceClassification(self._model_path)
        self.sentiment_pipeline = pipeline("text-classification",
                                           model = self.model,
                                           tokenizer = self.tokenizer)
        with open(self.mapping_path, "r") as f:
            self.label_mapping = json.load(f)
        
    def analyze(self, text: str) -> dict:
        result = self.sentiment_pipeline(text)
        label = result[0]['label']
        score = result[0]['score']
        
        self._result =  {
            "label": label,
            "text": self.label_mapping[label]['text'],
            "score": score,
            "numeric": self.label_mapping[label]['numeric_label']  
        }
        self._human_sentiment = self.label_mapping[label]['text']
        self._score = score
        self._raw_sentiment = self.label_mapping[label]['numeric_label']
        
    
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