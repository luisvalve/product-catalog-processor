"""
Product Merger - Core functionality for merging and enriching automotive product data.
"""
import pandas as pd
import os
import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

@dataclass
class MergerConfig:
    """Configuration for the product merger."""
    data_dir: str = "data"
    log_file: str = "product_merge.log"
    primary_file: str = "product_catalog.csv"
    secondary_file: str = "vehicle_fitments.xlsx"
    abbr_file: str = "brand_mappings.csv"
    output_file: str = "enriched_catalog.csv"

class ProductMerger:
    """
    Core product merger class that handles merging and enriching automotive product data
    with vehicle fitment information.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.data_dir = "data"
        self.file1 = os.path.join(self.data_dir, "product_catalog.csv")
        self.file2 = os.path.join(self.data_dir, "vehicle_fitments.xlsx")
        self.abbr_file = os.path.join(self.data_dir, "brand_mappings.csv")
        self.output_file = os.path.join(self.data_dir, "enriched_catalog.csv")
        self.log_file = "product_merge.log"
        
    def log(self, message: str) -> None:
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp} {message}\n")

    def load_primary_file(self) -> pd.DataFrame:
        """Load and validate the primary CSV file."""
        df1 = pd.read_csv(
            self.file1,
            encoding="utf-8",
            engine="python",
            quotechar='"',
            skip_blank_lines=True
        )
        self.log("Loaded product_catalog.csv successfully.")
        
        # Fallback headers if necessary
        required_columns = ["PartNumber", "ASIN", "Title", "URL", "Bullets", "CharCount"]
        if not all(col in df1.columns for col in ["PartNumber", "Title"]):
            df1.columns = required_columns[:len(df1.columns)]

        if "PartNumber" not in df1.columns or "Title" not in df1.columns:
            raise KeyError("Missing required columns.")
            
        return df1

    def load_secondary_file(self) -> pd.DataFrame:
        """Load and validate the secondary Excel file."""
        df2 = pd.read_excel(self.file2, header=None)
        self.log("Loaded vehicle_fitments.xlsx.")
        return df2

    def normalize_merge_keys(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Normalize the merge keys."""
        df1["PartNumber"] = df1["PartNumber"].astype(str).str.strip().str.upper()
        df2[0] = df2[0].astype(str).str.strip().str.upper()
        return df1, df2

    def merge_data(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        """Merge the dataframes."""
        df_merged = pd.merge(
            df1,
            df2[[0, 11]],
            left_on="PartNumber",
            right_on=0,
            how='left'
        )
        df_merged.rename(columns={11: "Merged Description"}, inplace=True)
        self.log("Merged product info.")
        return df_merged

    def process_titles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process titles."""
        df["Title"] = df["Title"].apply(lambda x: x.strip().replace('"', '') if isinstance(x, str) else x)
        df["Title"] = df["Title"].apply(lambda x: x + " For" if isinstance(x, str) and not x.endswith("For") else x)
        return df

    def process_descriptions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process descriptions."""
        df["Merged Description"] = df["Merged Description"].apply(
            lambda x: f"VEHICLE FIT: {x.strip()}" if isinstance(x, str) and not x.startswith("VEHICLE FIT:") else x
        )
        return df

    def replace_abbreviations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Replace abbreviations."""
        if os.path.exists(self.abbr_file):
            abbr_df = pd.read_csv(self.abbr_file, header=None)
            abbr_map = dict(zip(abbr_df[0].astype(str), abbr_df[1].astype(str)))
            
            def replace_abbrs(text):
                if not isinstance(text, str):
                    return text
                for abbr, full in abbr_map.items():
                    text = text.replace(abbr, full)
                return text

            df["Merged Description"] = df["Merged Description"].apply(replace_abbrs)
        return df

    def normalize_model_year_blocks(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize model year blocks, handling both year ranges and single years.
        Only accepts years between 1955 and 2025.
        """
        def is_valid_year(year: int) -> bool:
            """Check if year is within valid range (1955-2025)."""
            return 1955 <= year <= 2025

        def normalize_blocks(text):
            if not isinstance(text, str):
                return text
            import re
            # Pattern for year ranges: (95-00) Model or (2015-2020) Model
            range_pattern = re.compile(r'\((\d{2,4})-(\d{2,4})\)\s+([^*,]+)')
            # Pattern for single years: (95) Model or (2015) Model
            single_pattern = re.compile(r'\((\d{2,4})\)\s+([^*,]+)')
            
            normalized_blocks = []
            
            # Process year ranges
            range_matches = range_pattern.findall(text)
            for y1, y2, model in range_matches:
                y1, y2 = int(y1), int(y2)
                # Convert 2-digit years to 4-digit
                y1 = 1900 + y1 if y1 < 100 and y1 >= 80 else 2000 + y1 if y1 < 100 else y1
                y2 = 1900 + y2 if y2 < 100 and y2 >= 80 else 2000 + y2 if y2 < 100 else y2
                
                # Only include if both years are valid
                if is_valid_year(y1) and is_valid_year(y2):
                    low, high = sorted([y1, y2])
                    normalized_blocks.append(f"{model.strip()} ({low}-{high})")
            
            # Process single years
            single_matches = single_pattern.findall(text)
            for year, model in single_matches:
                year = int(year)
                # Convert 2-digit years to 4-digit
                year = 1900 + year if year < 100 and year >= 80 else 2000 + year if year < 100 else year
                
                # Only include if year is valid
                if is_valid_year(year):
                    normalized_blocks.append(f"{model.strip()} ({year})")
            
            # If we found valid blocks, join them; otherwise, return empty description
            return "VEHICLE FIT: " + ", ".join(normalized_blocks) if normalized_blocks else "VEHICLE FIT: No valid year range"

        df["Merged Description"] = df["Merged Description"].apply(normalize_blocks)
        return df

    def enrich_titles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich titles with vehicle information."""
        def enrich_title(row):
            title = row["Title"]
            desc = row["Merged Description"]
            if not isinstance(title, str) or not isinstance(desc, str):
                return title
            desc_clean = desc.replace("VEHICLE FIT:", "").strip()
            # Updated pattern to match both ranges and single years
            matches = re.findall(r'(.+?)\s+\((\d{4}(?:-\d{4})?)\)', desc_clean)
            if len(matches) == 1:
                model, years = matches[0]
                vehicle_info = f"{years} {model.strip()}"
                return title.replace("For", f"For {vehicle_info}")
            return title

        df["Title"] = df.apply(enrich_title, axis=1)
        return df

    def process_bullets(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process bullet points."""
        if "Bullets" in df.columns:
            df["Bullets"] = df["Bullets"].apply(
                lambda x: x.replace(" | ", "@") if isinstance(x, str) else x
            )
            split_bullets = df["Bullets"].apply(
                lambda x: [b.strip() for b in str(x).split('@')] if pd.notnull(x) else []
            )
            max_bullets = min(5, split_bullets.map(len).max())

            for i in range(max_bullets):
                df[f"bullet0{i+1}"] = split_bullets.apply(lambda b: b[i] if i < len(b) else "")
        return df

    def finalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Finalize column order."""
        if 0 in df.columns:
            df.drop(columns=[0], inplace=True)

        bullet_cols = [col for col in df.columns if col.startswith("bullet")]
        final_columns = ["PartNumber", "ASIN", "Title", "Merged Description"] + bullet_cols
        if "URL" in df.columns:
            final_columns.append("URL")

        return df[[col for col in final_columns if col in df.columns]]

    def process(self) -> pd.DataFrame:
        """Main processing function that handles the complete product merging workflow."""
        # Load files
        df1 = self.load_primary_file()
        df2 = self.load_secondary_file()

        # Process data
        df1, df2 = self.normalize_merge_keys(df1, df2)
        df_merged = self.merge_data(df1, df2)
        
        # Log unmatched count
        unmatched = df_merged["Merged Description"].isna().sum()
        self.log(f"⚠️ Unmatched products from product_catalog.csv: {unmatched}")
        
        # Apply all transformations
        df_merged = self.process_titles(df_merged)
        df_merged = self.process_descriptions(df_merged)
        df_merged = self.replace_abbreviations(df_merged)
        df_merged = self.normalize_model_year_blocks(df_merged)
        df_merged = self.enrich_titles(df_merged)
        df_merged = self.process_bullets(df_merged)
        df_final = self.finalize_columns(df_merged)
        
        # Save output
        df_final.to_csv(self.output_file, index=False)
        self.log("Saved final output to enriched_catalog.csv")
        
        return df_final 