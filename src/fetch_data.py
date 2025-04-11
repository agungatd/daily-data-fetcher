import requests
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_URL = "https://api.publicapis.org/entries"
OUTPUT_FILE = "/app/output/animals_apis.json" # Path inside the container

def fetch_data(url):
    """Fetches data from the specified URL."""
    try:
        response = requests.get(url)
        response.raise_for_status() # Raises HTTPError for bad responses (4XX, 5XX)
        logging.info(f"Successfully fetched data from {url}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        sys.exit(1) # Exit if fetching fails

def filter_entries(data, category="Animals"):
    """Filters entries based on the specified category."""
    if not data or 'entries' not in data:
        logging.warning("No entries found in data.")
        return []

    filtered = [entry for entry in data['entries'] if entry.get('Category') == category]
    logging.info(f"Filtered {len(filtered)} entries for category '{category}'")
    return filtered

def save_data(data, filename):
    """Saves data to a JSON file."""
    try:
        # Ensure output directory exists (useful if running locally outside Docker initially)
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True) 
        # Note: In Docker, we'll ensure /app/output exists via Dockerfile

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Successfully saved data to {filename}")
    except IOError as e:
        logging.error(f"Error saving data to {filename}: {e}")
        sys.exit(1) # Exit if saving fails

if __name__ == "__main__":
    logging.info("Starting data fetching process...")
    raw_data = fetch_data(API_URL)
    filtered_data = filter_entries(raw_data)
    # Create a structured output
    output_data = {
        "category_filter": "Animals",
        "count": len(filtered_data),
        "entries": filtered_data
    }
    save_data(output_data, OUTPUT_FILE)
    logging.info("Data fetching process completed.")

