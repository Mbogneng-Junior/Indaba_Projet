import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
import joblib
import os
import json

class DonorEligibilityModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = None
        self.imputer = SimpleImputer(strategy='most_frequent')
        self.known_categories = {}
        
    def load_known_categories(self):
        """Charge les catégories connues depuis le fichier JSON"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'unique_values.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            self.known_categories = json.load(f)
    
    def normalize_text(self, text):
        """Normalise le texte en minuscules et gère les espaces"""
        if isinstance(text, str):
            return text.lower().strip()
        return text

    def handle_unknown_category(self, value, field):
        """Gère les valeurs inconnues en les remplaçant par 'autre'"""
        value = self.normalize_text(value)
        if field in self.known_categories:
            known_values = [self.normalize_text(v) for v in self.known_categories[field]]
            if value not in known_values:
                return 'autre'
        return value
        
    def preprocess_data(self, data, training=False):
        if training:
            # Extraire et sauvegarder les catégories connues
            self.load_known_categories()
        
        # Création des colonnes nécessaires
        if 'Date de naissance' in data.columns:
            data['Age'] = pd.to_datetime('now').year - pd.to_datetime(data['Date de naissance']).dt.year

        # Mapping des noms de colonnes
        column_mapping = {
            'Genre': 'Sexe',
            'Quartier de Résidence': 'Quartier_de_Residence',
            'Arrondissement de résidence': 'Arrondissement_de_residence'
        }
        
        # Renommer les colonnes
        data = data.rename(columns=column_mapping)

        # Normaliser les textes
        categorical_columns = ['Sexe', 'Profession', 'Quartier_de_Residence', 
                            'Arrondissement_de_residence']
        
        for col in categorical_columns:
            if col in data.columns:
                # Normaliser le texte
                data[col] = data[col].apply(self.normalize_text)
                
                # Remplacer les valeurs inconnues par 'autre'
                if not training:
                    data[col] = data[col].apply(lambda x: self.handle_unknown_category(x, col))
                
                # Ajouter 'autre' aux encodeurs lors de l'entraînement
                if training:
                    unique_values = list(data[col].unique())
                    if 'autre' not in unique_values:
                        unique_values.append('autre')
                    self.label_encoders[col] = LabelEncoder().fit(unique_values)
                
                data[col] = self.label_encoders[col].transform(data[col].astype(str))
        
        # Sélection des features pour le modèle
        features = ['Age', 'Sexe', 'Profession', 
                   'Quartier_de_Residence', 'Arrondissement_de_residence']
        
        self.feature_names = features
        X = data[features]
        
        # Imputation des valeurs manquantes numériques
        if self.imputer:
            X = pd.DataFrame(self.imputer.fit_transform(X) if training else 
                           self.imputer.transform(X), columns=X.columns)
        
        return X
    
    def train(self, data_path):
        # Chargement des données
        data = pd.read_csv(data_path)
        
        # Préparation des features
        X = self.preprocess_data(data, training=True)
        
        # Conversion de la variable cible en 0/1, en gérant les valeurs manquantes
        y = data['ÉLIGIBILITÉ AU DON.'].fillna('NON')  # Remplacer les NaN par 'NON'
        y = (y == 'OUI').astype(int)
        
        # Division des données
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Normalisation des features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Entraînement du modèle
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Évaluation du modèle
        X_test_scaled = self.scaler.transform(X_test)
        score = self.model.score(X_test_scaled, y_test)
        print(f"Précision du modèle: {score:.2f}")
        
        return score
    
    def predict(self, input_data):
        try:
            # Conversion en DataFrame
            input_df = pd.DataFrame([input_data])
            
            # Prétraitement des données
            processed_data = self.preprocess_data(input_df, training=False)
            
            # Normalisation
            scaled_data = self.scaler.transform(processed_data)
            
            # Prédiction
            prediction = self.model.predict(scaled_data)
            probabilities = self.model.predict_proba(scaled_data)
            
            return {
                'eligible': bool(prediction[0]),
                'probability': float(probabilities[0][1]) if prediction[0] else float(probabilities[0][0])
            }
        except Exception as e:
            print(f"Erreur dans la prédiction : {str(e)}")
            print(f"Input data : {input_data}")
            print(f"Processed data : {processed_data if 'processed_data' in locals() else 'Non traité'}")
            raise
    
    def save(self, model_path='model.joblib'):
        """Sauvegarde le modèle et les préprocesseurs"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'imputer': self.imputer,
            'known_categories': self.known_categories
        }
        joblib.dump(model_data, model_path)
    
    def load(self, model_path='model.joblib'):
        """Charge le modèle et les préprocesseurs"""
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoders = model_data['label_encoders']
        self.feature_names = model_data['feature_names']
        self.imputer = model_data['imputer']
        self.known_categories = model_data.get('known_categories', {})

if __name__ == '__main__':
    # Obtenir le chemin absolu du répertoire parent (racine du projet)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, 'data', 'processed_data.csv')

    # Entraînement du modèle
    model = DonorEligibilityModel()
    model.train(data_path)
    
    # Sauvegarder le modèle dans le dossier ml_api
    model_path = os.path.join(current_dir, 'donor_eligibility_model.joblib')
    model.save(model_path)