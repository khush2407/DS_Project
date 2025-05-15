import os
import requests
import pandas as pd
from pathlib import Path

def download_file(url: str, output_path: str):
    """Download a file from a URL."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def main():
    # Create necessary directories
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Dataset URLs - Updated to use Google Cloud Storage URLs
    base_url = "https://storage.googleapis.com/gresearch/goemotions/data/full_dataset"
    files = [
        "goemotions_1.csv",
        "goemotions_2.csv",
        "goemotions_3.csv"
    ]

    # Download and combine datasets
    dfs = []
    for file in files:
        url = f"{base_url}/{file}"
        output_path = data_dir / file
        print(f"Downloading {file}...")
        download_file(url, output_path)
        
        # Read the CSV file
        df = pd.read_csv(output_path)
        dfs.append(df)

    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Save the combined dataset
    output_file = data_dir / "goemotions.csv"
    combined_df.to_csv(output_file, index=False)
    print(f"Combined dataset saved to {output_file}")

    # Clean up individual files
    for file in files:
        (data_dir / file).unlink()

if __name__ == "__main__":
    main() 