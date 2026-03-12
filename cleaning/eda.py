import pandas as pd

# ----------------------------
# 1. Load datasets
# ----------------------------

# Load only necessary columns first if memory is tight
# pluto = pd.read_csv("data_pluto/pluto.csv", low_memory=False)
# likely = pd.read_csv("data_stabilized/likely_rent_stabilized.csv", low_memory=False)

pluto = pd.read_csv("datasets/pluto_25v4.csv")
likely = pd.read_csv("datasets/likely-rent-regulated.csv")

print("Datasets loaded")

# ----------------------------
# 2. Basic dataset shape
# ----------------------------

print("\nDataset sizes")
print("PLUTO shape:", pluto.shape)
print("Likely stabilized shape:", likely.shape)

# ----------------------------
# 3. Compare column lists
# ----------------------------

pluto_cols = set(pluto.columns)
likely_cols = set(likely.columns)

print("\nColumns in likely dataset:")
print(likely_cols)

print("\nColumns missing from PLUTO:")
print(likely_cols - pluto_cols)

print("\nColumns only in PLUTO:")
print(pluto_cols - likely_cols)

print("\nColumns shared by both:")
print(pluto_cols.intersection(likely_cols))

# ----------------------------
# 4. Check key column integrity
# ----------------------------

# convert BBL to string to avoid mismatch
pluto["bbl"] = pluto["bbl"].astype(str)
likely["bbl"] = likely["bbl"].astype(str)

print("\nBBL stats")

print("Unique BBL in PLUTO:", pluto["bbl"].nunique())
print("Unique BBL in likely:", likely["bbl"].nunique())

# intersection check
common_bbl = set(pluto["bbl"]).intersection(set(likely["bbl"]))
print("BBL overlap:", len(common_bbl))

# ----------------------------
# 5. Missing values summary
# ----------------------------

print("\nMissing values (top 10 columns)")

print(pluto.isnull().sum().sort_values(ascending=False).head(10))
print(likely.isnull().sum().sort_values(ascending=False).head(10))

# ----------------------------
# 6. Basic numeric statistics
# ----------------------------

print("\nPLUTO numeric summary")
print(pluto.describe())

print("\nLikely stabilized numeric summary")
print(likely.describe())

# ----------------------------
# 7. Distribution checks
# ----------------------------

print("\nResidential unit distribution")

print("PLUTO unitsres stats:")
print(pluto["unitsres"].describe())

print("\nLikely stabilized unitsres stats:")
print(likely["unitsres"].describe())

# ----------------------------
# 8. ZIP code coverage
# ----------------------------

print("\nZIP coverage")

print("Unique ZIPs in PLUTO:", pluto["zipcode"].nunique())
print("Unique ZIPs in likely:", likely["zipcode"].nunique())

# ----------------------------
# 9. Year built comparison
# ----------------------------

print("\nYear built distribution")

print("PLUTO yearbuilt:")
print(pluto["yearbuilt"].describe())

print("\nLikely stabilized yearbuilt:")
print(likely["yearbuilt"].describe())

# ----------------------------
# 10. Check duplicates
# ----------------------------

print("\nDuplicate BBL check")

print("PLUTO duplicates:", pluto["bbl"].duplicated().sum())
print("Likely duplicates:", likely["bbl"].duplicated().sum())