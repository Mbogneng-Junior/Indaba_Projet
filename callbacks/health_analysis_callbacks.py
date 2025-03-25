import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from datetime import datetime

def init_health_analysis_callbacks(app):
    """Initialise les callbacks pour l'analyse de santé"""
    
    # Charger et prétraiter les données
    df = pd.read_csv('data/processed_data.csv')
    
    # Conversion des dates
    df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
    
    # Identifier les colonnes par catégorie
    raisons_temp = [col for col in df.columns if "raison_indisponibilité__" in col]
    raisons_femmes = [col for col in df.columns if "raison_de_l'indisponibilité_de_la_femme_" in col]
    raisons_totales = [col for col in df.columns if "raison_de_non-eligibilité_totale__" in col]
    
    @app.callback(
        [Output('eligible-count', 'children'),
         Output('temp-unavailable-count', 'children'),
         Output('non-eligible-count', 'children')],
        [Input('url', 'pathname')]  # Utiliser le pathname comme trigger
    )
    def update_health_stats(_):
        # Calculer les statistiques
        total = len(df)
        eligible = (df['eligibilite_au_don'] == 'eligible').sum()
        temp_unavailable = df[raisons_temp].eq('oui').any(axis=1).sum()
        non_eligible = df[raisons_totales].eq('oui').any(axis=1).sum()
        
        # Calculer les pourcentages
        pct_eligible = (eligible / total) * 100
        pct_temp = (temp_unavailable / total) * 100
        pct_non = (non_eligible / total) * 100
        
        return (
            f"{eligible:,} ({pct_eligible:.1f}%)",
            f"{temp_unavailable:,} ({pct_temp:.1f}%)",
            f"{non_eligible:,} ({pct_non:.1f}%)"
        )
    
    @app.callback(
        Output('eligibility-pie-chart', 'figure'),
        [Input('url', 'pathname')]
    )
    def update_eligibility_pie(_):
        # Calculer les statistiques
        total = len(df)
        eligible = (df['eligibilite_au_don'] == 'eligible').sum()
        temp_unavailable = df[raisons_temp].eq('oui').any(axis=1).sum()
        non_eligible = df[raisons_totales].eq('oui').any(axis=1).sum()
        
        # Créer les données pour le graphique
        data = pd.DataFrame({
            'Statut': ['Éligible', 'Temporairement non disponible', 'Non éligible'],
            'Nombre': [eligible, temp_unavailable, non_eligible]
        })
        
        fig = px.pie(
            data,
            values='Nombre',
            names='Statut',
            color='Statut',
            color_discrete_map={
                'Éligible': '#28a745',
                'Temporairement non disponible': '#ffc107',
                'Non éligible': '#dc3545'
            }
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=True)
        
        return fig
    
    @app.callback(
        Output('top-health-issues', 'figure'),
        [Input('url', 'pathname')]
    )
    def update_top_health_issues(_):
        # Compter les problèmes de santé
        health_counts = df[raisons_totales].eq('oui').sum().sort_values(ascending=True)
        health_df = pd.DataFrame({
            'Problème': [col.split('[')[-1].split(']')[0].replace('_', ' ') for col in health_counts.index],
            'Nombre': health_counts.values
        })
        
        # Prendre les 3 premiers
        top_3 = health_df.nlargest(3, 'Nombre')
        
        fig = px.bar(
            top_3,
            x='Nombre',
            y='Problème',
            orientation='h',
            color='Nombre',
            color_continuous_scale=['#0d2c54', '#dc3545']
        )
        
        fig.update_layout(
            title='Top 3 des problèmes de santé',
            xaxis_title='Nombre de cas',
            yaxis_title=None,
            showlegend=False
        )
        
        return fig
    
    @app.callback(
        Output('top-unavailability-reasons', 'figure'),
        [Input('url', 'pathname')]
    )
    def update_top_unavailability_reasons(_):
        # Compter les raisons d'indisponibilité
        unavail_counts = df[raisons_temp + raisons_femmes].eq('oui').sum().sort_values(ascending=True)
        unavail_df = pd.DataFrame({
            'Raison': [col.split('[')[-1].split(']')[0].replace('_', ' ') for col in unavail_counts.index],
            'Nombre': unavail_counts.values
        })
        
        # Prendre les 3 premières
        top_3 = unavail_df.nlargest(3, 'Nombre')
        
        fig = px.bar(
            top_3,
            x='Nombre',
            y='Raison',
            orientation='h',
            color='Nombre',
            color_continuous_scale=['#0d2c54', '#dc3545']
        )
        
        fig.update_layout(
            title="Top 3 des raisons d'indisponibilité",
            xaxis_title='Nombre de cas',
            yaxis_title=None,
            showlegend=False
        )
        
        return fig
    
    @app.callback(
        Output('health-issues-bar', 'figure'),
        [Input('url', 'pathname')]
    )
    def update_health_issues_bar(_):
        # Compter tous les problèmes de santé
        health_counts = df[raisons_totales].eq('oui').sum().sort_values(ascending=True)
        health_df = pd.DataFrame({
            'Problème': [col.split('[')[-1].split(']')[0].replace('_', ' ') for col in health_counts.index],
            'Nombre': health_counts.values
        })
        
        fig = px.bar(
            health_df,
            x='Nombre',
            y='Problème',
            orientation='h',
            color='Nombre',
            color_continuous_scale=['#0d2c54', '#dc3545']
        )
        
        fig.update_layout(
            title='Tous les problèmes de santé',
            xaxis_title='Nombre de cas',
            yaxis_title=None,
            showlegend=False
        )
        
        return fig
    
    @app.callback(
        Output('temp-unavailability-bar', 'figure'),
        [Input('url', 'pathname')]
    )
    def update_temp_unavailability_bar(_):
        # Compter toutes les raisons d'indisponibilité
        unavail_counts = df[raisons_temp + raisons_femmes].eq('oui').sum().sort_values(ascending=True)
        unavail_df = pd.DataFrame({
            'Raison': [col.split('[')[-1].split(']')[0].replace('_', ' ') for col in unavail_counts.index],
            'Nombre': unavail_counts.values
        })
        
        fig = px.bar(
            unavail_df,
            x='Nombre',
            y='Raison',
            orientation='h',
            color='Nombre',
            color_continuous_scale=['#0d2c54', '#dc3545']
        )
        
        fig.update_layout(
            title="Toutes les raisons d'indisponibilité temporaire",
            xaxis_title='Nombre de cas',
            yaxis_title=None,
            showlegend=False
        )
        
        return fig
    
    @app.callback(
        [Output('city-analysis', 'figure'),
         Output('district-analysis', 'figure'),
         Output('neighborhood-analysis', 'figure')],
        [Input('url', 'pathname')]
    )
    def update_geographic_analysis(_):
        # Fonction helper pour créer les graphiques géographiques
        def create_geo_figure(df, col_name, title):
            # Calculer les statistiques par zone
            stats = df.groupby(col_name).agg({
                'eligibilite_au_don': lambda x: (x == 'eligible').mean() * 100
            }).reset_index()
            
            stats.columns = [col_name, "Taux d'éligibilité (%)"]
            
            fig = px.bar(
                stats,
                x=col_name,
                y="Taux d'éligibilité (%)",
                title=title,
                color="Taux d'éligibilité (%)",
                color_continuous_scale=['#dc3545', '#28a745']
            )
            
            fig.update_layout(
                xaxis_title=col_name.replace('_', ' ').title(),
                showlegend=False
            )
            
            return fig
        
        city_fig = create_geo_figure(df, 'ville', "Taux d'éligibilité par ville")
        district_fig = create_geo_figure(df, 'arrondissement_de_residence', "Taux d'éligibilité par arrondissement")
        neighborhood_fig = create_geo_figure(df, 'quartier_de_residence', "Taux d'éligibilité par quartier")
        
        return city_fig, district_fig, neighborhood_fig
