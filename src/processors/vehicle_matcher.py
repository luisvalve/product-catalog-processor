"""Vehicle compatibility matching functionality."""
import pandas as pd
from utils.data_cleaner import normalize_part_numbers
from utils.logger import setup_logger
from io_utils.file_loader import load_product_data, load_vehicle_data

logger = setup_logger(__name__)

def merge_vehicle_data(product_df: pd.DataFrame, vehicle_df: pd.DataFrame) -> pd.DataFrame:
    """Merge product and vehicle data."""
    # Normalize merge keys
    product_df = normalize_part_numbers(product_df)
    vehicle_df[0] = vehicle_df[0].astype(str).str.strip().str.upper()
    
    # Merge data
    df_merged = pd.merge(
        product_df,
        vehicle_df[[0, 11]],
        left_on="PartNumber",
        right_on=0,
        how='left'
    )
    
    # Rename merged description column
    df_merged.rename(columns={11: "Merged Description"}, inplace=True)
    
    # Add VEHICLE FIT: prefix if not present
    df_merged["Merged Description"] = df_merged["Merged Description"].apply(
        lambda x: f"VEHICLE FIT: {x.strip()}" if isinstance(x, str) and not str(x).startswith("VEHICLE FIT:") else x
    )
    
    # Log unmatched products
    unmatched = df_merged["Merged Description"].isna().sum()
    logger.info(f"⚠️ Unmatched products from file_001.csv: {unmatched}")
    print(f"\n⚠️ Unmatched rows: {unmatched}")
    
    # Remove merge key column if exists
    if 0 in df_merged.columns:
        df_merged.drop(columns=[0], inplace=True)
    
    return df_merged 