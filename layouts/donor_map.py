import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

def create_donor_map_layout():
    """Crée le layout pour la carte des donneurs"""
    
    return html.Div([
        dbc.Row([
            # En-tête
            dbc.Col([
                html.H1("Carte des Donneurs", className="page-title"),
                html.P(
                    "Visualisez la répartition géographique des donneurs de sang",
                    className="lead"
                ),
                html.Hr(),
            ], width=12)
        ]),
        
        dbc.Row([
            # Filtres
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Filtres", className="card-title"),
                        dbc.Form([
                            dbc.Row([
                                dbc.Label("Période"),
                                dcc.DatePickerRange(
                                    id='date-range',
                                    start_date_placeholder_text="Date début",
                                    end_date_placeholder_text="Date fin",
                                    calendar_orientation='vertical',
                                )
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Label("Type de donneur"),
                                dbc.Select(
                                    id='donor-type',
                                    options=[
                                        {"label": "Tous", "value": "all"},
                                        {"label": "Réguliers", "value": "regular"},
                                        {"label": "Occasionnels", "value": "occasional"},
                                        {"label": "Nouveaux", "value": "new"}
                                    ],
                                    value="all"
                                )
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Label("Groupe sanguin"),
                                dbc.Select(
                                    id='blood-type',
                                    options=[
                                        {"label": "Tous", "value": "all"},
                                        {"label": "A+", "value": "A+"},
                                        {"label": "A-", "value": "A-"},
                                        {"label": "B+", "value": "B+"},
                                        {"label": "B-", "value": "B-"},
                                        {"label": "AB+", "value": "AB+"},
                                        {"label": "AB-", "value": "AB-"},
                                        {"label": "O+", "value": "O+"},
                                        {"label": "O-", "value": "O-"}
                                    ],
                                    value="all"
                                )
                            ], className="mb-3")
                        ])
                    ])
                ], className="mb-4")
            ], width=3),
            
            # Carte
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            id='donor-map',
                            figure={},
                            style={'height': '70vh'}
                        )
                    ])
                ])
            ], width=9)
        ]),
        
        dbc.Row([
            # Statistiques par zone
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Statistiques par Zone", className="card-title"),
                        dcc.Graph(
                            id='zone-stats',
                            figure={}
                        )
                    ])
                ])
            ], width=12, className="mt-4")
        ])
    ], className="p-4")
