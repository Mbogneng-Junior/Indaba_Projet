from dash.dependencies import Input, Output, State
import requests
import pandas as pd
import numpy as np

def init_eligibility_prediction_callbacks(app):
    """Initialise les callbacks pour la prédiction d'éligibilité"""
    
    @app.callback(
        [
            Output("prediction-container", "style"),
            Output("prediction-result", "children"),
            Output("prediction-result", "className"),
            Output("prediction-probability", "children")
        ],
        [Input("predict-button", "n_clicks")],
        [
            State("donor-age", "value"),
            State("donor-gender", "value"),
            State("donor-education", "value"),
            State("donor-marital-status", "value"),
            State("donor-profession", "value"),
            State("donor-religion", "value"),
            State("donor-previous-donation", "value")
        ]
    )
    def predict_eligibility(n_clicks, age, gender, education, marital_status, 
                          profession, religion, previous_donation):
        if n_clicks is None:
            return {"display": "none"}, "", "", ""
        
        # Vérification des champs requis
        if not all([age, gender, education, marital_status, profession, religion, previous_donation]):
            return (
                {"display": "block"},
                "Veuillez remplir tous les champs",
                "text-warning",
                ""
            )
        
        try:
            # Préparation des données pour l'API
            data = {
                "age": age,
                "genre": gender,
                "niveau_d_etude": education,
                "situation_matrimoniale_sm": marital_status,
                "profession": profession,
                "religion": religion,
                "a_t_il_elle_deja_donne_le_sang": previous_donation
            }
            
            # Appel à l'API
            response = requests.post("http://localhost:8000/predict", json=data)
            prediction = response.json()
            
            # Formatage du résultat
            result_text = "ÉLIGIBLE" if prediction["eligibilite"] else "NON ÉLIGIBLE"
            result_class = "text-success" if prediction["eligibilite"] else "text-danger"
            probability = f"{prediction['probabilite']*100:.1f}%"
            
            return (
                {"display": "block"},
                result_text,
                result_class,
                probability
            )
            
        except Exception as e:
            return (
                {"display": "block"},
                f"Erreur lors de la prédiction : {str(e)}",
                "text-danger",
                ""
            )
