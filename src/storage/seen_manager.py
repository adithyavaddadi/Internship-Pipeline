import json
import os
from src.config.settings import get_seen_file_path
from src.utils.logger import log_success, log_warning

def load_seen() -> set:
    """Loads the set of scraped and processed internship URLs from the seen database JSON file."""
    seen_path = get_seen_file_path()
    if os.path.exists(seen_path):
        try:
            with open(seen_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data)
        except Exception as e:
            log_warning(f"Failed to load seen database ({e}). Starting fresh.")
    return set()

def save_seen(seen_urls: set) -> None:
    """Saves the set of tracked internship URLs to the seen database JSON file."""
    seen_path = get_seen_file_path()
    try:
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(seen_path), exist_ok=True)
        with open(seen_path, "w", encoding="utf-8") as f:
            json.dump(list(seen_urls), f, indent=4)
        log_success("Saved processed internship URLs to the seen tracker.")
    except Exception as e:
        log_warning(f"Could not save seen database ({e}).")
