import pandas as pd
import os
from datasets import Dataset
from datetime import datetime
from dateutil.relativedelta import relativedelta



def map(raw_path, delimiter, label, text,  map, clean_path):
    
    ds = pd.read_csv(raw_path, delimiter = delimiter) #delimiter is dependant on csv file
    
    ds[label] = ds[label].map(map)
    
    print("NaN values in '", label, "'column before processing:", ds[label].isna().sum())
    
    ds = ds.dropna(subset=[label, text])
    
    
    ds[label] = ds[label].astype(int)
    
    print("NaN values in '", label, "'column after processing:", ds[label].isna().sum())
    
    ds = ds.rename(columns = {label: "labels"})
    cleaned_file_path = os.path.join(clean_path, f"Formatted_{os.path.basename(raw_path)}")
    ds.to_csv(cleaned_file_path, index=False)
    print(ds.head())
    
    return cleaned_file_path
