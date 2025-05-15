import pandas as pd
from config.settings import REQUIRED_COLUMNS

def load_product_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(
        file_path,
        encoding="utf-8",
        engine="python",
        quotechar='"',
        skip_blank_lines=True
    )
    if not all(col in df.columns for col in ["PartNumber", "Title"]):
        df.columns = REQUIRED_COLUMNS[:len(df.columns)]
    if "PartNumber" not in df.columns or "Title" not in df.columns:
        raise KeyError("Missing required columns.")
    return df

def load_vehicle_data(file_path: str) -> pd.DataFrame:
    return pd.read_excel(file_path, header=None)

def load_brand_mappings(mapping_file: str) -> dict:
    mapping_df = pd.read_csv(mapping_file, header=None)
    return dict(zip(mapping_df[0].astype(str), mapping_df[1].astype(str))) 