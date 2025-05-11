import json
import re

# --- Helper Functions ---
def _parse_authors_json(val):
    """Safely parses a JSON string into a list, returns empty list on error."""
    if isinstance(val, str):
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            return []
    return val if isinstance(val, list) else []

def _add_mentions_to_authors(authors_list, text_content):
    """Adds mentioned users in text to the list of authors if not already present."""
    mentions = [m for m in re.findall(r'@([A-Za-z0-9_-]+)', text_content) if not m.startswith('username_')]
    updated_authors = authors_list.copy()
    for m in mentions:
        if m not in updated_authors:
            updated_authors.append(m)
    return updated_authors
