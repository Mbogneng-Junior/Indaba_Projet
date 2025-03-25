from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models.eligibility_model import EligibilityModel
import os
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Prédiction d'Éligibilité au Don de Sang",
    description="API pour prédire l'éligibilité des donneurs de sang",
    version="1.0.0"
)

# Chargement du modèle
model = EligibilityModel()

# Chemins absolus
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(os.path.dirname(current_dir), 'models', 'eligibility_model.joblib')
data_path = os.path.join(os.path.dirname(current_dir), 'data', 'processed_data.csv')

try:
    model.load(model_path)
    logger.info("Modèle chargé avec succès")
except:
    # Si le modèle n'existe pas, on l'entraîne
    logger.info("Entraînement d'un nouveau modèle...")
    model.train(data_path)
    model.save(model_path)
    logger.info("Modèle entraîné et sauvegardé")

class DonorFeatures(BaseModel):
    age: int
    genre: str
    niveau_d_etude: str
    situation_matrimoniale_sm: str
    profession: str
    religion: str
    a_t_il_elle_deja_donne_le_sang: str

class PredictionResponse(BaseModel):
    eligibilite: bool
    probabilite: float

@app.post("/predict", response_model=PredictionResponse)
async def predict_eligibility(features: DonorFeatures):
    try:
        logger.info(f"Réception des données : {features.dict()}")
        
        # Conversion du modèle Pydantic en dictionnaire
        features_dict = {
            'age': features.age,
            'genre': features.genre,
            'niveau_d_etude': features.niveau_d_etude,
            'situation_matrimoniale_(sm)': features.situation_matrimoniale_sm,
            'profession': features.profession,
            'religion': features.religion,
            'a_t_il_elle_deja_donne_le_sang': features.a_t_il_elle_deja_donne_le_sang
        }
        
        logger.info(f"Features préparées : {features_dict}")
        
        # Prédiction
        prediction = model.predict(features_dict)
        logger.info(f"Prédiction obtenue : {prediction}")
        
        return PredictionResponse(
            eligibilite=prediction['eligibilite'],
            probabilite=prediction['probabilite']
        )
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
