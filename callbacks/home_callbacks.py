from dash.dependencies import Input, Output, State
import pandas as pd
import folium
from folium import plugins
import numpy as np
from datetime import datetime
from branca.colormap import LinearColormap
import plotly.express as px
import json
import dash_bootstrap_components as dbc
from dash import html, dcc

def init_home_callbacks(app):
    """Initialise les callbacks pour la page d'accueil"""
    
    def load_data():
        """Charge et prépare les données"""
        df = pd.read_csv('data/processed_data.csv')
        df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
        
        # Ajouter les coordonnées pour chaque ville
        def get_coordinates(row):
            if 'douala' in str(row['arrondissement_de_residence']).lower():
                base_lat = 4.0500 + np.random.normal(0, 0.01)
                base_lon = 9.7000 + np.random.normal(0, 0.01)
            elif 'yaounde' in str(row['arrondissement_de_residence']).lower():
                base_lat = 3.8667 + np.random.normal(0, 0.01)
                base_lon = 11.5167 + np.random.normal(0, 0.01)
            else:
                base_lat = 4.0500 + np.random.normal(0, 0.01)
                base_lon = 9.7000 + np.random.normal(0, 0.01)
            return pd.Series({'latitude': base_lat, 'longitude': base_lon})
        
        df[['latitude', 'longitude']] = df.apply(get_coordinates, axis=1)
        return df
    
    @app.callback(
        [Output("stats-arrondissements", "children"),
         Output("stats-quartiers", "children"),
         Output("stats-donors", "children"),
         Output("stats-successful", "children"),
         Output("stats-ineligible", "children"),
         Output("date-filter", "min_date_allowed"),
         Output("date-filter", "max_date_allowed"),
         Output("date-filter", "start_date"),
         Output("date-filter", "end_date")],
        [Input("location-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_stats(location, start_date, end_date):
        """Met à jour les statistiques"""
        df = load_data()
        
        # Filtrer par ville et date
        if location != 'all':
            df = df[df['arrondissement_de_residence'].str.contains(location, case=False, na=False)]
        
        if start_date and end_date:
            df = df[(df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()) &
                   (df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date())]
        
        # Calculer les statistiques
        total_arrondissements = df['arrondissement_de_residence'].nunique()
        total_quartiers = df['quartier_de_residence'].nunique()
        total_donors = len(df)
        successful_donations = len(df[df['eligibilite_au_don'] == 'eligible'])
        ineligible_donations = len(df[df['eligibilite_au_don'] != 'eligible'])
        
        # Dates pour le filtre
        min_date = df['date_de_remplissage'].min()
        max_date = df['date_de_remplissage'].max()
        
        return (
            str(total_arrondissements),
            str(total_quartiers),
            f"{total_donors:,}",
            f"{successful_donations:,}",
            f"{ineligible_donations:,}",
            min_date.date(),
            max_date.date(),
            min_date.date(),
            max_date.date()
        )
    
    @app.callback(
        [Output("donor-map", "srcDoc"),
         Output("region-stats", "children"),
         Output("donor-stats-graph", "figure"),
         Output("donor-geo-distribution", "figure")],
        [Input("location-filter", "value"),
         Input("zone-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_map(location, zone_type, start_date, end_date):
        # Charger les données
        df = load_data()
        
        # Filtrer par ville et date
        if location and location != 'all':
            df = df[df['arrondissement_de_residence'].str.contains(location, case=False, na=False)]
        
        if start_date and end_date:
            df = df[
                (df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()) &
                (df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date())
            ]
        
        # Créer la carte avec folium
        def create_map(df, zone_type):
            if location == 'douala':
                center = [4.0500, 9.7000]
                zoom = 12
            elif location == 'yaounde':
                center = [3.8667, 11.5167]
                zoom = 12
            else:
                center = [4.0500, 9.7000]
                zoom = 6
            
            m = folium.Map(
                location=center,
                zoom_start=zoom,
                tiles='cartodbpositron'
            )
            
            # Ajouter la couche de chaleur
            heat_data = [[row['latitude'], row['longitude']] for index, row in df.iterrows()]
            plugins.HeatMap(
                heat_data,
                radius=15,
                blur=10,
                gradient={0.4: '#1a1f3c', 0.65: '#c62828', 1: '#ff5f52'}
            ).add_to(m)
            
            # Créer les clusters de points
            marker_cluster = plugins.MarkerCluster(
                options={
                    'spiderfyOnMaxZoom': True,
                    'showCoverageOnHover': True,
                    'zoomToBoundsOnClick': True
                }
            ).add_to(m)
            
            # Ajouter les points individuels
            for idx, row in df.iterrows():
                color = '#c62828' if row['eligibilite_au_don'].lower() == 'eligible' else '#1a1f3c'
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=3,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    popup=f"Quartier: {row['quartier_de_residence']}<br>Age: {row['age']}"
                ).add_to(marker_cluster)
            
            return m
        
        m = create_map(df, zone_type)
        
        # Créer les statistiques régionales
        def create_region_stats(df):
            if zone_type != 'tous':
                group_by = 'quartier_de_residence' if zone_type == 'quartier' else 'arrondissement_de_residence'
                stats_df = df.groupby(group_by).agg({
                    'age': ['count', 'mean'],
                    'eligibilite_au_don': lambda x: (x.str.lower() == 'eligible').sum()
                }).reset_index()
                
                stats_df.columns = [group_by, 'Donneurs', 'Age Moyen', 'Dons Éligibles']
                
                fig = px.bar(
                    stats_df,
                    x=group_by,
                    y='Donneurs',
                    color='Dons Éligibles',
                    color_continuous_scale=['#1a1f3c', '#c62828'],
                    template='plotly_white',
                    title=f"Statistiques par {group_by.replace('_', ' ').title()}"
                )
                
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font={'color': '#1a1f3c'},
                    title_x=0.5,
                    margin=dict(t=30, l=60, r=30, b=60),
                    xaxis_title=group_by.replace('_', ' ').title(),
                    yaxis_title="Nombre de Donneurs",
                    showlegend=True
                )
                
                stats_component = [
                    html.Div([
                        dcc.Graph(
                            figure=fig,
                            config={'displayModeBar': False}
                        )
                    ])
                ]
            else:
                stats_component = []
            
            return stats_component
        
        if not df.empty:
            stats_component = create_region_stats(df)
        else:
            stats_component = []
        
        # Créer le graphe des statistiques des donneurs
        donor_stats = df.groupby('eligibilite_au_don').size().reset_index(name='count')
        stats_fig = px.pie(
            donor_stats,
            values='count',
            names='eligibilite_au_don',
            title='Répartition des donneurs par éligibilité',
            color_discrete_map={
                'eligible': '#28a745',
                'ineligible': '#dc3545'
            }
        )
        stats_fig.update_traces(textposition='inside', textinfo='percent+label')
        stats_fig.update_layout(showlegend=True)
        
        # Créer le graphe de répartition géographique
        geo_stats = df.groupby('arrondissement_de_residence').agg({
            'eligibilite_au_don': 'count'
        }).reset_index()
        
        geo_stats.columns = ['arrondissement', 'nombre_donneurs']
        geo_stats = geo_stats[~geo_stats['arrondissement'].str.contains('pas précisé', case=False, na=False)]
        geo_stats = geo_stats.sort_values('nombre_donneurs', ascending=True)
        
        geo_fig = px.bar(
            geo_stats,
            x='nombre_donneurs',
            y='arrondissement',
            orientation='h',
            title='Répartition des donneurs par arrondissement',
            color='nombre_donneurs',
            color_continuous_scale=['#0d2c54', '#dc3545']
        )
        
        geo_fig.update_layout(
            xaxis_title="Nombre de donneurs",
            yaxis_title="Arrondissement",
            showlegend=False,
            height=400
        )
        
        return m._repr_html_(), stats_component, stats_fig, geo_fig
