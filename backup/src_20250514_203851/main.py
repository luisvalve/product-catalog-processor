"""Main script for the product merge application."""
from rich.console import Console
from rich.table import Table
from yaspin import yaspin

from config.settings import (
    INPUT_PRODUCT_FILE,
    INPUT_VEHICLE_FILE,
    BRAND_MAPPINGS_FILE,
    OUTPUT_FILE,
    REQUIRED_COLUMNS,
    MAX_BULLETS
)
from utils.logger import logger
from utils.data_cleaner import split_bullets
from processors.product_enricher import load_brand_mappings, enrich_product_data
from processors.vehicle_matcher import load_product_data, load_vehicle_data, match_vehicle_data

def main():
    """Main execution function."""
    console = Console()
    console.print("\n🚀 Starting Amazon Product Merge Tool\n", style="cyan bold")
    logger.info("Started processing job.")

    try:
        # Load product data
        with yaspin(text="Loading product data...", color="cyan") as spinner:
            df1 = load_product_data(INPUT_PRODUCT_FILE, REQUIRED_COLUMNS)
            spinner.ok("✅")
        logger.info("Loaded product data successfully.")

        # Load vehicle data
        with yaspin(text="Loading vehicle data...", color="cyan") as spinner:
            df2 = load_vehicle_data(INPUT_VEHICLE_FILE)
            spinner.ok("✅")
        logger.info("Loaded vehicle data successfully.")

        # Match data
        with yaspin(text="Merging product info...", color="cyan") as spinner:
            merged_df, unmatched = match_vehicle_data(df1, df2)
            spinner.ok("✅")
        logger.info("Merged product info successfully.")

        # Load and apply brand mappings
        brand_mappings = load_brand_mappings(BRAND_MAPPINGS_FILE)
        merged_df = enrich_product_data(merged_df, brand_mappings)
        logger.info("Enriched product data with brand information.")

        # Process bullet points
        if "Bullets" in merged_df.columns:
            merged_df = split_bullets(merged_df, max_bullets=MAX_BULLETS)
            logger.info(f"Split Bullets into {MAX_BULLETS} columns.")

        # Organize final columns
        bullet_cols = [col for col in merged_df.columns if col.startswith("bullet")]
        final_columns = ["PartNumber", "ASIN", "Title", "Merged Description", "URL"] + bullet_cols
        df_final = merged_df[[col for col in final_columns if col in merged_df.columns]]

        # Save output
        df_final.to_csv(OUTPUT_FILE, index=False)
        logger.info(f"Saved final output to {OUTPUT_FILE}")

        # Display summary
        summary_table = Table(title="✅ Product Merge Summary", show_lines=True)
        summary_table.add_column("Metric", style="bold cyan")
        summary_table.add_column("Value", style="green")
        summary_table.add_row("Rows processed", str(len(df1)))
        summary_table.add_row("Rows merged", str(merged_df['Merged Description'].notna().sum()))
        summary_table.add_row("Unmatched rows", str(unmatched))
        summary_table.add_row("Output file", str(OUTPUT_FILE))
        console.print(summary_table)

        console.print("\n✅ All tasks completed successfully!\n", style="green bold")
        logger.info("Finished successfully.")

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        console.print(f"\n❌ Error: {str(e)}\n", style="red bold")
        raise

if __name__ == "__main__":
    main() 