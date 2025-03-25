import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px
import pandas as pd
import os

def create_dashboard_layout():
    """Crée le layout de la page d'accueil du tableau de bord"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(current_dir), 'data', 'processed_data.csv')
    df = pd.read_csv(data_path)
    
    # Calcul des statistiques clés
    total_donors = len(df)
    regular_donors = len(df[df['a_t_il_elle_deja_donne_le_sang'] == 'Oui'])
    retention_rate = (regular_donors / total_donors * 100) if total_donors > 0 else 0
    
    return html.Div([
        # Hero Section avec dégradé rouge-bleu
        html.Div([
            html.Div([
                html.H1("Donnez votre sang, Sauvez des vies", 
                       className="display-3 text-white mb-4",
                       style={"fontWeight": "700", "textShadow": "2px 2px 4px rgba(0,0,0,0.2)"}),
                html.P("Ensemble, nous pouvons faire la différence", 
                      className="lead text-white mb-4",
                      style={"fontSize": "1.5rem"}),
                html.Hr(className="my-4 bg-white"),
                dbc.Button("Commencer maintenant", 
                         color="light",
                         size="lg",
                         className="me-3 pulse-button",
                         style={"fontWeight": "600"})
            ], className="text-center py-5")
        ], className="hero-banner mb-5"),

        # Statistiques en cartes
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.Div([
                        html.I(className="fas fa-users fa-3x text-primary mb-3"),
                        html.H2(f"{total_donors:,}", 
                               className="counter-number text-primary"),
                        html.P("Donneurs Totaux", className="text-muted")
                    ], className="text-center p-4")
                ], className="stat-card h-100")
            ], width=4),
            dbc.Col([
                dbc.Card([
                    html.Div([
                        html.I(className="fas fa-heart fa-3x text-danger mb-3"),
                        html.H2(f"{regular_donors:,}", 
                               className="counter-number text-danger"),
                        html.P("Donneurs Réguliers", className="text-muted")
                    ], className="text-center p-4")
                ], className="stat-card h-100")
            ], width=4),
            dbc.Col([
                dbc.Card([
                    html.Div([
                        html.I(className="fas fa-chart-line fa-3x text-success mb-3"),
                        html.H2(f"{retention_rate:.1f}%", 
                               className="counter-number text-success"),
                        html.P("Taux de Fidélisation", className="text-muted")
                    ], className="text-center p-4")
                ], className="stat-card h-100")
            ], width=4),
        ], className="mb-5"),

        # Sections principales
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.Div([
                        html.I(className="fas fa-chart-pie fa-3x feature-icon mb-3"),
                        html.H4("Analyse de la Rétention", className="feature-title"),
                        html.P("Suivez et optimisez la fidélisation de vos donneurs"),
                        dbc.Button("Explorer →", href="/donor-retention", 
                                 className="feature-button mt-3")
                    ], className="text-center p-4")
                ], className="feature-card h-100")
            ], width=4),
            dbc.Col([
                dbc.Card([
                    html.Div([
                        html.I(className="fas fa-comments fa-3x feature-icon mb-3"),
                        html.H4("Analyse des Retours", className="feature-title"),
                        html.P("Écoutez et comprenez vos donneurs"),
                        dbc.Button("Découvrir →", href="/feedback-analysis", 
                                 className="feature-button mt-3")
                    ], className="text-center p-4")
                ], className="feature-card h-100")
            ], width=4),
            dbc.Col([
                dbc.Card([
                    html.Div([
                        html.I(className="fas fa-bullhorn fa-3x feature-icon mb-3"),
                        html.H4("Gestion des Campagnes", className="feature-title"),
                        html.P("Optimisez l'impact de vos campagnes"),
                        dbc.Button("Gérer →", href="/campaign-analysis", 
                                 className="feature-button mt-3")
                    ], className="text-center p-4")
                ], className="feature-card h-100")
            ], width=4),
        ], className="mb-5"),

        # Section Impact
        html.Div([
            html.H2("Notre Impact", className="text-center text-white mb-5",
                   style={"fontWeight": "700"}),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-hospital fa-3x mb-3 impact-icon"),
                        html.H4("50+", className="impact-number"),
                        html.P("Hôpitaux Partenaires", className="text-white-50")
                    ], className="text-center")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-hand-holding-heart fa-3x mb-3 impact-icon"),
                        html.H4("1000+", className="impact-number"),
                        html.P("Vies Sauvées", className="text-white-50")
                    ], className="text-center")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-users fa-3x mb-3 impact-icon"),
                        html.H4("5000+", className="impact-number"),
                        html.P("Donneurs Actifs", className="text-white-50")
                    ], className="text-center")
                ], width=4),
            ])
        ], className="impact-section text-white p-5 mb-5"),

        # Call to Action
        dbc.Card([
            html.Div([
                html.H3("Prêt à faire la différence ?", 
                       className="text-white mb-4",
                       style={"fontWeight": "600"}),
                html.P("Votre don peut sauver jusqu'à trois vies. Rejoignez-nous aujourd'hui.",
                      className="text-white-50 mb-4"),
                dbc.Button("Commencer Maintenant", 
                         color="light",
                         size="lg",
                         className="pulse-button")
            ], className="text-center p-5")
        ], className="cta-card")
    ])
