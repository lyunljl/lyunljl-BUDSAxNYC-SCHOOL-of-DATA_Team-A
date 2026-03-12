import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("\n==============================")
print(" LOADING DATASET")
print("==============================\n")

df = pd.read_csv("datasets/final-usables/pluto_with_rent_stabilization_flag.csv", low_memory=False)

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])



print("\n==============================")
print(" COLUMN OVERVIEW")
print("==============================\n")

print(df.columns.tolist())

print("\nData types:\n")
print(df.dtypes)



print("\n==============================")
print(" MISSING VALUES")
print("==============================\n")

missing = df.isna().sum().sort_values(ascending=False)
missing_percent = (missing / len(df)) * 100

missing_table = pd.DataFrame({
    "missing_values": missing,
    "percent_missing": missing_percent
})

print(missing_table.head(20))



print("\n==============================")
print(" BOROUGH DISTRIBUTION")
print("==============================\n")

borough_counts = df["borough"].value_counts()
ymax = borough_counts.max() * 1.1

print(borough_counts)

plt.figure(figsize=(8,5))
borough_counts.plot(kind="bar", label="Buildings")
plt.title("Buildings by Borough")
plt.xlabel("Borough")
plt.ylabel("Count")
plt.ylim(0, ymax)
plt.legend()
plt.tight_layout()
plt.show()



print("\n==============================")
print(" ZIP CODE DISTRIBUTION")
print("==============================\n")

zip_counts = df["zipcode"].value_counts().head(15)
ymax = zip_counts.max() * 1.1

print(zip_counts)

plt.figure(figsize=(10,5))
zip_counts.plot(kind="bar", label="Buildings")
plt.title("Top 15 ZIP Codes")
plt.xlabel("ZIP Code")
plt.ylabel("Count")
plt.ylim(0, ymax)
plt.legend()
plt.tight_layout()
plt.show()



print("\n==============================")
print(" BUILDING AGE ANALYSIS")
print("==============================\n")

print(df["yearbuilt"].describe())

yearbuilt = df["yearbuilt"].dropna()
xmin = yearbuilt.min()
xmax = yearbuilt.max() * 1.05

plt.figure(figsize=(9,5))
plt.hist(yearbuilt, bins=50, label="Buildings")
plt.title("Year Built Distribution")
plt.xlabel("Year Built")
plt.ylabel("Buildings")
plt.xlim(xmin, xmax)
plt.legend()
plt.tight_layout()
plt.show()



print("\n==============================")
print(" BUILDING SIZE")
print("==============================\n")

print(df["unitsres"].describe())

unitsres = df["unitsres"].dropna()
xmin = unitsres.min()
xmax = unitsres.max() * 1.05

plt.figure(figsize=(9,5))
plt.hist(unitsres, bins=50, label="Buildings")
plt.title("Residential Units Distribution")
plt.xlabel("Units")
plt.ylabel("Buildings")
plt.xlim(xmin, xmax)
plt.legend()
plt.tight_layout()
plt.show()



print("\n==============================")
print(" BUILDING HEIGHT")
print("==============================\n")

print(df["numfloors"].describe())

numfloors = df["numfloors"].dropna()
xmin = numfloors.min()
xmax = numfloors.max() * 1.05

plt.figure(figsize=(9,5))
plt.hist(numfloors, bins=40, label="Buildings")
plt.title("Floors Distribution")
plt.xlabel("Floors")
plt.ylabel("Buildings")
plt.xlim(xmin, xmax)
plt.legend()
plt.tight_layout()
plt.show()



print("\n==============================")
print(" LOT SIZE VS BUILDING SIZE")
print("==============================\n")

scatter = df[["lotarea","bldgarea"]].dropna()

xmax = scatter["lotarea"].max() * 1.05
ymax = scatter["bldgarea"].max() * 1.05

plt.figure(figsize=(8,6))
plt.scatter(scatter["lotarea"], scatter["bldgarea"], alpha=0.3, s=10, label="Buildings")
plt.title("Lot Area vs Building Area")
plt.xlabel("Lot Area")
plt.ylabel("Building Area")
plt.xlim(0, xmax)
plt.ylim(0, ymax)
plt.legend()
plt.tight_layout()
plt.show()



print("\n==============================")
print(" LAND USE TYPES")
print("==============================\n")

landuse_counts = df["landuse"].value_counts()
print(landuse_counts)



print("\n==============================")
print(" BUILDING CLASS")
print("==============================\n")

print(df["bldgclass"].value_counts().head(20))



print("\n==============================")
print(" RENT STABILIZATION ANALYSIS")
print("==============================\n")

print(df["likely_rent_stabilized_binary"].value_counts())



print("\n==============================")
print(" STABILIZED UNITS")
print("==============================\n")

print(df["stabilized_units"].describe())

stabilized_units = df["stabilized_units"].dropna()
xmin = stabilized_units.min()
xmax = stabilized_units.max() * 1.05

plt.figure(figsize=(9,5))
plt.hist(stabilized_units, bins=40, label="Stabilized Units")
plt.title("Stabilized Units Distribution")
plt.xlabel("Units")
plt.ylabel("Buildings")
plt.xlim(xmin, xmax)
plt.legend()
plt.tight_layout()
plt.show()



print("\n==============================")
print(" STABILIZED BUILDINGS BY BOROUGH")
print("==============================\n")

stab_borough = df.groupby("borough")["likely_rent_stabilized_binary"].sum()
ymax = stab_borough.max() * 1.1

print(stab_borough)

plt.figure(figsize=(8,5))
stab_borough.plot(kind="bar", label="Stabilized Buildings")
plt.title("Rent Stabilized Buildings by Borough")
plt.xlabel("Borough")
plt.ylabel("Count")
plt.ylim(0, ymax)
plt.legend()
plt.tight_layout()
plt.show()



print("\n==============================")
print(" STABILIZED UNITS BY BOROUGH")
print("==============================\n")

stab_units_borough = df.groupby("borough")["stabilized_units"].sum()
ymax = stab_units_borough.max() * 1.1

print(stab_units_borough)

plt.figure(figsize=(8,5))
stab_units_borough.plot(kind="bar", label="Stabilized Units")
plt.title("Stabilized Units by Borough")
plt.xlabel("Borough")
plt.ylabel("Units")
plt.ylim(0, ymax)
plt.legend()
plt.tight_layout()
plt.show()



# ---- CREATE HUMAN READABLE LABELS ----

df["stabilized_label"] = df["likely_rent_stabilized_binary"].map({
    0: "Not Stabilized",
    1: "Likely Stabilized"
})



print("\n==============================")
print(" AVERAGE BUILDING SIZE (STABILIZED VS NOT)")
print("==============================\n")

print(df.groupby("stabilized_label")["unitsres"].describe())

avg_units = df.groupby("stabilized_label")["unitsres"].mean()
ymax = avg_units.max() * 1.1

plt.figure(figsize=(6,4))
avg_units.plot(kind="bar", label="Average Units")
plt.title("Average Residential Units by Stabilization Status")
plt.xlabel("Building Type")
plt.ylabel("Average Units")
plt.ylim(0, ymax)
plt.legend()
plt.tight_layout()
plt.show()



print("\n==============================")
print(" LARGEST BUILDINGS")
print("==============================\n")

print(
    df.sort_values("unitsres", ascending=False)[
        ["borough","zipcode","unitsres","numfloors","yearbuilt"]
    ].head(10)
)