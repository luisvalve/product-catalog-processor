"""Product data enrichment functionality."""
import re
from typing import Dict, Optional
import pandas as pd
from processors.description_normalizer import (
    prepend_vehicle_fit,
    replace_abbrs,
    normalize_model_year_blocks,
    remove_trailing_star,
    remove_alphanumeric_codes,
    remove_out_of_range_numeric_parens
)
from config.settings import MERGED_DESC_COLUMN
from io_utils.file_loader import load_brand_mappings
from utils.data_cleaner import clean_title

def enrich_product_data(df: pd.DataFrame, brand_mappings: dict) -> pd.DataFrame:
    df["Title"] = df["Title"].apply(clean_title)
    df[MERGED_DESC_COLUMN] = df[MERGED_DESC_COLUMN].apply(prepend_vehicle_fit)
    df[MERGED_DESC_COLUMN] = df[MERGED_DESC_COLUMN].apply(lambda x: replace_abbrs(x, brand_mappings))
    df[MERGED_DESC_COLUMN] = df[MERGED_DESC_COLUMN].apply(normalize_model_year_blocks)
    df[MERGED_DESC_COLUMN] = df[MERGED_DESC_COLUMN].apply(remove_trailing_star)
    df[MERGED_DESC_COLUMN] = df[MERGED_DESC_COLUMN].apply(remove_alphanumeric_codes)
    df[MERGED_DESC_COLUMN] = df[MERGED_DESC_COLUMN].apply(remove_out_of_range_numeric_parens)

    def enrich_title(row):
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
    df["Title"] = df.apply(enrich_title, axis=1)
    return df 