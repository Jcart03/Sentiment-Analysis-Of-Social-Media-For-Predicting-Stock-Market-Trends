import os
import pandas as pd
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from datasets import Dataset


# File paths for saving and loading
checkpoint_path = "Dissertation/Code/training/bertweetCheckpoints"
saved_model_path = "Dissertation/Code/training/models/berTweetSaved"


class FineTuneBerTweet:

    def __init__(self, model_name, checkpoint_path):

        # initializing model and tokenizer
        self.model_name = model_name
        self.checkpoint_path = checkpoint_path
        self.saved_model_path = saved_model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=3
        )  # specifies model and tokenizer for that model then assigns a memory capacity of 3 labels ie. positive negative neutral

        if not os.path.exists(self.checkpoint_path):
            os.makedirs(
                self.checkpoint_path
            )  # not necessary but in the event that there is no output dir it will create one

    def load_data(self, path):
        df = pd.read_csv(path)
        dataset = Dataset.from_pandas(df)
        return dataset

    def tokenize_data(self, dataset, text):
        tokenizer = self.tokenizer

        def tokenize_function(examples):

            text_column = examples[text]
            return tokenizer(
                text_column,
                padding="max_length",
                truncation=True,
                max_length=128,
                return_tensors="pt",
            )

        tokenized_dataset = dataset.map(tokenize_function, batched=True)

        return tokenized_dataset

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

    def save_model(self):
        self.model.save_pretrained(self.saved_model_path)
        self.tokenizer.save_pretrained(self.saved_model_path)
        print(f"Model saved to {self.saved_model_path}")

    def load_model(self):
        if os.path.exists(self.saved_model_path) and os.listdir(self.saved_model_path):
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.saved_model_path
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.saved_model_path)
            print(f"Model loaded from {self.saved_model_path}")
        else:
            print(
                f"No saved model found at {self.saved_model_path}, starting with base model."
            )
