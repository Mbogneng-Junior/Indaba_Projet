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
import dash_core_components as dcc

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
         Output("region-stats", "children")],
        [Input("location-filter", "value"),
         Input("zone-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_map_and_stats(location, zone, start_date, end_date):
        """Met à jour la carte et les statistiques régionales"""
        df = load_data()
        
        # Filtrer par ville et date
        if location != 'all':
            df = df[df['arrondissement_de_residence'].str.contains(location, case=False, na=False)]
        
        if start_date and end_date:
            df = df[(df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()) &
                   (df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date())]
        
        # Créer la carte
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
        
        # Créer les statistiques par région
        if zone != 'tous':
            group_by = 'quartier_de_residence' if zone == 'quartier' else 'arrondissement_de_residence'
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
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(
                            figure=fig,
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ]
        else:
            stats_component = []
        
        return m._repr_html_(), stats_component
