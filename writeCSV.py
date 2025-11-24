import pandas as pd
import App
import os

generated_csv = "generated application list.csv"

if os.path.exists(generated_csv):
    df = pd.read_csv(generated_csv, sep=",", header=0)
else:
    df = pd.read_csv("Liste Bewerbungen.csv", sep=",", header=0)

app = App.App()
for parameterFile in app.getAllParameterXml():
    cols, row = parameterFile.getRowCsv()
    # Check if already exists based on date and company
    existing = df[(df['beworben'] == row[0]) & (df['Firma'] == row[1])]
    if existing.empty:
        newDF = pd.DataFrame([row], columns=cols)
        df = pd.concat([df, newDF], ignore_index=True)
df.to_csv(generated_csv, index=False)
