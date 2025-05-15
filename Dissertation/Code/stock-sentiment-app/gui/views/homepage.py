from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
)

class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout()
        dropdown_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        
        ticker_label = QLabel("Select Stock Ticker: ")
        self.ticker_dropdown = QComboBox()
        self.ticker_dropdown.addItems(["AAPL", "GOOGL", "TSLA", "AMZN"])
        
        dropdown_layout.addWidget(ticker_label)
        dropdown_layout.addWidget(self.ticker_dropdown)
        
        self.upload_button = QPushButton("Upload CSV")
        self.analyze_button = QPushButton("Run Analysis")
        
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.analyze_button)
        
        main_layout.addLayout(dropdown_layout)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)