import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

def create_donor_retention_layout():
    """Crée le layout pour la page d'analyse de la fidélisation des donneurs"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Analyse de la Fidélisation des Donneurs", 
                        className="text-primary mb-4"),
                html.P("Analyse basée uniquement sur les donneurs ayant déjà effectué au moins un don",
                      className="text-muted mb-4")
            ])
        ]),
        
        # Statistiques générales
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Vue d'ensemble de la fidélisation"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H4(id="total-previous-donors", className="text-primary"),
                                html.P("Donneurs avec historique", className="text-muted")
                            ], width=4),
                            dbc.Col([
                                html.H4(id="avg-donations", className="text-success"),
                                html.P("Moyenne de dons par donneur", className="text-muted")
                            ], width=4),
                            dbc.Col([
                                html.H4(id="retention-rate", className="text-info"),
                                html.P("Taux de fidélisation", className="text-muted")
                            ], width=4)
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Analyse croisée des caractéristiques
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Analyse croisée des caractéristiques"),
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab([
                                dcc.Graph(id="age-gender-retention")
                            ], label="Âge × Genre"),
                            dbc.Tab([
                                dcc.Graph(id="education-gender-retention")
                            ], label="Niveau d'études × Genre"),
                            dbc.Tab([
                                dcc.Graph(id="location-gender-retention")
                            ], label="Localisation × Genre"),
                            dbc.Tab([
                                dcc.Graph(id="marital-gender-retention")
                            ], label="Situation matrimoniale × Genre")
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Distribution géographique
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Distribution géographique des donneurs fidèles"),
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab([
                                dcc.Graph(id="city-retention-map")
                            ], label="Par ville"),
                            dbc.Tab([
                                dcc.Graph(id="district-retention-map")
                            ], label="Par arrondissement"),
                            dbc.Tab([
                                dcc.Graph(id="neighborhood-retention-map")
                            ], label="Par quartier")
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Évolution temporelle
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Évolution de la fidélisation"),
                    dbc.CardBody([
                        dcc.Graph(id="retention-timeline")
                    ])
                ], className="mb-4")
            ])
        ])
        
    ], fluid=True, className="py-4")
