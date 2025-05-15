"""Vehicle compatibility matching functionality."""
from typing import List, Optional, Tuple
import pandas as pd
from utils.data_cleaner import normalize_part_numbers
from utils.logger import logger

def load_product_data(file_path: str, required_columns: List[str]) -> pd.DataFrame:
    """Load and validate product data from CSV file.
    
    Args:
        file_path: Path to the product data file
        required_columns: List of required column names
        
    Returns:
        DataFrame containing product data
    """
    df = pd.read_csv(
        file_path,
        encoding="utf-8",
        engine="python",
        quotechar='"',
        skip_blank_lines=True
    )
    
    # Validate columns
    if not all(col in df.columns for col in ["PartNumber", "Title"]):
        df.columns = required_columns[:len(df.columns)]
    
    if "PartNumber" not in df.columns or "Title" not in df.columns:
        raise KeyError("Missing required columns: PartNumber and Title")
    
    return df

def load_vehicle_data(file_path: str) -> pd.DataFrame:
    """Load vehicle compatibility data from Excel file.
    
    Args:
        file_path: Path to the vehicle data file
        
    Returns:
        DataFrame containing vehicle compatibility data
    """
    return pd.read_excel(file_path, header=None)

def match_vehicle_data(product_df: pd.DataFrame, 
                      vehicle_df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """Match product data with vehicle compatibility information.
    
    Args:
        product_df: DataFrame containing product data
        vehicle_df: DataFrame containing vehicle compatibility data
        
    Returns:
        Tuple of (merged DataFrame, count of unmatched rows)
    """
    # Normalize part numbers for matching
    product_df = normalize_part_numbers(product_df)
    vehicle_df[0] = vehicle_df[0].astype(str).str.strip().str.upper()
    
    # Merge data
    merged_df = pd.merge(
        product_df,
        vehicle_df[[0, 11]],
        left_on="PartNumber",
        right_on=0,
        how='left'
    )
    
    # Rename merged column
    merged_df.rename(columns={11: "Merged Description"}, inplace=True)
    
    # Count unmatched rows
    unmatched = merged_df["Merged Description"].isna().sum()
    logger.info(f"Unmatched products: {unmatched}")
    
    # Remove merge key if exists
    if 0 in merged_df.columns:
        merged_df.drop(columns=[0], inplace=True)
    
    return merged_df, unmatched 