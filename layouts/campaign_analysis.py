import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px
from datetime import datetime

def create_campaign_analysis_layout():
    """Crée le layout pour la page d'analyse des campagnes de don de sang"""
    return dbc.Container([
        # En-tête
        dbc.Row([
            dbc.Col([
                html.H2("Analyse de l'Efficacité des Campagnes", 
                       className="text-primary mb-3"),
                html.P("Analyse des tendances et comportements des donneurs de sang",
                      className="text-muted mb-4"),
            ])
        ]),
        
        # Filtres temporels
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Période d'analyse"),
                    dbc.CardBody([
                        dcc.DatePickerRange(
                            id='campaign-date-range',
                            className="mb-3 w-100",
                            start_date='1977-12-25',
                            end_date='2020-10-12',
                            min_date_allowed='1977-12-25',
                            max_date_allowed='2020-10-12',
                            style={'zIndex': 1000}
                        )
                    ])
                ], className="shadow-sm mb-4")
            ])
        ]),
        
        # KPIs des campagnes
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Indicateurs Clés", className="card-title mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3(id="campaign-total-donations", className="text-primary mb-0"),
                                    html.Small("Total des dons", className="text-muted")
                                ], className="text-center")
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="campaign-peak-period", className="text-success mb-0"),
                                    html.Small("Période la plus active", className="text-muted")
                                ], className="text-center")
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="campaign-growth-rate", className="text-warning mb-0"),
                                    html.Small("Taux de croissance", className="text-muted")
                                ], className="text-center")
                            ], width=4)
                        ])
                    ])
                ], className="shadow-sm mb-4")
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
                                dcc.Graph(id='campaign-age-analysis')
                            ], label="Âge"),
                            dbc.Tab([
                                dcc.Graph(id='campaign-gender-analysis')
                            ], label="Genre"),
                            dbc.Tab([
                                dcc.Graph(id='campaign-education-analysis')
                            ], label="Niveau d'études"),
                            dbc.Tab([
                                dcc.Graph(id='campaign-profession-analysis')
                            ], label="Profession"),
                            dbc.Tab([
                                dcc.Graph(id='campaign-religion-analysis')
                            ], label="Religion"),
                            dbc.Tab([
                                dcc.Graph(id='campaign-marital-analysis')
                            ], label="Situation matrimoniale")
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ])
        ]),
        
        # Analyse temporelle
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Évolution des dons dans le temps"),
                    dbc.CardBody([
                        dcc.Graph(id='campaign-timeline')
                    ])
                ], className="shadow-sm mb-4")
            ], md=8),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Distribution mensuelle"),
                    dbc.CardBody([
                        dcc.Graph(id='campaign-monthly-distribution')
                    ])
                ], className="shadow-sm mb-4")
            ], md=4)
        ])
        
    ], fluid=True, className="px-4 py-3")
