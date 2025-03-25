import pandas as pd


df = pd.read_csv('data/processed_data.csv')
print('Colonnes du dataset:\n', df.columns.tolist())
print('\nTypes des colonnes:\n', df.dtypes); 
print('\nAperçu des données:\n', df.head())