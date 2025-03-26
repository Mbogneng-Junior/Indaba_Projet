import pandas as pd
import numpy as np
from textblob import TextBlob
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Chargement des données
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(current_dir), 'data', 'processed_data.csv')
    df = pd.read_csv(data_path)
    df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    df['age'] = df['age'].fillna(30)  # Valeur par défaut
    df['age'] = df['age'].clip(lower=18, upper=100)
    
    # Création des tranches d'âge
    bins = [0, 25, 35, 45, 55, float('inf')]
    labels = ['18-25', '26-35', '36-45', '46-55', '56+']
    df['tranche_age'] = pd.cut(df['age'], bins=bins, labels=labels)
    
    # Créer un indicateur de satisfaction basé sur l'éligibilité
    df['satisfaction'] = df['eligibilite_au_don'].str.lower() == 'eligible'
    
    return df

# Fonction pour l'analyse de sentiment
def analyze_sentiment(row):
    # Créer une chaîne de texte avec toutes les informations pertinentes
    text_elements = []
    if row['a_t_il_elle_deja_donne_le_sang'] == 'Oui':
        text_elements.append("Donneur régulier")
    
    # Ajouter d'autres éléments si nécessaire
    text = " ".join(text_elements)
    
    if not text:
        return 'neutral'
    
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        return 'positive'
    elif polarity < -0.1:
        return 'negative'
    else:
        return 'neutral'

def init_feedback_analysis_callbacks(app):
    """Initialise les callbacks pour l'analyse des retours"""
    
    def load_data():
        """Charge et prépare les données"""
        try:
            file_path = os.path.join('data', 'processed_data.csv')
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
            
            df = pd.read_csv(file_path, low_memory=False)
            if df.empty:
                raise ValueError("Le fichier de données est vide")
            
            # Conversion des dates
            df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'], errors='coerce')
            
            # Calcul de l'âge
            df['age'] = pd.to_numeric(df['age'], errors='coerce')
            df['age'] = df['age'].fillna(30)  # Valeur par défaut
            df['age'] = df['age'].clip(lower=18, upper=100)
            
            # Création des tranches d'âge
            bins = [0, 25, 35, 45, 55, float('inf')]
            labels = ['18-25', '26-35', '36-45', '46-55', '56+']
            df['tranche_age'] = pd.cut(df['age'], bins=bins, labels=labels)
            
            # Créer un indicateur de satisfaction basé sur l'éligibilité
            df['satisfaction'] = df['eligibilite_au_don'].str.lower() == 'eligible'
            
            return df
            
        except Exception as e:
            print(f"Erreur lors du chargement des données: {str(e)}")
            return None
    
    @app.callback(
        [Output('total-feedback', 'children'),
         Output('positive-feedback', 'children'),
         Output('negative-feedback', 'children'),
         Output('feedback-pie-chart', 'figure')],
        [Input('feedback-date-range', 'start_date'),
         Input('feedback-date-range', 'end_date')]
    )
    def update_feedback_stats(start_date, end_date):
        try:
            df = load_data()
            if df is None:
                raise ValueError("Impossible de charger les données")
            
            # Appliquer les filtres de date
            mask = pd.Series(True, index=df.index)
            if start_date:
                mask &= df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()
            if end_date:
                mask &= df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()
            
            df_filtered = df[mask]
            
            # Calculer les statistiques
            total_feedback = len(df_filtered)
            positive_feedback = df_filtered['satisfaction'].sum()
            negative_feedback = total_feedback - positive_feedback
            
            # Créer le graphique en camembert
            pie_data = pd.DataFrame({
                'Type': ['Éligibles', 'Non éligibles'],
                'Nombre': [positive_feedback, negative_feedback]
            })
            
            pie_fig = px.pie(
                pie_data,
                values='Nombre',
                names='Type',
                title="Répartition des retours",
                color_discrete_sequence=['#28a745', '#dc3545']
            )
            pie_fig.update_layout(showlegend=True)
            
            return (
                f"{total_feedback:,}",
                f"{positive_feedback:,}",
                f"{negative_feedback:,}",
                pie_fig
            )
            
        except Exception as e:
            print(f"Erreur dans update_feedback_stats: {str(e)}")
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="Aucune donnée disponible",
                annotations=[dict(
                    text=str(e),
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=14)
                )]
            )
            return "0", "0", "0", empty_fig
    
    @app.callback(
        Output('feedback-timeline', 'figure'),
        [Input('feedback-date-range', 'start_date'),
         Input('feedback-date-range', 'end_date')]
    )
    def update_feedback_timeline(start_date, end_date):
        try:
            df = load_data()
            if df is None:
                raise ValueError("Impossible de charger les données")
            
            # Appliquer les filtres de date
            mask = pd.Series(True, index=df.index)
            if start_date:
                mask &= df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()
            if end_date:
                mask &= df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()
            
            df_filtered = df[mask]
            
            # Calculer les statistiques mensuelles
            monthly_stats = df_filtered.groupby(pd.Grouper(key='date_de_remplissage', freq='M')).agg({
                'satisfaction': 'mean'
            }).reset_index()
            
            # Convertir en pourcentage
            monthly_stats['satisfaction'] = monthly_stats['satisfaction'] * 100
            
            fig = px.line(
                monthly_stats,
                x='date_de_remplissage',
                y='satisfaction',
                title="Évolution du taux d'éligibilité",
                labels={
                    'date_de_remplissage': 'Date',
                    'satisfaction': "Taux d'éligibilité (%)"
                }
            )
            
            fig.update_layout(
                showlegend=False,
                xaxis_title="Période",
                yaxis_title="Taux d'éligibilité (%)",
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Erreur dans update_feedback_timeline: {str(e)}")
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="Aucune donnée disponible",
                annotations=[dict(
                    text=str(e),
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=14)
                )],
                height=400
            )
            return empty_fig
    
    @app.callback(
        [Output('age-feedback-analysis', 'figure'),
         Output('gender-feedback-analysis', 'figure'),
         Output('education-feedback-analysis', 'figure'),
         Output('location-feedback-analysis', 'figure')],
        [Input('feedback-date-range', 'start_date'),
         Input('feedback-date-range', 'end_date')]
    )
    def update_feedback_analysis(start_date, end_date):
        try:
            df = load_data()
            if df is None:
                raise ValueError("Impossible de charger les données")
            
            # Appliquer les filtres de date
            mask = pd.Series(True, index=df.index)
            if start_date:
                mask &= df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()
            if end_date:
                mask &= df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()
            
            df_filtered = df[mask]
            
            # 1. Analyse par âge
            age_analysis = df_filtered.groupby('tranche_age', observed=True).agg({
                'satisfaction': 'mean'
            }).reset_index()
            age_analysis['satisfaction'] = age_analysis['satisfaction'] * 100
            
            age_fig = px.bar(
                age_analysis,
                x='tranche_age',
                y='satisfaction',
                title="Éligibilité par tranche d'âge",
                labels={
                    'tranche_age': "Tranche d'âge",
                    'satisfaction': "Taux d'éligibilité (%)"
                },
                color='satisfaction',
                color_continuous_scale=['#dc3545', '#28a745']
            )
            
            # 2. Analyse par genre
            gender_analysis = df_filtered.groupby('genre').agg({
                'satisfaction': 'mean'
            }).reset_index()
            gender_analysis['satisfaction'] = gender_analysis['satisfaction'] * 100
            
            gender_fig = px.bar(
                gender_analysis,
                x='genre',
                y='satisfaction',
                title="Éligibilité par genre",
                labels={
                    'genre': 'Genre',
                    'satisfaction': "Taux d'éligibilité (%)"
                },
                color='satisfaction',
                color_continuous_scale=['#dc3545', '#28a745']
            )
            
            # 3. Analyse par niveau d'éducation
            education_analysis = df_filtered.groupby('niveau_d_etude').agg({
                'satisfaction': 'mean'
            }).reset_index()
            education_analysis['satisfaction'] = education_analysis['satisfaction'] * 100
            
            education_fig = px.bar(
                education_analysis,
                x='niveau_d_etude',
                y='satisfaction',
                title="Éligibilité par niveau d'études",
                labels={
                    'niveau_d_etude': "Niveau d'études",
                    'satisfaction': "Taux d'éligibilité (%)"
                },
                color='satisfaction',
                color_continuous_scale=['#dc3545', '#28a745']
            )
            
            # 4. Analyse par localisation
            location_analysis = df_filtered.groupby('ville').agg({
                'satisfaction': 'mean'
            }).reset_index()
            location_analysis['satisfaction'] = location_analysis['satisfaction'] * 100
            
            location_fig = px.bar(
                location_analysis,
                x='satisfaction',
                y='ville',
                title="Éligibilité par ville",
                labels={
                    'ville': 'Ville',
                    'satisfaction': "Taux d'éligibilité (%)"
                },
                color='satisfaction',
                color_continuous_scale=['#dc3545', '#28a745'],
                orientation='h'
            )
            
            # Mise en page des graphiques
            for fig in [age_fig, gender_fig, education_fig, location_fig]:
                fig.update_layout(
                    showlegend=False,
                    height=400,
                    margin=dict(l=0, r=0, t=40, b=0)
                )
            
            return age_fig, gender_fig, education_fig, location_fig
            
        except Exception as e:
            print(f"Erreur dans update_feedback_analysis: {str(e)}")
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="Aucune donnée disponible",
                annotations=[dict(
                    text=str(e),
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=14)
                )],
                height=400
            )
            return empty_fig, empty_fig, empty_fig, empty_fig
    
    @app.callback(
        [Output('positive-wordcloud', 'children'),
         Output('negative-wordcloud', 'children')],
        [Input('url', 'pathname')]
    )
    def update_wordclouds(_):
        """Cette fonction est désactivée car les colonnes de raisons ne sont pas disponibles"""
        # Créer un message d'erreur stylisé
        error_style = {
            'textAlign': 'center',
            'padding': '2rem',
            'backgroundColor': '#f8d7da',
            'color': '#721c24',
            'borderRadius': '0.25rem',
            'marginBottom': '1rem'
        }
        
        error_message = html.Div([
            html.I(className="fas fa-exclamation-circle me-2"),
            "Données non disponibles pour le nuage de mots"
        ], style=error_style)
        
        return error_message, error_message
    
    @app.callback(
        [Output('other-reasons-analysis', 'figure'),
         Output('main-reasons-analysis', 'figure')],
        [Input('url', 'pathname')]
    )
    def update_reasons_analysis(_):
        """Cette fonction est désactivée car les colonnes de raisons ne sont pas disponibles"""
        # Créer des graphiques vides avec un message
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Données non disponibles",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        
        return empty_fig, empty_fig
