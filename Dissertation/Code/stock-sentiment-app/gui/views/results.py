from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ResultsPage:
   def __init__(self):
       super().__init__()
       layout = QVBoxLayout()
       
       self.sentiment_label = QLabel("Sentiment:")
       self.confidence_label = QLabel("Confidence:")
       layout.addWidget(self.sentiment_label)
       layout.addWidget(self.confidence_label)
       
       self.setLayout(layout)