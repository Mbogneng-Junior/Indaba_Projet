from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc

def init_health_analysis_callbacks(app):
    """Initialise les callbacks pour la page d'analyse de santé"""
    
    def load_data():
        """Charge et prépare les données"""
        df = pd.read_csv('data/processed_data.csv')
        df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
        return df
    
    @app.callback(
        Output('health-location-filter', 'options'),
        Input('health-location-filter', 'search_value')
    )
    def update_location_options(search):
        df = load_data()
        locations = sorted(df['arrondissement_de_residence'].unique())
        return [{'label': loc, 'value': loc} for loc in locations]
    
    @app.callback(
        [Output('detailed-stats', 'children'),
         Output('top-health-issues', 'figure'),
         Output('top-unavailability-reasons', 'figure'),
         Output('temporary-unavailability-chart', 'figure'),
         Output('geographic-health-analysis', 'figure'),
         Output('health-issues-chart', 'figure'),
         Output('health-interpretation-table', 'children')],
        [Input('health-location-filter', 'value'),
         Input('health-date-range', 'start_date'),
         Input('health-date-range', 'end_date')]
    )
    def update_health_analysis(location, start_date, end_date):
        try:
            df = load_data()
            
            # Définir toutes les colonnes nécessaires au début
            health_cols = [col for col in df.columns if 'raison_de_non-eligibilité_totale__' in col]
            temp_unavail_cols = [col for col in df.columns if 'raison_indisponibilité__' in col]
            raisons_femmes = [col for col in df.columns if "raison_de_l'indisponibilité_de_la_femme_" in col]
            
            # Appliquer les filtres
            if location:
                df = df[df['arrondissement_de_residence'] == location]
            if start_date:
                df = df[df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()]
            if end_date:
                df = df[df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()]
            
            # Palette de couleurs
            color_scale = ['#8B0000', '#000000']
            
            # 1. Statistiques détaillées
            total = len(df)
            eligible = (df['eligibilite_au_don'] == 'eligible').sum()
            temp_unavailable = df[temp_unavail_cols + raisons_femmes].eq('oui').any(axis=1).sum()
            non_eligible = df[health_cols].eq('oui').any(axis=1).sum()
            
            # Calculer les pourcentages
            pct_eligible = (eligible / total) * 100 if total > 0 else 0
            pct_temp = (temp_unavailable / total) * 100 if total > 0 else 0
            pct_non = (non_eligible / total) * 100 if total > 0 else 0
            
            detailed_stats = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H4("Donneurs éligible", className="h6"),
                        html.P(f"{str(eligible)} ({pct_eligible:.1f}%)", className="h3 text-primary")
                    ], width=4),
                    dbc.Col([
                        html.H4("temporairement non disponible", className="h6"),
                        html.P(f"{str(temp_unavailable)} ({pct_temp:.1f}%)", className="h3 text-danger")
                    ], width=4),
                    dbc.Col([
                        html.H4("Non eligible", className="h6"),
                        html.P(f"{str(non_eligible)} ({pct_non:.1f}%)", className="h3 text-warning")
                    ], width=4)
                ])
            ])
            
            # Le reste du code reste identique...
            
            # 2. Top 3 des problèmes de santé
            health_issues = []
            for col in health_cols:
                count = df[col].map({'oui': 1, 'non': 0}).sum()
                if count > 0:
                    issue = col.split('__')[-1].replace('[', '').replace(']', '').replace('_', ' ')
                    health_issues.append({'issue': issue, 'count': count})
            
            health_issues = sorted(health_issues, key=lambda x: x['count'], reverse=True)[:3]
            health_df = pd.DataFrame(health_issues)
            
            top_health_fig = px.bar(
                health_df,
                x='issue',
                y='count',
                title="Top 3 des problèmes de santé",
                color='count',
                color_continuous_scale=color_scale
            )
            top_health_fig.update_layout(
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=100),
                xaxis_title="",
                yaxis_title="Nombre de cas",
                coloraxis_showscale=False,
                xaxis_tickangle=-45,
                height=400
            )
            
            # 3. Top 3 des raisons d'indisponibilité
            unavail_reasons = []
            for col in temp_unavail_cols:
                count = df[col].map({'oui': 1, 'non': 0}).sum()
                if count > 0:
                    reason = col.split('__')[-1].replace('[', '').replace(']', '').replace('_', ' ')
                    unavail_reasons.append({'reason': reason, 'count': count})
            
            unavail_reasons = sorted(unavail_reasons, key=lambda x: x['count'], reverse=True)[:3]
            unavail_df = pd.DataFrame(unavail_reasons)
            
            top_unavail_fig = px.bar(
                unavail_df,
                x='reason',
                y='count',
                title="Top 3 des raisons d'indisponibilité",
                color='count',
                color_continuous_scale=color_scale
            )
            top_unavail_fig.update_layout(
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=100),
                xaxis_title="",
                yaxis_title="Nombre de cas",
                coloraxis_showscale=False,
                xaxis_tickangle=-45,
                height=400
            )
            
            # 4. Raisons d'indisponibilité temporaire
            temp_fig = px.bar(
                unavail_df,
                x='count',
                y='reason',
                orientation='h',
                title="Raisons d'indisponibilité temporaire",
                color='count',
                color_continuous_scale=color_scale
            )
            temp_fig.update_layout(
                template='plotly_white',
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0),
                yaxis_title="",
                xaxis_title="Nombre de cas",
                coloraxis_showscale=False
            )
            
            # 5. Analyse par zone géographique
            geo_health = df.groupby('arrondissement_de_residence').agg({
                'eligibilite_au_don': lambda x: (x == 'ineligible').sum()
            }).reset_index()
            
            # Nettoyer et standardiser les noms d'arrondissements
            geo_health['arrondissement_de_residence'] = geo_health['arrondissement_de_residence'].apply(
                lambda x: x.strip().lower() if isinstance(x, str) else x
            )
            geo_health = geo_health[~geo_health['arrondissement_de_residence'].str.contains('pas précisé', na=False)]
            
            geo_fig = px.bar(
                geo_health,
                x='arrondissement_de_residence',
                y='eligibilite_au_don',
                title="Nombre de cas d'inéligibilité par zone",
                color='eligibilite_au_don',
                color_continuous_scale=color_scale
            )
            geo_fig.update_layout(
                template='plotly_white',
                xaxis_title="Arrondissement",
                yaxis_title="Nombre de cas d'inéligibilité",
                xaxis_tickangle=-45,
                margin=dict(l=0, r=0, t=40, b=100),
                coloraxis_showscale=False,
                height=400
            )
            
            # 6. Graphique des problèmes de santé
            health_fig = px.bar(
                health_df,
                x='count',
                y='issue',
                orientation='h',
                title="Problèmes de santé majeurs",
                color='count',
                color_continuous_scale=color_scale
            )
            health_fig.update_layout(
                template='plotly_white',
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0),
                yaxis_title="",
                xaxis_title="Nombre de cas",
                coloraxis_showscale=False
            )
            
            # 7. Tableau d'interprétation
            interpretation_table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Catégorie"),
                        html.Th("Observations"),
                        html.Th("Implications")
                    ], className="table-dark")
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td("Problèmes de santé majeurs"),
                        html.Td(f"Le problème principal est {health_issues[0]['issue']} avec {health_issues[0]['count']} cas"),
                        html.Td("Nécessite une attention particulière dans le processus de sélection")
                    ]),
                    html.Tr([
                        html.Td("Indisponibilité temporaire"),
                        html.Td(f"Principale raison : {unavail_reasons[0]['reason']} ({unavail_reasons[0]['count']} cas)"),
                        html.Td("Suggère des actions de sensibilisation ciblées")
                    ]),
                    html.Tr([
                        html.Td("Distribution géographique"),
                        html.Td(f"Zones avec taux d'inéligibilité élevé identifiées"),
                        html.Td("Permet de cibler les interventions par zone")
                    ])
                ])
            ], bordered=True, hover=True)
            
            return (
                detailed_stats,
                top_health_fig,
                top_unavail_fig,
                temp_fig,
                geo_fig,
                health_fig,
                interpretation_table
            )
            
        except Exception as e:
            print(f"Erreur dans update_health_analysis: {str(e)}")
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
                "Erreur",
                empty_fig,
                empty_fig,
                empty_fig,
                empty_fig,
                empty_fig,
                "Erreur"
            )
