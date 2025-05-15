import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import numpy as np
import pickle
import os
import json
from pathlib import Path
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import argparse

# Define emotion labels
emotion_labels = [
    "neutral", "approval", "admiration", "annoyance", "gratitude",
    "disapproval", "curiosity", "amusement", "realization", "optimism",
    "disappointment", "love", "anger", "joy", "confusion", "sadness",
    "caring", "excitement", "surprise", "disgust", "desire", "fear",
    "remorse", "embarrassment", "nervousness", "pride", "relief", "grief"
]

# Configuration
config = {
    "model_name": "distilbert-base-uncased",
    "max_length": 128,
    "batch_size": 32,
    "model_path": "data/processed/emotion_model.pkl",
    "full_model_path": "models/emotion_detector",
    "test_data_path": "data/processed/test.pkl",
    "output_dir": "data/evaluation"
}

# Custom dataset class
class EmotionDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx] if self.labels is not None else None
        
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Remove batch dimension
        item = {key: val.squeeze(0) for key, val in encoding.items()}
        
        if label is not None:
            # Convert label to a format that can be converted to a torch tensor
            if isinstance(label, (list, np.ndarray)):
                # Ensure the label is a flat array of floats
                label_array = np.array(label, dtype=np.float32)
                item["labels"] = torch.tensor(label_array, dtype=torch.float)
            else:
                # If it's a single value
                item["labels"] = torch.tensor([float(label)], dtype=torch.float)
            
        return item

def load_test_data(path):
    """Load test data from pickle file or CSV."""
    print(f"Loading test data from {path}")
    
    if path.endswith('.pkl'):
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
                if isinstance(data, tuple) and len(data) == 2:
                    texts, labels = data
                    return texts, labels
                else:
                    print("Unexpected format in pickle file")
                    return None, None
        except Exception as e:
            print(f"Error loading pickle file: {e}")
            return None, None
    elif path.endswith('.csv'):
        try:
            df = pd.read_csv(path)
            
            # Try to find text column
            if 'text' in df.columns:
                text_col = 'text'
            else:
                text_col_candidates = [col for col in df.columns if any(
                    text_name in col.lower() for text_name in ['text', 'content', 'message', 'comment'])]
                
                if text_col_candidates:
                    text_col = text_col_candidates[0]
                else:
                    text_col = df.columns[0]  # Assume first column is text
            
            texts = df[text_col].tolist()
            
            # Try to find label columns
            label_cols = [col for col in df.columns if col != text_col]
            
            if len(label_cols) == len(emotion_labels):
                labels = df[label_cols].values
            else:
                # Try to find columns that match emotion labels
                matching_cols = [col for col in df.columns if col in emotion_labels]
                
                if matching_cols:
                    labels = df[matching_cols].values
                else:
                    # Try numeric columns
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    
                    if numeric_cols:
                        labels = df[numeric_cols].values
                    else:
                        print("Could not determine label columns")
                        return texts, None
            
            return texts, labels
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return None, None
    else:
        print(f"Unsupported file format: {path}")
        return None, None

def load_model(config):
    """Load the pre-trained model."""
    print("Loading model...")
    
    # Initialize model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config["model_name"])
    model = AutoModelForSequenceClassification.from_pretrained(
        config["model_name"],
        num_labels=len(emotion_labels),
        problem_type="multi_label_classification"
    )
    
    # Try to load from saved model path
    model_path = Path(config["model_path"])
    if os.path.exists(model_path):
        try:
            print(f"Loading fine-tuned model from {model_path}")
            with open(model_path, 'rb') as f:
                model_state = pickle.load(f)
                if isinstance(model_state, dict):
                    model.load_state_dict(model_state)
                    print("Successfully loaded fine-tuned model weights")
                else:
                    print("Warning: Model file does not contain valid state dictionary")
        except Exception as e:
            print(f"Error loading fine-tuned model: {e}")
            print("Using base model instead")
    else:
        # Try loading from full model path
        full_model_path = Path(config["full_model_path"])
        if os.path.exists(full_model_path):
            try:
                print(f"Loading full model from {full_model_path}")
                model = AutoModelForSequenceClassification.from_pretrained(full_model_path)
                print("Successfully loaded full model")
            except Exception as e:
                print(f"Error loading full model: {e}")
                print("Using base model instead")
        else:
            print("No fine-tuned model found. Using base model.")
    
    return model, tokenizer

def evaluate_model(model, test_loader, device):
    """Evaluate the model on the test set."""
    print("Evaluating model...")
    
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Evaluating"):
            batch = {k: v.to(device) for k, v in batch.items()}
            labels = batch.pop("labels").cpu().numpy()
            
            outputs = model(**batch)
            logits = outputs.logits
            preds = torch.sigmoid(logits).cpu().numpy()
            preds = (preds > 0.5).astype(int)
            
            all_preds.extend(preds)
            all_labels.extend(labels)
    
    # Calculate metrics
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    precision = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
    recall = recall_score(all_labels, all_preds, average='weighted', zero_division=0)
    
    # Calculate per-class metrics
    per_class_f1 = f1_score(all_labels, all_preds, average=None, zero_division=0)
    per_class_precision = precision_score(all_labels, all_preds, average=None, zero_division=0)
    per_class_recall = recall_score(all_labels, all_preds, average=None, zero_division=0)
    
    # Create a dictionary of per-class metrics
    per_class_metrics = {
        emotion_labels[i]: {
            "f1": float(per_class_f1[i]),
            "precision": float(per_class_precision[i]),
            "recall": float(per_class_recall[i])
        }
        for i in range(len(emotion_labels))
    }
    
    # Create confusion matrix
    cm = confusion_matrix(all_labels.argmax(axis=1), all_preds.argmax(axis=1))
    
    return {
        "accuracy": float(accuracy),
        "f1": float(f1),
        "precision": float(precision),
        "recall": float(recall),
        "per_class_metrics": per_class_metrics,
        "confusion_matrix": cm.tolist()
    }

def plot_confusion_matrix(cm, output_path):
    """Plot and save confusion matrix."""
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_per_class_metrics(per_class_metrics, output_path):
    """Plot and save per-class metrics."""
    emotions = list(per_class_metrics.keys())
    f1_scores = [per_class_metrics[e]["f1"] for e in emotions]
    precision_scores = [per_class_metrics[e]["precision"] for e in emotions]
    recall_scores = [per_class_metrics[e]["recall"] for e in emotions]
    
    plt.figure(figsize=(15, 8))
    x = np.arange(len(emotions))
    width = 0.25
    
    plt.bar(x - width, f1_scores, width, label='F1')
    plt.bar(x, precision_scores, width, label='Precision')
    plt.bar(x + width, recall_scores, width, label='Recall')
    
    plt.xlabel('Emotions')
    plt.ylabel('Score')
    plt.title('Per-Class Metrics')
    plt.xticks(x, emotions, rotation=90)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main(args):
    # Update config with command line arguments
    if args.model_path:
        config["model_path"] = args.model_path
    if args.test_data:
        config["test_data_path"] = args.test_data
    if args.batch_size:
        config["batch_size"] = args.batch_size
    
    # Create output directory
    os.makedirs(config["output_dir"], exist_ok=True)
    
    # Load model and tokenizer
    model, tokenizer = load_model(config)
    
    # Load test data
    texts, labels = load_test_data(config["test_data_path"])
    if texts is None:
        print("Failed to load test data. Exiting.")
        return
    
    # Create test dataset and dataloader
    test_dataset = EmotionDataset(texts, labels, tokenizer, config["max_length"])
    test_loader = DataLoader(
        test_dataset,
        batch_size=config["batch_size"],
        shuffle=False
    )
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    model.to(device)
    
    # Evaluate model
    metrics = evaluate_model(model, test_loader, device)
    
    # Print metrics
    print("\nEvaluation Results:")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"F1 Score: {metrics['f1']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    
    # Save metrics to file
    metrics_path = os.path.join(config["output_dir"], "evaluation_metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {metrics_path}")
    
    # Plot and save confusion matrix
    cm_path = os.path.join(config["output_dir"], "confusion_matrix.png")
    plot_confusion_matrix(np.array(metrics["confusion_matrix"]), cm_path)
    print(f"Confusion matrix saved to {cm_path}")
    
    # Plot and save per-class metrics
    per_class_path = os.path.join(config["output_dir"], "per_class_metrics.png")
    plot_per_class_metrics(metrics["per_class_metrics"], per_class_path)
    print(f"Per-class metrics saved to {per_class_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate emotion detection model")
    parser.add_argument("--model_path", type=str, help="Path to the model file")
    parser.add_argument("--test_data", type=str, help="Path to the test data file")
    parser.add_argument("--batch_size", type=int, help="Batch size for evaluation")
    args = parser.parse_args()
    
    main(args)