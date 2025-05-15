"""Main script for the product merge application."""
from rich.console import Console
from rich.table import Table
from yaspin import yaspin
from termcolor import cprint

from config.settings import (
    INPUT_PRODUCT_FILE,
    INPUT_VEHICLE_FILE,
    BRAND_MAPPINGS_FILE,
    OUTPUT_FILE,
    REQUIRED_COLUMNS,
    MERGED_DESC_COLUMN
)
from utils.logger import setup_logger
from utils.data_cleaner import split_bullets
from io_utils.file_loader import load_product_data, load_vehicle_data, load_brand_mappings
from io_utils.file_writer import save_output
from processors.product_enricher import enrich_product_data
from processors.vehicle_matcher import merge_vehicle_data

def main():
    """Main execution function."""
    logger = setup_logger(__name__)
    console = Console()
    
    cprint("\n🚀 Starting Amazon Product Merge Tool\n", "cyan", attrs=["bold"])
    logger.info("Started processing job.")

    try:
        # Load product data
        with yaspin(text="Loading product data...", color="cyan") as spinner:
            df1 = load_product_data(INPUT_PRODUCT_FILE)
            spinner.ok("✅")
            logger.info("Loaded file_001.csv successfully.")

        # Load vehicle data
        with yaspin(text="Loading vehicle data...", color="cyan") as spinner:
            df2 = load_vehicle_data(INPUT_VEHICLE_FILE)
            spinner.ok("✅")
            logger.info("Loaded file_002.xlsx.")

        # Merge data
        with yaspin(text="Merging product info...", color="cyan") as spinner:
            df_merged = merge_vehicle_data(df1, df2)
            spinner.ok("✅")
            logger.info("Merged product info.")

        # Load brand mappings
        brand_mappings = load_brand_mappings(BRAND_MAPPINGS_FILE)
        
        # Enrich data
        df_merged = enrich_product_data(df_merged, brand_mappings)
        
        # Split bullets
        if "Bullets" in df_merged.columns:
            df_merged = split_bullets(df_merged)
            logger.info("Split Bullets into bullet columns.")
        else:
            logger.info("No 'Bullets' column found.")

        # Move URL to last if exists
        if "URL" in df_merged.columns:
            url_col = df_merged.pop("URL")
            df_merged["URL"] = url_col
            logger.info("Moved URL to last column.")

        # Define final column order
        bullet_cols = [col for col in df_merged.columns if col.startswith("bullet")]
        final_columns = [
            "PartNumber",
            "ASIN",
            "Title",
            MERGED_DESC_COLUMN,
            "URL"
        ] + bullet_cols

        # Save final output
        df_final = df_merged[[col for col in final_columns if col in df_merged.columns]]
        save_output(df_final, OUTPUT_FILE)
        logger.info("Saved final output to file_001_updated.csv")

        # Summary Table
        summary_table = Table(title="✅ Product Merge Summary", show_lines=True)
        summary_table.add_column("Metric", style="bold cyan")
        summary_table.add_column("Value", style="green")
        summary_table.add_row("Rows processed", str(len(df1)))
        summary_table.add_row("Rows merged", str(df_merged[MERGED_DESC_COLUMN].notna().sum()))
        summary_table.add_row("Unmatched rows", str(df_merged[MERGED_DESC_COLUMN].isna().sum()))
        summary_table.add_row("Output file", str(OUTPUT_FILE))
        console.print(summary_table)

        cprint("\n✅ All tasks completed successfully!\n", "green", attrs=["bold"])
        logger.info("Finished.\n")

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise e

if __name__ == "__main__":
    main() 