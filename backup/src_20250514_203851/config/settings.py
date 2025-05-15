"""Configuration settings for the product merge application."""
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Input/Output file paths
INPUT_PRODUCT_FILE = DATA_DIR / "file_001.csv"
INPUT_VEHICLE_FILE = DATA_DIR / "file_002.xlsx"
BRAND_MAPPINGS_FILE = DATA_DIR / "car_brands_abbreviations.csv"
OUTPUT_FILE = DATA_DIR / "file_001_updated.csv"

# Required columns for processing
REQUIRED_COLUMNS = ["PartNumber", "ASIN", "Title", "URL", "Bullets", "CharCount"]

# Logging configuration
LOG_FILE = BASE_DIR / "product_merge.log"
LOG_FORMAT = "[%(asctime)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Column name mappings
MERGED_DESC_COLUMN = "Merged Description"
VEHICLE_FIT_PREFIX = "VEHICLE FIT: "

# Maximum number of bullet points to process
MAX_BULLETS = 5 