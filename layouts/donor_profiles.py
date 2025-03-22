import dash_bootstrap_components as dbc
from dash import html, dcc

def create_donor_profiles_layout():
    """Crée le layout pour la page de profilage des donneurs"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("👥 Profilage des Donneurs", 
                       className="text-primary text-center mb-3"),
                html.P("Analyse et segmentation des profils de donneurs de sang",
                      className="text-muted text-center mb-4"),
            ])
        ]),
        
        # Contrôles et paramètres
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Paramètres d'analyse"),
                    dbc.CardBody([
                        html.Label("Nombre de clusters", className="fw-bold mb-2"),
                        dcc.Slider(
                            id='n-clusters-slider',
                            min=2,
                            max=8,
                            step=1,
                            value=4,
                            marks={i: str(i) for i in range(2, 9)},
                            className="mb-4"
                        ),
                        
                        html.Label("Caractéristiques à analyser", className="fw-bold mb-2"),
                        dcc.Checklist(
                            id='features-checklist',
                            options=[
                                {'label': ' Âge', 'value': 'age'},
                                {'label': ' Genre', 'value': 'genre'},
                                {'label': ' Profession', 'value': 'profession'},
                                {'label': ' État de santé', 'value': 'sante'},
                                {'label': ' Localisation', 'value': 'location'}
                            ],
                            value=['age', 'genre', 'sante'],
                            className="mb-3"
                        ),
                        
                        dbc.Button(
                            "Analyser les profils",
                            id="analyze-profiles",
                            color="primary",
                            className="w-100"
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], width=3),
            
            # Visualisation des clusters
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Distribution des profils"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='cluster-visualization',
                            style={'height': '60vh'}
                        )
                    ])
                ], className="shadow-sm")
            ], width=9)
        ]),
        
        # Caractéristiques des clusters
        dbc.Row([
            dbc.Col([
                html.H4("Caractéristiques des profils", 
                       className="text-primary fw-bold mt-4 mb-3"),
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='cluster-characteristics')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ]),
        
        # Détails des profils
        dbc.Row([
            dbc.Col([
                html.H4("Profils détaillés", 
                       className="text-primary fw-bold mt-4 mb-3"),
                html.Div(id='profile-details')
            ])
        ])
    ], fluid=True, className="px-4 py-3")
