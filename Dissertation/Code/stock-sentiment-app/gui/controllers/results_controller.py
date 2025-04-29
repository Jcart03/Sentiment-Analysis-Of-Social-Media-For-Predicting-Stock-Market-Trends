from PyQt6.QtWidgets import QMessageBox
from app_utils.handlers.error_handler import ErrorHandler

class ResultsController:
    
    
    def __init__ (self, resultsPage):
        self.view = resultsPage
        self.error_handler = ErrorHandler()
        self.error_handler.error_signal.connect(self.update_error)
        self.error_handler.confirmation_signal.connect(self.send_message)
        
        
    def update_results_single_sentiment(self, results: dict):
        sentiment = results.get("sentiment", "N/A")
        sentiment_score = results.get("sentiment_score", "N/A")
        
        self.view.sentiment_label.setText(f"Sentiment: {sentiment}")
        self.view.confidence_label.setText(f"confidence: {sentiment_score:.2f}")
    
    ##### Mainly for testing though I might add a button for just sentiment and another one for the full pipeline
    def update_results_bulk_sentiment(self, results: dict):
        avg_confidence = results.get("avg_confidence", "N/A")
        confidence_label = results.get("confidence_label", "N/A")
        avg_sentiment = results.get("avg_sentiment", "N/A")
        sentiment_label = results.get("sentiment_label", "N/A")
        positive_pct = results.get("positive_pct", "N/A")
        neutral_pct = results.get("neutral_pct", "N/A")
        negative_pct = results.get("negative_pct", "N/A")
        sentiment_std = results.get("sentiment_std", "N/A")
        confidence_std = results.get("confidence_std", "N/A")
        tweet_volume = results.get("tweet_volume", "N/A")
        
        
    def update_results_predict(self, results:dict):
        predicted_movement = results.get("predicted_movement", "N/A")
        
        
        
    def update_error(self, error_message, error_code):
        QMessageBox.critical(self.view, f"Error {error_code}", error_message)
    
    def send_message(self, confirmation_message):
        QMessageBox.information(self.view, "Confirmation", confirmation_message)