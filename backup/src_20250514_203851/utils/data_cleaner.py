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
    
    Format: (2000) Model Name (VQ30DE)
    
    Args:
        text: Text containing year information
        
    Returns:
        Text with normalized year format
    """
    if not isinstance(text, str):
        return text

    # Remove "VEHICLE Fiat: " prefix if exists
    text = text.replace("VEHICLE Fiat: ", "")
    
    # First handle single years with asterisk separator
    if "*" in text:
        parts = text.split("*")
        normalized_parts = []
        for part in parts:
            part = part.strip()
            # Extract year, model, and engine code
            year_match = re.search(r'\((\d{4})\)\s+(.+?)(?:\s+\(([^)]+)\))?$', part)
            if year_match:
                year, model, engine = year_match.groups()
                if 1950 <= int(year) <= 2026:
                    model_str = f"{model.strip()}"
                    if engine:
                        model_str = f"{model_str} ({engine})"
                    normalized_parts.append(f"({year}) {model_str}")
        return f"{VEHICLE_FIT_PREFIX}{' * '.join(normalized_parts)}"
    
    # Handle year ranges and single years
    pattern = re.compile(r'\((\d{2,4})-(\d{2,4})\)\s+(.+?)(?:\s+\(([^)]+)\))?$|\((\d{4})\)\s+(.+?)(?:\s+\(([^)]+)\))?$')
    matches = pattern.finditer(text)
    
    normalized_blocks = []
    for match in matches:
        if match.group(1) and match.group(2):  # Year range
            y1, y2, model, engine = match.group(1), match.group(2), match.group(3), match.group(4)
            # Convert 2-digit years to 4-digit
            y1 = int(y1)
            y2 = int(y2)
            y1 = 1900 + y1 if y1 < 100 and y1 >= 80 else 2000 + y1 if y1 < 100 else y1
            y2 = 1900 + y2 if y2 < 100 and y2 >= 80 else 2000 + y2 if y2 < 100 else y2
            low, high = sorted([y1, y2])
            if 1950 <= low <= 2026 and 1950 <= high <= 2026:
                model_str = f"{model.strip()}"
                if engine:
                    model_str = f"{model_str} ({engine})"
                normalized_blocks.append(f"({low}-{high}) {model_str}")
        elif match.group(5):  # Single year
            year, model, engine = match.group(5), match.group(6), match.group(7)
            year = int(year)
            if 1950 <= year <= 2026:
                model_str = f"{model.strip()}"
                if engine:
                    model_str = f"{model_str} ({engine})"
                normalized_blocks.append(f"({year}) {model_str}")
    
    return f"{VEHICLE_FIT_PREFIX}{' * '.join(normalized_blocks)}" if normalized_blocks else text

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