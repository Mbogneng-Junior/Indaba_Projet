import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import date

def create_donor_retention_layout():
    """Crée le layout pour la page d'analyse de la fidélisation des donneurs"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Analyse de la Fidélisation des Donneurs", 
                        className="text-primary mb-4"),
                html.P("Analyse détaillée des tendances de fidélisation des donneurs",
                      className="text-muted mb-4")
            ])
        ]),
        
        # Filtres
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Période d'analyse"),
                        dcc.DatePickerRange(
                            id='retention-date-range',
                            start_date=date(2019, 1, 1),  # Ajusté pour correspondre aux données
                            end_date=date(2024, 12, 31),
                            display_format='DD/MM/YYYY',
                            className="mb-3"
                        )
                    ], md=6),
                    dbc.Col([
                        html.Label("Zone géographique"),
                        dcc.Dropdown(
                            id='retention-location-filter',
                            options=[
                                {'label': 'Toutes les zones', 'value': 'all'},
                                {'label': 'Douala', 'value': 'douala'},
                                {'label': 'Yaoundé', 'value': 'yaounde'}
                            ],
                            value='all',
                            className="mb-3",
                            clearable=False
                        )
                    ], md=6)
                ])
            ])
        ], className="mb-4"),
        
        # Statistiques de rétention
        dbc.Card([
            dbc.CardHeader("Statistiques de rétention"),
            dbc.CardBody([
                html.Div(id='retention-stats'),
                dbc.Spinner(color="primary", type="grow", size="sm")
            ])
        ], className="mb-4"),
        
        # Graphiques d'analyse
        dbc.Row([
            # Colonne de gauche
            dbc.Col([
                # Tendance de rétention
                dbc.Card([
                    dbc.CardHeader("Évolution du taux de rétention"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id='retention-trend',
                                config={'displayModeBar': False}
                            ),
                            color="primary",
                            type="grow",
                            size="sm"
                        )
                    ])
                ], className="mb-4"),
                
                # Fréquence des dons
                dbc.Card([
                    dbc.CardHeader("Fréquence des dons"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id='donor-frequency',
                                config={'displayModeBar': False}
                            ),
                            color="primary",
                            type="grow",
                            size="sm"
                        )
                    ])
                ])
            ], md=6),
            
            # Colonne de droite
            dbc.Col([
                # Rétention par âge
                dbc.Card([
                    dbc.CardHeader("Rétention par tranche d'âge"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id='retention-by-age',
                                config={'displayModeBar': False}
                            ),
                            color="primary",
                            type="grow",
                            size="sm"
                        )
                    ])
                ], className="mb-4"),
                
                # Rétention par zone
                dbc.Card([
                    dbc.CardHeader("Rétention par zone géographique"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id='retention-by-location',
                                config={'displayModeBar': False}
                            ),
                            color="primary",
                            type="grow",
                            size="sm"
                        )
                    ])
                ])
            ], md=6)
        ])
    ], fluid=True)
