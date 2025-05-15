from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt
import pandas as pd
import traceback
from datetime import datetime
from app_utils.handlers.model_handlers import ModelHandler
from app_utils.loaders.modelLoader import ModelLoader as ml
from app_utils.handlers.API_handler import APIHandler
from app_utils.handlers.error_handler import ErrorHandler
from DTOs.Comment import CommentBatchDTO
class HomeController:
    def __init__(self, homepage, results_controller, tabs):
        self.view = homepage
        self.results_controller = results_controller
        self.tabs = tabs
        self.df = None
        self.error_handler = ErrorHandler()
        self.error_handler.error_signal.connect(self.update_error)
        self.error_handler.confirmation_signal.connect(self.send_message)
        self.model_handler = ModelHandler()
        
        
        
        
        self.view.analyze_button.clicked.connect(self.run_analysis)
        #self.view.upload_button.clicked.connect(self.upload_csv)
        
        self.progress_dialog = QProgressDialog("Loading models...", "Cancel", 0, 100, self.view)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setWindowTitle("Loading Models")
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setValue(0)
        self.download_models()
    
    
    def download_models(self):
        try:
            self.model_handler.download_models(progress_callback=self.update_progress)
            self.progress_dialog.setValue(100)
            self.progress_dialog.setLabelText("Models downloaded and loaded successfully!")
        except Exception as e:
            self.error_handler.handle_error(f"Error downloading models: {str(e)}", 700)
        
    def update_progress(self, value):
        self.progress_dialog.setValue(value)
        if self.progress_dialog.wasCanceled():
            raise Exception("Download was canceled by user.")        
        
    def run_analysis(self):
        print("Run Analysis Clicked")
        try:
            ticker = self.view.ticker_dropdown.currentText()
            print(f"Selected Ticker: {ticker}")
            if not ticker:
                self.error_handler.handle_error("Please select a ticker.", 101)
                return
            
            
            api_handler = APIHandler()
            
            print("Fetching Comments...")
            comment_batch: CommentBatchDTO = api_handler.fetch_comments(ticker)
            print("fetch complete")
            comment_df = comment_batch.to_pandas()
            if comment_df.empty:
                self.error_handler.handle_error("No comments found for this ticker.", 102)
                return
            print(comment_df)
            self.error_handler.handle_error("Test", 20)
            print("[Controller]loading model")
            self.model_handler.load_model_sentiment()
            print("[Controller]sentiment_loaded")
            self.model_handler.load_model_predict()
            print("[Controller]prediction_loaded")
        
            self.model_handler.sentiment_bulk(comment_df, "comment")
          
            print("[Controller]sentiment_complete")
        
            today = datetime.now().strftime("%Y-%m-%d")
            print("[Controller]stock data gathering")
            stock_data = api_handler._finance_api.get_price_data(ticker, today)
            print("[Controller]data gathered")
            closing_price = stock_data.close_price
            print(closing_price)
            if stock_data is None or stock_data.close_price is None:
                self.error_handler.handle_error("Unable to fetch closing price.", 103)
                return
            print("[Controller]predicting movement")
            self.model_handler.predict_movement(closing_price)
            print("[Controller]movement predicted")
            prediction = self.model_handler._prediction
            probs = self.model_handler._probs
            print("[Controller]populating results")
            self.results_controller.display_results(prediction, probs, self.model_handler._result)
            print("[Controller]results populated")
            self.tabs.setCurrentIndex(1)
        except Exception as e:
            self.error_handler.handle_error(f"Unexpected error during analysis: {e}", 999)
            traceback.print_exc()
            
        
        
    def update_error(self, error_message, error_code):
        print(f"error {error_message}")
        QMessageBox.critical(self.view, f"Error {error_code}", error_message)
    
    def send_message(self, confirmation_message):
        QMessageBox.information(self.view, "Confirmation", confirmation_message)