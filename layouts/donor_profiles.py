import dash_bootstrap_components as dbc
from dash import html, dcc

def create_donor_profiles_layout():
    """Crée le layout pour la page des profils donneurs"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Profils des Donneurs", className="text-primary mb-4")
            ])
        ]),
        
        # Filtres
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filtres"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Localisation"),
                                dcc.Dropdown(
                                    id='location-filter',
                                    placeholder="Sélectionner un arrondissement",
                                    className="mb-2"
                                )
                            ], md=4),
                            dbc.Col([
                                html.Label("Statut d'éligibilité"),
                                dcc.Dropdown(
                                    id='eligibility-filter',
                                    options=[
                                        {'label': 'Éligible', 'value': 'eligible'},
                                        {'label': 'Non éligible', 'value': 'ineligible'}
                                    ],
                                    placeholder="Sélectionner un statut",
                                    className="mb-2"
                                )
                            ], md=4),
                            dbc.Col([
                                html.Label("Nombre de clusters"),
                                dcc.Slider(
                                    id='cluster-slider',
                                    min=2,
                                    max=6,
                                    step=1,
                                    value=3,
                                    marks={i: str(i) for i in range(2, 7)},
                                    className="mt-2"
                                )
                            ], md=4)
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Section Clustering
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Analyse par Clustering"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(
                                    id='cluster-scatter',
                                    config={'displayModeBar': False}
                                )
                            ], md=8),
                            dbc.Col([
                                html.Div(id='cluster-characteristics', className="cluster-analysis")
                            ], md=4)
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Graphiques de distribution
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='age-distribution',
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='religion-distribution',
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='eligibility-distribution',
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='education-distribution',
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='marital-distribution',
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='gender-distribution',
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # Tableau d'interprétation des profils
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Interprétation des Profils"),
                    dbc.CardBody([
                        html.Div(id='profile-interpretation-table')
                    ])
                ])
            ])
        ])
    ], fluid=True)
