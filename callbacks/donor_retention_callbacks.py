from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import dash_bootstrap_components as dbc
from dash import html
import os

def init_donor_retention_callbacks(app):
    """Initialise les callbacks pour l'analyse de la fidélisation des donneurs"""
    
    def load_data():
        """Charge et prépare les données"""
        try:
            # Vérifier si le fichier existe
            file_path = 'data/processed_data.csv'
            if not os.path.exists(file_path):
                print(f"Erreur: Le fichier {file_path} n'existe pas")
                return None
                
            # Charger les données
            df = pd.read_csv(file_path)
            if df.empty:
                print("Erreur: Le fichier de données est vide")
                return None
                
            # Conversion et nettoyage des dates
            for col in ['date_de_remplissage', 'date_de_naissance', 'si_oui_preciser_la_date_du_dernier_don']:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except Exception as e:
                    print(f"Erreur lors de la conversion de la colonne {col}: {str(e)}")
            
            # Nettoyage des réponses oui/non
            df['a_t_il_elle_deja_donne_le_sang'] = df['a_t_il_elle_deja_donne_le_sang'].str.lower()
            
            # Calcul de l'âge
            current_year = datetime.now().year
            df['age'] = df['age'].fillna(current_year - df['date_de_naissance'].dt.year)
            df['age'] = df['age'].clip(lower=18, upper=100)  # Limiter l'âge entre 18 et 100 ans
            
            return df
            
        except Exception as e:
            print(f"Erreur lors du chargement des données: {str(e)}")
            return None
    
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
            # Charger les données
            df = load_data()
            if df is None:
                raise ValueError("Impossible de charger les données")
            
            # Appliquer les filtres
            mask = pd.Series(True, index=df.index)
            
            if start_date:
                mask &= df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()
            if end_date:
                mask &= df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()
            if location and location != 'all':
                mask &= df['ville'].str.contains(location, case=False, na=False)
            
            df = df[mask]
            
            if len(df) == 0:
                raise ValueError("Aucune donnée ne correspond aux filtres sélectionnés")
            
            # 1. Statistiques de rétention
            total_donors = len(df)
            returning_donors = (df['a_t_il_elle_deja_donne_le_sang'] == 'oui').sum()
            retention_rate = (returning_donors / total_donors * 100) if total_donors > 0 else 0
            
            stats = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H4("Donneurs totaux", className="h6"),
                        html.P(f"{total_donors:,}", className="h3 text-primary")
                    ], width=4),
                    dbc.Col([
                        html.H4("Donneurs réguliers", className="h6"),
                        html.P(f"{returning_donors:,}", className="h3 text-success")
                    ], width=4),
                    dbc.Col([
                        html.H4("Taux de rétention", className="h6"),
                        html.P(f"{retention_rate:.1f}%", className="h3 text-info")
                    ], width=4)
                ])
            ])
            
            # 2. Tendance de rétention
            monthly_stats = df.groupby(pd.Grouper(key='date_de_remplissage', freq='M')).agg({
                'a_t_il_elle_deja_donne_le_sang': lambda x: (x == 'oui').mean() * 100
            }).reset_index()
            
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
            trend_fig.update_layout(
                showlegend=False,
                xaxis_title="Période",
                yaxis_title="Taux de rétention (%)"
            )
            
            # 3. Fréquence des dons
            freq_ranges = [
                (0, 90, '1-3 mois'),
                (91, 180, '3-6 mois'),
                (181, 365, '6-12 mois'),
                (366, float('inf'), '> 12 mois')
            ]
            
            donor_frequency = df[df['a_t_il_elle_deja_donne_le_sang'] == 'oui'].copy()
            donor_frequency['temps_depuis_dernier_don'] = (
                donor_frequency['date_de_remplissage'] - 
                donor_frequency['si_oui_preciser_la_date_du_dernier_don']
            ).dt.days
            
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
            freq_fig.update_layout(
                showlegend=False,
                xaxis_title="Intervalle entre les dons",
                yaxis_title="Nombre de donneurs"
            )
            
            # 4. Rétention par âge
            age_bins = [0, 25, 35, 45, 55, float('inf')]
            age_labels = ['18-25', '26-35', '36-45', '46-55', '56+']
            
            df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)
            age_retention = df.groupby('age_group').agg({
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
            age_fig.update_layout(
                showlegend=False,
                xaxis_title="Tranche d'âge",
                yaxis_title="Taux de rétention (%)"
            )
            
            # 5. Rétention par zone
            location_retention = df.groupby('arrondissement_de_residence').agg({
                'a_t_il_elle_deja_donne_le_sang': lambda x: (x == 'oui').mean() * 100
            }).reset_index()
            
            location_retention.columns = ['Zone', 'Taux de rétention']
            location_retention = location_retention.sort_values('Taux de rétention', ascending=True)
            location_retention = location_retention[~location_retention['Zone'].str.contains('pas précisé', case=False, na=False)]
            
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
                margin=dict(l=0, r=0, t=40, b=0),
                xaxis_title="Taux de rétention (%)",
                yaxis_title="Zone géographique"
            )
            
            return stats, trend_fig, freq_fig, age_fig, location_fig
            
        except Exception as e:
            print(f"Erreur dans update_retention_analysis: {str(e)}")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text=f"Erreur lors du chargement des données: {str(e)}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return (
                html.Div(f"Erreur lors du chargement des statistiques: {str(e)}"),
                empty_fig,
                empty_fig,
                empty_fig,
                empty_fig
            )
