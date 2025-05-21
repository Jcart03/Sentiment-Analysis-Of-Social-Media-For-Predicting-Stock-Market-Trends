from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog, QApplication
from PyQt6.QtCore import Qt
import pandas as pd
import traceback
from datetime import datetime
from app_utils.handlers.error_handler import ErrorHandler
from app_utils.handlers.model_handlers import ModelHandler
from app_utils.loaders.modelLoader import ModelLoader as ml
from app_utils.handlers.API_handler import APIHandler
from DTOs.Comment import CommentBatchDTO
from DTOs.Features import FeaturesDTO
class HomeController:
    def __init__(self, homepage, results_controller, tabs):
        self.view = homepage
        self.results_controller = results_controller
        self.tabs = tabs
        self.df = None
    
        self.model_handler = ModelHandler()
        self.api_handler = APIHandler()
        
        ErrorHandler().handle_error("Test", 100)
        print("HomeController")
        
        
        self.view.analyze_button.clicked.connect(self.run_analysis)
        #self.view.upload_button.clicked.connect(self.upload_csv)
        
        self.model_progress_dialog = QProgressDialog("Loading models...", "Cancel", 0, 100, self.view)
        self.model_progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.model_progress_dialog.setWindowTitle("Loading Models")
        self.model_progress_dialog.setAutoClose(True)
        self.model_progress_dialog.setValue(0)
        
        self.cancelled = False
        
        self.download_models()
    
    
    def download_models(self):
        try:
            self.model_handler.download_models(progress_callback=self.update_progress)
            self.model_progress_dialog.setValue(100)
            self.model_progress_dialog.setLabelText("Models downloaded and loaded successfully!")
        except Exception as e:
            ErrorHandler().handle_error(f"Error downloading models: {str(e)}", 700)
        
    def update_progress(self, value):
        self.model_progress_dialog.setValue(value)
        if self.model_progress_dialog.wasCanceled():
            raise Exception("Download was canceled by user.")        
        
    def run_analysis(self):
        
        self.cancel_requested = False
        data = {}
        try:
            ticker = self.view.ticker_dropdown.currentText()
            print(f"Selected Ticker: {ticker}")
            if not ticker:
                ErrorHandler().handle_error("Please select a ticker.", 101)
                return
            
            progress = QProgressDialog(f"Running analysis for {ticker}...", "Cancel", 0, 100, self.view)
            progress.setWindowModality(Qt.WindowModality.ApplicationModal)
            progress.setWindowTitle(f"Running analysis for {ticker}...")
            progress.setAutoClose(False)
            progress.setValue(0)
            progress.canceled.connect(self.request_cancel)
            progress.show()
            
            print("Run Analysis Clicked")    
            
            
            self.run_step(
                lambda: self.api_handler.fetch_comments(ticker),
                progress, "Fetching Reddit Comments...", 10
            )
            comment_df = self.api_handler._comments.to_pandas()
            if comment_df.empty:
                ErrorHandler().handle_error("No comments found for this ticker.", 102)
                return
            
            self.run_step(
                lambda: self.model_handler.load_model_sentiment(),
                progress, "Loading sentiment model...", 25
            )
            
            self.run_step(
                lambda: self.model_handler.load_model_predict(),
                progress, "Loading prediction model...", 40
            )
            
            self.run_step(
                lambda: self.model_handler.sentiment_bulk(comment_df, "comment"),
                progress, "Running sentiment analysis...", 55
            )
            
            
            self.run_step(
                lambda: self.api_handler.get_finance_data(ticker, datetime.now().strftime("%Y-%m-%d")),
                progress, "Fetching financial data...", 70
            )
            
            
            features = FeaturesDTO(self.model_handler._sentiments, self.api_handler._stocks)
            
            self.run_step(
                lambda: self.model_handler.predict_movement(features),
                progress, "Predicting market movement...", 85
            )
            
            progress.setLabelText("Finalizing results...")
            progress.setValue(100)
            prediction = self.model_handler._prediction
            probs = self.model_handler._probs
            print("[Controller]populating results")
            results = features.construct_results()
            self.results_controller.display_results(prediction, probs, results)
            print("[Controller]results populated")
            self.tabs.setCurrentIndex(1)
            
            
        except Exception as e:
            ErrorHandler().handle_error(f"Unexpected error during analysis: {e}", 999)
            traceback.print_exc()
            return
    
    def request_cancel(self):
        self.cancel_requested = True
    
    def run_step(self, step_fn, progress, label, value):
        if self.cancel_requested:
            raise Exception("Operation cancelled by user.")
        progress.setLabelText(label)
        progress.setValue(value)
        QApplication.processEvents()
        result = step_fn()
        return result
    
    def update_error(self, error_message, error_code):
        print(f"error {error_message}")
        QMessageBox.critical(self.view, f"Error {error_code}", error_message)
    
    def send_message(self, confirmation_message):
        QMessageBox.information(self.view, "Confirmation", confirmation_message)
        
