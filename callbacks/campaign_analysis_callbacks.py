import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html
from datetime import datetime

def init_campaign_analysis_callbacks(app):
    """Initialise les callbacks pour l'analyse des campagnes"""
    
    # Charger et prétraiter les données
    df = pd.read_csv('data/processed_data.csv')
    
    # Conversion des dates
    df['Date de remplissage de la fiche'] = pd.to_datetime(df['Date de remplissage de la fiche'])
    df['Date de naissance'] = pd.to_datetime(df['Date de naissance'])
    
    # Extraire les informations temporelles
    df['Année'] = df['Date de remplissage de la fiche'].dt.year
    df['Mois'] = df['Date de remplissage de la fiche'].dt.month
    df['Jour'] = df['Date de remplissage de la fiche'].dt.day_name()
    df['Semaine'] = df['Date de remplissage de la fiche'].dt.isocalendar().week
    
    # Calculer l'âge
    df['Age'] = ((df['Date de remplissage de la fiche'] - df['Date de naissance']).dt.total_seconds() / (365.25 * 24 * 60 * 60)).round()
    
    # Créer des groupes d'âge
    df['Groupe_Age'] = pd.cut(df['Age'], 
                             bins=[0, 25, 35, 45, 55, 100],
                             labels=['18-25', '26-35', '36-45', '46-55', '55+'])
    
    @app.callback(
        [Output('total-campagnes', 'children'),
         Output('total-participants', 'children'),
         Output('taux-participation', 'children'),
         Output('seasonal-trends', 'figure'),
         Output('weekly-patterns', 'figure'),
         Output('demographic-distribution', 'figure'),
         Output('participation-rate', 'figure'),
         Output('donor-retention', 'figure'),
         Output('donation-frequency', 'figure'),
         Output('donor-journey', 'figure'),
         Output('campaign-recommendations', 'children')],
        [Input('campaign-period-slider', 'value'),
         Input('demographic-filter', 'value')]
    )
    def update_campaign_analysis(years, demographic):
        # Filtrer les données par période
        mask = df['Année'].between(years[0], years[1])
        dff = df[mask].copy()
        
        # 1. Calculer les KPIs
        n_campaigns = dff.groupby(['Année', 'Mois']).size().shape[0]
        n_participants = len(dff)
        participation_rate = f"{(dff['A-t-il (elle) déjà donné le sang'] == 'oui').mean() * 100:.1f}%"
        
        # 2. Tendances saisonnières
        monthly_trends = dff.groupby(['Année', 'Mois']).size().reset_index(name='Dons')
        seasonal_fig = px.line(monthly_trends, 
                             x='Mois', 
                             y='Dons',
                             color='Année',
                             title='Tendances saisonnières des dons',
                             labels={'Dons': 'Nombre de dons'},
                             template='plotly_white')
        seasonal_fig.update_layout(hovermode='x unified')
        
        # 3. Patterns hebdomadaires
        weekly_data = dff.groupby('Jour').size().reset_index(name='Dons')
        weekly_fig = px.bar(weekly_data,
                          x='Jour',
                          y='Dons',
                          title='Distribution des dons par jour de la semaine',
                          color_discrete_sequence=['#17a2b8'],
                          template='plotly_white')
        
        # 4. Distribution démographique
        if demographic == 'genre':
            demo_col = 'Genre'
        elif demographic == 'profession':
            demo_col = 'Profession'
        elif demographic == 'arrondissement':
            demo_col = 'Arrondissement de résidence'
        else:
            demo_col = 'Groupe_Age'
            
        demo_data = dff.groupby(demo_col).size().reset_index(name='Nombre')
        demo_fig = px.pie(demo_data,
                         values='Nombre',
                         names=demo_col,
                         title=f'Distribution par {demo_col}',
                         template='plotly_white')
        
        # 5. Taux de participation
        participation_data = dff.groupby([demo_col, 'A-t-il (elle) déjà donné le sang']).size().unstack(fill_value=0)
        participation_data['Taux'] = participation_data['oui'] / (participation_data['oui'] + participation_data['non'])
        participation_fig = px.bar(participation_data.reset_index(),
                                 x=demo_col,
                                 y='Taux',
                                 title='Taux de participation par groupe',
                                 color_discrete_sequence=['#28a745'],
                                 template='plotly_white')
        
        # 6. Fidélisation des donneurs
        retention_data = dff.groupby('A-t-il (elle) déjà donné le sang').size()
        retention_fig = px.pie(values=retention_data.values,
                             names=retention_data.index,
                             title='Taux de fidélisation des donneurs',
                             template='plotly_white')
        
        # 7. Fréquence des dons
        freq_data = dff.groupby(['Année', 'Mois']).size().reset_index(name='Dons')
        freq_fig = px.box(freq_data,
                         y='Dons',
                         title='Distribution de la fréquence des dons',
                         template='plotly_white')
        
        # 8. Parcours donneur
        journey_data = dff.groupby(['Année', demo_col]).size().reset_index(name='Dons')
        journey_fig = px.line(journey_data,
                            x='Année',
                            y='Dons',
                            color=demo_col,
                            title='Évolution des dons par groupe',
                            template='plotly_white')
        
        # 9. Générer des recommandations
        best_month = monthly_trends.loc[monthly_trends['Dons'].idxmax()]
        best_day = weekly_data.loc[weekly_data['Dons'].idxmax()]
        best_demo = demo_data.loc[demo_data['Nombre'].idxmax()]
        
        recommendations = dbc.Row([
            dbc.Col([
                html.H5("Recommandations pour les futures campagnes", className="mb-3"),
                html.Ul([
                    html.Li([
                        html.Strong("Période optimale : "),
                        f"Le mois {best_month['Mois']} montre historiquement le plus grand nombre de dons"
                    ], className="mb-2"),
                    html.Li([
                        html.Strong("Jour recommandé : "),
                        f"Les {best_day['Jour']} sont les plus productifs pour les collectes"
                    ], className="mb-2"),
                    html.Li([
                        html.Strong("Groupe cible : "),
                        f"Le groupe {best_demo[demo_col]} montre la plus forte participation"
                    ], className="mb-2"),
                    html.Li([
                        html.Strong("Stratégie de fidélisation : "),
                        f"Se concentrer sur la conversion des {participation_rate} de donneurs réguliers"
                    ])
                ])
            ])
        ])
        
        return (
            f"{n_campaigns:,}",
            f"{n_participants:,}",
            participation_rate,
            seasonal_fig,
            weekly_fig,
            demo_fig,
            participation_fig,
            retention_fig,
            freq_fig,
            journey_fig,
            recommendations
        )
