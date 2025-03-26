from dash.dependencies import Input, Output, State
import requests
import json
import dash_bootstrap_components as dbc
from dash import html

def init_eligibility_callbacks(app):
    @app.callback(
        [Output('prediction-result', 'children'),
         Output('prediction-probability', 'children')],
        [Input('predict-button', 'n_clicks')],
        [State('age-input', 'value'),
         State('gender-input', 'value'),
         State('education-input', 'value'),
         State('marital-input', 'value'),
         State('profession-input', 'value'),
         State('religion-input', 'value'),
         State('has-donated', 'value')]
    )
    def predict_eligibility(n_clicks, age, gender, education, marital, profession, religion, has_donated):
        if n_clicks is None:
            return "", "Cette prédiction est basée sur un modèle d'apprentissage automatique et ne remplace pas l'avis d'un professionnel de santé."
        
        try:
            # Vérifier que toutes les valeurs sont présentes
            if None in [age, gender, education, marital, profession, religion] or not age or not profession:
                return (
                    html.Div([
                        html.H4("Veuillez remplir tous les champs", className="text-warning"),
                        html.P("Tous les champs sont obligatoires pour faire une prédiction.")
                    ]),
                    ""
                )
            
            # Préparer les données pour l'API
            # Standardiser les valeurs
            gender = str(gender) if gender else "Femme"  
            education = str(education) if education else "Pas Précisé"
            marital = str(marital) if marital else "Célibataire"
            profession = str(profession).lower() if profession else "pas precisé"
            religion = str(religion).lower() if religion else "pas précisé"

            data = {
                "age": int(age),
                "genre": gender,
                "niveau_d_etude": education,
                "situation_matrimoniale": marital,
                "profession": profession,
                "ville": "douala",  
                "arrondissement_de_residence": "douala 1",  
                "nationalite": "camerounaise",  
                "religion": religion,
                "a_deja_donne": has_donated == "Oui",
                "date_dernier_don": None
            }
            
            print("Données envoyées à l'API:", data)  
            
            # Faire la requête à l'API
            response = requests.post('http://localhost:8000/predict', json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Créer le message de résultat
                if result['eligible']:
                    message = html.Div([
                        html.H4("Éligible au don de sang", className="text-success"),
                        html.P("Le modèle prédit que vous êtes éligible au don de sang.")
                    ])
                else:
                    message = html.Div([
                        html.H4("Non éligible au don de sang", className="text-danger"),
                        html.P("Le modèle prédit que vous n'êtes pas éligible au don de sang.")
                    ])
                
                # Créer le message de probabilité
                probability = f"Probabilité : {result['probability']:.1%}"
                
                return message, probability
            else:
                print(f"Erreur API: {response.status_code} - {response.text}")  
                return f"Erreur lors de la prédiction : {response.text}", "Probabilité : "
                
        except Exception as e:
            print(f"Erreur lors de la prédiction : {str(e)}")  
            return f"Erreur lors de la prédiction : {str(e)}", "Probabilité : "
