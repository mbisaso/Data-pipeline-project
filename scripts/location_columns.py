#check columns in location dataset
import pandas as pd
import zipfile

with zipfile.ZipFile("data/raw/g_location_disambiguated.tsv.zip", 'r') as z:
    with z.open(z.namelist()[0]) as f:
        df = pd.read_csv(f, sep='\t', nrows=3)

print(df.columns.tolist())
print(df.head(3).to_string())