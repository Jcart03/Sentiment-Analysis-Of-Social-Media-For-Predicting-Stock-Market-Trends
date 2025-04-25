import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

class SentimentModel:
    def __init__(self, model_path="models/sentiment_files", mapping_path = "Dissertation/Code/stock-sentiment-app/app_utils/config/label_mappings.json"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model=AutoModelForSequenceClassification(model_path)
        
        self.sentiment_pipeline = pipeline("text-classification",
                                           model=self.model,
                                           tokenizer = self.tokenizer,
                                           return_all_scores=True,
                                           device=0 if torch.cuda.is_available() else -1)
        
        with open(mapping_path, "r") as f:
            self.label_mapping = json.load(f)
        
        
    def analyze(self, text: str) -> dict:
        result = self.sentiment_pipeline(text)
        label = result[0]['label']
        score = result[0]['score']
        
        return {
            "label": label,
            "text": self.label_mapping[label]['text'],
            "score": score,
            "numeric": self.label_mapping[label]['numeric_label']
            
        }
    def numeric_sentiment(self, analysis_result: dict) -> int:
        return analysis_result["numeric"]
    def human_sentiment(self, analysis_result: dict) -> str:
        return analysis_result["text"]
    def score(self, analysis_result: dict) -> float:
        return analysis_result["score"]
    def raw_sentiment(self, analysis_result:dict) -> str:
        return analysis_result["label"]