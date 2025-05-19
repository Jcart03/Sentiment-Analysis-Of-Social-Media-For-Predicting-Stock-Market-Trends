
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from PyQt6.QtCore import Qt
from gui.views.homepage import HomePage
from gui.views.results import ResultsPage
from gui.controllers.home_controller import HomeController
from gui.controllers.results_controller import ResultsController
from app_utils.handlers.error_handler import ErrorHandler
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.resultsPage = ResultsPage(self)
        self.homePage = HomePage(self)
        
        self.tabs.addTab(self.homePage, "Home")
        self.tabs.addTab(self.resultsPage, "Results")
        
        self.error_handler = ErrorHandler()
        self.error_handler.error_signal.connect(self.update_error, Qt.ConnectionType.QueuedConnection)
        self.error_handler.confirmation_signal.connect(self.send_message, Qt.ConnectionType.QueuedConnection)
        self.resultsController = ResultsController(self.resultsPage)
        self.homeController = HomeController(self.homePage, self.resultsController, self.tabs)
        
        self.setWindowTitle("Stock Sentiment Prototype")
    
    
    
    def update_error(self, error_message, error_code):
        QMessageBox.critical(self, f"Error {error_code}", error_message)
    
    def send_message(self, confirmation_message):
        QMessageBox.information(self, "Confirmation", confirmation_message)