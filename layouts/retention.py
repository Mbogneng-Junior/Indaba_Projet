import dash_bootstrap_components as dbc
from dash import html, dcc

def create_retention_layout():
    """Crée le layout pour la page d'analyse de rétention"""
    return dbc.Container([
        # Filtres
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4("Filtres d'analyse", className="card-title mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Zone géographique", className="mb-2"),
                                dcc.Dropdown(
                                    id='retention-location-filter',
                                    options=[
                                        {'label': 'Toutes les zones', 'value': 'all'},
                                        {'label': 'Douala', 'value': 'douala'},
                                        {'label': 'Yaoundé', 'value': 'yaounde'}
                                    ],
                                    value='all',
                                    className="mb-3"
                                )
                            ], md=6),
                            dbc.Col([
                                html.Label("Période d'analyse", className="mb-2"),
                                dcc.DatePickerRange(
                                    id='retention-date-range',
                                    className="mb-3"
                                )
                            ], md=6)
                        ])
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # Statistiques de rétention
        dbc.Card([
            dbc.CardHeader("Statistiques de rétention"),
            dbc.CardBody(id='retention-stats')
        ], className="mb-4"),
        
        # Graphiques principaux
        dbc.Row([
            # Colonne de gauche
            dbc.Col([
                # Tendance de rétention
                dbc.Card([
                    dbc.CardHeader("Évolution du taux de rétention"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='retention-trend',
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4"),
                
                # Fréquence des dons
                dbc.Card([
                    dbc.CardHeader("Fréquence des dons"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='donor-frequency',
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], width=6),
            
            # Colonne de droite
            dbc.Col([
                # Rétention par âge
                dbc.Card([
                    dbc.CardHeader("Rétention par tranche d'âge"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='retention-by-age',
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4"),
                
                # Rétention par zone
                dbc.Card([
                    dbc.CardHeader("Rétention par zone géographique"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='retention-by-location',
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], width=6)
        ])
    ], fluid=True)
