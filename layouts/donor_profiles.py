import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime, timedelta

def create_donor_profiles_layout():
    """Crée le layout pour la page de profilage des donneurs"""
    # Définir les dates par défaut (2019-2021)
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2020, 10, 12)  # La dernière date disponible dans le dataset
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("👥 Profilage des Donneurs", 
                       className="text-primary text-center mb-3"),
                html.P("Analyse et segmentation des profils de donneurs de sang",
                      className="text-muted text-center mb-4"),
            ])
        ]),
        
        # Filtres et contrôles
        dbc.Row([
            # Sidebar avec défilement
            dbc.Col([
                # Header fixe du sidebar
                html.Div([
                    dbc.CardHeader("Filtres d'analyse", 
                                 className="bg-primary text-white",
                                 style={"position": "sticky", "top": "0", "z-index": "1"})
                ]),
                
                # Contenu défilant du sidebar
                html.Div([
                    dbc.Card([
                        dbc.CardBody([
                            # Filtre par période
                            html.Label("Période d'analyse", className="form-label"),
                            dcc.DatePickerRange(
                                id='date-range',
                                start_date=start_date.date(),
                                end_date=end_date.date(),
                                min_date_allowed=datetime(1977, 12, 25).date(),
                                max_date_allowed=datetime(2020, 10, 12).date(),
                                initial_visible_month=datetime(2019, 1, 1).date(),
                                display_format='DD/MM/YYYY',
                                first_day_of_week=1,
                                className="mb-3 w-100",
                                clearable=True,
                                with_portal=True,
                                updatemode='bothdates'
                            ),
                            
                            # Filtre par caractéristiques
                            html.Label("Caractéristiques à analyser", className="form-label mt-3"),
                            dcc.Checklist(
                                id='features-checklist',
                                options=[
                                    {'label': ' Âge', 'value': 'age'},
                                    {'label': ' Niveau d\'études', 'value': 'niveau_d_etude'},
                                    {'label': ' Genre', 'value': 'genre'},
                                    {'label': ' Situation matrimoniale', 'value': 'situation_matrimoniale_(sm)'},
                                    {'label': ' Profession', 'value': 'profession'},
                                    {'label': ' Religion', 'value': 'religion'},
                                    {'label': ' Localisation', 'value': 'arrondissement_de_residence'}
                                ],
                                value=['age', 'niveau_d_etude', 'genre'],
                                className="checklist-container",
                                inputClassName="me-2",
                                labelClassName="ms-2 mb-2"
                            ),
                            
                            # Filtre par éligibilité
                            html.Label("Statut d'éligibilité", className="form-label mt-3"),
                            dcc.Dropdown(
                                id='eligibility-filter',
                                options=[
                                    {'label': 'Tous', 'value': 'all'},
                                    {'label': 'Éligibles', 'value': 'eligible'},
                                    {'label': 'Non éligibles', 'value': 'non_eligible'}
                                ],
                                value='all',
                                className="mb-3",
                                clearable=False
                            )
                        ])
                    ], className="border-0")
                ], style={
                    "overflowY": "auto",
                    "maxHeight": "calc(100vh - 200px)",  # Hauteur maximale avec défilement
                    "position": "relative"
                }),
                
                # Footer fixe du sidebar
                html.Div([
                    dbc.Button(
                        "Appliquer les filtres",
                        color="primary",
                        className="w-100 mt-3",
                        id="apply-filters"
                    )
                ], style={
                    "position": "sticky",
                    "bottom": "0",
                    "backgroundColor": "white",
                    "padding": "1rem 0",
                    "borderTop": "1px solid #dee2e6"
                })
            ], width=3, className="shadow-sm", style={"height": "calc(100vh - 100px)"}),
            
            # Visualisations principales
            dbc.Col([
                dbc.Row([
                    # Distribution démographique
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Distribution démographique"),
                            dbc.CardBody([
                                dcc.Loading(
                                    dcc.Graph(
                                        id='demographic-distribution',
                                        config={'displayModeBar': True, 'scrollZoom': True},
                                        style={'height': '400px'}
                                    ),
                                    type="circle"
                                )
                            ])
                        ], className="shadow-sm mb-4")
                    ], width=12),
                    
                    # Statistiques par caractéristique
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Statistiques par caractéristique"),
                            dbc.CardBody([
                                dcc.Loading(
                                    dcc.Graph(
                                        id='feature-statistics',
                                        config={'displayModeBar': True, 'scrollZoom': True},
                                        style={'height': '400px'}
                                    ),
                                    type="circle"
                                )
                            ])
                        ], className="shadow-sm")
                    ], width=12)
                ])
            ], width=9)
        ]),
        
        # Analyse détaillée
        dbc.Row([
            # Historique des dons
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Historique des dons"),
                    dbc.CardBody([
                        dcc.Loading(
                            dcc.Graph(
                                id='donation-history',
                                config={'displayModeBar': True, 'scrollZoom': True},
                                style={'height': '400px'}
                            ),
                            type="circle"
                        )
                    ])
                ], className="shadow-sm")
            ], width=6),
            
            # Taux de retour
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Taux de retour par profil"),
                    dbc.CardBody([
                        dcc.Loading(
                            dcc.Graph(
                                id='return-rate',
                                config={'displayModeBar': True, 'scrollZoom': True},
                                style={'height': '400px'}
                            ),
                            type="circle"
                        )
                    ])
                ], className="shadow-sm")
            ], width=6)
        ], className="mt-4"),
        
        # Tableau récapitulatif
        dbc.Row([
            dbc.Col([
                html.H4("Résumé des profils", 
                       className="text-primary fw-bold mt-4 mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(
                            id='profile-summary',
                            className="table-responsive"
                        )
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ], fluid=True, className="px-4 py-3")
