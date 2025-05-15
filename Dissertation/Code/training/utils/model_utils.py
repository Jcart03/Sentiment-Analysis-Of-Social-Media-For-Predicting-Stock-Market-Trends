import os
from httplib2 import Credentials
import pandas as pd
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from datasets import Dataset
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import numpy as np
from sklearn.model_selection import GridSearchCV



class SentimentModelLoader:
    def __init__(self, model_name, saved_model_path=None, num_labels=3):
        self.model_name = model_name
        self.saved_model_path = saved_model_path
        self.num_labels = num_labels
        self.model = None
        self.model_tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.load_sentiment_model()
        
    def load_sentiment_model(self):
        
        try: 
            if self.saved_model_path and os.path.exists(self.saved_model_path) and os.listdir(self.saved_model_path):
                required_files = []
                self.model = AutoModelForSequenceClassification.from_pretrained(self.saved_model_path)
                self.model_tokenizer = AutoTokenizer.from_pretrained(self.saved_model_path)
                print(f"Model loaded from {self.saved_model_path}")
            else:
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=self.num_labels)
                self.model_tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                print(f"No saved model found, loaded base model '{self.model_name}' with {self.num_labels} labels")
        except Exception:
            print("Error loading model: ")
            
    def get_model_and_tokenizer(self):
        return self.model, self.model_tokenizer
    
class ModelSaver:
    def __init__(self, model, tokenizer, saved_model_path):
        self.saved_model_path = saved_model_path
        self.model=model
        self.tokenizer=tokenizer
        
    def save(self):
        try:
            if not os.path.exists(self.saved_model_path):
                os.makedirs(self.saved_model_path)
            self.model.save_pretrained(self.saved_model_path)
            self.tokenizer.save_pretrained(self.saved_model_path)
            print(f"Model saved to {self.saved_model_path}")
        except Exception as e:
            print(f"Failed to save model: {e}")
            

class SentimentModelTrainer:
    def __init__(self, model, tokenizer, checkpoint_path):
        self.model = model
        self.tokenizer = tokenizer
        self.checkpoint_path = checkpoint_path
        
    def fine_tune(self, train_dataset, val_dataset):
        training_args = TrainingArguments(
            output_dir=self.checkpoint_path,
            eval_strategy="epoch",
            save_strategy="epoch",
            learning_rate=2e-5,  # standard for finetuning models
            per_device_train_batch_size=4,  # number of datapoints processed before learning ( adjust as necessary)
            per_device_eval_batch_size=8,
            num_train_epochs=3,
            weight_decay=0.01,  # reduce learning as training goes on to avoid overfitting
            save_total_limit=2,  # limit the number of checkpoints to reduce overloading the git repo
            logging_dir=os.path.join(self.checkpoint_path, "logs"),
            logging_steps=10,
            load_best_model_at_end=True,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            processing_class=self.tokenizer,
        )

        trainer.train()
        
        
class SentimentDataTokenizer:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
    
    def tokenize_data(self, dataset, text_column):
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples[text_column], 
                padding="max_length",
                truncation=True,
                max_length=128,
                return_tensors="pt"               
            )
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        return tokenized_dataset
    

class DataLoader:
    def __init__(self, path):
        self.path = path
    
    def load_data(self):
        df = pd.read_csv(self.path)
        dataset = Dataset.from_pandas(df)
        return dataset
    
    
    #############################~~~~~~~~~~~~~~~~~~#############################
    #                                                                          #
    #        Future feature for runtime loading models from google drive       #
    #                                                                          #
    #############################~~~~~~~~~~~~~~~~~~#############################
class LoadFromDrive:
    def __init__(self, folder_id: str):
        self_folder_id = folder_id
        self.credentials = self.load_credentials()
        self.service = build('drive', 'v3', credentials=self.credentials)
        
class PredictionModelLoader:
    def __init__(self, saved_model_path=None):
        self.saved_model_path = saved_model_path
        self.model = None   
        self.load_model()
    def load_model(self):
        try:
            if self.saved_model_path and os.path.exists(self.saved_model_path):
                self.model = xgb.Booster()
                self.model.load_model(self.saved_model_path)
            else:
                self.model = xgb.XGBClassifier(objective='multi:softprob')
                
        except Exception as e:
            None
    
    def get_model(self):
        return self.model
    
    
class PredictionModelSaver:
    def __init__(self, model, saved_model_path):
        self.model = model
        self.saved_model_path = saved_model_path
        
    def save(self):
        try:
            self.model.save_model(self.saved_model_path)
            print(f"Model saved to {self.saved_model_path}")
        except Exception as e:
            print(f"Failed to save model: {e}")
            
            
            
class PredictionTrainer:
    def __init__(self, model, saved_model_path):
        self.model = model
        self.saved_model_path = saved_model_path
        
    def train(self, train_data, val_data, num_rounds=500, params=None):
        if params is None:
            param_grid = {
                'objective': ['multi:softprob'],
                'device' : ['cpu'],
                'num_class': [3],
                'eval_metric': ['mlogloss'],
                'tree_method': ['exact'],
                'learning_rate': [0.1, 0.05, 0.1, 0.2],
                'max_depth': [3, 5, 6, 8, 10],
                'min_child_weight': [1, 2, 3, 5],
                'subsample': [0.7, 0.8, 0.9],
                'colsample_bytree': [0.7, 0.8, 0.9],
                'alpha': [0.1, 0.5, 1, 2],
                'lambda': [1, 2, 3],
                'gamma': [0, 1, 3, 5, 6],
                'booster': ['gbtree']
            }
        dtrain = xgb.DMatrix(train_data[0], label=train_data[1])
        dval = xgb.DMatrix(val_data[0], label=val_data[1])
        print(dtrain)
        print(dval)
        evals = [(dtrain, 'train'), (dval, 'eval')]
        xgb_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
        grid_search = GridSearchCV(estimator = xgb_model, param_grid = param_grid, scoring = 'accuracy', cv=2, verbose=3, n_jobs=1)
        grid_search.fit(train_data[0], train_data[1])
        
        print("Best Params found: ", grid_search.best_params_)
        print("Best Cross-validation Accuracy: ", grid_search.best_score_)
        best_model = grid_search.best_estimator_
        self.model = xgb.train(best_model.get_xgb_params(), dtrain=dtrain, num_boost_round=num_rounds, evals= evals, early_stopping_rounds=10)
        
        y_pred_probs = self.model.predict(dval)
        y_pred = np.argmax(y_pred_probs, axis=1)
        print("Accuracy: ", accuracy_score(val_data[1], y_pred))
        print("F1 Score (macro): ", f1_score(val_data[1], y_pred, average='macro'))
        print("F1 Score (weighted): ", f1_score(val_data[1], y_pred, average='weighted'))
        print("Confusion Matrix: ", confusion_matrix(val_data[1], y_pred))
        print("Classification Report: ", classification_report(val_data[1], y_pred) )
        model_saver = PredictionModelSaver(self.model, self.saved_model_path)
        model_saver.save()
        
        