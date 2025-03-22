import dash_bootstrap_components as dbc
from dash import html, dcc

def create_feedback_analysis_layout():
    """Crée le layout pour la page d'analyse des retours"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("💬 Analyse des Retours", 
                       className="text-primary text-center mb-3"),
                html.P("Analyse de sentiment et classification des retours des donneurs",
                      className="text-muted text-center mb-4"),
            ])
        ]),
        
        # KPIs et filtres
        dbc.Row([
            # KPIs
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3(id="total-feedback", className="text-primary mb-0"),
                                    html.Small("Retours analysés", className="text-muted")
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="sentiment-positif", className="text-success mb-0"),
                                    html.Small("Sentiment positif", className="text-muted")
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="sentiment-neutre", className="text-warning mb-0"),
                                    html.Small("Sentiment neutre", className="text-muted")
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                html.Div([
                                    html.H3(id="sentiment-negatif", className="text-danger mb-0"),
                                    html.Small("Sentiment négatif", className="text-muted")
                                ], className="text-center")
                            ], width=3),
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ], width=12),
            
            # Filtres
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filtres d'analyse"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Période", className="fw-bold mb-2"),
                                dcc.RangeSlider(
                                    id='feedback-period-slider',
                                    min=2019,
                                    max=2023,
                                    value=[2019, 2023],
                                    marks={str(year): str(year) for year in range(2019, 2024)},
                                    className="mb-3"
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Groupe démographique", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id='feedback-demographic-dropdown',
                                    options=[
                                        {'label': 'Genre', 'value': 'genre'},
                                        {'label': 'Âge', 'value': 'age'},
                                        {'label': 'Profession', 'value': 'profession'},
                                        {'label': 'Arrondissement', 'value': 'arrondissement'}
                                    ],
                                    value='genre',
                                    className="mb-3"
                                )
                            ], width=6)
                        ])
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Visualisations principales
        dbc.Row([
            # Analyse de sentiment
            dbc.Col([
                html.H4("Analyse de Sentiment", 
                       className="text-primary fw-bold mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='sentiment-evolution')
                    ])
                ], className="shadow-sm mb-4"),
                
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='sentiment-by-group')
                    ])
                ], className="shadow-sm")
            ], width=8),
            
            # Nuage de mots et thèmes
            dbc.Col([
                html.H4("Thèmes Principaux", 
                       className="text-primary fw-bold mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        html.Img(id='wordcloud-positive', 
                               className="img-fluid mb-3",
                               style={'width': '100%'}),
                        html.H6("Mots positifs fréquents", 
                               className="text-success text-center")
                    ])
                ], className="shadow-sm mb-4"),
                
                dbc.Card([
                    dbc.CardBody([
                        html.Img(id='wordcloud-negative', 
                               className="img-fluid mb-3",
                               style={'width': '100%'}),
                        html.H6("Points d'amélioration fréquents", 
                               className="text-danger text-center")
                    ])
                ], className="shadow-sm")
            ], width=4)
        ]),
        
        # Analyse détaillée
        dbc.Row([
            dbc.Col([
                html.H4("Analyse Détaillée", 
                       className="text-primary fw-bold mt-4 mb-3"),
                dbc.Tabs([
                    dbc.Tab([
                        dcc.Graph(id='topic-distribution')
                    ], label="Distribution des thèmes"),
                    
                    dbc.Tab([
                        dcc.Graph(id='sentiment-patterns')
                    ], label="Patterns de sentiment"),
                    
                    dbc.Tab([
                        dcc.Graph(id='feedback-categories')
                    ], label="Catégories de retour")
                ])
            ], width=12)
        ]),
        
        # Exemples de retours
        dbc.Row([
            dbc.Col([
                html.H4("Exemples de Retours", 
                       className="text-primary fw-bold mt-4 mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='feedback-examples')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ], fluid=True, className="px-4 py-3")
