from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

def init_retention_callbacks(app):
    """Initialise les callbacks pour la page de rétention"""
    
    def load_data():
        """Charge et prépare les données"""
        df = pd.read_csv('data/processed_data.csv')
        df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
        if 'si_oui_preciser_la_date_du_dernier_don' in df.columns:
            df['si_oui_preciser_la_date_du_dernier_don'] = pd.to_datetime(df['si_oui_preciser_la_date_du_dernier_don'])
        return df
    
    @app.callback(
        [Output('retention-stats', 'children'),
         Output('retention-trend', 'figure'),
         Output('donor-frequency', 'figure'),
         Output('retention-by-age', 'figure'),
         Output('retention-by-location', 'figure')],
        [Input('retention-date-range', 'start_date'),
         Input('retention-date-range', 'end_date'),
         Input('retention-location-filter', 'value')]
    )
    def update_retention_analysis(start_date, end_date, location):
        try:
            df = load_data()
            
            # Appliquer les filtres
            if start_date:
                df = df[df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()]
            if end_date:
                df = df[df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()]
            if location and location != 'all':
                df = df[df['ville'].str.contains(location, case=False, na=False)]
            
            # 1. Statistiques de rétention
            total_donors = len(df)
            returning_donors = df['a_t_il_elle_deja_donne_le_sang'].eq('oui').sum()
            retention_rate = (returning_donors / total_donors * 100) if total_donors > 0 else 0
            
            stats = html.Div([
                html.H4("Statistiques de rétention", className="mb-4"),
                html.Div([
                    html.Div([
                        html.H6("Donneurs totaux"),
                        html.P(f"{total_donors:,}", className="h3")
                    ], className="stat-box"),
                    html.Div([
                        html.H6("Donneurs réguliers"),
                        html.P(f"{returning_donors:,}", className="h3")
                    ], className="stat-box"),
                    html.Div([
                        html.H6("Taux de rétention"),
                        html.P(f"{retention_rate:.1f}%", className="h3")
                    ], className="stat-box")
                ], className="stats-container")
            ])
            
            # 2. Tendance de rétention
            monthly_stats = df.groupby(df['date_de_remplissage'].dt.to_period('M')).agg({
                'a_t_il_elle_deja_donne_le_sang': lambda x: (x == 'oui').mean() * 100
            }).reset_index()
            monthly_stats['date_de_remplissage'] = monthly_stats['date_de_remplissage'].astype(str)
            
            trend_fig = px.line(
                monthly_stats,
                x='date_de_remplissage',
                y='a_t_il_elle_deja_donne_le_sang',
                title="Évolution du taux de rétention",
                labels={
                    'date_de_remplissage': 'Période',
                    'a_t_il_elle_deja_donne_le_sang': 'Taux de rétention (%)'
                }
            )
            trend_fig.update_layout(showlegend=False)
            
            # 3. Fréquence des dons
            donor_frequency = df[df['a_t_il_elle_deja_donne_le_sang'] == 'oui'].copy()
            donor_frequency['temps_depuis_dernier_don'] = (
                donor_frequency['date_de_remplissage'] - 
                donor_frequency['si_oui_preciser_la_date_du_dernier_don']
            ).dt.days
            
            freq_ranges = [
                (0, 90, '1-3 mois'),
                (91, 180, '3-6 mois'),
                (181, 365, '6-12 mois'),
                (366, float('inf'), '> 12 mois')
            ]
            
            donor_frequency['frequence'] = 'Non spécifié'
            for start, end, label in freq_ranges:
                mask = (donor_frequency['temps_depuis_dernier_don'] >= start) & (donor_frequency['temps_depuis_dernier_don'] <= end)
                donor_frequency.loc[mask, 'frequence'] = label
            
            freq_stats = donor_frequency['frequence'].value_counts().reset_index()
            freq_stats.columns = ['Intervalle', 'Nombre']
            
            freq_fig = px.bar(
                freq_stats,
                x='Intervalle',
                y='Nombre',
                title="Fréquence des dons",
                color='Nombre',
                color_continuous_scale=['#0d2c54', '#dc3545']
            )
            freq_fig.update_layout(showlegend=False)
            
            # 4. Rétention par âge
            age_retention = df.groupby(pd.qcut(df['age'], q=5)).agg({
                'a_t_il_elle_deja_donne_le_sang': lambda x: (x == 'oui').mean() * 100
            }).reset_index()
            age_retention.columns = ['Tranche d\'âge', 'Taux de rétention']
            
            age_fig = px.bar(
                age_retention,
                x='Tranche d\'âge',
                y='Taux de rétention',
                title="Taux de rétention par âge",
                color='Taux de rétention',
                color_continuous_scale=['#0d2c54', '#dc3545']
            )
            age_fig.update_layout(showlegend=False)
            
            # 5. Rétention par zone géographique
            location_retention = df.groupby('arrondissement_de_residence').agg({
                'a_t_il_elle_deja_donne_le_sang': lambda x: (x == 'oui').mean() * 100
            }).reset_index()
            location_retention.columns = ['Zone', 'Taux de rétention']
            location_retention = location_retention.sort_values('Taux de rétention', ascending=True)
            
            location_fig = px.bar(
                location_retention,
                x='Taux de rétention',
                y='Zone',
                orientation='h',
                title="Taux de rétention par zone",
                color='Taux de rétention',
                color_continuous_scale=['#0d2c54', '#dc3545']
            )
            location_fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            return stats, trend_fig, freq_fig, age_fig, location_fig
            
        except Exception as e:
            print(f"Erreur dans update_retention_analysis: {str(e)}")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Erreur lors du chargement des données",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return (
                html.Div("Erreur lors du chargement des statistiques"),
                empty_fig,
                empty_fig,
                empty_fig,
                empty_fig
            )
