import dash_bootstrap_components as dbc
from dash import html, dcc
import json
import os

def load_unique_values():
    """Charge les valeurs uniques depuis le fichier JSON"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        json_path = os.path.join(project_root, 'ml_api', 'unique_values.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des valeurs uniques : {str(e)}")
        return {
            'Profession': [],
            'Quartier_de_Residence': [],
            'Arrondissement_de_residence': [],
            'Genre': []
        }

def create_eligibility_prediction_layout():
    # Charger les valeurs uniques
    unique_values = load_unique_values()
    
    # Ajouter "Autre" à chaque liste
    for key in unique_values:
        if 'Autre' not in unique_values[key]:
            unique_values[key].append('Autre')
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Prédiction d'Éligibilité au Don de Sang", className="text-center mb-4"),
                html.P("Remplissez le formulaire ci-dessous pour vérifier l'éligibilité au don de sang.", className="text-center")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Âge"),
                                dbc.Input(
                                    id="age-input",
                                    type="number",
                                    min=18,
                                    max=100,
                                    placeholder="Entrez votre âge"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Sexe"),
                                dcc.Dropdown(
                                    id="sexe-input",
                                    options=[{"label": s, "value": s} for s in unique_values['Genre']],
                                    placeholder="Sélectionnez votre sexe"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Profession"),
                                dcc.Dropdown(
                                    id="profession-input",
                                    options=[{"label": p, "value": p} for p in unique_values['Profession']],
                                    placeholder="Sélectionnez votre profession"
                                )
                            ], width=12)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Quartier de Résidence"),
                                dcc.Dropdown(
                                    id="quartier-input",
                                    options=[{"label": q, "value": q} for q in unique_values['Quartier_de_Residence']],
                                    placeholder="Sélectionnez votre quartier"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Arrondissement de Résidence"),
                                dcc.Dropdown(
                                    id="arrondissement-input",
                                    options=[{"label": a, "value": a} for a in unique_values['Arrondissement_de_residence']],
                                    placeholder="Sélectionnez votre arrondissement"
                                )
                            ], width=6)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Prédire l'Éligibilité",
                                    id="predict-button",
                                    color="primary",
                                    className="w-100"
                                )
                            ], width={"size": 6, "offset": 3})
                        ], className="mt-4"),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Div(id="prediction-output", className="mt-4 text-center")
                            ])
                        ])
                    ])
                ])
            ], width={"size": 8, "offset": 2})
        ])
    ], fluid=True)
