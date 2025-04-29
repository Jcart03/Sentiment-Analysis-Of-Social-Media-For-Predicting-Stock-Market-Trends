from PyQt6.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
from app_utils.handlers.model_handlers import ModelHandler as mh
from app_utils.handlers.error_handler import ErrorHandler
class HomeController:
    def __init__(self, homepage, results_controller, tabs):
        self.view = homepage
        self.results_controller = results_controller
        self.tabs = tabs
        self.df = None
        self.error_handler = ErrorHandler()
        self.error_handler.error_signal.connect(self.update_error)
        self.error_handler.confirmation_signal.connect(self.send_message)
        
        
        
        self.view.analyze_button.clicked.connect(self.run_analysis)
        self.view.upload_button.clicked.connect(self.upload_csv)
        
        
    def upload_csv(self):
        
        filepath, _ = QFileDialog.getOpenFilename(self.view, "Open CSV", "", "CSV Files (*.csv)")
        if filepath:
            self.df = pd.read_csv(filepath)
            QMessageBox.information(self.view, "Success", f"Loaded{len(self.df)} rows")
    
    def run_analysis(self):
        text = self.view.textbox.toPlainText()
        
        try: 
            if text:
                result = self.analyze_single(text)
                self.results_controller.update_results(result)
                self.tabs.setCurrentIndex(1)
            elif self.df is not None:
                result = self.analyze_bulk(self.df)
                self.results_controller.update_results(result)
                self.tabs.setCurrentIndex(1)
                
            else: 
                QMessageBox.warning(self.view, "Input Missing", "Please enter a tweet or upload a CSV")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", str(e))
    
    def analyze_single(self, text):
        sentiment: dict = mh.sentiment_single(text)
        return sentiment
    
    
    def analyze_bulk(self, df):
        sentiment: dict = mh.sentiment_bulk(df)
        return sentiment 
    
    def update_error(self, error_message, error_code):
        QMessageBox.critical(self.view, f"Error {error_code}", error_message)
    
    def send_message(self, confirmation_message):
        QMessageBox.information(self.view, "Confirmation", confirmation_message)