import json
import os
from tools.cleaner import map as clean_dataset
from train_BerTweet import FineTuneBerTweet
from datasets import Dataset
from utils.model_utils import DataLoader

def load_configurations():
    with open("Dissertation/Code/training/config/datasets_config.json") as f:
        datasets_config = json.load(f)
    with open("Dissertation/Code/training/config/mappings.json") as f:
        mappings = json.load(f)

    for dataset, mapping in mappings.items():
        if all(k.lstrip("-").isdigit() for k in mapping.keys()): # To convert the strings in the json to integers
            mappings[dataset] = {int(k): v for k, v in mapping.items()}
    return datasets_config, mappings


def fine_tune_model():
    datasets_config, mappings = load_configurations()

    
    

    for dataset_cfg in datasets_config["datasets"]:
        
        
        
        name = dataset_cfg["name"]
        raw_path = dataset_cfg["path"]
        delimiter = dataset_cfg["delimiter"]
        label_column = dataset_cfg["label_column"]
        text_column = dataset_cfg["text_column"]
        map_dict = mappings[name]
        clean_path = "Dissertation/datasets/berTweet/clean"

        clean_file_path = clean_dataset(
            raw_path, delimiter, label_column, text_column, map_dict, clean_path
        )
        
        data_loader = DataLoader(clean_file_path)
        dataset = data_loader.load_data()

        print(f"Original dataset size before splitting: {len(dataset)}")

        split = dataset.train_test_split(test_size=0.2, seed=42)
        train_dataset = split["train"]
        val_dataset = split["test"]

        print(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}")
        
        
        
        fine_tune_bertweet = FineTuneBerTweet(
            model_name = "vinai/bertweet-base",
            checkpoint_path = "Dissertation/Code/training/bertweetCheckpoints",
            saved_model_path="Dissertation/Code/training/models/berTweetSaved",
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            text_column=dataset_cfg["text_column"]
        )
        
        
       
        fine_tune_bertweet.fine_tune()
        fine_tune_bertweet.save_model()


if __name__ == "__main__":
    fine_tune_model()
