import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
from torch.optim import AdamW
import pandas as pd
import numpy as np
import pickle
import os
import json
from pathlib import Path
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from tqdm import tqdm

# Create directories if they don't exist
os.makedirs("data/processed", exist_ok=True)
os.makedirs("models", exist_ok=True)

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
    "train_batch_size": 16,
    "eval_batch_size": 64,
    "learning_rate": 5e-5,
    "weight_decay": 0.01,
    "num_epochs": 3,
    "warmup_ratio": 0.1,
    "seed": 42,
    "validation_split": 0.1,
    "save_path": "data/processed/emotion_model.pkl",
    "save_model_path": "models/emotion_detector"
}

# Set random seed for reproducibility
torch.manual_seed(config["seed"])
np.random.seed(config["seed"])

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

# Load GoEmotions dataset
print("Loading GoEmotions dataset...")
try:
    df = pd.read_csv("data/raw/goemotions.csv")
    print(f"Dataset loaded with {len(df)} examples")
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit(1)

# Process labels based on the CSV format
print("Processing dataset...")
# Check if 'text' column exists
if 'text' not in df.columns:
    # Try to find a text column
    text_col_candidates = [col for col in df.columns if any(
        text_name in col.lower() for text_name in ['text', 'content', 'message', 'comment'])]
    
    if text_col_candidates:
        text_col = text_col_candidates[0]
        print(f"Using '{text_col}' as the text column")
    else:
        # Assume first column is text
        text_col = df.columns[0]
        print(f"Assuming first column '{text_col}' contains text")
else:
    text_col = 'text'

# Extract texts
texts = df[text_col].tolist()

# Extract labels
# Try different approaches to get labels
if len(df.columns) > 1:
    # Approach 1: Assume all columns except text are labels
    label_cols = [col for col in df.columns if col != text_col]
    
    # Check if we have the expected number of emotion labels
    if len(label_cols) == len(emotion_labels):
        print(f"Using columns {label_cols} as emotion labels")
        labels = df[label_cols].values
    else:
        # Approach 2: Try to find columns that match emotion labels
        matching_cols = [col for col in df.columns if col in emotion_labels]
        
        if matching_cols:
            print(f"Found {len(matching_cols)} columns matching emotion labels")
            labels = df[matching_cols].values
        else:
            # Approach 3: Assume all numeric columns are labels
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if numeric_cols:
                print(f"Using numeric columns as labels: {numeric_cols}")
                labels = df[numeric_cols].values
            else:
                # Fallback: Create dummy labels
                print("Could not determine label columns, creating dummy labels")
                labels = np.zeros((len(texts), len(emotion_labels)))
                # Set a random emotion to 1 for each text
                for i in range(len(texts)):
                    labels[i, np.random.randint(0, len(emotion_labels))] = 1
else:
    # Only one column in the dataset, create dummy labels
    print("Only one column in dataset, creating dummy labels")
    labels = np.zeros((len(texts), len(emotion_labels)))
    # Set a random emotion to 1 for each text
    for i in range(len(texts)):
        labels[i, np.random.randint(0, len(emotion_labels))] = 1

print(f"Processed {len(texts)} texts with labels of shape {labels.shape}")

# Split dataset into train and validation
dataset_size = len(texts)
val_size = int(dataset_size * config["validation_split"])
train_size = dataset_size - val_size

# Load tokenizer
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(config["model_name"])

# Create datasets
train_texts, val_texts = texts[:train_size], texts[train_size:]
train_labels, val_labels = labels[:train_size], labels[train_size:]

train_dataset = EmotionDataset(train_texts, train_labels, tokenizer, config["max_length"])
val_dataset = EmotionDataset(val_texts, val_labels, tokenizer, config["max_length"])

# Create data loaders
train_loader = DataLoader(
    train_dataset,
    batch_size=config["train_batch_size"],
    shuffle=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=config["eval_batch_size"],
    shuffle=False
)

# Load model
print("Loading base model...")
model = AutoModelForSequenceClassification.from_pretrained(
    config["model_name"],
    num_labels=len(emotion_labels),
    problem_type="multi_label_classification"
)

# Setup training
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
model.to(device)

# Prepare optimizer and scheduler
optimizer = AdamW(
    model.parameters(),
    lr=config["learning_rate"],
    weight_decay=config["weight_decay"]
)

total_steps = len(train_loader) * config["num_epochs"]
warmup_steps = int(total_steps * config["warmup_ratio"])

scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=warmup_steps,
    num_training_steps=total_steps
)

# Training loop
print("Starting training...")
best_f1 = 0
best_model_state = None

for epoch in range(config["num_epochs"]):
    # Training
    model.train()
    train_loss = 0
    progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{config['num_epochs']}")
    
    for batch in progress_bar:
        # Move batch to device
        batch = {k: v.to(device) for k, v in batch.items()}
        
        # Forward pass
        outputs = model(**batch)
        loss = outputs.loss
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        scheduler.step()
        
        train_loss += loss.item()
        progress_bar.set_postfix({"loss": loss.item()})
    
    avg_train_loss = train_loss / len(train_loader)
    print(f"Epoch {epoch+1}/{config['num_epochs']} - Avg. Training Loss: {avg_train_loss:.4f}")
    
    # Evaluation
    model.eval()
    val_loss = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in tqdm(val_loader, desc="Evaluating"):
            batch = {k: v.to(device) for k, v in batch.items()}
            labels = batch.pop("labels").cpu().numpy()
            
            outputs = model(**batch)
            loss = outputs.loss
            val_loss += loss.item()
            
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
    
    avg_val_loss = val_loss / len(val_loader)
    
    print(f"Validation Loss: {avg_val_loss:.4f}")
    print(f"Accuracy: {accuracy:.4f}, F1: {f1:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")
    
    # Save best model
    if f1 > best_f1:
        best_f1 = f1
        best_model_state = model.state_dict().copy()
        print(f"New best model with F1: {best_f1:.4f}")

# Save evaluation results
eval_results = {
    "accuracy": float(accuracy),
    "f1": float(f1),
    "precision": float(precision),
    "recall": float(recall),
    "val_loss": float(avg_val_loss)
}

with open(Path("data/processed/eval_results.json"), 'w') as f:
    json.dump(eval_results, f, indent=2)

# Save the best model state dictionary
print("Saving the model...")
model_path = Path(config["save_path"])

# If we found a best model during training, use that
if best_model_state is not None:
    model.load_state_dict(best_model_state)

with open(model_path, 'wb') as f:
    pickle.dump(model.state_dict(), f)

# Save the full model and tokenizer
os.makedirs(config["save_model_path"], exist_ok=True)
model.save_pretrained(config["save_model_path"])
tokenizer.save_pretrained(config["save_model_path"])

print(f"Model state dictionary saved to {model_path}")
print(f"Full model and tokenizer saved to {config['save_model_path']}")