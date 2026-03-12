import pandas as pd

# load combined tabula dataset
tabula = pd.read_csv("datasets/combined_tabula_dataset.csv", low_memory=False)

# map borough names to numeric codes
borough_map = {
    "MANHATTAN": 1,
    "BRONX": 2,
    "BROOKLYN": 3,
    "QUEENS": 4,
    "STATEN ISLAND": 5
}

# create borocode
tabula["borocode"] = tabula["Borough"].str.upper().map(borough_map)

# clean and format block and lot
tabula["BLOCK"] = tabula["BLOCK"].astype(str).str.strip().str.zfill(5)
tabula["LOT"] = tabula["LOT"].astype(str).str.strip().str.zfill(4)

# create bbl
tabula["bbl"] = (
    tabula["borocode"].astype("Int64").astype(str) +
    tabula["BLOCK"] +
    tabula["LOT"]
)

# save new tabula file with bbl
tabula.to_csv("datasets/combined_tabula_with_bbl.csv", index=False)

print("Saved: datasets/tabula_with_bbl.csv")
print(tabula[["Borough", "BLOCK", "LOT", "borocode", "bbl"]].head())
print("Rows:", tabula.shape[0])