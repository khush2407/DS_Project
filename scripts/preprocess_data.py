import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from transformers import DistilBertTokenizer
import logging
from pathlib import Path
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoEmotionsPreprocessor:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.emotion_columns = None
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        
    def load_data(self) -> None:
        """Load the raw dataset."""
        logger.info(f"Loading data from {self.data_path}")
        self.df = pd.read_csv(self.data_path)
        
        # Identify emotion columns
        metadata_columns = ['text', 'id', 'author', 'subreddit', 'link_id', 
                          'parent_id', 'created_utc', 'rater_id', 'example_very_unclear']
        self.emotion_columns = [col for col in self.df.columns if col not in metadata_columns]
        
        logger.info(f"Loaded {len(self.df)} samples with {len(self.emotion_columns)} emotion labels")
    
    def preprocess_text(self) -> None:
        """Clean and tokenize text data."""
        logger.info("Preprocessing text data...")
        
        # Clean text
        self.df['cleaned_text'] = self.df['text'].str.lower()
        self.df['cleaned_text'] = self.df['cleaned_text'].str.replace(r'http\S+|www\S+|https\S+', '', regex=True)
        self.df['cleaned_text'] = self.df['cleaned_text'].str.replace(r'[^\w\s]', '', regex=True)
        self.df['cleaned_text'] = self.df['cleaned_text'].str.replace(r'\s+', ' ', regex=True).str.strip()
        
        # Tokenize text
        logger.info("Tokenizing text...")
        self.df['tokenized'] = self.df['cleaned_text'].apply(
            lambda x: self.tokenizer.encode(
                x,
                add_special_tokens=True,
                max_length=128,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )[0].numpy()
        )
        
        # Generate attention mask
        self.df['attention_mask'] = self.df['tokenized'].apply(
            lambda x: (x != self.tokenizer.pad_token_id).astype(int)
        )
        
        logger.info("Text preprocessing complete")
    
    def prepare_labels(self) -> None:
        """Prepare emotion labels for training."""
        logger.info("Preparing emotion labels...")
        
        # Convert emotion columns to numpy array
        self.df['labels'] = self.df[self.emotion_columns].values.tolist()
        
        logger.info("Label preparation complete")
    
    def split_data(self) -> None:
        """Split data into train, validation, and test sets."""
        logger.info("Splitting data into train, validation, and test sets...")
        
        # First split: 80% train+val, 20% test
        train_val_df, test_df = train_test_split(
            self.df, test_size=0.2, random_state=42
        )
        
        # Second split: 80% train, 20% validation
        train_df, val_df = train_test_split(
            train_val_df, test_size=0.2, random_state=42
        )
        
        # Save splits
        train_df.to_pickle('data/processed/train.pkl')
        val_df.to_pickle('data/processed/val.pkl')
        test_df.to_pickle('data/processed/test.pkl')
        
        logger.info(f"Train set size: {len(train_df)}")
        logger.info(f"Validation set size: {len(val_df)}")
        logger.info(f"Test set size: {len(test_df)}")
    
    def save_metadata(self) -> None:
        """Save dataset metadata."""
        metadata = {
            'num_classes': len(self.emotion_columns),
            'emotion_labels': self.emotion_columns,
            'max_length': 128,
            'vocab_size': self.tokenizer.vocab_size
        }
        
        with open('data/processed/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=4)
        
        logger.info("Metadata saved to data/processed/metadata.json")
    
    def run_preprocessing(self) -> None:
        """Run the complete preprocessing pipeline."""
        # Create output directory
        Path('data/processed').mkdir(parents=True, exist_ok=True)
        
        # Run preprocessing steps
        self.load_data()
        self.preprocess_text()
        self.prepare_labels()
        self.split_data()
        self.save_metadata()
        
        logger.info("Preprocessing complete! Check the data/processed directory for results.")

def main():
    preprocessor = GoEmotionsPreprocessor('data/raw/goemotions.csv')
    preprocessor.run_preprocessing()

if __name__ == "__main__":
    main() 