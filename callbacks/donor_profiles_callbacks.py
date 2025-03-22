import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html

def init_donor_profiles_callbacks(app):
    """Initialise les callbacks pour le profilage des donneurs"""
    
    # Charger et prétraiter les données
    df = pd.read_csv('data/processed_data.csv')
    
    # Conversion des dates et calcul de l'âge
    df['Date de remplissage de la fiche'] = pd.to_datetime(df['Date de remplissage de la fiche'])
    df['Date de naissance'] = pd.to_datetime(df['Date de naissance'])
    df['Age'] = ((df['Date de remplissage de la fiche'] - df['Date de naissance']).dt.total_seconds() / (365.25 * 24 * 60 * 60)).round()
    
    # Encodeurs pour les variables catégorielles
    label_encoders = {}
    
    def prepare_clustering_data(features):
        data_for_clustering = pd.DataFrame()
        
        if 'age' in features:
            data_for_clustering['Age'] = df['Age'].fillna(df['Age'].median())
            
        if 'genre' in features:
            label_encoders['Genre'] = LabelEncoder()
            data_for_clustering['Genre'] = label_encoders['Genre'].fit_transform(df['Genre'].fillna('Non spécifié'))
            
        if 'profession' in features:
            label_encoders['Profession'] = LabelEncoder()
            data_for_clustering['Profession'] = label_encoders['Profession'].fit_transform(df['Profession'].fillna('Non spécifié'))
            
        if 'sante' in features:
            # Créer un score de santé basé sur les conditions médicales
            health_cols = [col for col in df.columns if col.startswith(('non_elig_', 'indispo_'))]
            df['score_sante'] = df[health_cols].sum(axis=1)
            data_for_clustering['score_sante'] = df['score_sante']
            
        if 'location' in features:
            label_encoders['Location'] = LabelEncoder()
            data_for_clustering['Location'] = label_encoders['Location'].fit_transform(
                df['Arrondissement de résidence'].fillna('Non spécifié')
            )
        
        # Normalisation des données
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(data_for_clustering)
        
        return X_scaled, data_for_clustering.columns
    
    @app.callback(
        [Output('cluster-visualization', 'figure'),
         Output('cluster-characteristics', 'figure'),
         Output('profile-details', 'children')],
        [Input('analyze-profiles', 'n_clicks')],
        [State('n-clusters-slider', 'value'),
         State('features-checklist', 'value')]
    )
    def update_clustering(n_clicks, n_clusters, features):
        if not n_clicks or not features:
            return {}, {}, []
        
        # Préparer les données
        X_scaled, feature_names = prepare_clustering_data(features)
        
        # Appliquer le clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # Ajouter les labels au DataFrame
        df['Cluster'] = cluster_labels
        
        # 1. Visualisation des clusters (PCA)
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        viz_df = pd.DataFrame(X_pca, columns=['Composante 1', 'Composante 2'])
        viz_df['Cluster'] = [f'Profil {i+1}' for i in cluster_labels]
        
        cluster_viz = px.scatter(viz_df, 
                               x='Composante 1', 
                               y='Composante 2',
                               color='Cluster',
                               title='Distribution des profils de donneurs',
                               template='plotly_white')
        
        # 2. Caractéristiques des clusters
        cluster_stats = []
        
        for cluster in range(n_clusters):
            cluster_mask = df['Cluster'] == cluster
            cluster_data = df[cluster_mask]
            
            stats = {
                'Cluster': f'Profil {cluster + 1}',
                'Taille': len(cluster_data),
                'Âge moyen': f"{cluster_data['Age'].mean():.1f} ans",
                'Genre principal': cluster_data['Genre'].mode().iloc[0],
                'Profession principale': cluster_data['Profession'].mode().iloc[0],
                'Arrondissement principal': cluster_data['Arrondissement de résidence'].mode().iloc[0],
                'Taux d\'éligibilité': f"{(cluster_data['ÉLIGIBILITÉ AU DON.'] == 'eligible').mean()*100:.1f}%"
            }
            
            cluster_stats.append(stats)
        
        # Créer le tableau des caractéristiques
        chars_fig = go.Figure(data=[
            go.Table(
                header=dict(
                    values=['Profil', 'Taille', 'Âge moyen', 'Genre principal', 
                           'Profession principale', 'Arrondissement', 'Taux d\'éligibilité'],
                    fill_color='#007bff',
                    align='left',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=[
                        [s['Cluster'] for s in cluster_stats],
                        [s['Taille'] for s in cluster_stats],
                        [s['Âge moyen'] for s in cluster_stats],
                        [s['Genre principal'] for s in cluster_stats],
                        [s['Profession principale'] for s in cluster_stats],
                        [s['Arrondissement principal'] for s in cluster_stats],
                        [s['Taux d\'éligibilité'] for s in cluster_stats]
                    ],
                    fill_color='white',
                    align='left'
                )
            )
        ])
        
        chars_fig.update_layout(
            title='Caractéristiques des profils',
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        # 3. Cartes de profil
        profile_cards = []
        for stats in cluster_stats:
            card = dbc.Card([
                dbc.CardHeader(stats['Cluster'], className="fw-bold"),
                dbc.CardBody([
                    html.H5(f"{stats['Taille']} donneurs", className="text-primary"),
                    html.P([
                        html.Strong("Âge moyen : "), stats['Âge moyen']
                    ], className="mb-1"),
                    html.P([
                        html.Strong("Genre principal : "), stats['Genre principal']
                    ], className="mb-1"),
                    html.P([
                        html.Strong("Profession : "), stats['Profession principale']
                    ], className="mb-1"),
                    html.P([
                        html.Strong("Taux d'éligibilité : "), stats['Taux d\'éligibilité']
                    ], className="mb-0")
                ])
            ], className="shadow-sm mb-3")
            
            profile_cards.append(dbc.Col(card, width=12//n_clusters))
        
        profile_details = dbc.Row(profile_cards)
        
        return cluster_viz, chars_fig, profile_details
