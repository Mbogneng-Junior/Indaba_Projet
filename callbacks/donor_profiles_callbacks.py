import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html
import numpy as np

def init_donor_profiles_callbacks(app):
    """Initialise les callbacks pour la page de profilage des donneurs"""
    
    # Charger les données
    df = pd.read_csv('data/processed_data.csv')
    
    # Conversion des dates
    df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
    
    # Debug: Afficher les informations sur le dataset
    print("Shape du DataFrame:", df.shape)
    print("\nColonnes disponibles:", df.columns.tolist())
    print("\nAperçu des dates:", df['date_de_remplissage'].head())
    print("\nPériode couverte:", df['date_de_remplissage'].min(), "à", df['date_de_remplissage'].max())
    
    def create_empty_figure(title="Aucune donnée disponible"):
        """Crée un graphique vide avec un message"""
        fig = go.Figure()
        fig.add_annotation(
            text=title,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        return fig
    
    def create_distribution_figure(data, column, title, is_continuous=False):
        """Fonction utilitaire pour créer les graphiques de distribution"""
        if data.empty:
            return create_empty_figure(f"Aucune donnée disponible pour {title}")
            
        if is_continuous:
            fig = px.histogram(
                data,
                x=column,
                title=title,
                labels={column: title}
            )
        else:
            value_counts = data[column].value_counts()
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=title,
                labels={'x': title, 'y': 'Nombre'}
            )
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            height=400
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        return fig
    
    @app.callback(
        [Output('demographic-distribution', 'figure'),
         Output('feature-statistics', 'figure'),
         Output('donation-history', 'figure'),
         Output('return-rate', 'figure')],
        [Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('features-checklist', 'value'),
         Input('eligibility-filter', 'value')]
    )
    def update_profile_visualizations(start_date, end_date, selected_features, eligibility_status):
        # Debug: Afficher les paramètres reçus
        print("\nParamètres reçus:")
        print("start_date:", start_date)
        print("end_date:", end_date)
        print("selected_features:", selected_features)
        print("eligibility_status:", eligibility_status)
        
        if not selected_features:
            empty_fig = create_empty_figure("Veuillez sélectionner au moins une caractéristique")
            return empty_fig, empty_fig, empty_fig, empty_fig
        
        # Convertir les dates en datetime si elles sont des strings
        if start_date:
            start_date = pd.to_datetime(start_date)
        if end_date:
            end_date = pd.to_datetime(end_date)
            
        # Filtrer les données par date
        mask = pd.Series(True, index=df.index)
        if start_date and end_date:
            mask &= (df['date_de_remplissage'].dt.date >= start_date.date()) & (df['date_de_remplissage'].dt.date <= end_date.date())
        
        # Debug: Afficher les informations sur le filtrage
        print("\nNombre de lignes après filtrage par date:", mask.sum())
        
        # Filtrer par éligibilité
        if eligibility_status != 'all':
            mask &= df['eligibilite_au_don'] == eligibility_status
        
        filtered_df = df[mask].copy()
        
        # Debug: Afficher les informations sur le DataFrame filtré
        print("\nNombre final de lignes:", len(filtered_df))
        if not filtered_df.empty:
            print("Aperçu des dates filtrées:", filtered_df['date_de_remplissage'].head())
        
        if filtered_df.empty:
            empty_fig = create_empty_figure("Aucune donnée disponible pour les filtres sélectionnés")
            return empty_fig, empty_fig, empty_fig, empty_fig
        
        # 1. Distribution démographique
        if 'age' in selected_features:
            demo_fig = create_distribution_figure(filtered_df, 'age', "Distribution par âge", is_continuous=True)
        elif 'genre' in selected_features:
            demo_fig = create_distribution_figure(filtered_df, 'genre', "Distribution par genre")
        else:
            demo_fig = create_distribution_figure(filtered_df, 'niveau_d_etude', "Distribution par niveau d'éducation")
        
        # 2. Statistiques par caractéristique
        feature_stats = []
        for feature in selected_features:
            if feature == 'age':
                stats = filtered_df.groupby('genre')['age'].mean().reset_index()
                stats.columns = ['Catégorie', 'Valeur']
                feature_stats.append({'feature': 'Âge moyen par genre', 'data': stats})
            else:
                stats = filtered_df[feature].value_counts().reset_index()
                stats.columns = ['Catégorie', 'Valeur']
                feature_stats.append({'feature': f'Distribution par {feature}', 'data': stats})
        
        if feature_stats:
            stats_fig = px.bar(
                feature_stats[0]['data'],
                x='Catégorie',
                y='Valeur',
                title=feature_stats[0]['feature']
            )
        else:
            stats_fig = create_empty_figure("Aucune caractéristique sélectionnée")
        
        stats_fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            height=400
        )
        
        # 3. Historique des dons
        monthly_stats = filtered_df.groupby(pd.Grouper(key='date_de_remplissage', freq='M')).size().reset_index()
        monthly_stats.columns = ['Date', 'Nombre de donneurs']
        
        history_fig = px.line(
            monthly_stats,
            x='Date',
            y='Nombre de donneurs',
            title="Évolution du nombre de donneurs dans le temps"
        )
        history_fig.update_traces(mode='lines+markers')
        history_fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            height=400
        )
        
        # 4. Taux de retour par profil
        if 'genre' in selected_features and not filtered_df['genre'].empty:
            return_stats = filtered_df.groupby('genre').agg({
                'eligibilite_au_don': lambda x: (x == 'eligible').mean() * 100
            }).reset_index()
            return_stats.columns = ['Catégorie', 'Taux d\'éligibilité']
        else:
            return_stats = filtered_df.groupby('niveau_d_etude').agg({
                'eligibilite_au_don': lambda x: (x == 'eligible').mean() * 100
            }).reset_index()
            return_stats.columns = ['Catégorie', 'Taux d\'éligibilité']
        
        return_fig = px.bar(
            return_stats,
            x='Catégorie',
            y='Taux d\'éligibilité',
            title="Taux d'éligibilité par catégorie"
        )
        return_fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            height=400
        )
        
        return demo_fig, stats_fig, history_fig, return_fig
    
    @app.callback(
        Output('profile-summary', 'children'),
        [Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('features-checklist', 'value')]
    )
    def update_profile_summary(start_date, end_date, selected_features):
        if not selected_features:
            return dbc.Alert("Veuillez sélectionner au moins une caractéristique", color="warning")
            
        # Filtrer les données par date
        mask = pd.Series(True, index=df.index)
        if start_date and end_date:
            mask &= (df['date_de_remplissage'] >= start_date) & (df['date_de_remplissage'] <= end_date)
        filtered_df = df[mask]
        
        if filtered_df.empty:
            return dbc.Alert("Aucune donnée disponible pour la période sélectionnée", color="warning")
        
        # Créer le résumé des profils
        summary_data = []
        
        if 'age' in selected_features:
            summary_data.append({
                'Caractéristique': 'Âge',
                'Moyenne': f"{filtered_df['age'].mean():.1f} ans",
                'Médiane': f"{filtered_df['age'].median():.1f} ans",
                'Min': f"{filtered_df['age'].min():.0f} ans",
                'Max': f"{filtered_df['age'].max():.0f} ans"
            })
        
        for feature in selected_features:
            if feature != 'age':
                value_counts = filtered_df[feature].value_counts()
                if not value_counts.empty:
                    summary_data.append({
                        'Caractéristique': feature,
                        'Catégorie principale': value_counts.index[0],
                        'Nombre': value_counts.iloc[0],
                        'Pourcentage': f"{(value_counts.iloc[0] / len(filtered_df) * 100):.1f}%"
                    })
        
        if not summary_data:
            return dbc.Alert("Aucune donnée à afficher", color="warning")
        
        # Créer le tableau HTML
        table = dbc.Table.from_dataframe(
            pd.DataFrame(summary_data),
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            className="mb-0"
        )
        
        return table
