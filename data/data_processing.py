import pandas as pd
from datasets import load_dataset
from .config import DATASET_NAME, DATASET_SPLIT, SAMPLE_SIZE, TARGET_REPO
from .helpers import _parse_authors_json, _add_mentions_to_authors

# --- Core Logic Functions ---
def load_and_sample_data(dataset_name=DATASET_NAME, split=DATASET_SPLIT, sample_size=SAMPLE_SIZE):
    """Loads, samples, and performs initial processing of the dataset."""
    print(f"Loading dataset: {dataset_name} (split: {split})")
    ds = load_dataset(dataset_name, split=split, streaming=True)
    print(f"Taking a sample of {sample_size} items...")
    sample_data = [ex for _, ex in zip(range(sample_size), ds)]
    
    print("Processing sample data into a DataFrame...")
    rows = []
    for item in sample_data:
        for event in item.get('events', []):
            rows.append({
                'repo': item.get('repo'),
                'author': event.get('author'),
                'authors': item.get('usernames'), # This seems to be the list of authors involved in the issue
                'datetime': event.get('datetime'),
                'text': event.get('text')
            })
    df = pd.DataFrame(rows)
    
    # Clean 'authors' column
    df['authors'] = df['authors'].apply(_parse_authors_json)
    print("Initial DataFrame created.")
    return df

def filter_and_process_repo_data(df, target_repo=TARGET_REPO):
    """Filters data for a specific repository and processes it further."""
    print(f"Filtering data for repository: {target_repo}")
    repo_df = df[df['repo'] == target_repo].copy() # Use .copy() to avoid SettingWithCopyWarning
    
    if repo_df.empty:
        print(f"No data found for repository: {target_repo}")
        return pd.DataFrame()

    print("Adding mentions to authors list...")
    repo_df['authors_with_mentions'] = repo_df.apply(
        lambda row: _add_mentions_to_authors(row['authors'], row['text'] if pd.notnull(row['text']) else ''), 
        axis=1
    )
    
    # Use 'authors_with_mentions' for further processing if it's more comprehensive
    # For now, sticking to the original logic which used 'authors' for 'authors_except_original'
    repo_df["authors_except_original"] = repo_df.apply(
        lambda row: [a for a in row["authors"] if a != row["author"]],
        axis=1
    )
    
    repo_df = repo_df[repo_df["authors_except_original"].map(len) > 0]
    
    # Select relevant columns and convert datetime
    repo_df = repo_df[['author', 'datetime', 'authors_except_original']].copy() # Use .copy()
    repo_df['datetime'] = pd.to_datetime(
        repo_df['datetime'],
        format='ISO8601',
        utc=True,
        errors='coerce' # Handle potential parsing errors
    )
    repo_df.dropna(subset=['datetime'], inplace=True) # Drop rows where datetime conversion failed
    print(f"Processed data for {target_repo}.")
    return repo_df
