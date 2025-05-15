import pandas as pd
import numpy as np
import os
import pickle
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from sklearn.pipeline import Pipeline
import argparse
from tqdm import tqdm
from pathlib import Path

def load_data(data_path):
    """Load data from pickle file."""
    print(f"Loading data from {data_path}")
    
    try:
        # Load the DataFrame
        df = pd.read_pickle(data_path)
        print(f"Successfully loaded DataFrame with shape {df.shape}")
        
        # Identify text column
        text_col = None
        for col in df.columns:
            if col.lower() in ['text', 'content', 'message', 'comment']:
                text_col = col
                break
        
        if text_col is None:
            # Assume first column is text
            text_col = df.columns[0]
        
        print(f"Using '{text_col}' as text column")
        
        # Extract texts
        texts = df[text_col].tolist()
        
        # Extract labels (all columns except text column)
        label_cols = [col for col in df.columns if col != text_col]
        
        # Check if we have numeric columns for labels
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            label_cols = [col for col in numeric_cols if col != text_col]
        
        if not label_cols:
            print("No label columns found. Cannot proceed with training.")
            return None, None, None
        
        print(f"Using {len(label_cols)} columns as labels: {label_cols[:5]}...")
        labels = df[label_cols].values
        
        return texts, labels, label_cols
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None

def train_and_evaluate_model(train_texts, train_labels, test_texts, test_labels, label_cols, output_dir):
    """Train a TF-IDF + Logistic Regression model and evaluate it."""
    print("Training a TF-IDF + Logistic Regression model...")
    
    # Create the pipeline
    pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ('classifier', MultiOutputClassifier(LogisticRegression(max_iter=1000)))
    ])
    
    # Train the model
    pipeline.fit(train_texts, train_labels)
    
    # Make predictions
    train_preds = pipeline.predict(train_texts)
    test_preds = pipeline.predict(test_texts)
    
    # Calculate metrics
    train_accuracy = accuracy_score(train_labels, train_preds)
    train_f1 = f1_score(train_labels, train_preds, average='weighted', zero_division=0)
    
    test_accuracy = accuracy_score(test_labels, test_preds)
    test_f1 = f1_score(test_labels, test_preds, average='weighted', zero_division=0)
    test_precision = precision_score(test_labels, test_preds, average='weighted', zero_division=0)
    test_recall = recall_score(test_labels, test_preds, average='weighted', zero_division=0)
    
    print(f"Training Accuracy: {train_accuracy:.4f}, F1: {train_f1:.4f}")
    print(f"Test Accuracy: {test_accuracy:.4f}, F1: {test_f1:.4f}")
    
    # Calculate per-class metrics
    per_class_f1 = f1_score(test_labels, test_preds, average=None, zero_division=0)
    per_class_precision = precision_score(test_labels, test_preds, average=None, zero_division=0)
    per_class_recall = recall_score(test_labels, test_preds, average=None, zero_division=0)
    
    # Create a dictionary of per-class metrics
    per_class_metrics = {
        label_cols[i]: {
            "f1": float(per_class_f1[i]),
            "precision": float(per_class_precision[i]),
            "recall": float(per_class_recall[i])
        }
        for i in range(len(label_cols))
    }
    
    # Sort per-class metrics by F1 score
    per_class_metrics = {k: v for k, v in sorted(
        per_class_metrics.items(), 
        key=lambda item: item[1]['f1'], 
        reverse=True
    )}
    
    # Save the model
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "simple_emotion_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"Model saved to {model_path}")
    
    # Save the metrics
    metrics = {
        "train_accuracy": float(train_accuracy),
        "train_f1": float(train_f1),
        "test_accuracy": float(test_accuracy),
        "test_f1": float(test_f1),
        "test_precision": float(test_precision),
        "test_recall": float(test_recall),
        "per_class_metrics": per_class_metrics
    }
    
    metrics_path = os.path.join(output_dir, "simple_model_metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {metrics_path}")
    
    # Plot and save top and bottom class metrics
    plot_class_metrics(per_class_metrics, output_dir)
    
    return pipeline, metrics

def plot_class_metrics(per_class_metrics, output_dir):
    """Plot and save top and bottom class metrics."""
    # Get top 15 classes by F1 score
    top_classes = list(per_class_metrics.keys())[:15]
    
    # Create a DataFrame for plotting
    top_df = pd.DataFrame({
        'Class': top_classes,
        'F1': [per_class_metrics[cls]['f1'] for cls in top_classes],
        'Precision': [per_class_metrics[cls]['precision'] for cls in top_classes],
        'Recall': [per_class_metrics[cls]['recall'] for cls in top_classes]
    })
    
    # Melt the DataFrame for easier plotting
    top_df_melted = pd.melt(top_df, id_vars=['Class'], var_name='Metric', value_name='Score')
    
    # Plot top classes
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Class', y='Score', hue='Metric', data=top_df_melted)
    plt.title('Top 15 Classes by F1 Score')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "top_classes.png"))
    plt.close()
    
    # Get bottom 15 classes by F1 score if there are more than 15 classes
    if len(per_class_metrics) > 15:
        bottom_classes = list(per_class_metrics.keys())[-15:]
        
        # Create a DataFrame for plotting
        bottom_df = pd.DataFrame({
            'Class': bottom_classes,
            'F1': [per_class_metrics[cls]['f1'] for cls in bottom_classes],
            'Precision': [per_class_metrics[cls]['precision'] for cls in bottom_classes],
            'Recall': [per_class_metrics[cls]['recall'] for cls in bottom_classes]
        })
        
        # Melt the DataFrame for easier plotting
        bottom_df_melted = pd.melt(bottom_df, id_vars=['Class'], var_name='Metric', value_name='Score')
        
        # Plot bottom classes
        plt.figure(figsize=(12, 8))
        sns.barplot(x='Class', y='Score', hue='Metric', data=bottom_df_melted)
        plt.title('Bottom 15 Classes by F1 Score')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "bottom_classes.png"))
        plt.close()

def main():
    parser = argparse.ArgumentParser(description="Train a simple emotion detection model")
    parser.add_argument("--data", type=str, default="data/processed/train.pkl",
                        help="Path to the training data")
    parser.add_argument("--test_size", type=float, default=0.2,
                        help="Proportion of data to use for testing")
    parser.add_argument("--output_dir", type=str, default="data/simple_model",
                        help="Directory to save the model and results")
    args = parser.parse_args()
    
    # Load data
    texts, labels, label_cols = load_data(args.data)
    if texts is None or labels is None:
        print("Failed to load data. Exiting.")
        return
    
    # Split data into train and test sets
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts, labels, test_size=args.test_size, random_state=42
    )
    
    print(f"Split data into {len(train_texts)} training and {len(test_texts)} test examples")
    
    # Train and evaluate model
    model, metrics = train_and_evaluate_model(
        train_texts, train_labels, test_texts, test_labels, label_cols, args.output_dir
    )
    
    # Print summary
    print("\nTraining Complete!")
    print(f"Model and results saved to {args.output_dir}")
    print(f"Test Accuracy: {metrics['test_accuracy']:.4f}")
    print(f"Test F1 Score: {metrics['test_f1']:.4f}")
    
    # Print top 5 classes by F1 score
    print("\nTop 5 Classes by F1 Score:")
    top_classes = list(metrics['per_class_metrics'].keys())[:5]
    for cls in top_classes:
        print(f"  {cls}: F1={metrics['per_class_metrics'][cls]['f1']:.4f}")

if __name__ == "__main__":
    main()