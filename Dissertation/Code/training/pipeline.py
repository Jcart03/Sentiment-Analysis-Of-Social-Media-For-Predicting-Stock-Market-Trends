import json
import os
from tools.cleaner import map as clean_dataset
from train_BerTweet import FineTuneBerTweet
from datasets import Dataset


def load_configurations():
    with open("Dissertation/Code/training/config/datasets_config.json") as f:
        datasets_config = json.load(f)
    with open("Dissertation/Code/training/config/mappings.json") as f:
        mappings = json.load(f)

    for dataset, mapping in mappings.items():
        if all(k.lstrip("-").isdigit() for k in mapping.keys()):
            mappings[dataset] = {int(k): v for k, v in mapping.items()}
    return datasets_config, mappings


def fine_tune_model():
    datasets_config, mappings = load_configurations()

    fine_tune_bertweet = FineTuneBerTweet(
        "vinai/bertweet-base", "Dissertation/Code/training/bertweetCheckpoints"
    )
    fine_tune_bertweet.load_model()

    for dataset_cfg in datasets_config["datasets"]:

        name = dataset_cfg["name"]
        raw_path = dataset_cfg["path"]
        delimiter = dataset_cfg["delimiter"]
        label_column = dataset_cfg["label_column"]
        text_column = dataset_cfg["text_column"]
        map_dict = mappings[name]
        clean_path = "Dissertation/datasets/berTweet/clean"

        dataset = clean_dataset(
            raw_path, delimiter, label_column, text_column, map_dict, clean_path
        )

        dataset = Dataset.from_pandas(dataset)

        print(f"Original dataset size before splitting: {len(dataset)}")

        tokenized_datasets = fine_tune_bertweet.tokenize_data(dataset, text_column)

        split = tokenized_datasets.train_test_split(
            test_size=0.2, shuffle=True, seed=42
        )
        train_dataset = split["train"]
        val_dataset = split["test"]

        print(f"Number of examples after tokenization: {len(tokenized_datasets)}")

        fine_tune_bertweet.fine_tune(train_dataset, val_dataset)

    fine_tune_bertweet.save_model()


if __name__ == "__main__":
    fine_tune_model()
