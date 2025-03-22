import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def create_home_layout():
    return html.Div([
        # Hero Section
        html.Div([
            html.Div([
                html.H1("Campagne de Don de Sang", className="hero-title"),
                html.P("Analyse et Optimisation des Campagnes de Don de Sang en Afrique", 
                      className="hero-subtitle"),
                dbc.Button("Explorer le Dashboard", href="/cartographie", 
                          className="hero-button", size="lg"),
            ], className="hero-content")
        ], className="hero-section"),

        # Stats Cards Section
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.Div([
                            html.I(className="fas fa-map-marker-alt stat-icon"),
                            html.Div([
                                html.H3("10+", className="stat-number"),
                                html.P("Régions", className="stat-label")
                            ])
                        ], className="stat-content")
                    ], className="stat-card")
                ], width=12, md=4),
                dbc.Col([
                    dbc.Card([
                        html.Div([
                            html.I(className="fas fa-users stat-icon"),
                            html.Div([
                                html.H3("1000+", className="stat-number"),
                                html.P("Donneurs", className="stat-label")
                            ])
                        ], className="stat-content")
                    ], className="stat-card")
                ], width=12, md=4),
                dbc.Col([
                    dbc.Card([
                        html.Div([
                            html.I(className="fas fa-tint stat-icon"),
                            html.Div([
                                html.H3("500+", className="stat-number"),
                                html.P("Dons Réussis", className="stat-label")
                            ])
                        ], className="stat-content")
                    ], className="stat-card")
                ], width=12, md=4),
            ], className="stats-row"),
        ], fluid=True, className="stats-section"),

        # Features Section
        dbc.Container([
            html.H2("Fonctionnalités Principales", className="section-title text-center mb-5"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.Div([
                            html.I(className="fas fa-map-marked-alt feature-icon"),
                            html.H4("Cartographie", className="feature-title"),
                            html.P("Visualisation géographique interactive des donneurs et des centres de don",
                                 className="feature-description")
                        ], className="feature-content")
                    ], className="feature-card")
                ], width=12, md=4),
                dbc.Col([
                    dbc.Card([
                        html.Div([




                            html.I(className="fas fa-chart-line feature-icon"),
                            html.H4("Analyses", className="feature-title"),
                            html.P("Analyses détaillées des tendances et des performances des campagnes",
                                 className="feature-description")
                        ], className="feature-content")
                    ], className="feature-card")
                ], width=12, md=4),
                dbc.Col([
                    dbc.Card([
                        html.Div([
                            html.I(className="fas fa-brain feature-icon"),
                            html.H4("IA Prédictive", className="feature-title"),
                            html.P("Prédiction de l'éligibilité des donneurs grâce à l'intelligence artificielle",
                                 className="feature-description")
                        ], className="feature-content")
                    ], className="feature-card")
                ], width=12, md=4),
            ], className="features-row"),
        ], fluid=True, className="features-section"),

        # Map Preview Section
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Img(src="/assets/map-preview.png", className="map-preview-image"),
                        html.Div([
                            html.H3("Visualisation Interactive", className="overlay-title"),
                            html.P("Explorez la répartition géographique des donneurs", 
                                 className="overlay-text"),
                            dbc.Button("Voir la carte", href="/cartographie", 
                                     className="overlay-button")
                        ], className="map-overlay")
                    ], className="map-preview-container")
                ], width=12)
            ])
        ], fluid=True, className="map-section")
    ], className="home-container")
