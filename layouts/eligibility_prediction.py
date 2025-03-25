import dash_bootstrap_components as dbc
from dash import html, dcc
from utils.data_utils import get_unique_values

def create_eligibility_prediction_layout():
    """Crée le layout pour la page de prédiction d'éligibilité"""
    # Récupération des professions uniques
    professions = get_unique_values('profession')
    
    return dbc.Container([
        # En-tête
        dbc.Row([
            dbc.Col([
                html.H2("Prédiction d'Éligibilité au Don de Sang", 
                       className="text-primary mb-3"),
                html.P("Utilisez notre modèle d'IA pour prédire l'éligibilité d'un nouveau donneur",
                      className="text-muted mb-4"),
            ])
        ]),
        
        # Formulaire de prédiction
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Informations du Donneur"),
                    dbc.CardBody([
                        # Informations démographiques
                        dbc.Row([
                            dbc.Col([
                                html.Label("Âge", className="fw-bold mb-2"),
                                dbc.Input(
                                    id="donor-age",
                                    type="number",
                                    min=18,
                                    max=65,
                                    placeholder="Entrez l'âge",
                                    className="mb-3"
                                )
                            ], md=6),
                            dbc.Col([
                                html.Label("Genre", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="donor-gender",
                                    options=[
                                        {"label": "Homme", "value": "Homme"},
                                        {"label": "Femme", "value": "Femme"}
                                    ],
                                    placeholder="Sélectionnez le genre",
                                    className="mb-3"
                                )
                            ], md=6)
                        ]),
                        
                        # Niveau d'études et situation matrimoniale
                        dbc.Row([
                            dbc.Col([
                                html.Label("Niveau d'études", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="donor-education",
                                    options=[
                                        {"label": "Aucun", "value": "Aucun"},
                                        {"label": "Primaire", "value": "Primaire"},
                                        {"label": "Secondaire", "value": "Secondaire"},
                                        {"label": "Universitaire", "value": "Universitaire"}
                                    ],
                                    placeholder="Sélectionnez le niveau d'études",
                                    className="mb-3"
                                )
                            ], md=6),
                            dbc.Col([
                                html.Label("Situation matrimoniale", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="donor-marital-status",
                                    options=[
                                        {"label": "Célibataire", "value": "Célibataire"},
                                        {"label": "Marié(e)", "value": "Marié (e)"},
                                        {"label": "Divorcé(e)", "value": "Divorcé (e)"},
                                        {"label": "Veuf/Veuve", "value": "Veuf (ve)"}
                                    ],
                                    placeholder="Sélectionnez la situation matrimoniale",
                                    className="mb-3"
                                )
                            ], md=6)
                        ]),
                        
                        # Profession et religion
                        dbc.Row([
                            dbc.Col([
                                html.Label("Profession", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="donor-profession",
                                    options=[{"label": p, "value": p} for p in professions],
                                    placeholder="Sélectionnez la profession",
                                    className="mb-3"
                                )
                            ], md=6),
                            dbc.Col([
                                html.Label("Religion", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="donor-religion",
                                    options=[
                                        {"label": "Chrétien (Catholique)", "value": "chretien (catholique)"},
                                        {"label": "Chrétien (Protestant)", "value": "chretien (protestant)"},
                                        {"label": "Musulman", "value": "musulman"},
                                        {"label": "Autre", "value": "autre"}
                                    ],
                                    placeholder="Sélectionnez la religion",
                                    className="mb-3"
                                )
                            ], md=6)
                        ]),
                        
                        # Historique de don
                        dbc.Row([
                            dbc.Col([
                                html.Label("A déjà donné le sang ?", className="fw-bold mb-2"),
                                dcc.RadioItems(
                                    id="donor-previous-donation",
                                    options=[
                                        {"label": "Oui", "value": "Oui"},
                                        {"label": "Non", "value": "Non"}
                                    ],
                                    className="mb-3"
                                )
                            ], md=12)
                        ]),
                        
                        # Bouton de prédiction
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Prédire l'éligibilité",
                                    id="predict-button",
                                    color="primary",
                                    className="w-100 mt-3"
                                )
                            ])
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ], md=8),
            
            # Résultat de la prédiction
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Résultat de la Prédiction"),
                    dbc.CardBody([
                        html.Div([
                            html.H4(id="prediction-result", className="mb-3"),
                            html.Div([
                                html.Strong("Probabilité : "),
                                html.Span(id="prediction-probability")
                            ], className="mb-2"),
                            html.Small(
                                "Cette prédiction est basée sur un modèle d'apprentissage automatique "
                                "et ne remplace pas l'avis d'un professionnel de santé.",
                                className="text-muted"
                            )
                        ], id="prediction-container", style={"display": "none"})
                    ])
                ], className="shadow-sm")
            ], md=4)
        ])
    ], fluid=True, className="px-4 py-3")
