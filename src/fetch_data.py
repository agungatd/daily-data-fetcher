import requests
import json
import logging
import sys
import os
import time

from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Parameterization ---
# Get parameters from environment variables with defaults
TARGET_CATEGORY = os.getenv('API_CATEGORY', 'Physics') 
OUTPUT_FILENAME = os.getenv('OUTPUT_FILE', f'/app/output/{TARGET_CATEGORY.lower()}_apis.json')
API_URL = "https://api.nobelprize.org/2.1/nobelPrizes"
PUSHGATEWAY_URL = os.getenv('PUSHGATEWAY_URL', 'pushgateway:9091') # Internal Docker network address
# For running locally connecting to localhost:9091
if os.getenv('RUNNING_LOCALLY') == 'true':
    PUSHGATEWAY_URL = os.getenv('PUSHGATEWAY_URL', 'localhost:9091') 
# --- End Parameterization ---

# --- Prometheus Metrics Definition ---
registry = CollectorRegistry() # Use a specific registry for the job

job_last_success_timestamp = Gauge(
    'data_fetcher_job_last_success_timestamp_seconds',
    'Timestamp of the last successful completion of the data fetcher job',
    registry=registry
)
records_fetched_total = Counter(
    'data_fetcher_records_fetched_total',
    'Total number of raw records fetched from the API by the job',
    ['category'], # Label to distinguish different runs
    registry=registry
)
records_filtered_total = Counter(
    'data_fetcher_records_filtered_total',
    'Total number of records remaining after filtering by the job',
    ['category'],
    registry=registry
)
job_duration_seconds = Gauge(
    'data_fetcher_job_duration_seconds',
    'Duration of the data fetcher job execution in seconds',
    ['category'],
    registry=registry
)
# --- End Prometheus Metrics Definition ---


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


# --- Function to Push Metrics ---
def push_metrics(duration, raw_count, filtered_count, category):
    try:
        # Set metric values
        job_last_success_timestamp.set_to_current_time()
        job_duration_seconds.labels(category=category).set(duration)
        # Counters should ideally reflect totals over time, but for a gauge-like view
        # of the last run via Pushgateway, setting might be okay for counts too, 
        # or use Gauges instead. Let's use counters and see how they behave.
        # Note: Pushgateway keeps the *last* pushed value for a metric+label set.
        records_fetched_total.labels(category=category).inc(raw_count) # Increment - better for counters
        records_filtered_total.labels(category=category).inc(filtered_count) # Increment

        # Push metrics to Pushgateway
        # Grouping key helps distinguish instances if multiple jobs push
        push_to_gateway(
            PUSHGATEWAY_URL, 
            job='data_fetcher_job', 
            registry=registry,
            grouping_key={'instance': f'data_fetcher_{category.lower()}'} 
        )
        logging.info(f"Successfully pushed metrics to Pushgateway at {PUSHGATEWAY_URL}")
    except Exception as e:
        logging.error(f"Error pushing metrics to Pushgateway: {e}")
        # Decide if this failure should stop the job (e.g., sys.exit(1))
        # For now, just log the error.
# --- End Function to Push Metrics ---


if __name__ == "__main__":
    start_time = time.time()
    logging.info("="*30)
    logging.info("Starting data fetching process...")
    logging.info(f"Parameter - Target Category: {TARGET_CATEGORY}")
    logging.info(f"Parameter - Output File: {OUTPUT_FILENAME}")
    logging.info(f"Parameter - Pushgateway URL: {PUSHGATEWAY_URL}")

    raw_data = fetch_data(API_URL)
    raw_entry_count = 0
    filtered_data = []

    if raw_data:
        raw_entry_count = raw_data.get('count', 0)

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

    # --- Push Metrics at the end ---
    push_metrics(
        duration=processing_time,
        raw_count=raw_entry_count,
        filtered_count=len(filtered_data),
        category=TARGET_CATEGORY
    )

    logging.info("Data fetching process completed successfully.")
    logging.info("="*30)
