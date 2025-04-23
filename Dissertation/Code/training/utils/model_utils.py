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


class ModelLoader:
    def __init__(self, model_name, saved_model_path=None, num_labels=3):
        self.model_name = model_name
        self.saved_model_path = saved_model_path
        self.num_labels = num_labels
        self.model = None
        self.model_tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.load_model()
        
    def load_model(self):
        
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
            

class ModelTrainer:
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
        
        
class DataTokenizer:
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
        
    