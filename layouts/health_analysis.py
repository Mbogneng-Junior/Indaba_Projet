import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px

def create_health_analysis_layout():
    """Crée le layout pour la page d'analyse de santé et d'éligibilité"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("🏥 Conditions de Santé & Éligibilité", 
                       className="text-primary text-center mb-3"),
                html.P("Analyse des facteurs d'éligibilité et des raisons d'indisponibilité",
                      className="text-muted text-center mb-4"),
            ])
        ]),
        
        # Vue d'ensemble de l'éligibilité
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Statut d'éligibilité global"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='eligibility-pie-chart',
                            figure={}  # Sera mis à jour par le callback
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Statistiques détaillées"),
                    dbc.CardBody([
                        html.Div([
                            html.H4(id="eligible-count", className="text-success"),
                            html.P("Individus éligibles", className="text-muted")
                        ], className="mb-3"),
                        html.Div([
                            html.H4(id="temp-unavailable-count", className="text-warning"),
                            html.P("Temporairement non disponibles", className="text-muted")
                        ], className="mb-3"),
                        html.Div([
                            html.H4(id="non-eligible-count", className="text-danger"),
                            html.P("Non éligibles", className="text-muted")
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ], width=6)
        ]),
        
        # Problèmes de santé et raisons d'indisponibilité
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Top 3 des problèmes de santé"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='top-health-issues',
                            figure={}  # Sera mis à jour par le callback
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Top 3 des raisons d'indisponibilité"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='top-unavailability-reasons',
                            figure={}  # Sera mis à jour par le callback
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], width=6)
        ]),
        
        # Graphiques détaillés
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Problèmes de santé - Non éligibilité"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='health-issues-bar',
                            figure={}  # Sera mis à jour par le callback
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Raisons d'indisponibilité temporaire"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='temp-unavailability-bar',
                            figure={}  # Sera mis à jour par le callback
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Analyse géographique
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Analyse par zone géographique"),
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab([
                                dcc.Graph(
                                    id='city-analysis',
                                    figure={}  # Sera mis à jour par le callback
                                )
                            ], label="Par ville"),
                            dbc.Tab([
                                dcc.Graph(
                                    id='district-analysis',
                                    figure={}  # Sera mis à jour par le callback
                                )
                            ], label="Par arrondissement"),
                            dbc.Tab([
                                dcc.Graph(
                                    id='neighborhood-analysis',
                                    figure={}  # Sera mis à jour par le callback
                                )
                            ], label="Par quartier")
                        ])
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
        
    ], fluid=True, className="px-4 py-3")
