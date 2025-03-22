import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html
from datetime import datetime

def init_donor_retention_callbacks(app):
    """Initialise les callbacks pour l'analyse de fidélisation"""
    
    # Charger et prétraiter les données
    df = pd.read_csv('data/processed_data.csv')
    
    # Conversion des dates
    df['Date de remplissage de la fiche'] = pd.to_datetime(df['Date de remplissage de la fiche'])
    df['Date de naissance'] = pd.to_datetime(df['Date de naissance'])
    df['Si oui preciser la date du dernier don.'] = pd.to_datetime(df['Si oui preciser la date du dernier don.'])
    
    # Calcul de l'âge et création des groupes d'âge
    df['Age'] = ((df['Date de remplissage de la fiche'] - df['Date de naissance']).dt.total_seconds() / (365.25 * 24 * 60 * 60)).round()
    df['Groupe_Age'] = pd.cut(df['Age'], 
                             bins=[0, 25, 35, 45, 55, 100],
                             labels=['18-25', '26-35', '36-45', '46-55', '55+'])
    
    # Calcul de l'intervalle entre les dons
    df['Intervalle_Dons'] = (df['Date de remplissage de la fiche'] - df['Si oui preciser la date du dernier don.']).dt.days
    
    @app.callback(
        [Output('taux-fidelisation', 'children'),
         Output('moyenne-dons', 'children'),
         Output('intervalle-moyen', 'children'),
         Output('retention-by-factor', 'figure'),
         Output('retention-correlation', 'figure'),
         Output('donation-frequency-dist', 'figure'),
         Output('time-between-donations', 'figure'),
         Output('retention-evolution', 'figure'),
         Output('risk-factors', 'figure'),
         Output('donor-segments', 'figure'),
         Output('loyalty-patterns', 'figure'),
         Output('retention-recommendations', 'children')],
        [Input('retention-period-slider', 'value'),
         Input('retention-factor-dropdown', 'value')]
    )
    def update_retention_analysis(years, factor):
        # Filtrer les données par période
        mask = df['Date de remplissage de la fiche'].dt.year.between(years[0], years[1])
        dff = df[mask].copy()
        
        # 1. Calculer les KPIs
        taux_fidelisation = (dff['A-t-il (elle) déjà donné le sang'] == 'oui').mean() * 100
        moyenne_dons = dff[dff['A-t-il (elle) déjà donné le sang'] == 'oui'].shape[0] / dff.shape[0]
        intervalle_moyen = dff['Intervalle_Dons'].median()
        
        # 2. Taux de fidélisation par facteur
        if factor == 'age':
            group_col = 'Groupe_Age'
        elif factor == 'genre':
            group_col = 'Genre'
        elif factor == 'profession':
            group_col = 'Profession'
        else:
            group_col = 'Arrondissement de résidence'
            
        retention_data = dff.groupby(group_col)['A-t-il (elle) déjà donné le sang'].apply(
            lambda x: (x == 'oui').mean()
        ).reset_index()
        retention_data.columns = [group_col, 'Taux de fidélisation']
        
        retention_fig = px.bar(retention_data,
                             x=group_col,
                             y='Taux de fidélisation',
                             title=f'Taux de fidélisation par {group_col}',
                             template='plotly_white')
        
        # 3. Matrice de corrélation
        numeric_cols = ['Age', 'Taille', 'Poids', 'Intervalle_Dons']
        corr_data = dff[numeric_cols].corr()
        
        correlation_fig = px.imshow(corr_data,
                                  title='Corrélations entre facteurs',
                                  color_continuous_scale='RdBu',
                                  template='plotly_white')
        
        # 4. Distribution de la fréquence des dons
        freq_fig = px.histogram(dff[dff['A-t-il (elle) déjà donné le sang'] == 'oui'],
                              x='Intervalle_Dons',
                              nbins=30,
                              title='Distribution des intervalles entre dons',
                              template='plotly_white')
        
        # 5. Temps entre les dons
        time_fig = px.box(dff[dff['Intervalle_Dons'].notna()],
                         x=group_col,
                         y='Intervalle_Dons',
                         title='Intervalle entre dons par groupe',
                         template='plotly_white')
        
        # 6. Évolution de la fidélisation
        evolution_data = dff.groupby(
            pd.Grouper(key='Date de remplissage de la fiche', freq='M')
        )['A-t-il (elle) déjà donné le sang'].apply(
            lambda x: (x == 'oui').mean()
        ).reset_index()
        evolution_data.columns = ['Date', 'Taux']
        
        evolution_fig = px.line(evolution_data,
                              x='Date',
                              y='Taux',
                              title='Évolution du taux de fidélisation',
                              template='plotly_white')
        
        # 7. Facteurs de risque
        risk_data = dff.groupby(['ÉLIGIBILITÉ AU DON.', group_col]).size().unstack(fill_value=0)
        risk_data = risk_data.div(risk_data.sum(axis=1), axis=0)
        
        risk_fig = px.imshow(risk_data,
                           title='Matrice des facteurs de risque',
                           template='plotly_white')
        
        # 8. Segments de donneurs
        segments_data = dff.groupby(group_col)['Intervalle_Dons'].agg(['mean', 'count']).reset_index()
        
        segments_fig = px.scatter(segments_data,
                                x='mean',
                                y='count',
                                text=group_col,
                                title='Segments de donneurs',
                                template='plotly_white')
        
        # 9. Patterns de fidélité
        loyalty_data = dff.groupby([group_col, 'A-t-il (elle) déjà donné le sang']).size().unstack(fill_value=0)
        loyalty_data['ratio'] = loyalty_data['oui'] / (loyalty_data['oui'] + loyalty_data['non'])
        
        loyalty_fig = px.bar(loyalty_data.reset_index(),
                           x=group_col,
                           y='ratio',
                           title='Patterns de fidélité',
                           template='plotly_white')
        
        # 10. Générer des recommandations
        best_group = retention_data.loc[retention_data['Taux de fidélisation'].idxmax()]
        optimal_interval = dff[dff['Intervalle_Dons'].notna()]['Intervalle_Dons'].median()
        
        recommendations = dbc.Row([
            dbc.Col([
                html.H5("Recommandations pour améliorer la fidélisation", className="mb-3"),
                html.Ul([
                    html.Li([
                        html.Strong("Groupe cible prioritaire : "),
                        f"Le groupe {best_group[group_col]} montre le meilleur taux de fidélisation ({best_group['Taux de fidélisation']:.1%})"
                    ], className="mb-2"),
                    html.Li([
                        html.Strong("Intervalle optimal : "),
                        f"Encourager les dons tous les {optimal_interval:.0f} jours en moyenne"
                    ], className="mb-2"),
                    html.Li([
                        html.Strong("Taux actuel : "),
                        f"Le taux de fidélisation global est de {taux_fidelisation:.1f}%"
                    ], className="mb-2"),
                    html.Li([
                        html.Strong("Actions recommandées : "),
                        html.Ul([
                            html.Li("Mettre en place un système de rappel personnalisé"),
                            html.Li("Organiser des campagnes ciblées pour les groupes moins fidèles"),
                            html.Li("Développer un programme de reconnaissance des donneurs réguliers")
                        ], className="mt-2")
                    ])
                ])
            ])
        ])
        
        return (
            f"{taux_fidelisation:.1f}%",
            f"{moyenne_dons:.1f}",
            f"{intervalle_moyen:.0f}",
            retention_fig,
            correlation_fig,
            freq_fig,
            time_fig,
            evolution_fig,
            risk_fig,
            segments_fig,
            loyalty_fig,
            recommendations
        )
