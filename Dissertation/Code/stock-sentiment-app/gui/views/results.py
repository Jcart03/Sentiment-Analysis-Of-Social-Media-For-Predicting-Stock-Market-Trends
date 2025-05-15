from PyQt6.QtWidgets import (QWidget, QVBoxLayout,QHBoxLayout, QLabel, QSizePolicy, QFrame)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
class ResultsPage(QWidget):
   def __init__(self, parent=None):
       super().__init__(parent)
       self.prediction_label = QLabel("Prediction here")
       self.prediction_label.setStyleSheet("font-size: 20px; font-weight: bold;")
       self.prediction_label.setWordWrap(True)
       
       self.metrics_label = QLabel("Sentiment metrics here")
       self.metrics_label.setWordWrap(True)
       
       self.prob_chart = FigureCanvas(Figure(figsize= (4, 3)))
       self.sentiment_pie = FigureCanvas(Figure(figsize=(3, 3)))
       
       charts_layout = QHBoxLayout()
       charts_layout.addWidget(self.prob_chart)
       charts_layout.addWidget(self.sentiment_pie)
       
       layout = QVBoxLayout()
       layout.addWidget(self.prediction_label)
       layout.addWidget(self.metrics_label)
       layout.addLayout(charts_layout)
       self.setLayout(layout)
       