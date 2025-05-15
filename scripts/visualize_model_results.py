import json
import os
import matplotlib.pyplot as plt
import numpy as np
import argparse
from pathlib import Path

def load_evaluation_results(file_path):
    """Load evaluation results from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            results = json.load(f)
        return results
    except Exception as e:
        print(f"Error loading evaluation results: {e}")
        return None

def plot_metrics(results, output_dir):
    """Plot and save metrics visualization."""
    if not results:
        print("No results to visualize")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot overall metrics
    metrics = ['accuracy', 'f1', 'precision', 'recall']
    values = [results.get(metric, 0) for metric in metrics]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(metrics, values, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.4f}', ha='center', va='bottom')
    
    plt.title('Model Performance Metrics')
    plt.ylim(0, 1.1)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'overall_metrics.png'))
    plt.close()
    
    # Plot per-class metrics if available
    if 'per_class_metrics' in results:
        per_class = results['per_class_metrics']
        emotions = list(per_class.keys())
        
        # Sort emotions by F1 score
        emotions = sorted(emotions, key=lambda x: per_class[x].get('f1', 0), reverse=True)
        
        # Plot top 15 emotions by F1 score for readability
        top_emotions = emotions[:15]
        
        f1_scores = [per_class[e].get('f1', 0) for e in top_emotions]
        precision_scores = [per_class[e].get('precision', 0) for e in top_emotions]
        recall_scores = [per_class[e].get('recall', 0) for e in top_emotions]
        
        plt.figure(figsize=(15, 8))
        x = np.arange(len(top_emotions))
        width = 0.25
        
        plt.bar(x - width, f1_scores, width, label='F1', color='#3498db')
        plt.bar(x, precision_scores, width, label='Precision', color='#2ecc71')
        plt.bar(x + width, recall_scores, width, label='Recall', color='#e74c3c')
        
        plt.xlabel('Emotions')
        plt.ylabel('Score')
        plt.title('Top 15 Emotions by F1 Score')
        plt.xticks(x, top_emotions, rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'top_emotions_metrics.png'))
        plt.close()
        
        # Plot bottom 15 emotions by F1 score
        if len(emotions) > 15:
            bottom_emotions = emotions[-15:]
            
            f1_scores = [per_class[e].get('f1', 0) for e in bottom_emotions]
            precision_scores = [per_class[e].get('precision', 0) for e in bottom_emotions]
            recall_scores = [per_class[e].get('recall', 0) for e in bottom_emotions]
            
            plt.figure(figsize=(15, 8))
            x = np.arange(len(bottom_emotions))
            width = 0.25
            
            plt.bar(x - width, f1_scores, width, label='F1', color='#3498db')
            plt.bar(x, precision_scores, width, label='Precision', color='#2ecc71')
            plt.bar(x + width, recall_scores, width, label='Recall', color='#e74c3c')
            
            plt.xlabel('Emotions')
            plt.ylabel('Score')
            plt.title('Bottom 15 Emotions by F1 Score')
            plt.xticks(x, bottom_emotions, rotation=45, ha='right')
            plt.legend()
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'bottom_emotions_metrics.png'))
            plt.close()
    
    # Plot confusion matrix if available
    if 'confusion_matrix' in results:
        try:
            cm = np.array(results['confusion_matrix'])
            plt.figure(figsize=(12, 10))
            plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
            plt.title('Confusion Matrix')
            plt.colorbar()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
            plt.close()
        except Exception as e:
            print(f"Error plotting confusion matrix: {e}")

def main():
    parser = argparse.ArgumentParser(description="Visualize model evaluation results")
    parser.add_argument("--results", type=str, default="data/processed/eval_results.json",
                        help="Path to evaluation results JSON file")
    parser.add_argument("--output", type=str, default="data/visualization",
                        help="Output directory for visualizations")
    args = parser.parse_args()
    
    # Load results
    results = load_evaluation_results(args.results)
    
    if results:
        # Plot metrics
        plot_metrics(results, args.output)
        print(f"Visualizations saved to {args.output}")
        
        # Print summary
        print("\nModel Performance Summary:")
        for metric in ['accuracy', 'f1', 'precision', 'recall']:
            if metric in results:
                print(f"{metric.capitalize()}: {results[metric]:.4f}")
    else:
        print("Failed to load results. Please check the file path.")

if __name__ == "__main__":
    main()