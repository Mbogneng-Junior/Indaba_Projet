import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html
from datetime import datetime

def init_donor_map_callbacks(app):
    """Initialise les callbacks pour la carte des donneurs"""
    
    # Charger les données
    df = pd.read_csv('data/processed_data.csv')
    
    # Conversion des dates
    df['Date de remplissage de la fiche'] = pd.to_datetime(df['Date de remplissage de la fiche'])
    df['Date de naissance'] = pd.to_datetime(df['Date de naissance'])
    df['Année'] = df['Date de remplissage de la fiche'].dt.year
    df['Mois'] = df['Date de remplissage de la fiche'].dt.month
    df['Jour'] = df['Date de remplissage de la fiche'].dt.day_name()
    
    # Calculer l'âge
    df['Age'] = (df['Date de remplissage de la fiche'] - df['Date de naissance']).dt.total_seconds() / (365.25 * 24 * 60 * 60)
    df['Age'] = df['Age'].round().astype('Int64')
    
    # Coordonnées des arrondissements de Yaoundé
    arrondissements_coords = {
        '1er': {'lat': 3.8667, 'lon': 11.5167, 'zoom': 12},
        '2e': {'lat': 3.8567, 'lon': 11.5067, 'zoom': 12},
        '3e': {'lat': 3.8467, 'lon': 11.5267, 'zoom': 12},
        '4e': {'lat': 3.8767, 'lon': 11.5367, 'zoom': 12},
        '5e': {'lat': 3.8367, 'lon': 11.4967, 'zoom': 12},
        '6e': {'lat': 3.8967, 'lon': 11.5467, 'zoom': 12},
        '7e': {'lat': 3.8267, 'lon': 11.5567, 'zoom': 12}
    }
    
    # Ajouter les coordonnées avec variation
    df['random_lat'] = df['Arrondissement de résidence'].map(
        lambda x: arrondissements_coords.get(x, {}).get('lat', 0) + np.random.normal(0, 0.002)
    )
    df['random_lon'] = df['Arrondissement de résidence'].map(
        lambda x: arrondissements_coords.get(x, {}).get('lon', 0) + np.random.normal(0, 0.002)
    )
    
    @app.callback(
        [Output('donor-map', 'figure'),
         Output('monthly-donations', 'figure'),
         Output('yearly-trend', 'figure'),
         Output('weekday-pattern', 'figure'),
         Output('eligibility-pie', 'figure'),
         Output('gender-distribution', 'figure'),
         Output('age-distribution', 'figure'),
         Output('factors-heatmap', 'figure'),
         Output('total-donneurs', 'children'),
         Output('taux-retour', 'children'),
         Output('summary-stats', 'children')],
        [Input('update-viz', 'n_clicks')],
        [State('annees-filter', 'value'),
         State('ville-filter', 'value'),
         State('sexe-filter', 'value'),
         State('eligibility-filter', 'value'),
         State('visualization-mode', 'value')]
    )
    def update_visualizations(n_clicks, years, villes, sexe, eligibility, viz_mode):
        # Filtrer les données
        dff = df.copy()
        
        # Appliquer les filtres
        if years:
            dff = dff[dff['Année'].between(years[0], years[1])]
        if villes and len(villes) > 0:
            dff = dff[dff['Arrondissement de résidence'].isin(villes)]
        if sexe != 'all':
            dff = dff[dff['Genre'] == sexe]
        if eligibility != 'all':
            dff = dff[dff['ÉLIGIBILITÉ AU DON.'] == eligibility]
            
        # 1. Carte géographique
        if viz_mode == 'heatmap':
            map_fig = px.density_mapbox(dff,
                                      lat='random_lat',
                                      lon='random_lon',
                                      zoom=11,
                                      mapbox_style='carto-positron',
                                      opacity=0.7)
        elif viz_mode == 'scatter':
            map_fig = px.scatter_mapbox(dff,
                                      lat='random_lat',
                                      lon='random_lon',
                                      color='ÉLIGIBILITÉ AU DON.',
                                      hover_data=['Genre', 'Age', 'Arrondissement de résidence'],
                                      size_max=12,
                                      zoom=11,
                                      mapbox_style='carto-positron',
                                      color_discrete_map={
                                          'eligible': '#28a745',
                                          'temporairement non-eligible': '#ffc107',
                                          'définitivement non-eligible': '#dc3545'
                                      })
            map_fig.update_traces(marker=dict(size=8))
        else:  # cluster
            map_fig = px.scatter_mapbox(dff,
                                      lat='random_lat',
                                      lon='random_lon',
                                      color='Arrondissement de résidence',
                                      size_max=15,
                                      zoom=11,
                                      mapbox_style='carto-positron')
            
        map_fig.update_layout(
            mapbox=dict(
                center=dict(lat=3.8667, lon=11.5167),
                style='carto-positron',
                zoom=11.5
            ),
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.8)'
            )
        )
        
        # 2. Dons mensuels
        monthly_data = dff.groupby(['Année', 'Mois']).size().reset_index(name='Dons')
        monthly_fig = px.line(monthly_data,
                            x='Mois',
                            y='Dons',
                            color='Année',
                            title='Évolution mensuelle des dons')
        monthly_fig.update_layout(
            xaxis_title="Mois",
            yaxis_title="Nombre de dons",
            showlegend=True,
            hovermode='x unified'
        )
        
        # 3. Tendance annuelle
        yearly_data = dff.groupby('Année').size().reset_index(name='Dons')
        yearly_fig = px.bar(yearly_data,
                          x='Année',
                          y='Dons',
                          title='Tendance annuelle',
                          color_discrete_sequence=['#007bff'])
        yearly_fig.update_layout(
            xaxis_title="Année",
            yaxis_title="Nombre de dons",
            showlegend=False
        )
        
        # 4. Pattern hebdomadaire
        weekday_data = dff.groupby('Jour').size().reset_index(name='Dons')
        weekday_fig = px.bar(weekday_data,
                           x='Jour',
                           y='Dons',
                           title='Répartition par jour de la semaine',
                           color_discrete_sequence=['#17a2b8'])
        weekday_fig.update_layout(
            xaxis_title="Jour",
            yaxis_title="Nombre de dons",
            showlegend=False
        )
        
        # 5. Diagramme d'éligibilité
        elig_counts = dff['ÉLIGIBILITÉ AU DON.'].value_counts()
        pie_fig = px.pie(values=elig_counts.values,
                        names=elig_counts.index,
                        title='Distribution de l\'éligibilité',
                        color_discrete_map={
                            'eligible': '#28a745',
                            'temporairement non-eligible': '#ffc107',
                            'définitivement non-eligible': '#dc3545'
                        })
        pie_fig.update_traces(textposition='inside', textinfo='percent+label')
        
        # 6. Distribution par genre
        gender_data = dff.groupby('Genre').size().reset_index(name='Nombre')
        gender_fig = px.bar(gender_data,
                          x='Genre',
                          y='Nombre',
                          title='Distribution par genre',
                          color='Genre',
                          color_discrete_map={
                              'homme': '#007bff',
                              'femme': '#e83e8c'
                          })
        gender_fig.update_layout(showlegend=False)
        
        # 7. Distribution par âge
        # Filtrer les âges valides
        age_data = dff[dff['Age'].between(15, 100)]  # Supposons que les âges valides sont entre 15 et 100 ans
        age_fig = px.histogram(age_data,
                             x='Age',
                             nbins=20,
                             title='Distribution des âges',
                             color_discrete_sequence=['#6f42c1'])
        age_fig.update_layout(
            xaxis_title="Âge",
            yaxis_title="Nombre de donneurs",
            showlegend=False,
            bargap=0.1
        )
        
        # 8. Heatmap des facteurs
        numeric_cols = ['Taille', 'Poids']
        hemoglobine_col = next((col for col in df.columns if 'moglobine' in col.lower()), None)
        if hemoglobine_col:
            numeric_cols.append(hemoglobine_col)
            
        if len(numeric_cols) > 1:
            # Convertir les colonnes en numérique si nécessaire
            numeric_df = dff[numeric_cols].copy()
            for col in numeric_cols:
                if numeric_df[col].dtype == 'object':
                    numeric_df[col] = pd.to_numeric(numeric_df[col].str.replace(',', '.'), errors='coerce')
            
            corr_matrix = numeric_df.corr()
            heatmap_fig = px.imshow(corr_matrix,
                                   title='Corrélation entre les facteurs',
                                   color_continuous_scale='RdBu')
        else:
            heatmap_fig = go.Figure()
            heatmap_fig.update_layout(
                title='Données insuffisantes pour la corrélation'
            )
        
        # Calculer les KPIs
        total_donneurs = len(dff)
        donneurs_uniques = dff['A-t-il (elle) déjà donné le sang'].value_counts()
        taux_retour = (donneurs_uniques.get('oui', 0) / len(dff) * 100) if len(dff) > 0 else 0
        
        # Créer le résumé
        summary = html.Div([
            html.Div([
                html.I(className="fas fa-calendar me-2"),
                f"Période : {years[0] if years else 'N/A'} - {years[1] if years else 'N/A'}"
            ], className="mb-2"),
            html.Div([
                html.I(className="fas fa-map-marker-alt me-2"),
                f"Arrondissements : {len(dff['Arrondissement de résidence'].unique())}"
            ], className="mb-2"),
            html.Div([
                html.I(className="fas fa-venus-mars me-2"),
                f"H/F : {(dff['Genre'] == 'homme').mean():.0%}/{(dff['Genre'] == 'femme').mean():.0%}"
            ], className="mb-2"),
            html.Div([
                html.I(className="fas fa-heartbeat me-2"),
                f"Taux d'éligibilité : {(dff['ÉLIGIBILITÉ AU DON.'] == 'eligible').mean():.0%}"
            ])
        ])
        
        return (map_fig, monthly_fig, yearly_fig, weekday_fig, pie_fig, gender_fig,
                age_fig, heatmap_fig, f"{total_donneurs:,}",
                f"{taux_retour:.1f}%", summary)
    
    # Callback pour le collapse
    @app.callback(
        Output("collapse-content", "is_open"),
        [Input("collapse-button", "n_clicks")],
        [State("collapse-content", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open
    
    # Callback pour mettre à jour les options de ville
    @app.callback(
        Output('ville-filter', 'options'),
        [Input('annees-filter', 'value')]
    )
    def update_ville_options(years):
        if not years:
            return []
        dff = df[df['Année'].between(years[0], years[1])]
        villes = sorted(dff['Arrondissement de résidence'].unique())
        return [{'label': ville, 'value': ville} for ville in villes]
