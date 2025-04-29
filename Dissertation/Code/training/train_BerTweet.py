from utils.model_utils import SentimentModelLoader, DataLoader, SentimentDataTokenizer, SentimentModelTrainer, ModelSaver


# File paths for saving and loading
checkpoint_path = "Dissertation/Code/training/bertweetCheckpoints"
saved_model_path = "Dissertation/Code/training/models/berTweetSaved"


class FineTuneBerTweet:

    def __init__(self, model_name, checkpoint_path, saved_model_path, train_dataset, val_dataset, text_column):

        self.model_name = model_name
        self.checkpoint_path = checkpoint_path
        self.saved_model_path = saved_model_path
        self.text_column = text_column
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        
        model_loader = SentimentModelLoader(self.model_name, saved_model_path)
        self.model, self.tokenizer = model_loader.get_model_and_tokenizer()
        
        data_tokenizer = SentimentDataTokenizer(self.tokenizer)
        self.train_dataset = data_tokenizer.tokenize_data(self.train_dataset, self.text_column)
        self.val_dataset = data_tokenizer.tokenize_data(self.val_dataset, self.text_column)        
        

    def fine_tune(self):
        model_trainer = SentimentModelTrainer(self.model, self.tokenizer, self.checkpoint_path)
        model_trainer.fine_tune(self.train_dataset, self.val_dataset)

    def save_model(self):
        model_saver = ModelSaver(self.model, self.tokenizer, self.saved_model_path)
        model_saver.save()
    
