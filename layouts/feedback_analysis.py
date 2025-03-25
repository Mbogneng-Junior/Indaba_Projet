import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_feedback_analysis_layout():
    """Crée le layout de la page d'analyse des retours"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Analyse des Retours", 
                        className="text-primary mb-4")
            ])
        ]),
        
        # Vue d'ensemble des retours
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Distribution des retours"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id="feedback-pie-chart")
                            ], width=6),
                            dbc.Col([
                                html.Div([
                                    html.H4(id="total-feedback", className="text-primary"),
                                    html.P("Total des retours", className="text-muted")
                                ], className="mb-3"),
                                html.Div([
                                    html.H4(id="positive-feedback", className="text-success"),
                                    html.P("Retours positifs", className="text-muted")
                                ], className="mb-3"),
                                html.Div([
                                    html.H4(id="negative-feedback", className="text-danger"),
                                    html.P("Retours négatifs", className="text-muted")
                                ])
                            ], width=6)
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Analyse des raisons
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Analyse des raisons"),
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab([
                                dcc.Graph(id="other-reasons-analysis")
                            ], label="Autres raisons"),
                            dbc.Tab([
                                dcc.Graph(id="main-reasons-analysis")
                            ], label="Raisons principales")
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Analyse par caractéristiques
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Analyse par caractéristiques"),
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab([
                                dcc.Graph(id="age-feedback-analysis")
                            ], label="Par âge"),
                            dbc.Tab([
                                dcc.Graph(id="gender-feedback-analysis")
                            ], label="Par genre"),
                            dbc.Tab([
                                dcc.Graph(id="education-feedback-analysis")
                            ], label="Par niveau d'études"),
                            dbc.Tab([
                                dcc.Graph(id="location-feedback-analysis")
                            ], label="Par localisation")
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Évolution temporelle
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Évolution des retours dans le temps"),
                    dbc.CardBody([
                        dcc.Graph(id="feedback-timeline")
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Nuage de mots des commentaires
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Analyse des commentaires"),
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab([
                                html.Div(id="positive-wordcloud")
                            ], label="Commentaires positifs"),
                            dbc.Tab([
                                html.Div(id="negative-wordcloud")
                            ], label="Commentaires négatifs")
                        ])
                    ])
                ], className="mb-4")
            ])
        ])
        
    ], fluid=True, className="py-4")
