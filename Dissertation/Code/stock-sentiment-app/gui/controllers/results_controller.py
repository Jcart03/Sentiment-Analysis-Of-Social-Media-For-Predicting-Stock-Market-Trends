from PyQt6.QtWidgets import QMessageBox, QLabel, QVBoxLayout, QHBoxLayout 
from matplotlib.ticker import MaxNLocator


class ResultsController:
    
    
    def __init__ (self, resultspage):
        self.view = resultspage

        
        
  
    
    ##### Mainly for testing though I might add a button for just sentiment and another one for the full pipeline
    def display_results(self, prediction: str, probs: dict, sentiment_result: dict):
        self.view.prediction_label.setText(f"Prediction: {prediction.upper()}")
        self.view.metrics_label.setText(
            "Sentiment Summary: \n"
            f"Avg_Sentiment: {sentiment_result['avg_sentiment']:.2f} ({sentiment_result['sentiment_label']})\n"
            f"Standard Deviation: {sentiment_result['sentiment_std']:.2f}\n"
            f"Volume: {sentiment_result['volume']}\n")
        
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
            sentiment_result['positive_pct'],
            sentiment_result['neutral_pct'],
            sentiment_result['negative_pct']
            ]
        labels = ['Positive', 'Neutral', 'Negative']
        colors = ['green', 'gold', 'red']
        ax2.pie(sentiment_parts, labels=labels, colors=colors, autopct= '%1.1f%%', startangle=140)
        ax2.set_title("Sentiment Breakdown")
        self.view.sentiment_pie.draw_idle()
        
        
        