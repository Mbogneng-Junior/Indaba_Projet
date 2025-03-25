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
    df['age'] = pd.to_datetime('now').year - pd.to_datetime(df['date_de_naissance']).dt.year
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
        df = pd.read_csv('data/processed_data.csv')
        df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
        df['date_de_naissance'] = pd.to_datetime(df['date_de_naissance'])
        df['age'] = pd.to_datetime('now').year - df['date_de_naissance'].dt.year
        return df
    
    @app.callback(
        [Output('total-feedback', 'children'),
         Output('positive-feedback', 'children'),
         Output('negative-feedback', 'children'),
         Output('feedback-pie-chart', 'figure')],
        [Input('url', 'pathname')]
    )
    def update_feedback_overview(_):
        df = load_data()
        
        # Calculer les statistiques
        total = len(df)
        positive = df['a_t_il_elle_deja_donne_le_sang'].value_counts().get('Oui', 0)
        negative = df['a_t_il_elle_deja_donne_le_sang'].value_counts().get('Non', 0)
        
        # Créer le graphique en camembert
        pie_data = pd.DataFrame({
            'Statut': ['A déjà donné', 'N\'a jamais donné'],
            'Nombre': [positive, negative]
        })
        
        fig = px.pie(
            pie_data,
            values='Nombre',
            names='Statut',
            color='Statut',
            color_discrete_map={
                'A déjà donné': '#28a745',
                'N\'a jamais donné': '#dc3545'
            }
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=True)
        
        return (
            f"{total:,}",
            f"{positive:,} ({(positive/total)*100:.1f}%)",
            f"{negative:,} ({(negative/total)*100:.1f}%)",
            fig
        )
    
    @app.callback(
        [Output('age-feedback-analysis', 'figure'),
         Output('gender-feedback-analysis', 'figure'),
         Output('education-feedback-analysis', 'figure'),
         Output('location-feedback-analysis', 'figure')],
        [Input('url', 'pathname')]
    )
    def update_characteristic_analysis(_):
        df = load_data()
        
        def create_characteristic_analysis(data, char_col, title):
            # Calculer les statistiques par caractéristique
            char_stats = pd.crosstab(
                data[char_col],
                data['a_t_il_elle_deja_donne_le_sang'],
                normalize='index'
            ) * 100
            
            char_stats = char_stats.reset_index()
            
            # Renommer les colonnes
            char_stats.columns = [char_col, 'N\'a jamais donné (%)', 'A déjà donné (%)']
            
            fig = px.bar(
                char_stats,
                x=char_col,
                y=['A déjà donné (%)', 'N\'a jamais donné (%)'],
                title=title,
                barmode='group',
                color_discrete_map={
                    'A déjà donné (%)': '#28a745',
                    'N\'a jamais donné (%)': '#dc3545'
                }
            )
            
            fig.update_layout(
                xaxis_title=char_col.replace('_', ' ').title(),
                yaxis_title='Pourcentage',
                template='plotly_white'
            )
            
            return fig
        
        age_fig = create_characteristic_analysis(
            df,
            'age',
            'Retours par âge'
        )
        
        gender_fig = create_characteristic_analysis(
            df,
            'genre',
            'Retours par genre'
        )
        
        education_fig = create_characteristic_analysis(
            df,
            'niveau_d_etude',
            "Retours par niveau d'études"
        )
        
        location_fig = create_characteristic_analysis(
            df,
            'arrondissement_de_residence',
            'Retours par arrondissement'
        )
        
        return age_fig, gender_fig, education_fig, location_fig
    
    @app.callback(
        Output('feedback-timeline', 'figure'),
        [Input('url', 'pathname')]
    )
    def update_feedback_timeline(_):
        df = load_data()
        
        # Calculer l'évolution temporelle des retours
        timeline_stats = df.groupby(pd.Grouper(key='date_de_remplissage', freq='M')).apply(
            lambda x: pd.Series({
                'Total': len(x),
                'A déjà donné': (x['a_t_il_elle_deja_donne_le_sang'] == 'Oui').sum(),
                'N\'a jamais donné': (x['a_t_il_elle_deja_donne_le_sang'] == 'Non').sum()
            })
        ).reset_index()
        
        fig = go.Figure()
        
        # Ajouter les lignes pour chaque type de retour
        fig.add_trace(go.Scatter(
            x=timeline_stats['date_de_remplissage'],
            y=timeline_stats['A déjà donné'],
            name='A déjà donné',
            line=dict(color='#28a745', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=timeline_stats['date_de_remplissage'],
            y=timeline_stats['N\'a jamais donné'],
            name='N\'a jamais donné',
            line=dict(color='#dc3545', width=2)
        ))
        
        fig.update_layout(
            title='Évolution des retours dans le temps',
            xaxis_title='Date',
            yaxis_title='Nombre de retours',
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
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
