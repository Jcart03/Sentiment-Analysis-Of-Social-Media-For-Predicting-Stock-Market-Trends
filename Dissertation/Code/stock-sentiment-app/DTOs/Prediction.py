from typing import List
from dataclasses import dataclass
from typing import List, Dict
import json

@dataclass
class PredictionDTO:
    readable_value:str
    predicted_value:int
    probabilities:Dict[str, float]
    
    _label_map = {0: "down", 1:"neutral", 2:"up"}
    
    @classmethod
    def from_prediction(cls, predicted_value:int, probabilities: List[float]) -> 'PredictionDTO':
        readable_value = cls._label_map.get(predicted_value, "unknown")
        probabilities = {cls._label_map[i]: prob for i, prob in enumerate(probabilities)}
        return cls(readable_value=readable_value, predicted_value=predicted_value, probabilities=probabilities)
    def format_prediction(self)-> str:
        probs_str = ", ".join([f"Class {label}: {prob:.2f}" for label, prob in self.probabilities.items()])
        return f"Predicted Value: {self.readable_value}, Probabilities: {probs_str}"