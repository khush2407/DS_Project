import sys
import os
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np

# Add the backend directory to the path so we can import the services
sys.path.append(os.path.abspath('backend'))

# Import the emotion service
try:
    from services.emotion_service import EmotionService
    print("Successfully imported EmotionService from backend")
except ImportError as e:
    print(f"Error importing EmotionService: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)

def analyze_text(emotion_service, text):
    """Analyze text using the emotion service."""
    print(f"\nAnalyzing text: '{text}'")
    
    try:
        # Get predictions from emotion service
        emotions, primary_emotion = emotion_service.detect_emotions(text)
        
        print(f"\nPrimary emotion: {primary_emotion}")
        print("\nTop emotions:")
        for emotion, prob in sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {emotion}: {prob:.4f}")
        
        # Get emotion summary
        summary = emotion_service.get_emotion_summary(emotions)
        print(f"\nEmotion summary:\n{summary}")
        
        return emotions, primary_emotion, summary
    
    except Exception as e:
        print(f"Error analyzing text: {e}")
        return None, None, None

def plot_emotions(emotions, output_path=None):
    """Plot emotions as a bar chart."""
    if not emotions:
        print("No emotions to plot")
        return
    
    # Sort emotions by value
    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_emotions[:10])  # Show top 10 emotions
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(labels, values, color='skyblue')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.2f}', ha='center', va='bottom')
    
    plt.title('Emotion Probabilities')
    plt.xlabel('Emotions')
    plt.ylabel('Probability')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        print(f"Plot saved to {output_path}")
    else:
        plt.show()
    
    plt.close()

def batch_analyze(emotion_service, texts, output_dir=None):
    """Analyze multiple texts and save results."""
    results = []
    
    for i, text in enumerate(texts):
        print(f"\n--- Text {i+1}/{len(texts)} ---")
        emotions, primary_emotion, summary = analyze_text(emotion_service, text)
        
        if emotions and primary_emotion:
            result = {
                "text": text,
                "primary_emotion": primary_emotion,
                "emotions": emotions,
                "summary": summary
            }
            results.append(result)
            
            # Plot emotions if output directory is specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                plot_path = os.path.join(output_dir, f"emotions_{i+1}.png")
                plot_emotions(emotions, plot_path)
    
    # Save results if output directory is specified
    if output_dir and results:
        results_path = os.path.join(output_dir, "inference_results.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {results_path}")
    
    return results

def interactive_mode(emotion_service):
    """Run in interactive mode."""
    print("\nEmotion Analysis Interactive Mode")
    print("Type 'exit' to quit\n")
    
    while True:
        text = input("\nEnter text to analyze: ")
        if text.lower() == 'exit':
            break
        
        emotions, primary_emotion, summary = analyze_text(emotion_service, text)
        
        if emotions:
            # Plot emotions
            plot_emotions(emotions)
            
            print("\n" + "-"*50)

def main():
    parser = argparse.ArgumentParser(description="Run inference using the backend emotion service")
    parser.add_argument("--text", type=str, help="Text to analyze")
    parser.add_argument("--file", type=str, help="File containing text to analyze")
    parser.add_argument("--output", type=str, help="Output directory for results")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    args = parser.parse_args()
    
    # Initialize the emotion service
    emotion_service = EmotionService()
    
    # Create output directory if specified
    if args.output:
        os.makedirs(args.output, exist_ok=True)
    
    if args.interactive:
        interactive_mode(emotion_service)
    
    elif args.text:
        # Analyze single text
        emotions, primary_emotion, summary = analyze_text(emotion_service, args.text)
        
        if emotions and args.output:
            plot_path = os.path.join(args.output, "emotions.png")
            plot_emotions(emotions, plot_path)
    
    elif args.file:
        # Analyze text from file
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if '\n' in text:
                # Multiple lines, treat as multiple texts
                texts = [line.strip() for line in text.split('\n') if line.strip()]
                batch_analyze(emotion_service, texts, args.output)
            else:
                # Single text
                emotions, primary_emotion, summary = analyze_text(emotion_service, text)
                
                if emotions and args.output:
                    plot_path = os.path.join(args.output, "emotions.png")
                    plot_emotions(emotions, plot_path)
        
        except Exception as e:
            print(f"Error reading file: {e}")
    
    else:
        # No arguments provided, use sample texts
        print("No text provided. Analyzing sample texts...")
        
        sample_texts = [
            "I'm feeling so happy today! Everything is going well and I'm excited about the future.",
            "I'm feeling really down today. Nothing seems to be going right and I miss my friends.",
            "I can't believe they did that! It's so frustrating and unfair. I'm really upset about it.",
            "I'm worried about my upcoming presentation. What if I mess up? I can't stop thinking about it.",
            "Wow! I didn't expect that at all. This is such an unexpected turn of events."
        ]
        
        batch_analyze(emotion_service, sample_texts, args.output)

if __name__ == "__main__":
    main()