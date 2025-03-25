import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px
from datetime import datetime

def create_campaign_analysis_layout():
    """Crée le layout pour la page d'analyse des campagnes"""
    return html.Div([
        # Filtres en position fixe
        html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Filtres"),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Ville"),
                                        dcc.Dropdown(
                                            id='city-filter',
                                            options=[
                                                {'label': 'Toutes', 'value': 'all'},
                                                {'label': 'Douala', 'value': 'douala'},
                                                {'label': 'Yaoundé', 'value': 'yaounde'}
                                            ],
                                            value='all',
                                            className="mb-2"
                                        )
                                    ], md=3),
                                    dbc.Col([
                                        html.Label("Arrondissement"),
                                        dcc.Dropdown(
                                            id='district-filter',
                                            placeholder="Sélectionner un arrondissement",
                                            className="mb-2"
                                        )
                                    ], md=3),
                                    dbc.Col([
                                        html.Label("Quartier"),
                                        dcc.Dropdown(
                                            id='neighborhood-filter',
                                            placeholder="Sélectionner un quartier",
                                            className="mb-2"
                                        )
                                    ], md=3),
                                    dbc.Col([
                                        html.Label("Période"),
                                        dcc.DatePickerRange(
                                            id='date-range',
                                            className="mb-2"
                                        )
                                    ], md=3)
                                ])
                            ])
                        ], className="mb-4")
                    ])
                ])
            ], fluid=True)
        ], style={
            'position': 'sticky',
            'top': 0,
            'zIndex': 1000,
            'backgroundColor': 'white',
            'paddingTop': '1rem',
            'paddingBottom': '1rem',
            'borderBottom': '1px solid #dee2e6'
        }),
        
        # Contenu principal
        dbc.Container([
            # Statistiques générales
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Nombre total de dons", className="card-title"),
                            html.H2(id="total-donations", className="text-primary")
                        ])
                    ])
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Taux d'éligibilité", className="card-title"),
                            html.H2(id="eligibility-rate", className="text-success")
                        ])
                    ])
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Nombre de quartiers", className="card-title"),
                            html.H2(id="total-neighborhoods", className="text-info")
                        ])
                    ])
                ], md=4)
            ], className="mb-4"),
            
            # Graphiques
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(
                                id='donations-timeline',
                                config={'displayModeBar': False}
                            )
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(
                                id='eligibility-age-distribution',
                                config={'displayModeBar': False}
                            )
                        ])
                    ])
                ])
            ])
        ], fluid=True)
    ])
