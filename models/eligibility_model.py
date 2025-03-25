import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from datetime import datetime
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EligibilityModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.features = ['age', 'genre', 'niveau_d_etude', 'situation_matrimoniale_(sm)',
                        'profession', 'religion', 'a_t_il_elle_deja_donne_le_sang']
        
    def preprocess_data(self, df):
        """Prétraitement des données"""
        logger.info("Début du prétraitement des données")
        
        # Copie des données pour éviter la modification de l'original
        df_processed = df.copy()
        
        # Calcul de l'âge à partir de la date de naissance si nécessaire
        if 'date_de_naissance' in df_processed.columns and 'age' not in df_processed.columns:
            logger.info("Calcul de l'âge à partir de la date de naissance")
            df_processed['date_de_naissance'] = pd.to_datetime(df_processed['date_de_naissance'])
            df_processed['age'] = (datetime.now() - df_processed['date_de_naissance']).dt.days // 365
        
        # Encodage des variables catégorielles
        for feature in self.features:
            if feature not in df_processed.columns:
                logger.warning(f"Feature manquante : {feature}")
                continue
            
            logger.info(f"Traitement de la feature : {feature}")
            if df_processed[feature].dtype == 'object':
                if feature not in self.label_encoders:
                    logger.info(f"Création d'un nouvel encodeur pour {feature}")
                    self.label_encoders[feature] = LabelEncoder()
                    df_processed[feature] = self.label_encoders[feature].fit_transform(df_processed[feature].fillna('inconnu'))
                else:
                    logger.info(f"Utilisation de l'encodeur existant pour {feature}")
                    # Gérer les nouvelles catégories
                    known_categories = set(self.label_encoders[feature].classes_)
                    new_categories = set(df_processed[feature].unique()) - known_categories
                    if new_categories:
                        logger.warning(f"Nouvelles catégories trouvées pour {feature}: {new_categories}")
                        df_processed[feature] = df_processed[feature].map(lambda x: 'inconnu' if x not in known_categories else x)
                    df_processed[feature] = self.label_encoders[feature].transform(df_processed[feature].fillna('inconnu'))
        
        # Standardisation des variables numériques
        numeric_features = df_processed.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_features) > 0:
            logger.info(f"Standardisation des features numériques : {numeric_features.tolist()}")
            if not hasattr(self.scaler, 'scale_') or self.scaler.scale_ is None:
                df_processed[numeric_features] = self.scaler.fit_transform(df_processed[numeric_features])
            else:
                df_processed[numeric_features] = self.scaler.transform(df_processed[numeric_features])
        
        logger.info("Prétraitement terminé")
        return df_processed
    
    def train(self, data_path):
        """Entraînement du modèle"""
        logger.info(f"Chargement des données depuis {data_path}")
        # Chargement des données
        df = pd.read_csv(data_path)
        
        # Prétraitement
        logger.info("Préparation des features")
        X = df[self.features]
        y = (df.iloc[:, 12] == 'eligible').astype(int)
        
        # Prétraitement des features
        X_processed = self.preprocess_data(X)
        
        # Division train/test
        logger.info("Division train/test")
        X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)
        
        # Entraînement du modèle
        logger.info("Entraînement du modèle")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Évaluation du modèle
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        logger.info(f"Score d'entraînement : {train_score:.3f}")
        logger.info(f"Score de test : {test_score:.3f}")
        
        return train_score, test_score
    
    def predict(self, features_dict):
        """Prédiction pour un nouveau donneur"""
        logger.info("Début de la prédiction")
        if self.model is None:
            raise ValueError("Le modèle n'a pas été entraîné")
        
        # Conversion en DataFrame
        logger.info(f"Features reçues : {features_dict}")
        df = pd.DataFrame([features_dict])
        
        # Prétraitement
        logger.info("Prétraitement des features")
        df_processed = self.preprocess_data(df)
        logger.info(f"Features prétraitées : {df_processed.to_dict()}")
        
        # Prédiction
        logger.info("Calcul de la prédiction")
        prediction = self.model.predict_proba(df_processed)[0]
        
        result = {
            'eligibilite': bool(prediction[1] > 0.5),
            'probabilite': float(prediction[1])
        }
        logger.info(f"Résultat de la prédiction : {result}")
        
        return result
    
    def save(self, model_path):
        """Sauvegarde du modèle"""
        if self.model is None:
            raise ValueError("Le modèle n'a pas été entraîné")
        
        # Création du dossier si nécessaire
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Sauvegarde du modèle et des préprocesseurs
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'features': self.features
        }
        logger.info(f"Sauvegarde du modèle dans {model_path}")
        joblib.dump(model_data, model_path)
    
    def load(self, model_path):
        """Chargement du modèle"""
        logger.info(f"Chargement du modèle depuis {model_path}")
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoders = model_data['label_encoders']
        self.features = model_data['features']
        logger.info("Modèle chargé avec succès")

if __name__ == '__main__':
    # Exemple d'utilisation
    model = EligibilityModel()
    
    # Chemin absolu vers les données
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(current_dir), 'data', 'processed_data.csv')
    model_path = os.path.join(current_dir, 'eligibility_model.joblib')
    
    # Entraînement
    train_score, test_score = model.train(data_path)
    
    # Sauvegarde du modèle
    model.save(model_path)
    
    # Test de prédiction
    example_donor = {
        'age': 30,
        'genre': 'Homme',
        'niveau_d_etude': 'Universitaire',
        'situation_matrimoniale_(sm)': 'Célibataire',
        'profession': 'Ingénieur',
        'religion': 'chretien (catholique)',
        'a_t_il_elle_deja_donne_le_sang': 'Non'
    }
    
    prediction = model.predict(example_donor)
    print(f"\nPrédiction pour le donneur exemple :")
    print(f"Éligible : {prediction['eligibilite']}")
    print(f"Probabilité : {prediction['probabilite']:.2f}")
