import pandas as pd
import os
import re
from yaspin import yaspin
from termcolor import cprint
from rich.console import Console
from rich.table import Table
from datetime import datetime

# === Logging Setup ===
log_file = "product_merge.log"
console = Console()

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} {message}\n")

# === File paths ===
data_dir = "data"
file1 = os.path.join(data_dir, "file_001.csv")
file2 = os.path.join(data_dir, "file_002.xlsx")
abbr_file = os.path.join(data_dir, "car_brands_abbreviations.csv")
output_file = os.path.join(data_dir, "file_001_updated.csv")

cprint("\n🚀 Starting Amazon Product Merge Tool\n", "cyan", attrs=["bold"])
log("Started processing job.")

# === Load file_001.csv ===
with yaspin(text="Loading file_001.csv...", color="cyan") as spinner:
    try:
        df1 = pd.read_csv(
            file1,
            encoding="utf-8",
            engine="python",
            quotechar='"',
            skip_blank_lines=True
        )
        spinner.ok("✅")
        log("Loaded file_001.csv successfully.")
    except Exception as e:
        spinner.fail("❌")
        log(f"❌ Failed to load file_001.csv: {str(e)}")
        raise e

# === Fallback headers if necessary ===
required_columns = ["PartNumber", "ASIN", "Title", "URL", "Bullets", "CharCount"]
if not all(col in df1.columns for col in ["PartNumber", "Title"]):
    df1.columns = required_columns[:len(df1.columns)]

if "PartNumber" not in df1.columns or "Title" not in df1.columns:
    raise KeyError("Missing required columns.")

# === Load file_002.xlsx ===
with yaspin(text="Loading file_002.xlsx...", color="cyan") as spinner:
    df2 = pd.read_excel(file2, header=None)
    spinner.ok("✅")
log("Loaded file_002.xlsx.")

# === Normalize merge keys ===
df1["PartNumber"] = df1["PartNumber"].astype(str).str.strip().str.upper()
df2[0] = df2[0].astype(str).str.strip().str.upper()

# === Merge data ===
with yaspin(text="Merging product info...", color="cyan") as spinner:
    df_merged = pd.merge(
        df1,
        df2[[0, 11]],
        left_on="PartNumber",
        right_on=0,
        how='left'
    )
    df_merged.rename(columns={11: "Merged Description"}, inplace=True)
    spinner.ok("✅")
log("Merged product info.")

unmatched = df_merged["Merged Description"].isna().sum()
log(f"⚠️ Unmatched products from file_001.csv: {unmatched}")
print(f"\n⚠️ Unmatched rows: {unmatched}")

# === Clean Title ===
df_merged["Title"] = df_merged["Title"].apply(lambda x: x.strip().replace('"', '') if isinstance(x, str) else x)
df_merged["Title"] = df_merged["Title"].apply(lambda x: x + " For" if isinstance(x, str) and not x.endswith("For") else x)

# === Prepend VEHICLE FIT:
df_merged["Merged Description"] = df_merged["Merged Description"].apply(
    lambda x: f"VEHICLE FIT: {x.strip()}" if isinstance(x, str) and not x.startswith("VEHICLE FIT:") else x
)

# === Replace brand abbreviations
abbr_df = pd.read_csv(abbr_file, header=None)
abbr_map = dict(zip(abbr_df[0].astype(str), abbr_df[1].astype(str)))

def replace_abbrs(text):
    if not isinstance(text, str):
        return text
    for abbr, full in abbr_map.items():
        text = text.replace(abbr, full)
    return text

df_merged["Merged Description"] = df_merged["Merged Description"].apply(replace_abbrs)

# === Normalize model-year ranges
def normalize_model_year_blocks(text):
    if not isinstance(text, str):
        return text
    pattern = re.compile(r'\((\d{2,4})-(\d{2,4})\)\s+([^*]+)')
    matches = pattern.findall(text)
    normalized_blocks = []
    for y1, y2, model in matches:
        y1, y2 = int(y1), int(y2)
        y1 = 1900 + y1 if y1 < 100 and y1 >= 80 else 2000 + y1 if y1 < 100 else y1
        y2 = 1900 + y2 if y2 < 100 and y2 >= 80 else 2000 + y2 if y2 < 100 else y2
        low, high = sorted([y1, y2])
        normalized_blocks.append(f"{model.strip()} ({low}-{high})")
    return "VEHICLE FIT: " + ", ".join(normalized_blocks) if normalized_blocks else text

df_merged["Merged Description"] = df_merged["Merged Description"].apply(normalize_model_year_blocks)

# === Remove trailing ' *'
df_merged["Merged Description"] = df_merged["Merged Description"].apply(
    lambda x: str(x).replace(" *", "") if pd.notnull(x) else x
)

# === Enrich Title with year/model if single match
def enrich_title(row):
    title = row["Title"]
    desc = row["Merged Description"]
    if not isinstance(title, str) or not isinstance(desc, str):
        return title
    desc_clean = desc.replace("VEHICLE FIT:", "").strip()
    matches = re.findall(r'(.+?)\s+\((\d{4})-(\d{4})\)', desc_clean)
    if len(matches) == 1:
        model, y1, y2 = matches[0]
        vehicle_info = f"{y1}-{y2} {model.strip()}"
        return title.replace("For", f"For {vehicle_info}")
    return title

df_merged["Title"] = df_merged.apply(enrich_title, axis=1)

# === Split Bullets column into bullet01-bullet05 using '@'
if "Bullets" in df_merged.columns:
    df_merged["Bullets"] = df_merged["Bullets"].apply(
        lambda x: x.replace(" | ", "@") if isinstance(x, str) else x
    )
    split_bullets = df_merged["Bullets"].apply(
        lambda x: [b.strip() for b in str(x).split('@')] if pd.notnull(x) else []
    )
    max_bullets = min(5, split_bullets.map(len).max())

    for i in range(max_bullets):
        df_merged[f"bullet0{i+1}"] = split_bullets.apply(lambda b: b[i] if i < len(b) else "")
    log(f"Split Bullets into {max_bullets} bullet columns.")
else:
    log("No 'Bullets' column found.")

# === Remove column [0] if exists (merge key)
if 0 in df_merged.columns:
    df_merged.drop(columns=[0], inplace=True)
    log("Removed column [0] from merged output.")

# === Move URL to last
if "URL" in df_merged.columns:
    url_col = df_merged.pop("URL")
    df_merged["URL"] = url_col
    log("Moved URL to last column.")

# === Define final column order
bullet_cols = [col for col in df_merged.columns if col.startswith("bullet")]

final_columns = [
    "PartNumber",
    "ASIN",
    "Title",
    "Merged Description",
    "URL"
] + bullet_cols

df_final = df_merged[[col for col in final_columns if col in df_merged.columns]]
df_final.to_csv(output_file, index=False)
log("Saved final output to file_001_updated.csv")

# === Summary Table
summary_table = Table(title="✅ Product Merge Summary", show_lines=True)
summary_table.add_column("Metric", style="bold cyan")
summary_table.add_column("Value", style="green")
summary_table.add_row("Rows processed", str(len(df1)))
summary_table.add_row("Rows merged", str(df_merged['Merged Description'].notna().sum()))
summary_table.add_row("Unmatched rows", str(unmatched))
summary_table.add_row("Output file", output_file)
console.print(summary_table)

cprint("\n✅ All tasks completed successfully!\n", "green", attrs=["bold"])
log("Finished.\n")
