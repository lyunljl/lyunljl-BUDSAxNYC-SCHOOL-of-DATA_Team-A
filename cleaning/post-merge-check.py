import pandas as pd

# ----------------------------
# LOAD FILES
# ----------------------------
pluto_flagged = pd.read_csv("datasets/final-usables/pluto_with_rent_stabilization_flag.csv", low_memory=False)
tabula = pd.read_csv("datasets/tabula_with_bbl.csv", low_memory=False)
zip_data = pd.read_csv("datasets/final-usables/final_zip_stabilization_dataset.csv", low_memory=False)

# ----------------------------
# CLEAN KEY COLUMNS
# ----------------------------
pluto_flagged["bbl"] = pluto_flagged["bbl"].astype(str).str.strip()
tabula["bbl"] = tabula["bbl"].astype(str).str.strip()

# keep only valid 10-digit tabula BBLs
tabula_valid = tabula[tabula["bbl"].str.fullmatch(r"\d{10}", na=False)].copy()
tabula_bbls = set(tabula_valid["bbl"].drop_duplicates())

# make sure flag is numeric/bool-safe
if "likely_rent_stabilized_binary" in pluto_flagged.columns:
    flag_col = "likely_rent_stabilized_binary"
elif "likely_rent_stabilized" in pluto_flagged.columns:
    flag_col = "likely_rent_stabilized"
else:
    raise ValueError("No stabilization flag column found in PLUTO file.")

# normalize flag to 0/1
pluto_flagged[flag_col] = pluto_flagged[flag_col].replace({True: 1, False: 0}).astype(int)

# ----------------------------
# 1. BASIC COUNTS
# ----------------------------
print("\n=== BASIC COUNTS ===")
print("PLUTO flagged rows:", len(pluto_flagged))
print("Valid Tabula rows:", len(tabula_valid))
print("Unique valid Tabula BBLs:", len(tabula_bbls))
print("Flagged PLUTO rows:", pluto_flagged[flag_col].sum())

# ----------------------------
# 2. CHECK FLAGGED ROWS REALLY EXIST IN TABULA
# ----------------------------
print("\n=== FLAG CONSISTENCY CHECK ===")
flagged_rows = pluto_flagged[pluto_flagged[flag_col] == 1].copy()
bad_flagged = flagged_rows[~flagged_rows["bbl"].isin(tabula_bbls)]

print("Flagged PLUTO rows not found in Tabula:", len(bad_flagged))

if len(bad_flagged) > 0:
    print("\nSample bad flagged rows:")
    print(bad_flagged[["bbl", "zipcode", "unitsres"]].head(10))

# ----------------------------
# 3. CHECK TABULA COVERAGE IN PLUTO
# ----------------------------
print("\n=== TABULA COVERAGE IN PLUTO ===")
pluto_bbls = set(pluto_flagged["bbl"])
tabula_found_in_pluto = tabula_valid["bbl"].isin(pluto_bbls)

print("Share of valid Tabula BBLs found in PLUTO:", round(tabula_found_in_pluto.mean(), 4))
print("Count of valid Tabula BBLs found in PLUTO:", int(tabula_found_in_pluto.sum()))
print("Count of valid Tabula BBLs not found in PLUTO:", int((~tabula_found_in_pluto).sum()))

# ----------------------------
# 4. SAMPLE MANUAL CHECKS
# ----------------------------
print("\n=== SAMPLE MATCH CHECKS ===")
sample_bbls = list(tabula_valid["bbl"].drop_duplicates().sample(min(10, len(tabula_bbls)), random_state=42))

for bbl in sample_bbls:
    sample_match = pluto_flagged.loc[
        pluto_flagged["bbl"] == bbl,
        ["bbl", "zipcode", "unitsres", flag_col]
    ]
    print("\nBBL:", bbl)
    print(sample_match.head())

# ----------------------------
# 5. IMPOSSIBLE VALUE CHECKS
# ----------------------------
print("\n=== IMPOSSIBLE VALUE CHECKS ===")
print("Rows with missing zipcode:", pluto_flagged["zipcode"].isna().sum())
print("Rows with missing unitsres:", pluto_flagged["unitsres"].isna().sum())
print("Rows with unitsres < 0:", (pd.to_numeric(pluto_flagged["unitsres"], errors="coerce") < 0).sum())

if "stabilized_units" in pluto_flagged.columns:
    print("Rows where stabilized_units > unitsres:",
            (pd.to_numeric(pluto_flagged["stabilized_units"], errors="coerce") >
            pd.to_numeric(pluto_flagged["unitsres"], errors="coerce")).sum())
else:
    print("Column 'stabilized_units' not found.")

# ----------------------------
# 6. ZIP-LEVEL CHECKS
# ----------------------------
print("\n=== ZIP-LEVEL CHECKS ===")
print("ZIP dataset rows:", len(zip_data))

if "stabilization_share" in zip_data.columns:
    print("\nStabilization share summary:")
    print(zip_data["stabilization_share"].describe())

    print("\nZIPs with share < 0:", (zip_data["stabilization_share"] < 0).sum())
    print("ZIPs with share > 1:", (zip_data["stabilization_share"] > 1).sum())

    print("\nTop 15 ZIPs by stabilization share:")
    print(
        zip_data.sort_values("stabilization_share", ascending=False)[
            ["zipcode", "total_units", "stabilized_units", "stabilization_share"]
        ].head(15)
    )

    print("\nBottom 15 ZIPs by stabilization share:")
    print(
        zip_data.sort_values("stabilization_share", ascending=True)[
            ["zipcode", "total_units", "stabilized_units", "stabilization_share"]
        ].head(15)
    )
else:
    print("Column 'stabilization_share' not found in ZIP dataset.")

# ----------------------------
# 7. BOROUGH-LEVEL CHECKS
# ----------------------------
if "borough" in pluto_flagged.columns:
    print("\n=== BOROUGH-LEVEL CHECKS ===")

    borough_summary = (
        pluto_flagged.groupby("borough")
        .agg(
            total_units=("unitsres", "sum"),
            stabilized_units=("stabilized_units", "sum"),
            stabilized_buildings=(flag_col, "sum"),
            total_buildings=("bbl", "count")
        )
        .reset_index()
    )

    borough_summary["stabilization_share"] = (
        borough_summary["stabilized_units"] / borough_summary["total_units"]
    )

    print(borough_summary.sort_values("stabilization_share", ascending=False))
else:
    print("\nNo 'borough' column found for borough-level checks.")

# ----------------------------
# 8. FINAL VERDICT
# ----------------------------
print("\n=== FINAL VERDICT ===")

problems = []

if len(bad_flagged) > 0:
    problems.append("Some PLUTO rows were flagged stabilized even though their BBL is not in Tabula.")

if (~tabula_found_in_pluto).sum() > 0:
    problems.append("Some valid Tabula BBLs were not found in PLUTO.")

if "stabilization_share" in zip_data.columns and (zip_data["stabilization_share"] > 1).any():
    problems.append("Some ZIP stabilization shares are greater than 1.")

if "stabilization_share" in zip_data.columns and (zip_data["stabilization_share"] < 0).any():
    problems.append("Some ZIP stabilization shares are below 0.")

if len(problems) == 0:
    print("Audit passed. The merge logic appears consistent and the outputs look structurally valid.")
else:
    print("Audit found potential issues:")
    for p in problems:
        print("-", p)