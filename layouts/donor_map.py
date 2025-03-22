import dash_bootstrap_components as dbc
from dash import html, dcc

def create_donor_map_layout():
    """Crée le layout pour la carte des donneurs"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("📍 Cartographie des Donneurs", 
                       className="text-primary text-center mb-3"),
                html.P("Analyse de la distribution géographique des donneurs de sang à Yaoundé",
                      className="text-muted text-center mb-4"),
            ])
        ]),
        
        # Ligne principale avec carte et contrôles
        dbc.Row([
            # Contrôles à gauche
            dbc.Col([
                # KPIs en haut
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3(id="total-donneurs", className="text-primary mb-0"),
                                    html.Small("Donneurs", className="text-muted")
                                ], className="text-center")
                            ], width=6),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="taux-retour", className="text-success mb-0"),
                                    html.Small("Taux de retour", className="text-muted")
                                ], className="text-center")
                            ], width=6),
                        ]),
                    ])
                ], className="shadow-sm mb-3"),

                # Menu accordéon pour les filtres
                dbc.Accordion([
                    dbc.AccordionItem([
                        html.Label("Période", className="fw-bold mb-2"),
                        dcc.RangeSlider(
                            id='annees-filter',
                            min=2019,
                            max=2023,
                            value=[2019, 2023],
                            marks={str(year): str(year) for year in range(2019, 2024)},
                            className="mb-3"
                        ),
                        
                        html.Label("Arrondissements", className="fw-bold mb-2"),
                        dcc.Dropdown(
                            id='ville-filter',
                            multi=True,
                            placeholder="Tous les arrondissements",
                            className="mb-3"
                        ),
                        
                        html.Label("Mode de visualisation", className="fw-bold mb-2"),
                        dbc.RadioItems(
                            id='visualization-mode',
                            options=[
                                {'label': ' Points localisateurs', 'value': 'scatter'},
                                {'label': ' Carte de chaleur', 'value': 'heatmap'},
                                {'label': ' Clusters', 'value': 'cluster'}
                            ],
                            value='scatter',
                            className="mb-3"
                        ),
                    ], title="Filtres principaux", className="border-0"),
                    
                    dbc.AccordionItem([
                        html.Label("Genre", className="fw-bold mb-2"),
                        dcc.Dropdown(
                            id='sexe-filter',
                            options=[
                                {'label': 'Tous', 'value': 'all'},
                                {'label': 'Homme', 'value': 'homme'},
                                {'label': 'Femme', 'value': 'femme'}
                            ],
                            value='all',
                            className="mb-3"
                        ),
                        
                        html.Label("Éligibilité", className="fw-bold mb-2"),
                        dcc.Dropdown(
                            id='eligibility-filter',
                            options=[
                                {'label': 'Tous', 'value': 'all'},
                                {'label': 'Éligible', 'value': 'eligible'},
                                {'label': 'Temporairement non-éligible', 'value': 'temp-non-elig'},
                                {'label': 'Définitivement non-éligible', 'value': 'def-non-elig'}
                            ],
                            value='all',
                            className="mb-3"
                        ),
                    ], title="Filtres avancés", className="border-0"),
                ], start_collapsed=True, className="mb-3"),

                dbc.Button(
                    "Actualiser la carte",
                    id="update-viz",
                    color="primary",
                    className="w-100 mb-3"
                ),
                
                # Mini statistiques
                dbc.Card([
                    dbc.CardHeader("Aperçu rapide"),
                    dbc.CardBody(id="summary-stats")
                ], className="shadow-sm")
            ], width=3, className="h-100"),
            
            # Carte principale à droite
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='donor-map',
                            style={'height': 'calc(100vh - 200px)'},  # Ajuster pour correspondre à la hauteur du menu
                            config={
                                'displayModeBar': True,
                                'scrollZoom': True,
                                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                            }
                        )
                    ], className="p-0")  # Réduire le padding pour maximiser l'espace
                ], className="shadow-sm h-100")
            ], width=9),
        ], className="mb-4"),
        
        # Analyses détaillées
        dbc.Row([
            dbc.Col([
                html.H4("Dons mensuels", 
                       className="text-danger fw-bold mb-3",
                       style={"fontSize": "24px", "letterSpacing": "0.5px"}),
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='monthly-donations')
                    ])
                ], className="shadow-sm")
            ], width=8),
            
            dbc.Col([
                html.H4("Éligibilité", 
                       className="text-danger fw-bold mb-3",
                       style={"fontSize": "24px", "letterSpacing": "0.5px"}),
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='eligibility-pie',
                                style={'height': '400px'})  # Augmenter la hauteur
                    ])
                ], className="shadow-sm")
            ], width=4),
        ]),
        
        # Autres analyses
        dbc.Row([
            dbc.Col([
                html.H4("Analyses temporelles", 
                       className="text-primary fw-bold mt-4 mb-3",
                       style={"fontSize": "20px"}),
                dbc.Tabs([
                    dbc.Tab([
                        dcc.Graph(id='yearly-trend')
                    ], label="Tendance annuelle", tab_id="tab-yearly"),
                    
                    dbc.Tab([
                        dcc.Graph(id='weekday-pattern')
                    ], label="Jours de la semaine", tab_id="tab-weekday"),
                ])
            ], width=8),
            
            dbc.Col([
                html.H4("Répartition", 
                       className="text-primary fw-bold mt-4 mb-3",
                       style={"fontSize": "20px"}),
                dbc.Tabs([
                    dbc.Tab([
                        dcc.Graph(id='gender-distribution')
                    ], label="Genre", tab_id="tab-gender"),
                ])
            ], width=4),
        ]),
        
        # Analyses avancées (collapsible)
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Analyses avancées ▼",
                    id="collapse-button",
                    color="link",
                    className="text-decoration-none mt-4"
                ),
                dbc.Collapse([
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='age-distribution')
                        ], width=6),
                        dbc.Col([
                            dcc.Graph(id='factors-heatmap')
                        ], width=6),
                    ]),
                ], id="collapse-content", is_open=False),
            ])
        ])
    ], fluid=True, className="px-4 py-3")
