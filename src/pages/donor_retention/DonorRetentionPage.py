import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, date
import os
from ...services.data.DataService import DataService

class DonorRetentionPage:
    def __init__(self):
        self.data_service = DataService()

    def init_callbacks(self, app):
        @app.callback(
            [
                Output('retention-stats', 'children'),
                Output('retention-trend', 'figure'),
                Output('donor-frequency', 'figure'),
                Output('retention-by-age', 'figure'),
                Output('age-stack-figure', 'figure'),
                Output('religion-stack-figure', 'figure'),
                Output('profession-stack-figure', 'figure'),
                Output('genre-stack-figure', 'figure'),
            ],
            [
                Input('retention-date-range', 'start_date'),
                Input('retention-date-range', 'end_date'),
                Input('retention-location-filter', 'value')
            ]
        )

        def update_retention_analysis(start_date, end_date, location):
            try:
                # Charger les données
                df = self.data_service.get_donor_data()
                df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
                df['si_oui_preciser_la_date_du_dernier_don'] = pd.to_datetime(df['si_oui_preciser_la_date_du_dernier_don'])
                successful_donations = len(df[df['eligibilite_au_don'] == 'eligible'])
                
                # Appliquer les filtres
                mask = pd.Series(True, index=df.index)
                
                if start_date:
                    mask &= df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()
                if end_date:
                    mask &= df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()
                if location and location != 'all':
                    mask &= df['ville'].str.contains(location, case=False, na=False)
                
                df = df[mask]
                
                if len(df) == 0:
                    raise ValueError("Aucune donnée ne correspond aux filtres sélectionnés")
                
                # 1. Statistiques de rétention
                total_donors = len(df)
                returning_donors = (df['a_t_il_elle_deja_donne_le_sang'] == 'oui').sum()
                # retention_rate = (returning_donors / total_donors * 100) if total_donors > 0 else 0
                
                """stats = html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.H4("Donneurs totaux", className="h6"),
                            html.P(f"{total_donors:,}", className="h3 text-primary")
                        ], width=4),
                        dbc.Col([
                            html.H4("Donneurs réguliers", className="h6"),
                            html.P(f"{returning_donors:,}", className="h3 text-success")
                        ], width=4),
                        dbc.Col([
                            html.H4("Taux de rétention", className="h6"),
                            html.P(f"{retention_rate:.1f}%", className="h3 text-info")
                        ], width=4)
                    ])
                ])"""
                stats =html.Div([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    html.Div([
                                        html.Span(className="stat-icon-bg"),
                                        html.I(className="fas fa-users stat-icon")
                                    ], className="stat-icon-wrapper"),
                                    html.H3(
                                        children=f"{total_donors:,}", 
                                        className="stat-value"),
                                    html.P("Participants", className="stat-label"),
                                    html.Small("Total participants", className="stat-detail")
                                ], className="stat-card")
                            ], xs=12, sm=6, md=4, lg=4, className="mb-3"),

                            dbc.Col([
                                dbc.Card([
                                    html.Div([
                                        html.Span(className="stat-icon-bg success"),
                                        html.I(className="fas fa-check-circle stat-icon")
                                    ], className="stat-icon-wrapper"),
                                    html.H3(
                                        children=f"{(successful_donations/total_donors*100):.1f}%", 
                                        className="stat-value text-success"),
                                    html.P("Participants Éligibles", className="stat-label"),
                                    html.Small(f"{successful_donations} Participants Éligibles", className="stat-detail")
                                ], className="stat-card")
                            ], xs=12, sm=6, md=4, lg=4, className="mb-3"),

                            dbc.Col([
                                dbc.Card([
                                    html.Div([
                                        html.Span(className="stat-icon-bg success"),
                                        html.I(className="fas fa-star stat-icon")
                                    ], className="stat-icon-wrapper"),
                                    html.H3(
                                        children=f"{(returning_donors / total_donors * 100):.1f}%", 
                                        className="stat-value text-info"),
                                    html.P("Participants Fidèles", className="stat-label"),
                                    html.Small(f"{returning_donors} Participants Fidèles", className="stat-detail")
                                ], className="stat-card")
                            ], xs=12, sm=6, md=4, lg=4, className="mb-3")

                        ], className="mb-4"),
            
                ])
                # 2. Tendance de rétention
                monthly_stats = df.groupby(pd.Grouper(key='date_de_remplissage', freq='M')).agg({
                    'a_t_il_elle_deja_donne_le_sang': lambda x: (x == 'oui').mean() * 100
                }).reset_index()
                
                trend_fig = px.line(
                    monthly_stats,
                    x='date_de_remplissage',
                    y='a_t_il_elle_deja_donne_le_sang',
                    title="Évolution par date de derniers dons",
                    labels={
                        'date_de_remplissage': 'Période',
                        'a_t_il_elle_deja_donne_le_sang': 'Taux de rétention (%)'
                    }
                )
                trend_fig.update_layout(
                    showlegend=False,
                    xaxis_title="Période",
                    yaxis_title="Taux de rétention (%)",
                    height=400,
                    template='plotly_white'
                )
                
                # 3. Fréquence des dons
                freq_ranges = [
                    (0, 90, '1-3 mois'),
                    (91, 180, '3-6 mois'),
                    (181, 365, '6-12 mois'),
                    (366, float('inf'), '> 12 mois')
                ]
                
                donor_frequency = df[df['a_t_il_elle_deja_donne_le_sang'] == 'oui'].copy()
                donor_frequency['temps_depuis_dernier_don'] = (
                    donor_frequency['date_de_remplissage'] - 
                    donor_frequency['si_oui_preciser_la_date_du_dernier_don']
                ).dt.days
                
                donor_frequency['frequence'] = 'Non spécifié'
                for start, end, label in freq_ranges:
                    mask = (donor_frequency['temps_depuis_dernier_don'] >= start) & (donor_frequency['temps_depuis_dernier_don'] <= end)
                    donor_frequency.loc[mask, 'frequence'] = label
                
                freq_stats = donor_frequency['frequence'].value_counts().reset_index()
                freq_stats.columns = ['Intervalle', 'Nombre']
                
                freq_fig = px.bar(
                    freq_stats,
                    x='Intervalle',
                    y='Nombre',
                    title="Fréquence des dons",
                    color='Nombre',
                    color_continuous_scale=['#0d2c54', '#dc3545']
                )
                freq_fig.update_layout(
                    showlegend=False,
                    xaxis_title="Intervalle entre les dons",
                    yaxis_title="Nombre de donneurs",
                    height=400,
                    template='plotly_white'
                )
                
                # 4. Rétention par âge
                age_bins = [0, 25, 35, 45, 55, float('inf')]
                age_labels = ['18-25', '26-35', '36-45', '46-55', '56+']
                
                df['age'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)
                age_retention = df.groupby('age').agg({
                    'a_t_il_elle_deja_donne_le_sang': lambda x: (x == 'oui').mean() * 100
                }).reset_index()
                
                age_retention.columns = ['Tranche d\'âge', 'Taux de rétention']
                
                age_fig = px.bar(
                    age_retention,
                    x='Tranche d\'âge',
                    y='Taux de rétention',
                    title="Taux de rétention par âge",
                    color='Taux de rétention',
                    color_continuous_scale=['#0d2c54', '#dc3545']
                )
                age_fig.update_layout(
                    showlegend=False,
                    xaxis_title="Tranche d'âge",
                    yaxis_title="Taux de rétention (%)",
                    height=400,
                    template='plotly_white'
                )
                
                # 5. Rétention par zone
                # location_retention = df.groupby('arrondissement_de_residence').agg({
                #     'a_t_il_elle_deja_donne_le_sang': lambda x: (x == 'oui').mean() * 100
                # }).reset_index()
                
                # location_retention.columns = ['Zone', 'Taux de rétention']
                # location_retention = location_retention.sort_values('Taux de rétention', ascending=True)
                # location_retention = location_retention[~location_retention['Zone'].str.contains('pas précisé', case=False, na=False)]
                
                # location_fig = px.bar(
                #     location_retention,
                #     x='Taux de rétention',
                #     y='Zone',
                #     orientation='h',
                #     title="Taux de rétention par zone",
                #     color='Taux de rétention',
                #     color_continuous_scale=['#0d2c54', '#dc3545']
                # )
                # location_fig.update_layout(
                #     showlegend=False,
                #     xaxis_title="Taux de rétention (%)",
                #     yaxis_title="Zone géographique",
                #     height=400,
                #     template='plotly_white'
                # )

                # 6. Diagramme empilé par catégorie "a t'il déjà fait un don de sang" par âge
                age_donation = df.groupby(['age', 'a_t_il_elle_deja_donne_le_sang']).size().reset_index(name='nombre')
                age_stack_fig = px.bar(
                    age_donation,
                    x='age',
                    y='nombre',
                    color='a_t_il_elle_deja_donne_le_sang',
                    title="Donneurs par tranche d'âge et historique de dons",
                    labels={'nombre': 'Nombre de donneurs', 'age': "Tranche d'âge", 'a_t_il_elle_deja_donne_le_sang': 'A déjà donné'},
                    barmode='stack',
                    template='plotly_white',
                    color_discrete_map={
                        'non': '#0d2c54',
                        'oui': '#dc3545'
                    }
                )
                age_stack_fig.update_layout(height=400)

                # 7. Diagramme empilé par catégorie religion
                religion_donation = df.groupby(['religion', 'a_t_il_elle_deja_donne_le_sang']).size().reset_index(name='nombre')
                religion_stack_fig = px.bar(
                    religion_donation,
                    x='religion',
                    y='nombre',
                    color='a_t_il_elle_deja_donne_le_sang',
                    title="Donneurs par religion et historique de dons",
                    labels={'nombre': 'Nombre de donneurs', 'religion': 'Religion', 'a_t_il_elle_deja_donne_le_sang': 'A déjà donné'},
                    barmode='stack',
                    template='plotly_white',
                    color_discrete_map={
                        'non': '#0d2c54',
                        'oui': '#dc3545'
                    }
                )
                religion_stack_fig.update_layout(height=400)

                # 8. Diagramme empilé par catégorie profession
                profession_donation = df.groupby(['profession', 'a_t_il_elle_deja_donne_le_sang']).size().reset_index(name='nombre')
                profession_stack_fig = px.bar(
                    profession_donation,
                    x='profession',
                    y='nombre',
                    color='a_t_il_elle_deja_donne_le_sang',
                    title="Donneurs par profession et historique de dons",
                    labels={'nombre': 'Nombre de donneurs', 'profession': 'Profession', 'a_t_il_elle_deja_donne_le_sang': 'A déjà donné'},
                    barmode='stack',
                    template='plotly_white',
                    color_discrete_map={
                        'non': '#0d2c54',
                        'oui': '#dc3545'
                    }
                )
                profession_stack_fig.update_layout(height=400)

                # 9. Diagramme empilé par catégorie genre
                genre_donation = df.groupby(['genre', 'a_t_il_elle_deja_donne_le_sang']).size().reset_index(name='nombre')
                genre_stack_fig = px.bar(
                    genre_donation,
                    x='genre',
                    y='nombre',
                    color='a_t_il_elle_deja_donne_le_sang',
                    title="Donneurs par genre et historique de dons",
                    labels={'nombre': 'Nombre de donneurs', 'genre': 'genre', 'a_t_il_elle_deja_donne_le_sang': 'A déjà donné'},
                    barmode='stack',
                    template='plotly_white',
                    color_discrete_map={
                        'non': '#0d2c54',
                        'oui': '#dc3545'
                    }
                )
                genre_stack_fig.update_layout(height=400)
                
                return stats, trend_fig, freq_fig, age_fig, age_stack_fig, religion_stack_fig, profession_stack_fig, genre_stack_fig
                
            except Exception as e:
                print(f"Erreur dans update_retention_analysis: {str(e)}")
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
                    html.Div("Erreur lors du chargement des données"),
                    empty_fig,
                    empty_fig,
                    empty_fig,
                    empty_fig,
                    empty_fig,
                    empty_fig,
                    empty_fig
                )


    def render(self):
        """Rendu de la page d'analyse de la fidélisation des donneurs"""
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Fidélisation des Donneurs", 
                            className="mb-4"),
                    # html.P("Analyse détaillée des tendances de fidélisation des donneurs",
                    #       className="text-muted mb-4")
                ])
            ]),
            
            # Filtres
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Période d'analyse"),
                            dcc.DatePickerRange(
                                id='retention-date-range',
                                start_date=date(2019, 1, 1),
                                end_date=date(2024, 12, 31),
                                display_format='DD/MM/YYYY',
                                className="mb-3"
                            )
                        ], md=6),
                        dbc.Col([
                            html.Label("Zone géographique"),
                            dcc.Dropdown(
                                id='retention-location-filter',
                                options=[
                                    {'label': 'Toutes les zones', 'value': 'all'},
                                    {'label': 'Douala', 'value': 'douala'},
                                    {'label': 'Yaoundé', 'value': 'yaounde'}
                                ],
                                value='all',
                                className="mb-3",
                                clearable=False
                            )
                        ], md=6)
                    ])
                ])
            ], className="mb-4"),
            
            # Statistiques de rétention
            dbc.Row([
                dbc.CardBody([
                    html.Div(id='retention-stats'),
                    dbc.Spinner(color="primary", type="grow", size="sm")
                ])
            ]),
            
            # Graphiques d'analyse
            dbc.Row([
                # Colonne de gauche
                dbc.Col([
                    # Tendance de rétention
                    dbc.Card([
                        dbc.CardHeader("Évolution par date de derniers dons"),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(
                                    id='retention-trend',
                                    config={'displayModeBar': False}
                                ),
                                color="primary",
                                type="grow",
                                size="sm"
                            )
                        ])
                    ], className="mb-4"),

                    # Rétention par âge
                    dbc.Card([
                        dbc.CardHeader("Rétention par tranche d'âge"),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(
                                    id='retention-by-age',
                                    config={'displayModeBar': False}
                                ),
                                color="primary",
                                type="grow",
                                size="sm"
                            )
                        ])
                    ], className="mb-4")

                ], md=6),
                
                # Colonne de droite
                dbc.Col([
                    # Fréquence des dons
                    dbc.Card([
                        dbc.CardHeader("Fréquence des dons"),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(
                                    id='donor-frequency',
                                    config={'displayModeBar': False}
                                ),
                                color="primary",
                                type="grow",
                                size="sm"
                            )
                        ])
                    ]),

                    dbc.Card([
                        dbc.CardHeader("Historique de dons par âge"),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(id='age-stack-figure', config={'displayModeBar': False}),
                                color="primary", type="grow", size="sm"
                            )
                        ])
                    ], className="mb-4")
                    
                    # Rétention par zone
                    # dbc.Card([
                    #     dbc.CardHeader("Rétention par zone géographique"),
                    #     dbc.CardBody([
                    #         dbc.Spinner(
                    #             dcc.Graph(
                    #                 id='retention-by-location',
                    #                 config={'displayModeBar': False}
                    #             ),
                    #             color="primary",
                    #             type="grow",
                    #             size="sm"
                    #         )
                    #     ])
                    # ])
                ], md=6),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Historique de dons par genre"),
                            dbc.CardBody([
                                dbc.Spinner(
                                    dcc.Graph(id='genre-stack-figure', config={'displayModeBar': False}),
                                    color="primary", type="grow", size="sm"
                                )
                            ]),
                        dbc.Card([
                            dbc.CardHeader("Historique de dons par profession"),
                            dbc.CardBody([
                                dbc.Spinner(
                                    dcc.Graph(id='profession-stack-figure', config={'displayModeBar': False}),
                                    color="primary", type="grow", size="sm"
                                )
                            ])
                        ], className="mb-4")
                        ], className="mb-4"),
                    ], md=6),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Historique de dons par religion"),
                            dbc.CardBody([
                                dbc.Spinner(
                                    dcc.Graph(id='religion-stack-figure', config={'displayModeBar': False}),
                                    color="primary", type="grow", size="sm"
                                )
                            ])
                        ], className="mb-4")
                    ], md=6)
                ])
            ])
        ], fluid=True, className="retention-container")