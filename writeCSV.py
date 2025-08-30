import pandas as pd
import App

df = pd.read_csv("Liste Bewerbungen.csv", sep=",", header=0)

app = App.App()
for parameterFile in app.getAllParameterXml():
    cols, row = parameterFile.getRowCsv()
    newDF = pd.DataFrame([row], columns=cols)
    df = pd.concat([df, newDF], ignore_index=True)
df.to_csv("generated application list.csv", index=False)
