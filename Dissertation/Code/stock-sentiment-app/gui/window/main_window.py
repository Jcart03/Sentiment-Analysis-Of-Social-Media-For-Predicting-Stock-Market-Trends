from PyQt6.QtWidgets import QMainWindow, QTabWidget
from views.homepage import HomePage
from views.results import ResultsPage
from controllers.home_controller import HomeController
from controllers.results_controller import ResultsController

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.resultsPage = ResultsPage()
        self.homePage = HomePage()
        
        self.tabs.addTab(self.homePage, "Home")
        self.tabs.addTab(self.resultsPage, "Results")
        
        
        self.resultsController = ResultsController(self.resultsPage)
        self.homeController = HomeController(self.homePage)
        
        self.setWindowTitle("Stock Sentiment Prototype")
    