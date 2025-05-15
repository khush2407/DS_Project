import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup
import json
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, accuracy_score
import os

class EmotionDataset(Dataset):
    def __init__(self, df):
        self.encodings = torch.tensor(np.array(df['tokenized'].tolist()))
        self.labels = torch.tensor(df['labels'].tolist(), dtype=torch.float32)

    def __getitem__(self, idx):
        return {
            'input_ids': self.encodings[idx],
            'labels': self.labels[idx]
        }

    def __len__(self):
        return len(self.labels)

def load_data(data_path):
    """Load preprocessed data from pickle file."""
    return pd.read_pickle(data_path)

def compute_metrics(pred, labels):
    """Compute evaluation metrics for multi-label classification."""
    preds = (pred > 0).astype(int)
    f1 = f1_score(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'f1': f1,
        'accuracy': acc
    }

def train_model(train_df, val_df, model_name, num_labels, output_dir):
    """Train the emotion detection model."""
    # Initialize model and tokenizer
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        problem_type='multi_label_classification'
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Create datasets
    train_dataset = EmotionDataset(train_df)
    val_dataset = EmotionDataset(val_df)

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16)

    # Setup training
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    optimizer = AdamW(model.parameters(), lr=5e-5)
    num_epochs = 3
    num_training_steps = len(train_loader) * num_epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=num_training_steps
    )

    # Training loop
    best_f1 = 0
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0

        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(
                input_ids=input_ids,
                labels=labels
            )

            loss = outputs.loss
            total_loss += loss.item()

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

        avg_train_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch + 1}/{num_epochs}, Average training loss: {avg_train_loss:.4f}")

        # Validation
        model.eval()
        val_preds = []
        val_labels = []

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                labels = batch['labels']

                outputs = model(
                    input_ids=input_ids
                )

                preds = torch.sigmoid(outputs.logits).cpu().numpy()
                val_preds.extend(preds)
                val_labels.extend(labels.numpy())

        # Calculate metrics
        val_f1 = f1_score(val_labels, val_preds, average='weighted')
        val_acc = accuracy_score(val_labels, val_preds)

        print(f"Validation F1: {val_f1:.4f}, Accuracy: {val_acc:.4f}")

        # Save best model
        if val_f1 > best_f1:
            best_f1 = val_f1
            model.save_pretrained(output_dir)
            tokenizer.save_pretrained(output_dir)
            print(f"New best model saved with F1: {best_f1:.4f}")

def main():
    # Load data
    train_df = load_data('data/processed/train.pkl')
    val_df = load_data('data/processed/val.pkl')

    # Training parameters
    model_name = 'distilbert-base-uncased'
    num_labels = 28  # Number of emotion classes
    output_dir = 'models/emotion_detector'

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Train model
    train_model(train_df, val_df, model_name, num_labels, output_dir)

if __name__ == "__main__":
    main() 