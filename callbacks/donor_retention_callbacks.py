from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def init_donor_retention_callbacks(app):
    """Initialise les callbacks pour l'analyse de la fidélisation des donneurs"""
    
    def load_data():
        """Charge et prépare les données"""
        df = pd.read_csv('data/processed_data.csv')
        df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
        df['date_de_naissance'] = pd.to_datetime(df['date_de_naissance'])
        df['age'] = pd.to_datetime('now').year - df['date_de_naissance'].dt.year
        
        # Convertir la date du dernier don en datetime avec gestion des erreurs
        df['si_oui_preciser_la_date_du_dernier_don'] = pd.to_datetime(
            df['si_oui_preciser_la_date_du_dernier_don'], 
            format='mixed',
            errors='coerce'
        )
        return df
    
    @app.callback(
        [Output('total-previous-donors', 'children'),
         Output('avg-donations', 'children'),
         Output('retention-rate', 'children')],
        [Input('url', 'pathname')]
    )
    def update_retention_stats(_):
        try:
            df = load_data()
            
            # Filtrer les donneurs avec historique
            previous_donors = df[df['a_t_il_elle_deja_donne_le_sang'] == 'Oui']
            
            # Calculer les statistiques
            total_donors = len(previous_donors)
            avg_donations = 1.0  # Par défaut, on suppose 1 don par donneur
            retention_rate = (total_donors / len(df)) * 100 if len(df) > 0 else 0
            
            return (
                f"{total_donors:,}",
                f"{avg_donations:.1f} dons",
                f"{retention_rate:.1f}%"
            )
        except Exception as e:
            print(f"Erreur dans update_retention_stats: {str(e)}")
            return "N/A", "N/A", "N/A"
    
    @app.callback(
        Output('retention-timeline', 'figure'),
        [Input('url', 'pathname')]
    )
    def update_retention_timeline(_):
        try:
            df = load_data()
            
            # Calculer l'évolution temporelle des dons
            timeline_stats = df.groupby(
                pd.Grouper(key='date_de_remplissage', freq='M')
            ).agg({
                'a_t_il_elle_deja_donne_le_sang': lambda x: (x == 'Oui').sum()
            }).reset_index()
            
            timeline_stats.columns = ['Date', 'Nombre de donneurs']
            
            fig = go.Figure()
            
            # Ajouter la ligne pour le nombre de donneurs
            fig.add_trace(go.Scatter(
                x=timeline_stats['Date'],
                y=timeline_stats['Nombre de donneurs'],
                name='Nombre de donneurs',
                line=dict(color='#0d2c54', width=2),
                mode='lines'
            ))
            
            fig.update_layout(
                title='Évolution de la fidélisation dans le temps',
                xaxis_title='Date',
                yaxis_title='Nombre de donneurs',
                template='plotly_white',
                hovermode='x unified'
            )
            
            return fig
        except Exception as e:
            print(f"Erreur dans update_retention_timeline: {str(e)}")
            # Retourner un graphique vide avec message d'erreur
            fig = go.Figure()
            fig.add_annotation(
                text="Erreur lors du chargement des données",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return fig

    @app.callback(
        [Output('age-gender-retention', 'figure'),
         Output('education-gender-retention', 'figure'),
         Output('location-gender-retention', 'figure'),
         Output('marital-gender-retention', 'figure')],
        [Input('url', 'pathname')]
    )
    def update_characteristic_analysis(_):
        try:
            df = load_data()
            
            def create_cross_analysis(data, char_col, title):
                # Calculer le nombre de donneurs par caractéristique et genre
                cross_stats = pd.crosstab(
                    [data[char_col], data['genre']],
                    data['a_t_il_elle_deja_donne_le_sang']
                ).reset_index()
                
                # Calculer les pourcentages
                total = cross_stats['Oui'] + cross_stats['Non']
                cross_stats['Pourcentage'] = (cross_stats['Oui'] / total * 100).round(1)
                
                fig = px.bar(
                    cross_stats,
                    x=char_col,
                    y='Pourcentage',
                    color='genre',
                    title=title,
                    barmode='group',
                    color_discrete_map={
                        'Homme': '#0d2c54',
                        'Femme': '#dc3545'
                    }
                )
                
                fig.update_layout(
                    xaxis_title=char_col.replace('_', ' ').title(),
                    yaxis_title='Pourcentage de donneurs (%)',
                    template='plotly_white'
                )
                
                return fig
            
            # Créer les différentes analyses croisées
            age_gender_fig = create_cross_analysis(
                df,
                'age',
                'Donneurs par âge et genre'
            )
            
            education_gender_fig = create_cross_analysis(
                df,
                'niveau_d_etude',
                "Donneurs par niveau d'études et genre"
            )
            
            location_gender_fig = create_cross_analysis(
                df,
                'arrondissement_de_residence',
                'Donneurs par arrondissement et genre'
            )
            
            marital_gender_fig = create_cross_analysis(
                df,
                'situation_matrimoniale_(sm)',
                'Donneurs par situation matrimoniale et genre'
            )
            
            return age_gender_fig, education_gender_fig, location_gender_fig, marital_gender_fig
        except Exception as e:
            print(f"Erreur dans update_characteristic_analysis: {str(e)}")
            # Retourner des graphiques vides avec message d'erreur
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Erreur lors du chargement des données",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return empty_fig, empty_fig, empty_fig, empty_fig
