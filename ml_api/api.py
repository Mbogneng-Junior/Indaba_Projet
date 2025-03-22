from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model import DonorEligibilityModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API de Prédiction d'Éligibilité au Don de Sang")

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement du modèle
model = DonorEligibilityModel()
try:
    model.load('donor_eligibility_model.joblib')
except Exception as e:
    print(f"Erreur lors du chargement du modèle : {str(e)}")
    raise

class DonorData(BaseModel):
    Age: int
    Sexe: str
    Profession: str
    Quartier_de_Residence: str
    Arrondissement_de_residence: str

@app.post("/predict")
async def predict_eligibility(donor: DonorData):
    try:
        # Conversion des données en dictionnaire
        donor_dict = donor.dict()
        
        # Prédiction
        result = model.predict(donor_dict)
        
        return {
            "eligible": result["eligible"],
            "probability": result["probability"]
        }
    except Exception as e:
        print(f"Erreur de prédiction : {str(e)}")  # Pour le débogage
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
