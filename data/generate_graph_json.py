import json
from huggingface_hub import login

# Import functions from new modules
from .config import TARGET_REPO, HUGGING_FACE_TOKEN
from .data_processing import load_and_sample_data, filter_and_process_repo_data
from .collaboration_analysis import analyze_monthly_collaboration

# --- Main Execution ---
def main():
    """Main function to run the analysis pipeline."""
    print("Starting SynapseAI analysis...")

    # Attempt to log in to Hugging Face if a token is provided
    if HUGGING_FACE_TOKEN:
        print("Attempting to log in to Hugging Face using token...")
        try:
            login(token=HUGGING_FACE_TOKEN)
            print("Successfully logged in to Hugging Face.")
        except Exception as e:
            print(f"Failed to log in to Hugging Face: {e}")
            print("Proceeding without explicit login. This may fail for private/gated datasets.")
    else:
        print("HUGGING_FACE_TOKEN not found in .env. Proceeding without explicit login.")
        print("This may fail for private/gated datasets.")
        print("To enable login, add HUGGING_FACE_TOKEN to your .env file.")

    initial_df = load_and_sample_data()
    
    if initial_df.empty:
        print("No data loaded. Exiting.")
        return

    # Step 2: Filter and process data for the target repository
    repo_specific_df = filter_and_process_repo_data(initial_df, target_repo=TARGET_REPO)
    
    if repo_specific_df.empty:
        print(f"No data to process for {TARGET_REPO}. Exiting further analysis for this repo.")
        return

    # Step 4: Analyze monthly collaboration
    monthly_data = analyze_monthly_collaboration(repo_specific_df)
    
    # Step 5: Export monthly collaboration data to JSON
    output_file = f"{TARGET_REPO.replace('/', '_')}_monthly_collaboration.json"
    print(f"Exporting monthly collaboration data to {output_file}...")
    try:
        with open(output_file, 'w') as f:
            json.dump(monthly_data, f, indent=4)
        print(f"Monthly collaboration data successfully exported to {output_file}.")
    except Exception as e:
        print(f"Failed to export monthly collaboration data: {e}")

if __name__ == "__main__":
    main()
