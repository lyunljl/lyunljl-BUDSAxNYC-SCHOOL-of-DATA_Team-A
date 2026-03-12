import pandas as pd

# ----------------------------
# LOAD DATA
# ----------------------------
pluto = pd.read_csv("datasets/pluto25-raw.csv", low_memory=False)
tabula = pd.read_csv("datasets/tabula_with_bbl.csv", low_memory=False)

# ----------------------------
# CLEAN PLUTO BBL
# ----------------------------
pluto["bbl"] = pd.to_numeric(pluto["bbl"], errors="coerce")
pluto = pluto.dropna(subset=["bbl"]).copy()
pluto["bbl"] = pluto["bbl"].astype("Int64").astype(str).str.zfill(10)

# ----------------------------
# CLEAN TABULA BBL
# ----------------------------
tabula["bbl"] = tabula["bbl"].astype(str).str.strip()
tabula_valid = tabula[tabula["bbl"].str.fullmatch(r"\d{10}", na=False)].copy()

# unique stabilized parcel set
stabilized_bbls = set(tabula_valid["bbl"].drop_duplicates())

# ----------------------------
# CLEAN OTHER PLUTO FIELDS
# ----------------------------
pluto["unitsres"] = pd.to_numeric(pluto["unitsres"], errors="coerce")
pluto["zipcode"] = pd.to_numeric(pluto["zipcode"], errors="coerce").astype("Int64")

# keep only residential properties
pluto = pluto[pluto["unitsres"] > 0].copy()

# ----------------------------
# CREATE STABILIZATION FLAG
# ----------------------------
pluto["likely_rent_stabilized_binary"] = pluto["bbl"].isin(stabilized_bbls).astype(int)

pluto["stabilized_units"] = (
    pluto["unitsres"] * pluto["likely_rent_stabilized_binary"]
)

# ----------------------------
# AGGREGATE BY ZIP
# ----------------------------
zip_data = (
    pluto.groupby("zipcode", dropna=True)
    .agg(
        total_units=("unitsres", "sum"),
        stabilized_units=("stabilized_units", "sum"),
        stabilized_buildings=("likely_rent_stabilized_binary", "sum"),
        total_buildings=("bbl", "count")
    )
    .reset_index()
)

zip_data["stabilization_share"] = (
    zip_data["stabilized_units"] / zip_data["total_units"]
)

# ----------------------------
# SAVE OUTPUTS
# ----------------------------
pluto.to_csv("datasets/final-usables/pluto_with_rent_stabilization_flag.csv", index=False)
zip_data.to_csv("datasets/final-usables/final_zip_stabilization_dataset.csv", index=False)

# ----------------------------
# PRINT CHECKS
# ----------------------------
print("Done.")
print("Residential PLUTO rows:", len(pluto))
print("Unique valid stabilized Tabula BBLs:", len(stabilized_bbls))
print("Flagged stabilized PLUTO rows:", pluto["likely_rent_stabilized_binary"].sum())
print(zip_data.head())