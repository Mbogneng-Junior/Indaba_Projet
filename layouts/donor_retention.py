import dash_bootstrap_components as dbc
from dash import html, dcc

def create_donor_retention_layout():
    """Crée le layout pour la page de fidélisation des donneurs"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("🔄 Fidélisation des Donneurs", 
                       className="text-primary text-center mb-3"),
                html.P("Analyse des facteurs influençant le retour des donneurs",
                      className="text-muted text-center mb-4"),
            ])
        ]),
        
        # KPIs et Filtres
        dbc.Row([
            # KPIs
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3(id="taux-fidelisation", className="text-primary mb-0"),
                                    html.Small("Taux de fidélisation", className="text-muted")
                                ], className="text-center")
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="moyenne-dons", className="text-success mb-0"),
                                    html.Small("Moyenne de dons/donneur", className="text-muted")
                                ], className="text-center")
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="intervalle-moyen", className="text-info mb-0"),
                                    html.Small("Intervalle moyen (jours)", className="text-muted")
                                ], className="text-center")
                            ], width=4),
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ], width=12),
            
            # Filtres
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Paramètres d'analyse"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Période d'analyse", className="fw-bold mb-2"),
                                dcc.RangeSlider(
                                    id='retention-period-slider',
                                    min=2019,
                                    max=2023,
                                    value=[2019, 2023],
                                    marks={str(year): str(year) for year in range(2019, 2024)},
                                    className="mb-3"
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Facteur d'analyse", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id='retention-factor-dropdown',
                                    options=[
                                        {'label': 'Âge', 'value': 'age'},
                                        {'label': 'Genre', 'value': 'genre'},
                                        {'label': 'Profession', 'value': 'profession'},
                                        {'label': 'Arrondissement', 'value': 'arrondissement'}
                                    ],
                                    value='age',
                                    className="mb-3"
                                )
                            ], width=6)
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Analyses principales
        dbc.Row([
            # Taux de fidélisation par facteur
            dbc.Col([
                html.H4("Taux de Fidélisation", 
                       className="text-primary fw-bold mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='retention-by-factor')
                    ])
                ], className="shadow-sm mb-4"),
                
                # Matrice de corrélation
                html.H4("Corrélations", 
                       className="text-primary fw-bold mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='retention-correlation')
                    ])
                ], className="shadow-sm")
            ], width=8),
            
            # Analyses complémentaires
            dbc.Col([
                html.H4("Analyses Détaillées", 
                       className="text-primary fw-bold mb-3"),
                dbc.Tabs([
                    dbc.Tab([
                        dcc.Graph(id='donation-frequency-dist')
                    ], label="Fréquence des dons"),
                    
                    dbc.Tab([
                        dcc.Graph(id='time-between-donations')
                    ], label="Intervalles"),
                    
                    dbc.Tab([
                        dcc.Graph(id='retention-evolution')
                    ], label="Évolution")
                ], className="mb-4"),
                
                # Facteurs de risque
                html.H4("Facteurs de Risque", 
                       className="text-primary fw-bold mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='risk-factors')
                    ])
                ], className="shadow-sm")
            ], width=4)
        ]),
        
        # Analyse comportementale
        dbc.Row([
            dbc.Col([
                html.H4("Analyse Comportementale", 
                       className="text-primary fw-bold mt-4 mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='donor-segments')
                            ], width=6),
                            dbc.Col([
                                dcc.Graph(id='loyalty-patterns')
                            ], width=6)
                        ])
                    ])
                ], className="shadow-sm")
            ], width=12)
        ]),
        
        # Recommandations
        dbc.Row([
            dbc.Col([
                html.H4("Recommandations de Fidélisation", 
                       className="text-primary fw-bold mt-4 mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='retention-recommendations')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ], fluid=True, className="px-4 py-3")
