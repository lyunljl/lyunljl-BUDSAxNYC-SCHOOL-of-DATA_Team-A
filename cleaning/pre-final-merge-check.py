import pandas as pd

# ----------------------------
# LOAD DATA
# ----------------------------
pluto = pd.read_csv("datasets/pluto25-raw.csv", low_memory=False)
tabula = pd.read_csv("datasets/tabula_with_bbl.csv", low_memory=False)

print("Files loaded.")
print("PLUTO rows:", len(pluto))
print("Tabula rows:", len(tabula))


# ----------------------------
# BASIC COLUMN CHECKS
# ----------------------------
print("\n--- COLUMN CHECKS ---")
print("PLUTO has bbl column:", "bbl" in pluto.columns)
print("Tabula has bbl column:", "bbl" in tabula.columns)

required_tabula_cols = ["Borough", "BLOCK", "LOT", "bbl"]
for col in required_tabula_cols:
    print(f"Tabula has {col}:", col in tabula.columns)

required_pluto_cols = ["bbl", "zipcode", "borough", "unitsres"]
for col in required_pluto_cols:
    print(f"PLUTO has {col}:", col in pluto.columns)


# ----------------------------
# CLEAN BBL FIELDS
# ----------------------------
print("\n--- CLEANING BBL FIELDS ---")
pluto["bbl"] = pluto["bbl"].astype(str).str.replace(".0", "", regex=False).str.strip()
tabula["bbl"] = tabula["bbl"].astype(str).str.replace(".0", "", regex=False).str.strip()

print("BBL fields converted to string.")


# ----------------------------
# MISSING BBL CHECKS
# ----------------------------
print("\n--- MISSING BBL CHECKS ---")
print("PLUTO missing bbl:", pluto["bbl"].isna().sum())
print("Tabula missing bbl:", tabula["bbl"].isna().sum())

print("PLUTO blank bbl:", (pluto["bbl"] == "").sum())
print("Tabula blank bbl:", (tabula["bbl"] == "").sum())


# ----------------------------
# BBL FORMAT CHECKS
# ----------------------------
print("\n--- BBL FORMAT CHECKS ---")

print("\nPLUTO bbl length distribution:")
print(pluto["bbl"].str.len().value_counts(dropna=False).sort_index())

print("\nTabula bbl length distribution:")
print(tabula["bbl"].str.len().value_counts(dropna=False).sort_index())

pluto_valid_10 = pluto["bbl"].str.fullmatch(r"\d{10}", na=False)
tabula_valid_10 = tabula["bbl"].str.fullmatch(r"\d{10}", na=False)

print("\nPLUTO valid 10-digit bbl share:", pluto_valid_10.mean())
print("Tabula valid 10-digit bbl share:", tabula_valid_10.mean())

print("\nSample invalid PLUTO bbl values:")
print(pluto.loc[~pluto_valid_10, "bbl"].drop_duplicates().head(10).tolist())

print("\nSample invalid Tabula bbl values:")
print(tabula.loc[~tabula_valid_10, "bbl"].drop_duplicates().head(10).tolist())


# ----------------------------
# DUPLICATE CHECKS
# ----------------------------
print("\n--- DUPLICATE CHECKS ---")
print("PLUTO unique bbls:", pluto["bbl"].nunique())
print("Tabula unique bbls:", tabula["bbl"].nunique())

print("PLUTO duplicate bbl rows:", pluto["bbl"].duplicated().sum())
print("Tabula duplicate bbl rows:", tabula["bbl"].duplicated().sum())

print("\nTop repeated Tabula bbls:")
print(tabula["bbl"].value_counts().head(10))

print("\nTop repeated PLUTO bbls:")
print(pluto["bbl"].value_counts().head(10))


# ----------------------------
# OVERLAP CHECKS
# ----------------------------
print("\n--- OVERLAP CHECKS ---")

pluto_bbl_set = set(pluto.loc[pluto_valid_10, "bbl"])
tabula_bbl_set = set(tabula.loc[tabula_valid_10, "bbl"])

tabula_in_pluto = tabula.loc[tabula_valid_10, "bbl"].isin(pluto_bbl_set)
pluto_in_tabula = pluto.loc[pluto_valid_10, "bbl"].isin(tabula_bbl_set)

print("Share of valid Tabula bbls found in PLUTO:", tabula_in_pluto.mean())
print("Share of valid PLUTO bbls found in Tabula:", pluto_in_tabula.mean())

print("Count of shared valid bbls:", len(tabula_bbl_set.intersection(pluto_bbl_set)))
print("Count of valid Tabula bbls:", len(tabula_bbl_set))
print("Count of valid PLUTO bbls:", len(pluto_bbl_set))

print("\nSample Tabula bbls not found in PLUTO:")
print(tabula.loc[tabula_valid_10 & ~tabula["bbl"].isin(pluto_bbl_set), "bbl"]
      .drop_duplicates()
      .head(10)
      .tolist())

print("\nSample PLUTO bbls not found in Tabula:")
print(pluto.loc[pluto_valid_10 & ~pluto["bbl"].isin(tabula_bbl_set), "bbl"]
      .drop_duplicates()
      .head(10)
      .tolist())


# ----------------------------
# BOROUGH SANITY CHECKS
# ----------------------------
print("\n--- BOROUGH SANITY CHECKS ---")

if "Borough" in tabula.columns:
    print("\nTabula Borough distribution:")
    print(tabula["Borough"].value_counts(dropna=False))

if "borough" in pluto.columns:
    print("\nPLUTO borough distribution:")
    print(pluto["borough"].value_counts(dropna=False))


# ----------------------------
# ZIP COVERAGE CHECKS
# ----------------------------
print("\n--- ZIP CHECKS ---")

if "ZIP" in tabula.columns:
    print("\nTabula ZIP non-missing:", tabula["ZIP"].notna().sum())
    print("Tabula ZIP unique:", tabula["ZIP"].nunique(dropna=True))
    print("Top Tabula ZIP values:")
    print(tabula["ZIP"].value_counts(dropna=False).head(10))

if "zipcode" in pluto.columns:
    print("\nPLUTO zipcode non-missing:", pluto["zipcode"].notna().sum())
    print("PLUTO zipcode unique:", pluto["zipcode"].nunique(dropna=True))
    print("Top PLUTO zipcode values:")
    print(pluto["zipcode"].value_counts(dropna=False).head(10))


# ----------------------------
# RESIDENTIAL COVERAGE IN PLUTO
# ----------------------------
print("\n--- RESIDENTIAL CHECKS IN PLUTO ---")

if "unitsres" in pluto.columns:
    print("PLUTO rows with unitsres > 0:", (pluto["unitsres"] > 0).sum())
    print("PLUTO rows with unitsres missing:", pluto["unitsres"].isna().sum())
    print("PLUTO rows with unitsres = 0:", (pluto["unitsres"] == 0).sum())


# count rows where <NA> appears inside the BBL string
na_bbl_count = tabula["bbl"].astype(str).str.contains("<NA>", na=False).sum()
print("Occurrences of <NA> in bbl:", na_bbl_count)


# ----------------------------
# SAFE MERGE RISK SUMMARY
# ----------------------------
print("\n--- SAFE MERGE SUMMARY ---")

issues = []

if not pluto_valid_10.mean() > 0.95:
    issues.append("PLUTO has too many invalid BBLs.")

if not tabula_valid_10.mean() > 0.95:
    issues.append("Tabula has too many invalid BBLs.")

if not tabula_in_pluto.mean() > 0.50:
    issues.append("Too few Tabula BBLs match PLUTO. Merge key may be weak or broken.")

if tabula["bbl"].duplicated().sum() > 0:
    issues.append("Tabula has duplicate BBLs. You may need drop_duplicates() before merging.")

if pluto["bbl"].duplicated().sum() > 0:
    issues.append("PLUTO has duplicate BBLs. Check whether this is expected before merging.")

if len(issues) == 0:
    print("No major structural red flags found. Merge looks reasonably safe to try.")
else:
    print("Potential problems found:")
    for issue in issues:
        print("-", issue)

tabula["bbl"] = tabula["bbl"].astype(str).str.strip()

raw_rows = len(tabula)

tabula_valid = tabula[tabula["bbl"].str.fullmatch(r"\d{10}", na=False)].copy()
valid_rows = len(tabula_valid)

unique_valid_bbls = tabula_valid["bbl"].nunique()

removed_bad = raw_rows - valid_rows
removed_dupes_after_cleaning = valid_rows - unique_valid_bbls
removed_total = raw_rows - unique_valid_bbls

print("Raw rows:", raw_rows)
print("Rows after removing malformed BBLs:", valid_rows)
print("Unique valid BBLs after deduping:", unique_valid_bbls)

print("\nRemoved malformed BBL rows:", removed_bad)
print("Removed duplicate valid BBL rows:", removed_dupes_after_cleaning)
print("Removed total rows:", removed_total)

print("\nPercent retained:", round(unique_valid_bbls / raw_rows * 100, 2), "%")
print("Percent removed:", round(removed_total / raw_rows * 100, 2), "%")