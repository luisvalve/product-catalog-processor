#!/usr/bin/env python3
"""
Product Catalog Processor
Processes automotive product data and formats it for consistency.
"""
import pandas as pd
from rich.console import Console
from rich.table import Table
from yaspin import yaspin
from pathlib import Path

class ProductProcessor:
    def __init__(self):
        self.console = Console()
        self.input_file = Path("data/input.csv")
        self.output_file = Path("data/output.csv")

    def process_bullets(self, bullets_str: str) -> list:
        """Split bullet points into a list."""
        if not isinstance(bullets_str, str) or not bullets_str.strip():
            return []
        return [b.strip() for b in bullets_str.split("|")]

    def process_data(self) -> pd.DataFrame:
        """Process the product catalog data."""
        # Read input file
        df = pd.read_csv(self.input_file)
        
        # Process bullet points
        if "Bullets" in df.columns:
            # Process bullets and ensure we have exactly 5 columns
            processed_bullets = df["Bullets"].apply(self.process_bullets).apply(
                lambda x: x + [''] * (5 - len(x)) if len(x) < 5 else x[:5]
            ).tolist()
            
            bullets_df = pd.DataFrame(
                processed_bullets,
                columns=[f"bullet{i+1:02d}" for i in range(5)]
            )
            df = pd.concat([df, bullets_df], axis=1)
            df.drop("Bullets", axis=1, inplace=True)
        
        # Clean titles
        if "Title" in df.columns:
            df["Title"] = df["Title"].str.strip()
        
        return df

    def run(self):
        """Run the processing pipeline."""
        with yaspin(text="Processing product data...", color="cyan") as spinner:
            try:
                # Process data
                df_final = self.process_data()
                spinner.ok("✅")
                
                # Save output
                df_final.to_csv(self.output_file, index=False)
                print("\n")  # Add spacing
                
                # Show summary
                summary = Table(title="✅ Product Merge Summary", show_lines=True)
                summary.add_column("Metric", style="bold cyan")
                summary.add_column("Value", style="green")
                summary.add_row("Products Processed", str(len(df_final)))
                summary.add_row("Output Location", str(self.output_file))
                self.console.print(summary)
                
                print("\n✅ Processing completed successfully!\n")
                return True
                
            except Exception as e:
                spinner.fail("❌")
                print(f"\n❌ Error: {str(e)}\n")
                return False

def main():
    """Main entry point."""
    print("\n🚀 Starting Product Processor\n")
    processor = ProductProcessor()
    success = processor.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 