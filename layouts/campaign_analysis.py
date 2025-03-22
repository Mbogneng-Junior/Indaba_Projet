import dash_bootstrap_components as dbc
from dash import html, dcc

def create_campaign_analysis_layout():
    """Crée le layout pour la page d'analyse des campagnes"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("📊 Analyse des Campagnes", 
                       className="text-primary text-center mb-3"),
                html.P("Analyse de l'efficacité des campagnes de don de sang",
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
                                    html.H3(id="total-campagnes", className="text-primary mb-0"),
                                    html.Small("Campagnes", className="text-muted")
                                ], className="text-center")
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="total-participants", className="text-success mb-0"),
                                    html.Small("Participants", className="text-muted")
                                ], className="text-center")
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="taux-participation", className="text-info mb-0"),
                                    html.Small("Taux de participation", className="text-muted")
                                ], className="text-center")
                            ], width=4),
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
                                html.Label("Période", className="fw-bold mb-2"),
                                dcc.RangeSlider(
                                    id='campaign-period-slider',
                                    min=2019,
                                    max=2023,
                                    value=[2019, 2023],
                                    marks={str(year): str(year) for year in range(2019, 2024)},
                                    className="mb-3"
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Groupes démographiques", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id='demographic-filter',
                                    options=[
                                        {'label': 'Genre', 'value': 'genre'},
                                        {'label': 'Profession', 'value': 'profession'},
                                        {'label': 'Arrondissement', 'value': 'arrondissement'},
                                        {'label': 'Âge', 'value': 'age'}
                                    ],
                                    value='genre',
                                    className="mb-3"
                                )
                            ], width=6)
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Graphiques principaux
        dbc.Row([
            # Tendances temporelles
            dbc.Col([
                html.H4("Tendances Temporelles", 
                       className="text-primary fw-bold mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='seasonal-trends')
                    ])
                ], className="shadow-sm mb-4"),
                
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='weekly-patterns')
                    ])
                ], className="shadow-sm")
            ], width=8),
            
            # Analyse démographique
            dbc.Col([
                html.H4("Analyse Démographique", 
                       className="text-primary fw-bold mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='demographic-distribution')
                    ])
                ], className="shadow-sm mb-4"),
                
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='participation-rate')
                    ])
                ], className="shadow-sm")
            ], width=4)
        ]),
        
        # Analyses détaillées
        dbc.Row([
            dbc.Col([
                html.H4("Comportement des Donneurs", 
                       className="text-primary fw-bold mt-4 mb-3"),
                dbc.Tabs([
                    dbc.Tab([
                        dcc.Graph(id='donor-retention')
                    ], label="Fidélisation", tab_id="tab-retention"),
                    
                    dbc.Tab([
                        dcc.Graph(id='donation-frequency')
                    ], label="Fréquence des dons", tab_id="tab-frequency"),
                    
                    dbc.Tab([
                        dcc.Graph(id='donor-journey')
                    ], label="Parcours donneur", tab_id="tab-journey")
                ])
            ], width=12)
        ]),
        
        # Recommandations
        dbc.Row([
            dbc.Col([
                html.H4("Recommandations", 
                       className="text-primary fw-bold mt-4 mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='campaign-recommendations')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ], fluid=True, className="px-4 py-3")
