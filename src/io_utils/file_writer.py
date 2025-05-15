import pandas as pd

def save_output(df: pd.DataFrame, output_file: str):
    df.to_csv(output_file, index=False) 