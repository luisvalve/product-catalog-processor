"""
Command-line interface for the Product Merger tool.
"""
from rich.console import Console
from rich.table import Table
from .merger import ProductMerger, MergerConfig

def main():
    """Main entry point for the product merger CLI."""
    console = Console()
    
    try:
        console.print("\n🚀 [cyan]Starting Product Merger[/cyan]\n")
        
        # Initialize and run merger
        merger = ProductMerger()
        df_final = merger.process()
        
        # Display summary
        unmatched = df_final["Merged Description"].isna().sum()
        matched = len(df_final) - unmatched
        
        table = Table(title="✅ Summary", show_lines=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Products", str(len(df_final)))
        table.add_row("Matched Products", str(matched))
        table.add_row("Unmatched Products", str(unmatched))
        table.add_row("Output File", merger.output_file)
        
        console.print(table)
        console.print("\n✅ [green]Processing completed successfully![/green]\n")
        
    except Exception as e:
        console.print(f"\n❌ [red]Error: {str(e)}[/red]\n")
        raise

if __name__ == "__main__":
    main() 