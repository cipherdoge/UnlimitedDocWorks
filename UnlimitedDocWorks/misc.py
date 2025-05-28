import pandas as pd
df = pd.read_csv("archive/DataCoSupplyChainDataset.csv",encoding ='windows-1252')
print(df['Sales'].sum())
