import pandas as pd
import glob

# find all cleaned csv files
files = glob.glob("datasets/tabula-2024-clean/*.csv")

dfs = []

for file in files:
    df = pd.read_csv(file)
    dfs.append(df)

# stack them
combined = pd.concat(dfs, ignore_index=True)

# save result
combined.to_csv("datasets/combined_tabula_dataset.csv", index=False)

print("Combined dataset saved.")