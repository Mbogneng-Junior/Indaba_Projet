import pandas as pd
import os

def get_unique_values(column_name):
    """Récupère les valeurs uniques d'une colonne du dataset"""
    # Chemin vers le fichier de données
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(current_dir), 'data', 'processed_data.csv')
    
    # Lecture des données
    df = pd.read_csv(data_path)
    
    # Récupération des valeurs uniques triées
    unique_values = sorted(df[column_name].unique())
    
    return unique_values
