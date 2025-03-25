from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import dash_bootstrap_components as dbc

# Définir les couleurs
COLORS = ['#dc3545', '#000000', '#1a1f3c']  # Rouge, Noir, Bleu sombre

def init_donor_profiles_callbacks(app):
    """Initialise les callbacks pour la page des profils donneurs"""
    
    def load_data():
        """Charge et prépare les données"""
        df = pd.read_csv('data/processed_data.csv')
        df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
        return df
    
    def prepare_clustering_data(df):
        """Prépare les données pour le clustering"""
        try:
            # Sélectionner les colonnes numériques et catégorielles pertinentes
            numeric_cols = ['age']
            
            # Colonnes catégorielles principales
            categorical_cols = [
                'genre', 
                'niveau_d_etude', 
                'religion', 
                'situation_matrimoniale_(sm)',
                'profession'
            ]
            
            # Colonnes de santé (convertir en 0/1)
            health_cols = [
                'raison_indisponibilité__[est_sous_anti-biothérapie__]',
                'raison_indisponibilité__[taux_d\'hémoglobine_bas_]',
                'raison_indisponibilité__[date_de_dernier_don_<_3_mois_]',
                'raison_indisponibilité__[ist_récente_(exclu_vih,_hbs,_hcv)]',
                'raison_de_non-eligibilité_totale__[porteur(hiv,hbs,hcv)]',
                'raison_de_non-eligibilité_totale__[opéré]',
                'raison_de_non-eligibilité_totale__[drepanocytaire]',
                'raison_de_non-eligibilité_totale__[diabétique]',
                'raison_de_non-eligibilité_totale__[hypertendus]',
                'raison_de_non-eligibilité_totale__[asthmatiques]',
                'raison_de_non-eligibilité_totale__[cardiaque]'
            ]
            
            # Créer une copie du DataFrame pour éviter les modifications sur l'original
            df_prep = df.copy()
            
            # Convertir l'éligibilité en valeur numérique
            df_prep['eligibilite_num'] = (df_prep['eligibilite_au_don'] == 'eligible').astype(int)
            
            # Créer des variables dummy pour les colonnes catégorielles
            df_encoded = pd.get_dummies(df_prep[categorical_cols])
            
            # Ajouter les colonnes numériques
            for col in numeric_cols:
                df_encoded[col] = df_prep[col]
            
            # Ajouter l'éligibilité numérique
            df_encoded['eligibilite'] = df_prep['eligibilite_num']
            
            # Ajouter les colonnes de santé
            for col in health_cols:
                if col in df_prep.columns:
                    # Convertir les valeurs en 0/1
                    col_name = col.split('__')[-1].replace('[', '').replace(']', '')
                    df_encoded[col_name] = df_prep[col].fillna(0).map({'oui': 1, 'non': 0}).astype(int)
            
            # Standardiser les données
            scaler = StandardScaler()
            df_scaled = pd.DataFrame(scaler.fit_transform(df_encoded), columns=df_encoded.columns)
            
            return df_scaled
            
        except Exception as e:
            print(f"Erreur dans prepare_clustering_data: {str(e)}")
            raise e
    
    def analyze_cluster(cluster_df):
        """Analyse les caractéristiques d'un cluster"""
        analysis = []
        
        # Statistiques démographiques
        analysis.extend([
            f"Taille: {len(cluster_df)} donneurs",
            f"Âge moyen: {cluster_df['age'].mean():.1f} ans",
            f"Genre principal: {cluster_df['genre'].mode().iloc[0]}",
            f"Niveau d'études principal: {cluster_df['niveau_d_etude'].mode().iloc[0]}",
            f"Religion principale: {cluster_df['religion'].mode().iloc[0]}",
            f"Profession principale: {cluster_df['profession'].mode().iloc[0]}"
        ])
        
        # Statistiques de santé
        health_cols = [col for col in cluster_df.columns if 'raison' in col]
        health_issues = []
        for col in health_cols:
            if cluster_df[col].sum() > 0:
                issue = col.split('__')[-1].replace('[', '').replace(']', '').replace('_', ' ')
                count = cluster_df[col].sum()
                health_issues.append(f"{issue}: {count} cas")
        
        if health_issues:
            analysis.append("Problèmes de santé principaux:")
            analysis.extend(health_issues)
        
        return analysis
    
    def create_profile_interpretation(df, clusters):
        """Crée un tableau d'interprétation des profils"""
        interpretation_table = []
        
        for i in range(len(np.unique(clusters))):
            cluster_df = df[df['Cluster'] == i]
            
            # Caractéristiques principales
            age_mean = cluster_df['age'].mean()
            age_std = cluster_df['age'].std()
            gender_main = cluster_df['genre'].mode().iloc[0]
            education_main = cluster_df['niveau_d_etude'].mode().iloc[0]
            religion_main = cluster_df['religion'].mode().iloc[0]
            eligibility_rate = (cluster_df['eligibilite_au_don'] == 'eligible').mean()
            
            # Problèmes de santé principaux
            health_cols = [col for col in cluster_df.columns if 'raison' in col]
            health_issues = []
            for col in health_cols:
                count = cluster_df[col].map({'oui': 1, 'non': 0}).sum()
                if count > 0:
                    issue = col.split('__')[-1].replace('[', '').replace(']', '').replace('_', ' ')
                    health_issues.append(f"{issue} ({count})")
            
            # Créer le contenu des cellules avec des éléments HTML
            profile_content = [
                html.Span([
                    f"Age: {age_mean:.1f}±{age_std:.1f} ans",
                    html.Br(),
                    f"Genre: {gender_main}",
                    html.Br(),
                    f"Éducation: {education_main}",
                    html.Br(),
                    f"Religion: {religion_main}"
                ])
            ]
            
            health_content = [
                html.Span([
                    *[html.Span([issue, html.Br()]) for issue in health_issues[:3]]
                ]) if health_issues else "Aucun problème majeur"
            ]
            
            interpretation_table.append({
                "Cluster": f"Cluster {i+1}",
                "Taille": len(cluster_df),
                "Profil": profile_content,
                "Éligibilité": f"{eligibility_rate:.1%}",
                "Problèmes de santé": health_content
            })
        
        # Créer le tableau HTML
        table = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Cluster"),
                    html.Th("Taille"),
                    html.Th("Profil type"),
                    html.Th("Taux d'éligibilité"),
                    html.Th("Problèmes de santé principaux")
                ], className="table-dark")
            ),
            html.Tbody([
                html.Tr([
                    html.Td(row["Cluster"]),
                    html.Td(row["Taille"]),
                    html.Td(row["Profil"]),
                    html.Td(row["Éligibilité"]),
                    html.Td(row["Problèmes de santé"])
                ]) for row in interpretation_table
            ])
        ], bordered=True, hover=True, responsive=True)
        
        return table

    # Callback pour les options de localisation
    @app.callback(
        Output('location-filter', 'options'),
        [Input('url', 'pathname')]
    )
    def update_location_options(_):
        df = load_data()
        locations = df['arrondissement_de_residence'].unique()
        return [{'label': loc, 'value': loc} for loc in sorted(locations)]
    
    # Callback pour le clustering
    @app.callback(
        [Output('cluster-scatter', 'figure'),
         Output('cluster-characteristics', 'children'),
         Output('profile-interpretation-table', 'children')],
        [Input('location-filter', 'value'),
         Input('eligibility-filter', 'value'),
         Input('cluster-slider', 'value')]
    )
    def update_clustering(location, eligibility, n_clusters):
        try:
            df = load_data()
            
            # Appliquer les filtres
            if location:
                df = df[df['arrondissement_de_residence'] == location]
            if eligibility:
                df = df[df['eligibilite_au_don'] == eligibility]
            
            # Vérifier qu'il y a assez de données pour le clustering
            if len(df) < n_clusters:
                raise ValueError(f"Pas assez de données pour créer {n_clusters} clusters")
            
            # Préparer les données pour le clustering
            df_scaled = prepare_clustering_data(df)
            
            # Appliquer K-means avec n_init explicite
            kmeans = KMeans(
                n_clusters=n_clusters,
                random_state=42,
                n_init=10
            )
            clusters = kmeans.fit_predict(df_scaled)
            
            # Réduire la dimensionnalité pour la visualisation
            pca = PCA(n_components=2)
            components = pca.fit_transform(df_scaled)
            
            # Créer le DataFrame pour la visualisation
            viz_df = pd.DataFrame({
                'PC1': components[:, 0],
                'PC2': components[:, 1],
                'Cluster': [f"Cluster {i+1}" for i in clusters]
            })
            
            # Définir une palette de couleurs distinctes
            colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33'][:n_clusters]
            
            # Créer le scatter plot
            scatter_fig = px.scatter(
                viz_df,
                x='PC1',
                y='PC2',
                color='Cluster',
                color_discrete_sequence=colors,
                title='Analyse par Clustering'
            )
            
            scatter_fig.update_layout(
                template='plotly_white',
                margin=dict(l=0, r=0, t=30, b=0),
                showlegend=True,
                legend_title_text='',
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=0.99
                )
            )
            
            # Analyser les caractéristiques des clusters
            df['Cluster'] = clusters
            cluster_characteristics = []
            
            for i in range(n_clusters):
                cluster_df = df[df['Cluster'] == i]
                stats = [
                    html.H6(f"Cluster {i+1}", style={'color': colors[i]}),
                    html.P([
                        f"Taille: {len(cluster_df)} donneurs",
                        html.Br(),
                        f"Âge moyen: {cluster_df['age'].mean():.1f} ans",
                        html.Br(),
                        f"Genre principal: {cluster_df['genre'].mode().iloc[0]}",
                        html.Br(),
                        f"Niveau d'études: {cluster_df['niveau_d_etude'].mode().iloc[0]}",
                        html.Br(),
                        f"Éligibilité: {(cluster_df['eligibilite_au_don'] == 'eligible').mean():.1%}"
                    ])
                ]
                cluster_characteristics.extend(stats)
            
            # Créer le tableau d'interprétation
            interpretation_table = create_profile_interpretation(df, clusters)
            
            return scatter_fig, html.Div(cluster_characteristics), interpretation_table
            
        except Exception as e:
            print(f"Erreur dans update_clustering: {str(e)}")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Erreur lors du clustering",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return empty_fig, html.Div("Erreur lors de l'analyse des clusters"), html.Div("Erreur lors de l'interprétation des profils")
    
    # Callback pour les graphiques de distribution
    @app.callback(
        [Output('age-distribution', 'figure'),
         Output('religion-distribution', 'figure'),
         Output('eligibility-distribution', 'figure'),
         Output('education-distribution', 'figure'),
         Output('marital-distribution', 'figure'),
         Output('gender-distribution', 'figure')],
        [Input('location-filter', 'value'),
         Input('eligibility-filter', 'value')]
    )
    def update_graphs(location, eligibility):
        df = load_data()
        
        try:
            # Appliquer les filtres
            if location:
                df = df[df['arrondissement_de_residence'] == location]
            if eligibility:
                df = df[df['eligibilite_au_don'] == eligibility]
            
            # Distribution par âge
            age_fig = px.histogram(
                df,
                x='age',
                nbins=20,
                title='Distribution par âge',
                color_discrete_sequence=[COLORS[0]]  # Rouge
            )
            
            # Distribution par religion
            religion_counts = df['religion'].value_counts().reset_index()
            religion_counts.columns = ['Religion', 'Nombre']
            religion_fig = px.bar(
                religion_counts,
                x='Religion',
                y='Nombre',
                title='Répartition par religion',
                color_discrete_sequence=[COLORS[1]]  # Noir
            )
            
            # Distribution par éligibilité
            eligibility_counts = df['eligibilite_au_don'].value_counts().reset_index()
            eligibility_counts.columns = ['Statut', 'Nombre']
            eligibility_fig = px.bar(
                eligibility_counts,
                x='Statut',
                y='Nombre',
                title="Répartition par éligibilité",
                color_discrete_sequence=[COLORS[2]]  # Bleu sombre
            )
            
            # Distribution par niveau d'étude
            education_counts = df['niveau_d_etude'].value_counts().reset_index()
            education_counts.columns = ['Niveau', 'Nombre']
            education_fig = px.bar(
                education_counts,
                x='Niveau',
                y='Nombre',
                title="Répartition par niveau d'étude",
                color_discrete_sequence=[COLORS[0]]  # Rouge
            )
            
            # Distribution par statut matrimonial
            marital_counts = df['situation_matrimoniale_(sm)'].value_counts().reset_index()
            marital_counts.columns = ['Statut', 'Nombre']
            marital_fig = px.bar(
                marital_counts,
                x='Statut',
                y='Nombre',
                title='Répartition par statut matrimonial',
                color_discrete_sequence=[COLORS[1]]  # Noir
            )
            
            # Distribution par genre (pie chart)
            gender_counts = df['genre'].value_counts().reset_index()
            gender_counts.columns = ['Genre', 'Nombre']
            gender_fig = px.pie(
                gender_counts,
                names='Genre',
                values='Nombre',
                title='Répartition par genre',
                color_discrete_sequence=COLORS  # Utiliser toutes les couleurs
            )
            
            # Mettre à jour le layout de tous les graphiques
            for fig in [age_fig, religion_fig, eligibility_fig, education_fig, marital_fig]:
                fig.update_layout(
                    template='plotly_white',
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=False,
                    xaxis_tickangle=-45
                )
            
            gender_fig.update_layout(
                template='plotly_white',
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            return age_fig, religion_fig, eligibility_fig, education_fig, marital_fig, gender_fig
            
        except Exception as e:
            print(f"Erreur dans update_graphs: {str(e)}")
            # Retourner des graphiques vides en cas d'erreur
            empty_figs = []
            for _ in range(6):
                fig = go.Figure()
                fig.add_annotation(
                    text="Erreur lors du chargement des données",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
                empty_figs.append(fig)
            return tuple(empty_figs)
    
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
