import dash_bootstrap_components as dbc
from dash import html, dcc

def create_health_analysis_layout():
    """Crée le layout pour la page d'analyse de santé"""
    return dbc.Container([
        # Filtres (position fixe, z-index élevé)
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4("Filtres d'analyse", className="card-title mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Zone géographique", className="mb-2"),
                                dcc.Dropdown(
                                    id='health-location-filter',
                                    placeholder="Sélectionner une zone",
                                    className="mb-3",
                                    style={'zIndex': 9999}
                                )
                            ], md=6),
                            dbc.Col([
                                html.Label("Période d'analyse", className="mb-2"),
                                dcc.DatePickerRange(
                                    id='health-date-range',
                                    className="mb-3",
                                    style={'zIndex': 9999}
                                )
                            ], md=6)
                        ])
                    ])
                ])
            ])
        ], className="mb-4", style={'position': 'relative', 'zIndex': 1000}),

        # Statistiques détaillées en haut
        dbc.Card([
            dbc.CardHeader("Statistiques détaillées"),
            dbc.CardBody(id='detailed-stats')
        ], className="mb-4"),
        
        # Contenu principal
        dbc.Row([
            # Première colonne (plus petite)
            dbc.Col([
                # Top 3 problèmes de santé
                dbc.Card([
                    dbc.CardHeader("Top 3 des problèmes de santé"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='top-health-issues',
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4"),
                
                # Top 3 raisons d'indisponibilité
                dbc.Card([
                    dbc.CardHeader("Top 3 des raisons d'indisponibilité"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='top-unavailability-reasons',
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], width=4),
            
            # Deuxième colonne (plus grande)
            dbc.Col([
                # Raisons d'indisponibilité temporaire
                dbc.Card([
                    dbc.CardHeader("Raisons d'indisponibilité temporaire"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='temporary-unavailability-chart',
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4"),
                
                # Analyse par zone géographique
                dbc.Card([
                    dbc.CardHeader("Analyse par zone géographique"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='geographic-health-analysis',
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], width=8)
        ], className="mb-4"),
        
        # Graphique des problèmes de santé en bas
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Problèmes de santé - Non éligibilité"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='health-issues-chart',
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # Tableau d'interprétation
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Interprétation des résultats"),
                    dbc.CardBody([
                        html.Div(id='health-interpretation-table')
                    ])
                ])
            ])
        ])
    ], fluid=True)
