import requests
import json
import logging
import sys
import os
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Parameterization ---
# Get parameters from environment variables with defaults
TARGET_CATEGORY = os.getenv('API_CATEGORY', 'Physics') 
OUTPUT_FILENAME = os.getenv('OUTPUT_FILE', f'/app/output/{TARGET_CATEGORY.lower()}_apis.json')
# --- End Parameterization ---

API_URL = "https://api.nobelprize.org/2.1/nobelPrizes"


def fetch_data(url):
    """Fetches data from the specified URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses (4XX, 5XX)
        logging.info(f"Successfully fetched data from {url}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        sys.exit(1)  # Exit if fetching fails


def filter_category(data, category):
    """Filters entries based on the specified category."""
    if not data or 'nobelPrizes' not in data:
        logging.warning("No nobelPrizes found in data.")
        return []

    filtered = [
        entry for entry in data['nobelPrizes'] 
        if entry['category']['en'].lower() == category.lower()
    ]
    logging.info(f"Filtered {len(filtered)} nobelPrizes for category '{category}'")
    return filtered


# --- Data Quality ---
def validate_data(filtered_entries, category):
    """Performs basic data quality checks."""
    if not filtered_entries:
        logging.warning(f"Validation check: No entries found after filtering for category '{category}'. Processing continues, but check filter or source.")
        # Depending on requirements, you might exit here:
        # sys.exit(1)
        return True  # Allow processing empty results for now

    required_keys = ['awardYear', 'category', 'categoryFullName', 'dateAwarded', 'prizeAmount', 'prizeAmountAdjusted', 'links', 'laureates']
    all_entries_valid = True
    for i, entry in enumerate(filtered_entries):
        missing_keys = [key for key in required_keys if key not in entry or not entry[key]]
        if missing_keys:
            logging.error(f"Validation Error: Entry {i} (API: {entry.get('category', 'N/A')}) is missing or has empty required keys: {missing_keys}")
            all_entries_valid = False

        # Check if the category actually matches (post-filter sanity check)
        if entry.get('category', {}).get('en', '').lower() != category.lower():
            logging.error(f"Validation Error: Entry {i} (API: {entry.get('category', 'N/A')}) has wrong category '{entry.get('Category')}' after filtering for '{category}'")
            all_entries_valid = False

    if not all_entries_valid:
        logging.error("Critical data quality issues found. Aborting.")
        sys.exit(1)  # Exit if validation fails critically

    logging.info("Data quality checks passed.")
    return True
# --- End Data Quality ---

def save_data(data, filename):
    """Saves data to a JSON file."""
    try:
        # Ensure output directory exists (useful if running locally outside Docker initially)
        # import os
        # os.makedirs(os.path.dirname(filename), exist_ok=True)
        # Note: In Docker, we'll ensure /app/output exists via Dockerfile

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Successfully saved data to {filename}")
    except IOError as e:
        logging.error(f"Error saving data to {filename}: {e}")
        sys.exit(1)  # Exit if saving fails


if __name__ == "__main__":
    start_time = time.time()
    logging.info("="*30)
    logging.info("Starting data fetching process...")
    logging.info(f"Parameter - Target Category: {TARGET_CATEGORY}")
    logging.info(f"Parameter - Output File: {OUTPUT_FILENAME}")

    raw_data = fetch_data(API_URL)

    if raw_data:
        # Pass TARGET_CATEGORY to filter_entries
        filtered_data = filter_category(raw_data, category=TARGET_CATEGORY) 

        # --- Run Data Quality Checks ---
        validate_data(filtered_data, category=TARGET_CATEGORY)
        # --- End Data Quality Checks ---

        output_data = {
            "category_filter": TARGET_CATEGORY,
            "count": len(filtered_data),
            "metrics": {
                "raw_entry_count": raw_data.get('count', 0),
                "filtered_entry_count": len(filtered_data)
            },
            "entries": filtered_data
        }
        save_data(output_data, OUTPUT_FILENAME)
    else:
        logging.error("No raw data fetched. Skipping filtering and saving.")
        sys.exit(1)

    # For monitoring
    end_time = time.time()
    processing_time = end_time - start_time

    # --- Monitoring via Logging ---
    logging.info(f"Monitoring - Records Fetched (Raw Count): {raw_data.get('count', 'N/A')}")
    logging.info(f"Monitoring - Records Filtered ({TARGET_CATEGORY}): {len(filtered_data)}")
    logging.info(f"Monitoring - Processing Time: {processing_time:.4f} seconds")
    # --- End Monitoring via Logging ---

    logging.info("Data fetching process completed successfully.")
    logging.info("="*30)
