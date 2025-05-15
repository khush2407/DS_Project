import pickle
import os
import torch
import numpy as np
from pathlib import Path

def check_model_format(model_path):
    """Check the format of the model file."""
    print(f"\n=== Checking model file: {model_path} ===")
    
    if not os.path.exists(model_path):
        print(f"Model file not found at {model_path}")
        return
    
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        print(f"Model data type: {type(model_data)}")
        
        if isinstance(model_data, dict):
            print(f"Number of keys: {len(model_data)}")
            print("Sample keys:")
            for i, key in enumerate(list(model_data.keys())[:10]):
                print(f"  {key}: {type(model_data[key])}")
                if isinstance(model_data[key], (np.ndarray, list)):
                    print(f"    Shape: {np.array(model_data[key]).shape}")
        else:
            print(f"Model data is not a dictionary. Cannot inspect keys.")
    
    except Exception as e:
        print(f"Error loading model file: {e}")

def check_data_format(data_path):
    """Check the format of the data file."""
    print(f"\n=== Checking data file: {data_path} ===")
    
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}")
        return
    
    try:
        with open(data_path, 'rb') as f:
            data = pickle.load(f)
        
        print(f"Data type: {type(data)}")
        
        if isinstance(data, tuple):
            print(f"Tuple length: {len(data)}")
            for i, item in enumerate(data):
                print(f"  Item {i} type: {type(item)}")
                if hasattr(item, '__len__'):
                    print(f"    Length: {len(item)}")
                if isinstance(item, (list, np.ndarray)) and len(item) > 0:
                    print(f"    First element type: {type(item[0])}")
                    if isinstance(item[0], (list, np.ndarray)):
                        print(f"    First element shape: {np.array(item[0]).shape}")
        elif isinstance(data, dict):
            print(f"Dictionary with {len(data)} keys")
            print("Keys:", list(data.keys()))
        elif isinstance(data, (list, np.ndarray)):
            print(f"List/Array with {len(data)} elements")
            if len(data) > 0:
                print(f"First element type: {type(data[0])}")
        else:
            print("Data is not a tuple, dictionary, or list.")
    
    except Exception as e:
        print(f"Error loading data file: {e}")

def main():
    # Check model format
    model_paths = [
        "data/processed/emotion_model.pkl",
        "models/emotion_detector/pytorch_model.bin"
    ]
    
    for model_path in model_paths:
        if os.path.exists(model_path):
            check_model_format(model_path)
    
    # Check data format
    data_paths = [
        "data/processed/test.pkl",
        "data/processed/train.pkl",
        "data/processed/val.pkl"
    ]
    
    for data_path in data_paths:
        if os.path.exists(data_path):
            check_data_format(data_path)

if __name__ == "__main__":
    main()