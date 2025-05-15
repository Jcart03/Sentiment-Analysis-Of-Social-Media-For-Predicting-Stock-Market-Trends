from PyQt6.QtWidgets import QMainWindow, QTabWidget
from ..views.homepage import HomePage
from ..views.results import ResultsPage
from ..controllers.home_controller import HomeController
from ..controllers.results_controller import ResultsController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.resultsPage = ResultsPage(self)
        self.homePage = HomePage(self)
        
        self.tabs.addTab(self.homePage, "Home")
        self.tabs.addTab(self.resultsPage, "Results")
        
        
        self.resultsController = ResultsController(self.resultsPage)
        self.homeController = HomeController(self.homePage, self.resultsController, self.tabs)
        
        self.setWindowTitle("Stock Sentiment Prototype")
    