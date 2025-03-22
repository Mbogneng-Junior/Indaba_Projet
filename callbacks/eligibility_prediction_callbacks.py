from dash.dependencies import Input, Output, State
import requests
import dash_bootstrap_components as dbc
from dash import html
import os

# URL de l'API (locale ou production)
API_URL = os.getenv('API_URL', 'http://localhost:8000')

def init_eligibility_prediction_callbacks(app):
    @app.callback(
        Output("prediction-output", "children"),
        [Input("predict-button", "n_clicks")],
        [
            State("age-input", "value"),
            State("sexe-input", "value"),
            State("profession-input", "value"),
            State("quartier-input", "value"),
            State("arrondissement-input", "value")
        ]
    )
    def predict_eligibility(n_clicks, age, sexe, profession, quartier, arrondissement):
        if n_clicks is None:
            return ""
        
        if not all([age, sexe, profession, quartier, arrondissement]):
            return html.Div(
                "Veuillez remplir tous les champs obligatoires",
                style={"color": "red"}
            )
        
        try:
            # Préparation des données
            data = {
                "Age": int(age),
                "Sexe": sexe,
                "Profession": profession,
                "Quartier_de_Residence": quartier,
                "Arrondissement_de_residence": arrondissement
            }
            
            # Appel à l'API
            try:
                response = requests.post(f"{API_URL}/predict", json=data)
                response.raise_for_status()  # Vérifie si la requête a réussi
                result = response.json()
            except requests.exceptions.ConnectionError:
                return html.Div(
                    "Erreur : Impossible de se connecter à l'API. Assurez-vous que l'API est en cours d'exécution.",
                    style={"color": "red"}
                )
            except requests.exceptions.RequestException as e:
                return html.Div(
                    f"Erreur lors de l'appel à l'API : {str(e)}",
                    style={"color": "red"}
                )
            
            # Création de la carte de résultat
            if result["eligible"]:
                color = "success"
                icon = "✓"
                message = "Éligible au don de sang"
            else:
                color = "danger"
                icon = "✗"
                message = "Non éligible au don de sang"
            
            return dbc.Card(
                dbc.CardBody([
                    html.H4(f"{icon} {message}", className=f"text-{color}"),
                    html.P(f"Probabilité d'éligibilité : {result['probability']:.1%}")
                ]),
                className=f"border-{color} mb-3"
            )
            
        except Exception as e:
            print(f"Erreur détaillée : {str(e)}")  # Pour le débogage
            return html.Div(
                f"Une erreur s'est produite lors du traitement de votre demande : {str(e)}",
                style={"color": "red"}
            )
