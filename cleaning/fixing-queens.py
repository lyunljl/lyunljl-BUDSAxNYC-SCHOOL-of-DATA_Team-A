import pandas as pd
import numpy as np

# load file
queens = pd.read_csv(
    "datasets/tabula-2024-clean/tabula-2024-DHCR-Bldg-File-Queens_cleaned.csv",
    low_memory=False
)

# make sure the relevant columns exist and are treated as strings
for col in ["STATUS3 BLOCK", "Unnamed: 11", "STATUS3"]:
    if col in queens.columns:
        queens[col] = queens[col].replace(["nan", "NaN"], np.nan)

status3_block = queens["STATUS3 BLOCK"].astype(str).str.strip()
unnamed_11 = queens["Unnamed: 11"]
status3_existing = queens["STATUS3"] if "STATUS3" in queens.columns else pd.Series(index=queens.index, dtype="object")

# create empty output columns
queens["STATUS3_clean"] = pd.NA
queens["BLOCK_clean"] = pd.NA

# -------------------------
# Scenario 2:
# if Unnamed: 11 has a value, use that as BLOCK
# keep existing STATUS3 for that row
# -------------------------
mask_unnamed = unnamed_11.notna()

queens.loc[mask_unnamed, "BLOCK_clean"] = pd.to_numeric(
    unnamed_11[mask_unnamed], errors="coerce"
)

queens.loc[mask_unnamed, "STATUS3_clean"] = status3_existing[mask_unnamed]

# -------------------------
# Scenario 1:
# STATUS3 BLOCK has text + trailing number
# split into STATUS3 and BLOCK
# only apply where BLOCK_clean is still missing
# -------------------------
mask_text_num = (
    queens["BLOCK_clean"].isna()
    & status3_block.str.match(r"^.*\D\s+\d{1,5}$", na=False)
)

queens.loc[mask_text_num, "BLOCK_clean"] = pd.to_numeric(
    status3_block[mask_text_num].str.extract(r"(\d{1,5})\s*$")[0],
    errors="coerce"
)

queens.loc[mask_text_num, "STATUS3_clean"] = (
    status3_block[mask_text_num]
    .str.replace(r"\s*\d{1,5}\s*$", "", regex=True)
    .str.strip()
)

# -------------------------
# Scenario 3:
# STATUS3 BLOCK has only a number
# move it into BLOCK and leave STATUS3 empty
# only apply where BLOCK_clean is still missing
# -------------------------
mask_num_only = (
    queens["BLOCK_clean"].isna()
    & status3_block.str.match(r"^\d{1,5}$", na=False)
)

queens.loc[mask_num_only, "BLOCK_clean"] = pd.to_numeric(
    status3_block[mask_num_only], errors="coerce"
)

queens.loc[mask_num_only, "STATUS3_clean"] = pd.NA

# convert BLOCK to numeric
queens["BLOCK_clean"] = pd.to_numeric(queens["BLOCK_clean"], errors="coerce")

# replace old columns with clean ones
if "STATUS3" in queens.columns:
    queens.drop(columns=["STATUS3"], inplace=True)

if "BLOCK" in queens.columns:
    queens.drop(columns=["BLOCK"], inplace=True)

queens.rename(
    columns={
        "STATUS3_clean": "STATUS3",
        "BLOCK_clean": "BLOCK"
    },
    inplace=True
)

# drop broken merged column
queens.drop(columns=["STATUS3 BLOCK"], inplace=True)

# optionally drop Unnamed: 11 too since it has been absorbed
queens.drop(columns=["Unnamed: 11"], inplace=True)

# move BLOCK right after STATUS3
cols = list(queens.columns)
status3_idx = cols.index("STATUS3")
cols.insert(status3_idx + 1, cols.pop(cols.index("BLOCK")))
queens = queens[cols]

# inspect
print(queens[["STATUS3", "BLOCK"]].head(30))
print("Non-missing BLOCK values:", queens["BLOCK"].notna().sum())
print("Non-missing STATUS3 values:", queens["STATUS3"].notna().sum())
print("Total rows:", len(queens))

# save cleaned file
queens.to_csv(
    "datasets/tabula-2024-clean/fixed_tabula-2024-DHCR-Bldg-File-Queens.csv",
    index=False
)