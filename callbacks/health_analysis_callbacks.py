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
            
            # Définir les colonnes pour chaque catégorie
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
                        html.H4("Donneurs éligibles", className="h6"),
                        html.P(f"{eligible} ({pct_eligible:.1f}%)", className="h3 text-primary")
                    ], width=4),
                    dbc.Col([
                        html.H4("Temporairement non disponible", className="h6"),
                        html.P(f"{temp_unavailable} ({pct_temp:.1f}%)", className="h3 text-danger")
                    ], width=4),
                    dbc.Col([
                        html.H4("Non éligibles", className="h6"),
                        html.P(f"{non_eligible} ({pct_non:.1f}%)", className="h3 text-warning")
                    ], width=4)
                ])
            ])
            
            # 2. Top problèmes de santé
            health_issues = []
            for col in health_cols:
                count = (df[col] == 'oui').sum()
                if count > 0:
                    issue = col.split('__')[-1].replace('[', '').replace(']', '').replace('_', ' ')
                    health_issues.append({'issue': issue, 'count': count})
            
            health_df = pd.DataFrame(health_issues)
            if not health_df.empty:
                health_df = health_df.sort_values('count', ascending=False)
                
                top_health_fig = px.bar(
                    health_df,
                    x='issue',
                    y='count',
                    title="Principaux problèmes de santé",
                    labels={'issue': 'Problème de santé', 'count': 'Nombre de cas'},
                    color='count',
                    color_continuous_scale=['#8B0000', '#000000']
                )
                top_health_fig.update_layout(
                    showlegend=False,
                    xaxis_tickangle=-45,
                    margin=dict(l=0, r=0, t=40, b=100),
                    height=400
                )
            else:
                top_health_fig = go.Figure()
            
            # 3. Top raisons d'indisponibilité
            unavail_reasons = []
            for col in temp_unavail_cols + raisons_femmes:
                count = (df[col] == 'oui').sum()
                if count > 0:
                    reason = col.split('__')[-1].replace('[', '').replace(']', '').replace('_', ' ')
                    unavail_reasons.append({'reason': reason, 'count': count})
            
            unavail_df = pd.DataFrame(unavail_reasons)
            if not unavail_df.empty:
                unavail_df = unavail_df.sort_values('count', ascending=False)
                
                top_unavail_fig = px.bar(
                    unavail_df,
                    x='reason',
                    y='count',
                    title="Principales raisons d'indisponibilité",
                    labels={'reason': 'Raison', 'count': 'Nombre de cas'},
                    color='count',
                    color_continuous_scale=['#8B0000', '#000000']
                )
                top_unavail_fig.update_layout(
                    showlegend=False,
                    xaxis_tickangle=-45,
                    margin=dict(l=0, r=0, t=40, b=100),
                    height=400
                )
            else:
                top_unavail_fig = go.Figure()
            
            # 4. Graphique d'indisponibilité temporaire
            temp_fig = px.bar(
                unavail_df,
                x='count',
                y='reason',
                orientation='h',
                title="Raisons d'indisponibilité temporaire",
                labels={'reason': 'Raison', 'count': 'Nombre de cas'},
                color='count',
                color_continuous_scale=['#8B0000', '#000000']
            )
            temp_fig.update_layout(
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0),
                height=400
            )
            
            # 5. Analyse géographique
            geo_stats = df.groupby('arrondissement_de_residence').agg({
                'eligibilite_au_don': lambda x: (x != 'eligible').sum(),
                'date_de_remplissage': 'count'
            }).reset_index()
            
            geo_stats.columns = ['arrondissement', 'non_eligible', 'total']
            geo_stats['pourcentage'] = (geo_stats['non_eligible'] / geo_stats['total'] * 100).round(1)
            geo_stats = geo_stats.sort_values('non_eligible', ascending=True)
            
            # Exclure les valeurs non précisées
            geo_stats = geo_stats[~geo_stats['arrondissement'].str.contains('pas précisé', case=False, na=False)]
            
            geo_fig = px.bar(
                geo_stats,
                x='non_eligible',
                y='arrondissement',
                orientation='h',
                title="Cas d'inéligibilité par zone",
                text=geo_stats['pourcentage'].apply(lambda x: f'{x}%'),
                color='non_eligible',
                color_continuous_scale=['#8B0000', '#000000']
            )
            geo_fig.update_layout(
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0),
                height=400,
                xaxis_title="Nombre de cas",
                yaxis_title="Arrondissement"
            )
            
            # 6. Graphique détaillé des problèmes de santé
            health_fig = px.bar(
                health_df,
                x='count',
                y='issue',
                orientation='h',
                title="Détail des problèmes de santé",
                labels={'issue': 'Problème', 'count': 'Nombre de cas'},
                color='count',
                color_continuous_scale=['#8B0000', '#000000']
            )
            health_fig.update_layout(
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0),
                height=400
            )
            
            # 7. Tableau d'interprétation
            interpretation_table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Catégorie"),
                        html.Th("Observations"),
                        html.Th("Implications")
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td("Éligibilité"),
                        html.Td(f"{pct_eligible:.1f}% de donneurs éligibles"),
                        html.Td("Base de donneurs potentiels")
                    ]),
                    html.Tr([
                        html.Td("Indisponibilité temporaire"),
                        html.Td(f"{pct_temp:.1f}% temporairement indisponibles"),
                        html.Td("Potentiel de retour futur")
                    ]),
                    html.Tr([
                        html.Td("Non éligibilité"),
                        html.Td(f"{pct_non:.1f}% non éligibles"),
                        html.Td("Nécessite un suivi médical")
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
                html.Div("Erreur lors du chargement des statistiques"),
                empty_fig,
                empty_fig,
                empty_fig,
                empty_fig,
                empty_fig,
                html.Div("Erreur lors du chargement du tableau d'interprétation")
            )
