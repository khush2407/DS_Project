import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from collections import Counter
import re
from typing import Dict, List, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoEmotionsAnalyzer:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.emotion_columns = None
        self.text_column = 'text'
        
    def load_data(self) -> None:
        """Load and perform initial data inspection."""
        logger.info(f"Loading data from {self.data_path}")
        self.df = pd.read_csv(self.data_path)
        logger.info(f"Dataset shape: {self.df.shape}")
        
        # Identify emotion columns (all columns except metadata columns)
        metadata_columns = ['text', 'id', 'author', 'subreddit', 'link_id', 
                          'parent_id', 'created_utc', 'rater_id', 'example_very_unclear']
        self.emotion_columns = [col for col in self.df.columns if col not in metadata_columns]
        
        # Display basic information
        logger.info("\nDataset Info:")
        logger.info(self.df.info())
        
        # Display sample rows
        logger.info("\nSample rows:")
        logger.info(self.df.head())
        
    def clean_text(self, text: str) -> str:
        """Clean text data."""
        if not isinstance(text, str):
            return ""
        # Convert to lowercase
        text = text.lower()
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def analyze_emotions(self) -> Dict:
        """Analyze emotion distribution and patterns."""
        logger.info("\nAnalyzing emotion distribution...")
        
        # Calculate emotion frequencies
        emotion_counts = self.df[self.emotion_columns].sum().sort_values(ascending=False)
        
        # Create emotion distribution plot
        plt.figure(figsize=(12, 6))
        sns.barplot(x=emotion_counts.index, y=emotion_counts.values)
        plt.xticks(rotation=45, ha='right')
        plt.title('Distribution of Emotions in Dataset')
        plt.tight_layout()
        plt.savefig('data/processed/emotion_distribution.png')
        plt.close()
        
        return emotion_counts.to_dict()
    
    def analyze_text_length(self) -> None:
        """Analyze text length distribution."""
        logger.info("\nAnalyzing text length distribution...")
        
        # Clean text and calculate lengths
        self.df['cleaned_text'] = self.df[self.text_column].apply(self.clean_text)
        self.df['text_length'] = self.df['cleaned_text'].apply(len)
        
        # Create text length distribution plot
        plt.figure(figsize=(10, 6))
        sns.histplot(data=self.df, x='text_length', bins=50)
        plt.title('Distribution of Text Lengths')
        plt.xlabel('Text Length')
        plt.ylabel('Count')
        plt.savefig('data/processed/text_length_distribution.png')
        plt.close()
        
        # Print statistics
        logger.info(f"\nText Length Statistics:")
        logger.info(self.df['text_length'].describe())
    
    def analyze_emotion_correlations(self) -> None:
        """Analyze correlations between emotions."""
        logger.info("\nAnalyzing emotion correlations...")
        
        # Calculate correlation matrix
        corr_matrix = self.df[self.emotion_columns].corr()
        
        # Create correlation heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
        plt.title('Emotion Correlation Matrix')
        plt.tight_layout()
        plt.savefig('data/processed/emotion_correlations.png')
        plt.close()
    
    def analyze_multi_emotion(self) -> None:
        """Analyze how many emotions are typically present per text."""
        logger.info("\nAnalyzing multi-emotion patterns...")
        
        # Calculate number of emotions per text
        self.df['emotion_count'] = self.df[self.emotion_columns].sum(axis=1)
        
        # Create distribution plot
        plt.figure(figsize=(10, 6))
        sns.histplot(data=self.df, x='emotion_count', bins=range(0, 11))
        plt.title('Distribution of Number of Emotions per Text')
        plt.xlabel('Number of Emotions')
        plt.ylabel('Count')
        plt.savefig('data/processed/emotion_count_distribution.png')
        plt.close()
        
        # Print statistics
        logger.info("\nEmotion Count Statistics:")
        logger.info(self.df['emotion_count'].describe())
    
    def generate_summary_report(self) -> None:
        """Generate a comprehensive summary report."""
        logger.info("\nGenerating summary report...")
        
        def to_py(obj):
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            if isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            if isinstance(obj, (np.ndarray,)):
                return obj.tolist()
            return obj
        
        report = {
            'dataset_size': int(len(self.df)),
            'unique_emotions': int(len(self.emotion_columns)),
            'avg_text_length': float(self.df['text_length'].mean()),
            'emotion_distribution': {k: int(v) for k, v in self.analyze_emotions().items()},
            'text_length_stats': {k: to_py(v) for k, v in self.df['text_length'].describe().to_dict().items()},
            'emotion_count_stats': {k: to_py(v) for k, v in self.df['emotion_count'].describe().to_dict().items()},
            'metadata': {
                'subreddits': int(self.df['subreddit'].nunique()),
                'authors': int(self.df['author'].nunique()),
                'unclear_examples': int(self.df['example_very_unclear'].sum())
            }
        }
        
        # Save report
        with open('data/processed/dataset_summary.json', 'w') as f:
            json.dump(report, f, indent=4)
        
        logger.info("Summary report saved to data/processed/dataset_summary.json")
    
    def run_analysis(self) -> None:
        """Run the complete analysis pipeline."""
        # Create output directory
        Path('data/processed').mkdir(parents=True, exist_ok=True)
        
        # Run analysis steps
        self.load_data()
        self.analyze_emotions()
        self.analyze_text_length()
        self.analyze_emotion_correlations()
        self.analyze_multi_emotion()
        self.generate_summary_report()
        
        logger.info("\nAnalysis complete! Check the data/processed directory for results.")

def main():
    analyzer = GoEmotionsAnalyzer('data/raw/goemotions.csv')
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 