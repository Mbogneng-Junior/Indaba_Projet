import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px
import pandas as pd


def create_home_layout():
    """Crée le layout de la page d'accueil"""
    
    # Charger les données pour les statistiques initiales
    df = pd.read_csv('data/processed_data.csv')
    total_donors = len(df)
    # total_regions = df['arrondissement_de_residence'].str.extract(r'(Douala|Yaoundé)').dropna().nunique()
    total_arrondissements = df['arrondissement_de_residence'].nunique()
    total_quartiers = df['quartier_de_residence'].nunique()
    successful_donations = len(df[df['eligibilite_au_don'] == 'eligible'])
    ineligible_donations = len(df[df['eligibilite_au_don'] != 'eligible'])
    
    return html.Div([
        # En-tête avec titre et bouton
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Campagne de Don de Sang", 
                           className="app-title text-center mb-2"),
                    html.P("Analyse et Optimisation des Campagnes de Don de Sang en Afrique",
                          className="app-subtitle text-center mb-4"),
                    html.Div([
                        dbc.Button(
                            "Explorer le Dashboard",
                            href="/profils",  # Redirection vers la page Profils Donneurs
                            className="explore-button mx-auto",
                            style={
                                'backgroundColor': '#c62828',
                                'color': '#ffffff',
                                'borderColor': '#c62828',
                                'borderWidth': '2px',
                                'borderStyle': 'solid',
                                'borderRadius': '50px',
                                'padding': '12px 30px',
                                'fontSize': '16px',
                                'fontWeight': '600',
                                'boxShadow': '0 4px 15px rgba(198, 40, 40, 0.2)',
                                'transition': 'all 0.3s ease'
                            }
                        )
                    ], className="text-center mb-5")
                ], width=12)
            ])
        ], fluid=True, className="header-container"),
        
        # Section des statistiques principales
        dbc.Container([
            dbc.Row([
                # Première ligne de statistiques
               # """dbc.Col([
#                     dbc.Card([
#                         html.Div([
#                             html.Span(className="stat-icon-bg"),
#                             html.I(className="fas fa-map-marker-alt stat-icon")
#                         ], className="stat-icon-wrapper"),
#                         html.H3(id="stats-regions", 
#                                children=f"{total_regions}", 
#                                className="stat-value"),
#                         html.P("Régions", className="stat-label"),
#                         html.Small("Douala et Yaoundé", className="stat-detail")
#                     ], className="stat-card")
#                 ], xs=12, sm=6, md=4, lg=3, className="mb-3"),"""
                
                dbc.Col([
                    dbc.Card([
                        html.Div([
                            html.Span(className="stat-icon-bg"),
                            html.I(className="fas fa-building stat-icon")
                        ], className="stat-icon-wrapper"),
                        html.H3(id="stats-arrondissements",
                               children=f"{total_arrondissements}", 
                               className="stat-value"),
                        html.P("Arrondissements", className="stat-label"),
                        html.Small("Zones couvertes", className="stat-detail")
                    ], className="stat-card")
                ], xs=12, sm=6, md=4, lg=3, className="mb-3"),
                
                dbc.Col([
                    dbc.Card([
                        html.Div([
                            html.Span(className="stat-icon-bg"),
                            html.I(className="fas fa-home stat-icon")
                        ], className="stat-icon-wrapper"),
                        html.H3(id="stats-quartiers",
                               children=f"{total_quartiers}", 
                               className="stat-value"),
                        html.P("Quartiers", className="stat-label"),
                        html.Small("Zones de collecte", className="stat-detail")
                    ], className="stat-card")
                ], xs=12, sm=6, md=4, lg=3, className="mb-3"),
                
                dbc.Col([
                    dbc.Card([
                        html.Div([
                            html.Span(className="stat-icon-bg"),
                            html.I(className="fas fa-users stat-icon")
                        ], className="stat-icon-wrapper"),
                        html.H3(id="stats-donors",
                               children=f"{total_donors:,}", 
                               className="stat-value"),
                        html.P("Donneurs", className="stat-label"),
                        html.Small("Total participants", className="stat-detail")
                    ], className="stat-card")
                ], xs=12, sm=6, md=4, lg=3, className="mb-3"),
            ], className="mb-3"),
            
            # Deuxième ligne de statistiques
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.Div([
                            html.Span(className="stat-icon-bg success"),
                            html.I(className="fas fa-check-circle stat-icon")
                        ], className="stat-icon-wrapper"),
                        html.H3(id="stats-successful",
                               children=f"{successful_donations:,}", 
                               className="stat-value text-success"),
                        html.P("Dons Éligibles", className="stat-label"),
                        html.Small(f"{(successful_donations/total_donors*100):.1f}% du total", className="stat-detail")
                    ], className="stat-card")
                ], xs=12, sm=6, md=4, lg=3, className="mb-3"),
                
                dbc.Col([
                    dbc.Card([
                        html.Div([
                            html.Span(className="stat-icon-bg danger"),
                            html.I(className="fas fa-times-circle stat-icon")
                        ], className="stat-icon-wrapper"),
                        html.H3(id="stats-ineligible",
                               children=f"{ineligible_donations:,}", 
                               className="stat-value text-danger"),
                        html.P("Dons Non Éligibles", className="stat-label"),
                        html.Small(f"{(ineligible_donations/total_donors*100):.1f}% du total", className="stat-detail")
                    ], className="stat-card")
                ], xs=12, sm=6, md=4, lg=3, className="mb-3"),
            ], className="mb-4"),
            
            # Section de la carte et des filtres
            dbc.Row([
                # Filtres
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Filtres", className="filter-title mb-4"),
                            html.Div([
                                html.Label("Localisation", className="filter-label"),
                                dcc.Dropdown(
                                    id='location-filter',
                                    options=[
                                        {'label': 'Tout le Cameroun', 'value': 'all'},
                                        {'label': 'Douala', 'value': 'douala'},
                                        {'label': 'Yaoundé', 'value': 'yaounde'}
                                    ],
                                    value='all',
                                    className="filter-dropdown"
                                ),
                            ], className="filter-group"),
                            
                            html.Div([
                                html.Label("Zone", className="filter-label"),
                                dcc.Dropdown(
                                    id='zone-filter',
                                    options=[
                                        {'label': 'Tous les quartiers', 'value': 'tous'},
                                        {'label': 'Par Quartier', 'value': 'quartier'},
                                        {'label': 'Par Arrondissement', 'value': 'arrondissement'}
                                    ],
                                    value='tous',
                                    className="filter-dropdown"
                                ),
                            ], className="filter-group"),
                            
                            html.Div([
                                html.Label("Période", className="filter-label"),
                                dcc.DatePickerRange(
                                    id='date-filter',
                                    className="filter-date"
                                ),
                            ], className="filter-group"),
                        ])
                    ], className="filter-card")
                ], width=12, lg=3),
                
                # Carte
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Iframe(
                                id='donor-map',
                                srcDoc='',
                                style={
                                    'width': '100%',
                                    'height': '500px',
                                    'border': 'none'
                                }
                            )
                        ], className="p-0")
                    ], className="map-card")
                ], width=12, lg=9),
            ], className="mb-4"),
            
            # Nouvelle section pour les graphiques de statistiques
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(
                                id="donor-stats-graph",
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="graph-card mb-4")
                ], width=12, lg=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(
                                id="donor-geo-distribution",
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="graph-card mb-4")
                ], width=12, lg=6)
            ]),
            
            # Section des statistiques régionales
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            id="region-stats",
                            className="stats-body"
                        )
                    ], className="stats-card")
                ], width=12)
            ])
        ], fluid=True, className="main-container")
    ], className="dashboard-container")
