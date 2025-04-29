from typing import List
from dataclasses import dataclass


@dataclass
class PredictionDTO:
    readable_value:str
    predicted_value:int
    probabilities:List[float]
    
    def format_prediction(self)-> str:
        probs_str = ", ".join([f"Class {i}: {prob:.2f}" for i, prob in enumerate(self.probabilities)])
        return f"Predicted Value: {self.readable_value}, Probabilities: {probs_str}"