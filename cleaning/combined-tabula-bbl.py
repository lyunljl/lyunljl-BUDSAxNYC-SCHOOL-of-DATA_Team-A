import pandas as pd

# ----------------------------
# LOAD TABULA DATA
# ----------------------------
tabula = pd.read_csv(
    "datasets/combined_tabula_dataset.csv",
    low_memory=False
)

# ----------------------------
# CREATE BOROUGH CODE
# ----------------------------
borough_map = {
    "MANHATTAN": 1,
    "BRONX": 2,
    "BROOKLYN": 3,
    "QUEENS": 4,
    "STATEN ISLAND": 5
}

tabula["borocode"] = tabula["Borough"].str.upper().map(borough_map)

# ----------------------------
# CLEAN BLOCK AND LOT
# ----------------------------
# Convert to numeric first to remove decimals like 123.0
tabula["BLOCK"] = pd.to_numeric(tabula["BLOCK"], errors="coerce")
tabula["LOT"] = pd.to_numeric(tabula["LOT"], errors="coerce")

# Convert to integer type
tabula["BLOCK"] = tabula["BLOCK"].astype("Int64")
tabula["LOT"] = tabula["LOT"].astype("Int64")
tabula["borocode"] = tabula["borocode"].astype("Int64")

# Pad with leading zeros to match NYC format
tabula["BLOCK"] = tabula["BLOCK"].astype(str).str.zfill(5)
tabula["LOT"] = tabula["LOT"].astype(str).str.zfill(4)

# ----------------------------
# CREATE BBL
# ----------------------------
tabula["bbl"] = (
    tabula["borocode"].astype(str)
    + tabula["BLOCK"]
    + tabula["LOT"]
)

# ----------------------------
# SAVE RESULT
# ----------------------------
tabula.to_csv("datasets/tabula_with_bbl.csv", index=False)

print("Saved: datasets/tabula_with_bbl.csv")

# ----------------------------
# QUICK DATA CHECKS
# ----------------------------

print("\nBBL length distribution:")
print(tabula["bbl"].str.len().value_counts(dropna=False))

print("\nUnique BBLs:", tabula["bbl"].nunique())
print("Total rows:", len(tabula))

print("\nExample rows:")
print(tabula[["Borough", "BLOCK", "LOT", "borocode", "bbl"]].head())