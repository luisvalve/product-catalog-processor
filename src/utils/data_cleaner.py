"""Data cleaning utilities for the product merge application."""
import re
from typing import Dict, List
import pandas as pd
from config.settings import VEHICLE_FIT_PREFIX

def normalize_part_numbers(df: pd.DataFrame, column: str = "PartNumber") -> pd.DataFrame:
    """Normalize part numbers by converting to uppercase and removing whitespace.
    
    Args:
        df: Input DataFrame
        column: Column name containing part numbers
        
    Returns:
        DataFrame with normalized part numbers
    """
    return df.assign(**{column: df[column].astype(str).str.strip().str.upper()})

def clean_title(title: str) -> str:
    """Clean product title by removing quotes and ensuring proper format.
    
    Args:
        title: Raw product title
        
    Returns:
        Cleaned title string
    """
    if not isinstance(title, str):
        return title
    title = title.strip().replace('"', '')
    if not title.endswith("For"):
        title = f"{title} For"
    return title

def normalize_model_year_range(text: str) -> str:
    """Normalize vehicle model year ranges in text.
    
    Preserves the original format: (2000) Infiniti I30 (VQ30DE) * (2000) Nissan Maxima (2988)
    """
    if not isinstance(text, str):
        return text
        
    # Add VEHICLE FIT: prefix if not present
    if not text.startswith("VEHICLE FIT:"):
        text = f"VEHICLE FIT: {text.strip()}"
    
    # Remove trailing ' *' if present
    text = text.replace(" *", "")
    
    return text

def split_bullets(df: pd.DataFrame, bullet_column: str = "Bullets", 
                 separator: str = "@", max_bullets: int = 5) -> pd.DataFrame:
    """Split bullet points into separate columns.
    
    Args:
        df: Input DataFrame
        bullet_column: Column containing bullet points
        separator: Character used to separate bullets
        max_bullets: Maximum number of bullet columns to create
        
    Returns:
        DataFrame with split bullet columns
    """
    if bullet_column not in df.columns:
        return df
        
    # Replace separator if needed
    df[bullet_column] = df[bullet_column].apply(
        lambda x: x.replace(" | ", separator) if isinstance(x, str) else x
    )
    
    # Split bullets into list
    split_bullets = df[bullet_column].apply(
        lambda x: [b.strip() for b in str(x).split(separator)] if pd.notnull(x) else []
    )
    
    # Create bullet columns
    max_bullets = min(max_bullets, split_bullets.map(len).max())
    for i in range(max_bullets):
        df[f"bullet{i+1:02d}"] = split_bullets.apply(
            lambda b: b[i] if i < len(b) else ""
        )
    
    return df 