import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import date

def create_feedback_analysis_layout():
    """Crée le layout pour la page d'analyse des retours"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Analyse des Retours", 
                        className="text-primary mb-4"),
                html.P("Analyse détaillée des retours et de la satisfaction des donneurs",
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
                            id='feedback-date-range',
                            start_date=date(2019, 1, 1),  # Ajusté pour correspondre aux données
                            end_date=date(2024, 12, 31),
                            display_format='DD/MM/YYYY',
                            className="mb-3"
                        )
                    ], md=12)
                ])
            ])
        ], className="mb-4"),
        
        # Statistiques générales
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Retours totaux"),
                    dbc.CardBody([
                        html.H3(id="total-feedback", className="text-primary text-center"),
                        dbc.Spinner(color="primary", type="grow", size="sm")
                    ])
                ])
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Retours positifs"),
                    dbc.CardBody([
                        html.H3(id="positive-feedback", className="text-success text-center"),
                        dbc.Spinner(color="success", type="grow", size="sm")
                    ])
                ])
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Retours négatifs"),
                    dbc.CardBody([
                        html.H3(id="negative-feedback", className="text-danger text-center"),
                        dbc.Spinner(color="danger", type="grow", size="sm")
                    ])
                ])
            ], md=4)
        ], className="mb-4"),
        
        # Graphiques d'analyse
        dbc.Row([
            # Graphique en camembert
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Répartition des retours"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id='feedback-pie-chart',
                                config={'displayModeBar': False}
                            ),
                            color="primary",
                            type="grow",
                            size="sm"
                        )
                    ])
                ])
            ], md=6),
            
            # Timeline
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Évolution des retours dans le temps"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id='feedback-timeline',
                                config={'displayModeBar': False}
                            ),
                            color="primary",
                            type="grow",
                            size="sm"
                        )
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # Analyses croisées
        dbc.Row([
            # Colonne de gauche
            dbc.Col([
                # Analyse par âge
                dbc.Card([
                    dbc.CardHeader("Analyse par tranche d'âge"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id='age-feedback-analysis',
                                config={'displayModeBar': False}
                            ),
                            color="primary",
                            type="grow",
                            size="sm"
                        )
                    ])
                ], className="mb-4"),
                
                # Analyse par genre
                dbc.Card([
                    dbc.CardHeader("Analyse par genre"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id='gender-feedback-analysis',
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
                # Analyse par niveau d'études
                dbc.Card([
                    dbc.CardHeader("Analyse par niveau d'études"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id='education-feedback-analysis',
                                config={'displayModeBar': False}
                            ),
                            color="primary",
                            type="grow",
                            size="sm"
                        )
                    ])
                ], className="mb-4"),
                
                # Analyse par localisation
                dbc.Card([
                    dbc.CardHeader("Analyse par localisation"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id='location-feedback-analysis',
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
