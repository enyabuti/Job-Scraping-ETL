import os
import sys
import pandas as pd
from sqlalchemy import create_engine

# Add project root directory to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.config import APP_ID, APP_KEY, DB_URL, LOG_LEVEL, SCRAPE_NUM_PAGES
from src.extract import scrape_jobs
from src.transform import clean_data
from src.load import load_to_db

import logging

# Configure logging
logging.basicConfig(level=LOG_LEVEL)

def display_results():
    """
    Fetch and display the first few rows of the data from the database.
    """
    try:
        engine = create_engine(DB_URL)
        query = "SELECT * FROM jobs LIMIT 10;"  # Replace 'jobs' with your table name
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)

        if df.empty:
            logging.warning("No data found in the database.")
        else:
            logging.info("Displaying the first 10 rows of the job data:")
            print(df)
    except Exception as e:
        logging.error(f"Error displaying results: {e}")

def main():
    logging.info("Starting ETL pipeline...")
    
    # Extract jobs
    logging.info(f"Scraping {SCRAPE_NUM_PAGES} pages of job postings...")
    raw_jobs = scrape_jobs(APP_ID, APP_KEY, "Remote", num_pages=SCRAPE_NUM_PAGES)

    # Debug raw jobs
    if not raw_jobs or not isinstance(raw_jobs, list):
        logging.error("scrape_jobs returned an empty or invalid result. Ensure the scraping logic works correctly.")
        return
    logging.info(f"Raw jobs fetched: {len(raw_jobs)}")
    logging.debug(f"Sample raw jobs: {raw_jobs[:5]}")  # Print first 5 jobs

    # Transform data
    logging.info("Transforming data...")
    try:
        cleaned_jobs = clean_data(raw_jobs)
        if cleaned_jobs.empty:
            logging.warning("No data to load after transformation.")
            return
    except Exception as e:
        logging.error(f"Error during data transformation: {e}")
        return
    
    # Load into database
    logging.info("Loading data into the database...")
    try:
        load_to_db(cleaned_jobs, DB_URL)
        logging.info("Data loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading data into the database: {e}")
        return

    # Display the results
    try:
        display_results()
    except Exception as e:
        logging.error(f"Error displaying results: {e}")
    
    logging.info("ETL pipeline completed successfully.")

if __name__ == "__main__":
    main()
