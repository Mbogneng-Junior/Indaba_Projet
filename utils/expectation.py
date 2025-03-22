import pandas as pd

# Charger les données
df = pd.read_csv('data/processed_data.csv')

# Afficher les colonnes commençant par indispo_ ou non_elig_
print("Colonnes commençant par indispo_ ou non_elig_:")
print([col for col in df.columns if col.startswith(('indispo_', 'non_elig_'))])

# Afficher les types de données pour ces colonnes
print("\nTypes de données des colonnes:")
print(df[[col for col in df.columns if col.startswith(('indispo_', 'non_elig_'))]].dtypes)
print(df.columns)