from collections import defaultdict

def analyze_monthly_collaboration(repo_df):
    """Analyzes and accumulates collaboration data month over month."""
    if repo_df.empty:
        print("Cannot analyze monthly collaboration: DataFrame is empty.")
        return {}

    print("Analyzing monthly collaboration...")
    # Ensure 'datetime' is available and correctly formatted
    if 'datetime' not in repo_df.columns or repo_df['datetime'].isnull().all():
        print("Datetime column is missing or all null, cannot perform monthly analysis.")
        return {}

    repo_df_sorted = repo_df.copy()
    repo_df_sorted['month'] = repo_df_sorted['datetime'].dt.to_period('M').astype(str)
    repo_df_sorted = repo_df_sorted.sort_values(by='month')

    cumulative_edge_counter = defaultdict(int)
    collaboration_data_by_month = {}

    for month, group in repo_df_sorted.groupby('month'):
        for _, row in group.iterrows():
            source = row['author']
            targets = row['authors_except_original']
            
            if not source or not targets: # Skip if source or targets are missing
                continue

            for target in targets:
                if not target: # Skip if target is missing
                    continue
                if source != target: # Ensure interaction is not with self in this context
                    cumulative_edge_counter[(source, target)] += 1
        
        # Snapshot of cumulative edges up to this month
        collaboration_data_by_month[month] = [
            {"from": src, "to": tgt, "count": count}
            for (src, tgt), count in cumulative_edge_counter.items()
        ]
    print("Monthly collaboration analysis complete.")
    return collaboration_data_by_month
