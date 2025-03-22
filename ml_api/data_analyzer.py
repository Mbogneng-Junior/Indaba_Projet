import pandas as pd
import json
import os

def extract_unique_values():
    # Chemin vers les données
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, 'data', 'processed_data.csv')
    
    # Charger les données
    df = pd.read_csv(data_path)
    
    # Extraire les valeurs uniques pour chaque champ
    unique_values = {
        'Profession': sorted(df['Profession'].dropna().unique().tolist()),
        'Quartier_de_Residence': sorted(df['Quartier de Résidence'].dropna().unique().tolist()),
        'Arrondissement_de_residence': sorted(df['Arrondissement de résidence'].dropna().unique().tolist()),
        'Genre': sorted(df['Genre'].dropna().unique().tolist())
    }
    
    # Sauvegarder dans un fichier JSON
    output_path = os.path.join(current_dir, 'unique_values.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unique_values, f, ensure_ascii=False, indent=2)
    
    return unique_values

if __name__ == '__main__':
    unique_values = extract_unique_values()
    print("Valeurs uniques extraites et sauvegardées dans unique_values.json")
