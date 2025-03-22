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

def init_feedback_analysis_callbacks(app):
    """Initialise les callbacks pour l'analyse des retours"""
    
    # Charger et prétraiter les données
    df = pd.read_csv('data/processed_data.csv')
    
    # Conversion des dates
    df['Date de remplissage de la fiche'] = pd.to_datetime(df['Date de remplissage de la fiche'])
    
    # Créer une colonne combinée des raisons
    raison_columns = [col for col in df.columns if col.startswith(('indispo_', 'non_elig_'))]
    
    # Créer un dictionnaire de mapping pour des descriptions plus lisibles
    raison_mapping = {
        'indispo_Est sous anti-biothérapie': 'Sous traitement antibiotique',
        'indispo_Taux d\'hémoglobine bas': 'Taux d\'hémoglobine insuffisant',
        'indispo_date de dernier Don < 3 mois': 'Don trop récent',
        'indispo_IST récente': 'Infection récente',
        'non_elig_Antécédent de transfusion': 'Antécédent de transfusion',
        'non_elig_Porteur(HIV,hbs,hcv)': 'Porteur de maladie infectieuse',
        'non_elig_Opéré': 'Intervention chirurgicale récente',
        'non_elig_Drepanocytaire': 'Drépanocytaire',
        'non_elig_Diabétique': 'Diabétique',
        'non_elig_Hypertendus': 'Hypertension',
        'non_elig_Asthmatiques': 'Asthmatique',
        'non_elig_Cardiaque': 'Problème cardiaque',
        'non_elig_Tatoué': 'Tatouage récent',
        'non_elig_Scarifié': 'Scarification récente'
    }
    
    # Fonction pour combiner les raisons
    def combine_reasons(row):
        reasons = []
        for col in raison_columns:
            if row[col] == 1:
                reasons.append(raison_mapping.get(col, col))
        return '; '.join(reasons) if reasons else 'Pas de raison particulière'
    
    # Créer la colonne de commentaires combinés
    df['Commentaires'] = df.apply(combine_reasons, axis=1)
    
    # Fonction pour l'analyse de sentiment
    def analyze_sentiment(text):
        if pd.isna(text) or text == 'Pas de raison particulière':
            return 'neutre'
        
        # Classifier les raisons
        if any(word in text.lower() for word in ['infection', 'maladie', 'porteur']):
            return 'négatif'
        elif 'don trop récent' in text.lower():
            return 'positif'  # Car indique un donneur régulier
        else:
            return 'neutre'
    
    # Analyser les sentiments
    df['Sentiment'] = df['Commentaires'].apply(analyze_sentiment)
    
    # Fonction pour créer un nuage de mots
    def generate_wordcloud(text_data, background_color='white'):
        text = ' '.join(str(text) for text in text_data if pd.notna(text))
        if not text.strip() or text == "Pas de raison particulière":
            text = "Aucune donnée disponible"
            
        wordcloud = WordCloud(
            width=400,
            height=200,
            background_color=background_color,
            collocations=False
        ).generate(text)
        
        # Convertir le nuage de mots en image
        img = BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        
        return 'data:image/png;base64,{}'.format(
            base64.b64encode(img.getvalue()).decode()
        )
    
    @app.callback(
        [Output('total-feedback', 'children'),
         Output('sentiment-positif', 'children'),
         Output('sentiment-neutre', 'children'),
         Output('sentiment-negatif', 'children'),
         Output('sentiment-evolution', 'figure'),
         Output('sentiment-by-group', 'figure'),
         Output('wordcloud-positive', 'src'),
         Output('wordcloud-negative', 'src'),
         Output('topic-distribution', 'figure'),
         Output('sentiment-patterns', 'figure'),
         Output('feedback-categories', 'figure'),
         Output('feedback-examples', 'children')],
        [Input('feedback-period-slider', 'value'),
         Input('feedback-demographic-dropdown', 'value')]
    )
    def update_feedback_analysis(years, demographic):
        # Filtrer les données par période
        mask = df['Date de remplissage de la fiche'].dt.year.between(years[0], years[1])
        dff = df[mask].copy()
        
        # 1. Calculer les KPIs
        total_feedback = len(dff[dff['Commentaires'] != 'Pas de raison particulière'])
        sentiment_counts = dff['Sentiment'].value_counts()
        
        # 2. Évolution des sentiments
        sentiment_evolution = dff.groupby([
            pd.Grouper(key='Date de remplissage de la fiche', freq='M'),
            'Sentiment'
        ]).size().unstack(fill_value=0)
        
        evolution_fig = px.area(sentiment_evolution,
                              title='Évolution des retours au fil du temps',
                              color_discrete_map={
                                  'positif': '#28a745',
                                  'neutre': '#ffc107',
                                  'négatif': '#dc3545'
                              },
                              template='plotly_white')
        
        # 3. Sentiment par groupe démographique
        if demographic == 'age':
            dff['Groupe_Age'] = pd.cut(dff['Age'], 
                                     bins=[0, 25, 35, 45, 55, 100],
                                     labels=['18-25', '26-35', '36-45', '46-55', '55+'])
            group_col = 'Groupe_Age'
        elif demographic == 'genre':
            group_col = 'Genre'
        elif demographic == 'profession':
            group_col = 'Profession'
        else:
            group_col = 'Arrondissement de résidence'
            
        sentiment_by_group = dff.groupby([group_col, 'Sentiment']).size().unstack(fill_value=0)
        sentiment_by_group = sentiment_by_group.div(sentiment_by_group.sum(axis=1), axis=0)
        
        group_fig = px.bar(sentiment_by_group.reset_index(),
                          x=group_col,
                          y=['positif', 'neutre', 'négatif'],
                          title=f'Distribution des retours par {group_col}',
                          color_discrete_map={
                              'positif': '#28a745',
                              'neutre': '#ffc107',
                              'négatif': '#dc3545'
                          },
                          template='plotly_white')
        
        # 4. Nuages de mots
        positive_comments = dff[dff['Sentiment'] == 'positif']['Commentaires']
        negative_comments = dff[dff['Sentiment'] == 'négatif']['Commentaires']
        
        wordcloud_pos = generate_wordcloud(positive_comments)
        wordcloud_neg = generate_wordcloud(negative_comments)
        
        # 5. Distribution des thèmes
        topic_fig = px.pie(dff[dff['Commentaires'] != 'Pas de raison particulière'],
                          names='Sentiment',
                          title='Distribution des types de retours',
                          color_discrete_map={
                              'positif': '#28a745',
                              'neutre': '#ffc107',
                              'négatif': '#dc3545'
                          },
                          template='plotly_white')
        
        # 6. Patterns de retours
        patterns_fig = px.box(dff[dff['Commentaires'] != 'Pas de raison particulière'],
                            x='Sentiment',
                            y=group_col,
                            title='Distribution des groupes par type de retour',
                            color='Sentiment',
                            color_discrete_map={
                                'positif': '#28a745',
                                'neutre': '#ffc107',
                                'négatif': '#dc3545'
                            },
                            template='plotly_white')
        
        # 7. Catégories de retour
        categories_fig = px.sunburst(dff[dff['Commentaires'] != 'Pas de raison particulière'],
                                   path=[group_col, 'Sentiment'],
                                   title='Hiérarchie des retours',
                                   template='plotly_white')
        
        # 8. Exemples de retours
        examples = []
        for sentiment in ['positif', 'neutre', 'négatif']:
            sentiment_comments = dff[
                (dff['Sentiment'] == sentiment) & 
                (dff['Commentaires'] != 'Pas de raison particulière')
            ]['Commentaires'].dropna()
            
            if not sentiment_comments.empty:
                example = sentiment_comments.iloc[0]
            else:
                example = "Pas d'exemple disponible"
                
            examples.append(
                dbc.Card([
                    dbc.CardHeader(sentiment.capitalize(), 
                                 className=f"bg-{'success' if sentiment == 'positif' else 'warning' if sentiment == 'neutre' else 'danger'} text-white"),
                    dbc.CardBody([
                        html.P(example, className="mb-0")
                    ])
                ], className="mb-3")
            )
        
        feedback_examples = dbc.Row([dbc.Col(example, width=4) for example in examples])
        
        return (
            f"{total_feedback:,}",
            f"{sentiment_counts.get('positif', 0):,}",
            f"{sentiment_counts.get('neutre', 0):,}",
            f"{sentiment_counts.get('négatif', 0):,}",
            evolution_fig,
            group_fig,
            wordcloud_pos,
            wordcloud_neg,
            topic_fig,
            patterns_fig,
            categories_fig,
            feedback_examples
        )
