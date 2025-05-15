import re
import pandas as pd

def prepend_vehicle_fit(text: str) -> str:
    if not isinstance(text, str):
        return text
    return f"VEHICLE FIT: {text.strip()}" if not text.startswith("VEHICLE FIT:") else text

def replace_abbrs(text: str, brand_mappings: dict) -> str:
    if not isinstance(text, str):
        return text
    for abbr, full in brand_mappings.items():
        text = text.replace(abbr, full)
    return text

def normalize_model_year_blocks(text: str) -> str:
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

def remove_trailing_star(text: str) -> str:
    return str(text).replace(" *", "") if pd.notnull(text) else text

def remove_alphanumeric_codes(text: str) -> str:
    if not isinstance(text, str):
        return text
    return re.sub(r'\((?=[^)]*[A-Za-z])(?=[^)]*\d)[^)]*\)', '', text)

def remove_out_of_range_numeric_parens(text: str) -> str:
    if not isinstance(text, str):
        return text
    def repl(match):
        num = int(match.group(1))
        if num < 1950 or num > 2026:
            # Remove the code and any following space
            return ''
        return match.group(0)
    # Remove (number) and any following space if out of range
    return re.sub(r'\((\d+)\)\s*', repl, text) 