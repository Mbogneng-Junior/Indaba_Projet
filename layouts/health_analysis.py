import dash_bootstrap_components as dbc
from dash import html, dcc

def create_health_analysis_layout():
    """Crée le layout pour la page d'analyse de santé et d'éligibilité"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("🏥 Conditions de Santé & Éligibilité", 
                       className="text-primary text-center mb-3"),
                html.P("Analyse de l'impact des conditions médicales sur l'éligibilité au don",
                      className="text-muted text-center mb-4"),
            ])
        ]),
        
        # KPIs et filtres
        dbc.Row([
            # KPIs
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3(id="health-total-donneurs", className="text-primary mb-0"),
                                    html.Small("Total donneurs", className="text-muted")
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="health-taux-eligibilite", className="text-success mb-0"),
                                    html.Small("Taux d'éligibilité", className="text-muted")
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="health-conditions-frequentes", className="text-warning mb-0"),
                                    html.Small("Conditions fréquentes", className="text-muted")
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="health-taux-indisponibilite", className="text-danger mb-0"),
                                    html.Small("Taux d'indisponibilité", className="text-muted")
                                ], className="text-center")
                            ], width=3),
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ], width=12),
            
            # Filtres
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filtres d'analyse"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Groupe démographique", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id='health-demographic-dropdown',
                                    options=[
                                        {'label': 'Genre', 'value': 'genre'},
                                        {'label': 'Âge', 'value': 'age'},
                                        {'label': 'Profession', 'value': 'profession'},
                                        {'label': 'Arrondissement', 'value': 'arrondissement'}
                                    ],
                                    value='genre',
                                    className="mb-3"
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Type de condition", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id='health-condition-type-dropdown',
                                    options=[
                                        {'label': 'Toutes les conditions', 'value': 'all'},
                                        {'label': 'Maladies chroniques', 'value': 'chronic'},
                                        {'label': 'Conditions temporaires', 'value': 'temporary'},
                                        {'label': 'Facteurs de risque', 'value': 'risk'}
                                    ],
                                    value='all',
                                    className="mb-3"
                                )
                            ], width=6)
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Visualisations principales
        dbc.Row([
            # Distribution des conditions
            dbc.Col([
                html.H4("Distribution des Conditions Médicales", 
                       className="text-primary fw-bold mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='health-conditions-distribution')
                    ])
                ], className="shadow-sm mb-4"),
                
                # Impact sur l'éligibilité
                html.H4("Impact sur l'Éligibilité", 
                       className="text-primary fw-bold mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='health-eligibility-impact')
                    ])
                ], className="shadow-sm")
            ], width=8),
            
            # Analyses complémentaires
            dbc.Col([
                html.H4("Analyses Détaillées", 
                       className="text-primary fw-bold mb-3"),
                dbc.Tabs([
                    dbc.Tab([
                        dcc.Graph(id='health-condition-correlation')
                    ], label="Corrélations"),
                    
                    dbc.Tab([
                        dcc.Graph(id='health-demographic-patterns')
                    ], label="Patterns"),
                    
                    dbc.Tab([
                        dcc.Graph(id='health-temporal-trends')
                    ], label="Tendances")
                ], className="mb-4"),
                
                # Statistiques clés
                html.H4("Statistiques Clés", 
                       className="text-primary fw-bold mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='health-key-statistics')
                    ])
                ], className="shadow-sm")
            ], width=4)
        ]),
        
        # Analyse des facteurs de risque
        dbc.Row([
            dbc.Col([
                html.H4("Analyse des Facteurs de Risque", 
                       className="text-primary fw-bold mt-4 mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='health-risk-factors-heatmap')
                            ], width=6),
                            dbc.Col([
                                dcc.Graph(id='health-eligibility-prediction')
                            ], width=6)
                        ])
                    ])
                ], className="shadow-sm")
            ], width=12)
        ]),
        
        # Recommandations
        dbc.Row([
            dbc.Col([
                html.H4("Recommandations Médicales", 
                       className="text-primary fw-bold mt-4 mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='health-medical-recommendations')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ], fluid=True, className="px-4 py-3")
