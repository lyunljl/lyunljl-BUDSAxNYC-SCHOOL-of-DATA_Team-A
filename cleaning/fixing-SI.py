import pandas as pd
import numpy as np

# load Staten Island file
si = pd.read_csv(
    "datasets/tabula-2024-clean/tabula-2024-DHCR-Bldg-File-Staten-Island_cleaned.csv",
    low_memory=False
)

# make a clean string version of STATUS3
status3_str = si["STATUS3"].astype("string").str.strip()

# make sure BLOCK exists and is numeric-friendly
si["BLOCK"] = pd.to_numeric(si["BLOCK"], errors="coerce")

# -----------------------------
# Scenario 1:
# STATUS3 has text + trailing digits
# Example: "NON-EVICT COOP/CONDO 615"
# -----------------------------
mask_text_plus_digits = status3_str.str.match(r"^.*\D\s+\d{1,5}$", na=False)

extracted_block_1 = pd.to_numeric(
    status3_str[mask_text_plus_digits].str.extract(r"(\d{1,5})\s*$")[0],
    errors="coerce"
)

cleaned_status3_1 = (
    status3_str[mask_text_plus_digits]
    .str.replace(r"\s*\d{1,5}\s*$", "", regex=True)
    .str.strip()
)

si.loc[mask_text_plus_digits, "BLOCK"] = extracted_block_1
si.loc[mask_text_plus_digits, "STATUS3"] = cleaned_status3_1

# -----------------------------
# Scenario 2:
# STATUS3 has only digits
# Example: "3318"
# -----------------------------
mask_digits_only = status3_str.str.match(r"^\d{1,5}$", na=False)

extracted_block_2 = pd.to_numeric(
    status3_str[mask_digits_only],
    errors="coerce"
)

si.loc[mask_digits_only, "BLOCK"] = extracted_block_2
si.loc[mask_digits_only, "STATUS3"] = pd.NA

# optional: convert BLOCK to integer-like nullable type
si["BLOCK"] = pd.to_numeric(si["BLOCK"], errors="coerce").astype("Int64")

# quick diagnostics
print("\n--- STATEN ISLAND STATUS3/BLOCK FIX CHECK ---")
print("Total rows:", len(si))
print("Scenario 1 rows fixed:", mask_text_plus_digits.sum())
print("Scenario 2 rows fixed:", mask_digits_only.sum())
print("Non-missing BLOCK values:", si["BLOCK"].notna().sum())
print("Non-missing STATUS3 values:", si["STATUS3"].notna().sum())

print("\nSample cleaned rows:")
print(si.loc[mask_text_plus_digits | mask_digits_only, ["STATUS3", "BLOCK"]].head(20))

# save fixed file
si.to_csv(
    "datasets/tabula-2024-clean/tabula-2024-DHCR-Bldg-File-Staten-Island_fixed.csv",
    index=False
)