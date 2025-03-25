from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import os
from dash import html

def init_campaign_analysis_callbacks(app):
    """Initialise les callbacks pour l'analyse des campagnes"""
    
    def load_data():
        """Charge et prépare les données"""
        try:
            df = pd.read_csv('data/processed_data.csv')
            df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
            return df
        except FileNotFoundError:
            print("Erreur: Le fichier de données n'a pas été trouvé dans le chemin attendu")
            print("Chemin actuel:", os.getcwd())
            return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur
    
    @app.callback(
        Output('district-filter', 'options'),
        [Input('city-filter', 'value')]
    )
    def update_district_options(city):
        df = load_data()
        if city != 'all':
            df = df[df['ville'].str.contains(city, case=False, na=False)]
        districts = df['arrondissement_de_residence'].unique()
        return [{'label': d, 'value': d} for d in sorted(districts)]
    
    @app.callback(
        Output('neighborhood-filter', 'options'),
        [Input('city-filter', 'value'),
         Input('district-filter', 'value')]
    )
    def update_neighborhood_options(city, district):
        df = load_data()
        if city != 'all':
            df = df[df['ville'].str.contains(city, case=False, na=False)]
        if district:
            df = df[df['arrondissement_de_residence'] == district]
        neighborhoods = df['quartier_de_residence'].unique()
        return [{'label': n, 'value': n} for n in sorted(neighborhoods)]
    
    @app.callback(
        [Output('total-donations', 'children'),
         Output('eligibility-rate', 'children'),
         Output('total-neighborhoods', 'children'),
         Output('donations-timeline', 'figure'),
         Output('eligibility-age-distribution', 'figure')],
        [Input('city-filter', 'value'),
         Input('district-filter', 'value'),
         Input('neighborhood-filter', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_campaign_analysis(city, district, neighborhood, start_date, end_date):
        try:
            df = load_data()
            
            # Appliquer les filtres
            if city != 'all':
                df = df[df['ville'].str.contains(city, case=False, na=False)]
            if district:
                df = df[df['arrondissement_de_residence'] == district]
            if neighborhood:
                df = df[df['quartier_de_residence'] == neighborhood]
            if start_date:
                df = df[df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()]
            if end_date:
                df = df[df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()]
            
            # Calculer les statistiques
            total_donations = len(df)
            eligibility_rate = (df['eligibilite_au_don'] == 'eligible').mean()
            total_neighborhoods = df['quartier_de_residence'].nunique()
            
            # 1. Graphique temporel avec meilleure échelle
            timeline_df = df.groupby('date_de_remplissage').size().reset_index(name='Nombre de dons')
            timeline_fig = px.line(
                timeline_df,
                x='date_de_remplissage',
                y='Nombre de dons',
                title="Nombre de dons en fonction de la date de remplissage"
            )
            
            # Améliorer l'échelle et le style
            timeline_fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Nombre de dons",
                template='plotly_white',
                yaxis=dict(
                    rangemode='tozero',
                    tickformat=',d'
                ),
                margin=dict(l=50, r=20, t=40, b=30)
            )
            
            # 2. Distribution de l'éligibilité par âge
            eligible_df = df[df['eligibilite_au_don'] == 'eligible'].copy()
            
            age_bins = list(range(0, 101, 5))
            age_labels = [f"{i}-{i+4}" for i in range(0, 96, 5)]
            
            eligible_df['age_group'] = pd.cut(
                eligible_df['age'],
                bins=age_bins,
                labels=age_labels,
                include_lowest=True
            )
            
            age_dist = eligible_df.groupby('age_group').size().reset_index(name='Nombre de donneurs éligibles')
            
            age_dist_fig = px.bar(
                age_dist,
                x='age_group',
                y='Nombre de donneurs éligibles',
                title="Distribution des donneurs éligibles par âge",
                labels={'age_group': 'Groupe d\'âge'}
            )
            
            age_dist_fig.update_layout(
                template='plotly_white',
                xaxis_tickangle=-45,
                bargap=0.1,
                margin=dict(l=50, r=20, t=40, b=100),
                yaxis=dict(
                    rangemode='tozero',
                    tickformat=',d'
                )
            )
            
            return (
                f"{total_donations:,}",
                f"{eligibility_rate:.1%}",
                f"{total_neighborhoods:,}",
                timeline_fig,
                age_dist_fig
            )
            
        except Exception as e:
            print(f"Erreur dans update_campaign_analysis: {str(e)}")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Erreur lors du chargement des données",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return "0", "0%", "0", empty_fig, empty_fig

    @app.callback(
        [
            Output('campaign-total-donations', 'children'),
            Output('campaign-peak-period', 'children'),
            Output('campaign-growth-rate', 'children')
        ],
        [
            Input('campaign-date-range', 'start_date'),
            Input('campaign-date-range', 'end_date')
        ]
    )
    def update_campaign_kpis(start_date, end_date):
        df = load_data()
        
        if df.empty:
            return "0", "N/A", "0%"
        
        # Conversion des dates
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Filtrage par date
        mask = (df['date_de_remplissage'] >= start_date) & (df['date_de_remplissage'] <= end_date)
        filtered_df = df[mask]
        
        # Total des dons
        total_dons = len(filtered_df)
        
        # Période la plus active (mois)
        if not filtered_df.empty:
            monthly_counts = filtered_df['date_de_remplissage'].dt.to_period('M').value_counts()
            peak_month = monthly_counts.index[0] if not monthly_counts.empty else "N/A"
            peak_month = str(peak_month)
        else:
            peak_month = "N/A"
            
        # Taux de croissance
        if not filtered_df.empty:
            monthly_data = filtered_df.groupby(filtered_df['date_de_remplissage'].dt.to_period('M')).size()
            if len(monthly_data) > 1:
                first_month = monthly_data.iloc[0]
                last_month = monthly_data.iloc[-1]
                growth = ((last_month - first_month) / first_month) * 100
            else:
                growth = 0
        else:
            growth = 0
        
        return f"{total_dons:,}", peak_month, f"{growth:.1f}%"

    @app.callback(
        Output('campaign-timeline', 'figure'),
        [Input('campaign-date-range', 'start_date'),
         Input('campaign-date-range', 'end_date')]
    )
    def update_campaign_timeline(start_date, end_date):
        df = load_data()
        
        if df.empty:
            return go.Figure().add_annotation(
                text="Données non disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Conversion des dates
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Filtrage par date
        mask = (df['date_de_remplissage'] >= start_date) & (df['date_de_remplissage'] <= end_date)
        filtered_df = df[mask]
        
        if filtered_df.empty:
            return go.Figure().add_annotation(
                text="Aucune donnée disponible pour la période sélectionnée",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Agrégation par jour
        daily_counts = filtered_df.groupby('date_de_remplissage').size().reset_index(name='count')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_counts['date_de_remplissage'],
            y=daily_counts['count'],
            mode='lines+markers',
            line=dict(color='#dc3545', width=2),
            marker=dict(size=6, color='#0d2c54'),
            name='Nombre de dons'
        ))
        
        fig.update_layout(
            title='Évolution quotidienne des dons',
            xaxis_title='Date',
            yaxis_title='Nombre de dons',
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig

    @app.callback(
        Output('campaign-monthly-distribution', 'figure'),
        [Input('campaign-date-range', 'start_date'),
         Input('campaign-date-range', 'end_date')]
    )
    def update_monthly_distribution(start_date, end_date):
        df = load_data()
        
        if df.empty:
            return go.Figure().add_annotation(
                text="Données non disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Conversion des dates
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Filtrage par date
        mask = (df['date_de_remplissage'] >= start_date) & (df['date_de_remplissage'] <= end_date)
        filtered_df = df[mask]
        
        if filtered_df.empty:
            return go.Figure().add_annotation(
                text="Aucune donnée disponible pour la période sélectionnée",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Agrégation par mois
        monthly_counts = filtered_df.groupby(filtered_df['date_de_remplissage'].dt.month).size().reset_index(name='count')
        month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        monthly_counts['month_name'] = monthly_counts['date_de_remplissage'].apply(lambda x: month_names[x-1])
        
        fig = px.bar(
            monthly_counts,
            x='month_name',
            y='count',
            color='count',
            color_continuous_scale=['#0d2c54', '#dc3545']
        )
        
        fig.update_layout(
            title='Distribution mensuelle des dons',
            xaxis_title='Mois',
            yaxis_title='Nombre de dons',
            template='plotly_white'
        )
        
        return fig

    # Callbacks pour les analyses par caractéristique
    for characteristic in ['age', 'genre', 'niveau_d_etude', 'profession', 'religion', 'situation_matrimoniale_(sm)']:
        @app.callback(
            Output(f'campaign-{characteristic.replace("_", "-")}-analysis', 'figure'),
            [Input('campaign-date-range', 'start_date'),
             Input('campaign-date-range', 'end_date')]
        )
        def update_characteristic_analysis(start_date, end_date, characteristic=characteristic):
            df = load_data()
            
            if df.empty:
                return go.Figure().add_annotation(
                    text="Données non disponibles",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            
            # Conversion des dates
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            
            # Filtrage par date
            mask = (df['date_de_remplissage'] >= start_date) & (df['date_de_remplissage'] <= end_date)
            filtered_df = df[mask]
            
            if filtered_df.empty:
                return go.Figure().add_annotation(
                    text="Aucune donnée disponible pour la période sélectionnée",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            
            # Analyse par caractéristique
            char_counts = filtered_df[characteristic].value_counts().reset_index()
            char_counts.columns = ['Catégorie', 'Nombre']
            
            # Créer le graphique
            if characteristic == 'age':
                fig = px.histogram(
                    filtered_df,
                    x=characteristic,
                    nbins=20,
                    title=f'Distribution par {characteristic}',
                    color_discrete_sequence=['#dc3545']
                )
            else:
                fig = px.bar(
                    char_counts,
                    x='Catégorie',
                    y='Nombre',
                    title=f'Distribution par {characteristic}',
                    color='Nombre',
                    color_continuous_scale=['#0d2c54', '#dc3545']
                )
            
            fig.update_layout(
                xaxis_title=characteristic.replace("_", " ").title(),
                yaxis_title='Nombre de donneurs',
                template='plotly_white'
            )
            
            return fig
