"""Product data enrichment functionality."""
import re
from typing import Dict, Optional
import pandas as pd
from utils.data_cleaner import clean_title, normalize_model_year_range
from config.settings import MERGED_DESC_COLUMN

def load_brand_mappings(mapping_file: str) -> Dict[str, str]:
    """Load brand abbreviation mappings from file.
    
    Args:
        mapping_file: Path to the mappings file
        
    Returns:
        Dictionary of brand abbreviations to full names
    """
    mapping_df = pd.read_csv(mapping_file, header=None)
    return dict(zip(mapping_df[0].astype(str), mapping_df[1].astype(str)))

def replace_brand_abbreviations(text: str, mappings: Dict[str, str]) -> str:
    """Replace brand abbreviations with full names.
    
    Args:
        text: Text containing brand abbreviations
        mappings: Dictionary of abbreviation mappings
        
    Returns:
        Text with expanded brand names
    """
    if not isinstance(text, str):
        return text
    for abbr, full in mappings.items():
        text = text.replace(abbr, full)
    return text

def enrich_title_with_vehicle_info(row: pd.Series) -> str:
    """Enrich product title with vehicle year and model information.
    
    Args:
        row: DataFrame row containing title and description
        
    Returns:
        Enriched title string
    """
    title = row["Title"]
    desc = row[MERGED_DESC_COLUMN]
    
    if not isinstance(title, str) or not isinstance(desc, str):
        return title
        
    desc_clean = desc.replace("VEHICLE FIT:", "").strip()
    matches = re.findall(r'(.+?)\s+\((\d{4})-(\d{4})\)', desc_clean)
    
    if len(matches) == 1:
        model, y1, y2 = matches[0]
        vehicle_info = f"{y1}-{y2} {model.strip()}"
        return title.replace("For", f"For {vehicle_info}")
    
    return title

def enrich_product_data(df: pd.DataFrame, brand_mappings: Dict[str, str]) -> pd.DataFrame:
    """Enrich product data with additional information.
    
    Args:
        df: Input DataFrame
        brand_mappings: Dictionary of brand abbreviation mappings
        
    Returns:
        Enriched DataFrame
    """
    # Clean and normalize descriptions
    df[MERGED_DESC_COLUMN] = df[MERGED_DESC_COLUMN].apply(normalize_model_year_range)
    
    # Replace brand abbreviations
    df[MERGED_DESC_COLUMN] = df[MERGED_DESC_COLUMN].apply(
        lambda x: replace_brand_abbreviations(x, brand_mappings)
    )
    
    # Clean titles
    df["Title"] = df["Title"].apply(clean_title)
    
    # Enrich titles with vehicle information
    df["Title"] = df.apply(enrich_title_with_vehicle_info, axis=1)
    
    return df 