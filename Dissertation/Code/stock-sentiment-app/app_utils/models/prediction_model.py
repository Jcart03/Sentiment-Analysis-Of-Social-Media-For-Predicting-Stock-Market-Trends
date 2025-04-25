class PredictionModel:
    
  
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