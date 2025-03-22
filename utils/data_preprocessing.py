import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging
import os

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging
import os

def load_and_examine_data():
    """Charge et examine les données"""
    try:
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'Challenge dataset.xlsx')
        df = pd.read_excel(data_path)

        # 1. Standardisation des variables catégorielles
        categorical_columns = [
            'Genre', 'Niveau d\'etude', 'Situation Matrimoniale (SM)', 
            'Profession', 'Nationalité', 'Religion',
            'A-t-il (elle) déjà donné le sang', 'ÉLIGIBILITÉ AU DON.'
        ]
        
        for col in categorical_columns:
            df[col] = df[col].str.lower().str.strip()

        # 2. Traitement des dates
        def correct_date(date_str):
            if pd.isna(date_str):
                return pd.NaT
            if isinstance(date_str, str):
                if '/0019' in date_str:
                    date_str = date_str.replace('/0019', '/2019')
                try:
                    return pd.to_datetime(date_str)
                except:
                    return pd.NaT
            return date_str

        # Dates principales
        df['Date de remplissage de la fiche'] = df['Date de remplissage de la fiche'].apply(correct_date)
        df['Date de naissance'] = df['Date de naissance'].apply(correct_date)

        # 3. Traitement des mesures physiques (Taille et Poids)
        mesures_normales = {
            'homme': {'Taille': (160, 190), 'Poids': (50, 120)},
            'femme': {'Taille': (150, 180), 'Poids': (45, 100)}
        }

        for mesure in ['Taille', 'Poids']:
            df[mesure] = pd.to_numeric(df[mesure], errors='coerce')
            
            for genre in ['homme', 'femme']:
                mask = (df['Genre'] == genre)
                plage = mesures_normales[genre][mesure]
                
                # Identifier les valeurs valides
                valeurs_valides = df.loc[mask & df[mesure].between(plage[0], plage[1]), mesure]
                if not valeurs_valides.empty:
                    mediane = valeurs_valides.median()
                    # Remplir toutes les valeurs manquantes ou hors plage
                    df.loc[mask, mesure] = df.loc[mask, mesure].mask(
                        (df.loc[mask, mesure] < plage[0]) | 
                        (df.loc[mask, mesure] > plage[1]) | 
                        df.loc[mask, mesure].isna(),
                        mediane
                    )

        # 4. Traitement du taux d'hémoglobine
        hemoglobine_col = [col for col in df.columns if 'hémoglobine' in col.lower()][0]
        df[hemoglobine_col] = df[hemoglobine_col].astype(str).str.replace(',', '.').replace('nan', np.nan)
        df[hemoglobine_col] = pd.to_numeric(df[hemoglobine_col], errors='coerce')
        
        hemoglobine_normal = {
            'homme': (13, 17),
            'femme': (12, 15)
        }

        for genre, (min_val, max_val) in hemoglobine_normal.items():
            mask = (df['Genre'] == genre)
            valeurs_valides = df.loc[mask & df[hemoglobine_col].between(min_val, max_val), hemoglobine_col]
            if not valeurs_valides.empty:
                mediane = valeurs_valides.median()
                df.loc[mask, hemoglobine_col] = df.loc[mask, hemoglobine_col].mask(
                    (df.loc[mask, hemoglobine_col] < min_val) | 
                    (df.loc[mask, hemoglobine_col] > max_val) | 
                    df.loc[mask, hemoglobine_col].isna(),
                    mediane
                )

        # 5. Traitement des colonnes spécifiques au genre
        mask_femme = df['Genre'] == 'femme'
        
        # Dates spécifiques
        if 'Si oui preciser la date du dernier don.' in df.columns:
            df.loc[df['A-t-il (elle) déjà donné le sang'] != 'oui', 'Si oui preciser la date du dernier don.'] = pd.NaT

        if 'Date de dernières règles (DDR)' in df.columns:
            df.loc[~mask_femme, 'Date de dernières règles (DDR)'] = "non applicable"

        # 6. Création de colonnes binaires pour les raisons
        raison_cols = {
            'indispo': 'Raison indisponibilité',
            'non_elig': 'Raison de non-eligibilité totale'
        }

        for prefix, pattern in raison_cols.items():
            cols = [col for col in df.columns if pattern in col]
            for col in cols:
                new_col = col.split('[')[-1].split(']')[0].strip()
                df[f'{prefix}_{new_col}'] = df[col].notna().astype(int)
            df = df.drop(columns=cols)

        # 7. Nettoyage final
        columns_to_drop = [
            'Sélectionner "ok" pour envoyer',
            'Si autres raison préciser',
            'Autre raisons,  preciser'
        ]
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

        # 8. Afficher les statistiques
        print("\n=== Statistiques des mesures physiques par genre ===")
        for mesure in ['Taille', 'Poids', hemoglobine_col]:
            print(f"\n{mesure}:")
            print(df.groupby('Genre')[mesure].describe().round(2))

        print("\n=== Distribution de l'éligibilité ===")
        print(df['ÉLIGIBILITÉ AU DON.'].value_counts(normalize=True).round(3) * 100)

        # 9. Sauvegarder les données nettoyées
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed_data.csv')
        df.to_csv(output_path, index=False)
        print(f"\nDonnées prétraitées sauvegardées dans : {output_path}")

        return df
        
    except Exception as e:
        print(f"Erreur lors du chargement des données: {str(e)}")
        raise e

if __name__ == "__main__":
    df = load_and_examine_data()