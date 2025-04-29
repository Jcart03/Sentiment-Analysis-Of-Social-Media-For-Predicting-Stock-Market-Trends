from utils.model_utils import PredictionModelLoader, PredictionModelSaver, PredictionTrainer

class TrainXGBoostModel:
    def __init__(self, checkpoint_path, saved_model_path, train_data, val_data, feature_columns, label_column):
        self.checkpoint_path = checkpoint_path
        self.saved_model_path = saved_model_path
        self.train_data = train_data
        self.val_data = val_data
        self.feature_columns = feature_columns
        self.label_column = label_column
        
        
        model_loader = PredictionModelLoader(self.saved_model_path)
        self.model = model_loader.get_model()
        
    def train(self, params=None, num_rounds=100):
        train_features = self.train_data[self.feature_columns].values
        train_labels = self.train_data[self.label_column].values
        val_features = self.val_data[self.feature_columns].values
        val_labels = self.val_data[self.label_column].values
        
        model_trainer = PredictionTrainer(self.model, self.saved_model_path)
        self.model = model_trainer.train((train_features, train_labels), (val_features, val_labels), num_rounds=num_rounds, params=params)
        
        model_saver = PredictionModelSaver(self.model, self.saved_model_path)
        model_saver.save()
        