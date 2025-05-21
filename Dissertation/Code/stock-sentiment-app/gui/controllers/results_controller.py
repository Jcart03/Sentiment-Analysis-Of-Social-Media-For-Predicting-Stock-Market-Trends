from PyQt6.QtWidgets import QMessageBox, QLabel, QVBoxLayout, QHBoxLayout 
from matplotlib.ticker import MaxNLocator
from DTOs.Features import FeaturesDTO

class ResultsController:
    
    
    def __init__ (self, resultspage):
        self.view = resultspage

        
        
  
    
    ##### Mainly for testing though I might add a button for just sentiment and another one for the full pipeline
    def display_results(self, prediction: str, probs: dict, results: dict):
        self.view.prediction_label.setText(f"Prediction: {prediction.upper()}")
        self.view.metrics_label.setText(
            f"Ticker: {results.get('ticker', 'N/A')}\n"
            f"Close Price: {results.get('close_price', 'N/A')}\n\n"
            "Sentiment Summary: \n"
            f"Avg_Sentiment: {results['avg_sentiment']:.2f} ({results['sentiment_label']})\n"
            f"Standard Deviation: {results['sentiment_std']:.2f}\n"
            f"Volume: {results['volume']}\n")
        
        self.view.prob_chart.figure.clear()
        ax = self.view.prob_chart.figure.add_subplot(111)
        labels = list(probs.keys())
        values = [probs[k] for k in labels]
        
        ax.bar(labels, values, color=['green' if k==prediction.lower() else 'gray' for k in labels])
        ax.set_title("Prediction Probabilities")
        ax.set_ylabel("Probability")
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        self.view.prob_chart.draw()
        
        
        self.view.sentiment_pie.figure.clear()
        ax2 = self.view.sentiment_pie.figure.add_subplot(111)
        sentiment_parts = [
            results['positive_pct'],
            results['neutral_pct'],
            results['negative_pct']
            ]
        labels = ['Positive', 'Neutral', 'Negative']
        colors = ['green', 'gold', 'red']
        ax2.pie(sentiment_parts, labels=labels, colors=colors, autopct= '%1.1f%%', startangle=140)
        ax2.set_title("Sentiment Breakdown")
        self.view.sentiment_pie.draw_idle()
        
        
        