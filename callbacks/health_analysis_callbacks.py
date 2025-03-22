import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html

def init_health_analysis_callbacks(app):
    """Initialise les callbacks pour l'analyse de santé"""
    
    # Charger et prétraiter les données
    df = pd.read_csv('data/processed_data.csv')
    
    # Conversion des dates
    df['Date de remplissage de la fiche'] = pd.to_datetime(df['Date de remplissage de la fiche'])
    df['Date de naissance'] = pd.to_datetime(df['Date de naissance'])
    
    # Convertir l'éligibilité en valeur numérique
    df['eligibilite_num'] = (df['ÉLIGIBILITÉ AU DON.'] == 'OUI').astype(int)
    
    # Identifier les colonnes de conditions médicales
    chronic_conditions = [
        'non_elig_Drepanocytaire',
        'non_elig_Diabétique',
        'non_elig_Hypertendus',
        'non_elig_Asthmatiques',
        'non_elig_Cardiaque'
    ]
    
    temporary_conditions = [
        'indispo_Est sous anti-biothérapie',
        'indispo_Taux d\'hémoglobine bas',
        'indispo_date de dernier Don < 3 mois',
        'indispo_IST récente (Exclu VIH, Hbs, Hcv)'
    ]
    
    risk_factors = [
        'non_elig_Antécédent de transfusion',
        'non_elig_Porteur(HIV,hbs,hcv)',
        'non_elig_Opéré',
        'non_elig_Tatoué',
        'non_elig_Scarifié'
    ]
    
    # Vérifier que toutes les colonnes existent et les nettoyer si nécessaire
    all_conditions = chronic_conditions + temporary_conditions + risk_factors
    existing_columns = [col for col in all_conditions if col in df.columns]
    
    # Mapping pour des noms plus lisibles
    condition_mapping = {
        'non_elig_Drepanocytaire': 'Drépanocytose',
        'non_elig_Diabétique': 'Diabète',
        'non_elig_Hypertendus': 'Hypertension',
        'non_elig_Asthmatiques': 'Asthme',
        'non_elig_Cardiaque': 'Maladie cardiaque',
        'indispo_Est sous anti-biothérapie': 'Sous antibiotiques',
        'indispo_Taux d\'hémoglobine bas': 'Hémoglobine basse',
        'indispo_date de dernier Don < 3 mois': 'Don récent',
        'indispo_IST récente (Exclu VIH, Hbs, Hcv)': 'IST récente',
        'non_elig_Antécédent de transfusion': 'Antécédent transfusion',
        'non_elig_Porteur(HIV,hbs,hcv)': 'Porteur HIV/HBS/HCV',
        'non_elig_Opéré': 'Chirurgie récente',
        'non_elig_Tatoué': 'Tatouage récent',
        'non_elig_Scarifié': 'Scarification'
    }
    
    # Nettoyer le mapping pour ne garder que les colonnes existantes
    condition_mapping = {k: v for k, v in condition_mapping.items() if k in df.columns}
    
    @app.callback(
        [Output('health-total-donneurs', 'children'),
         Output('health-taux-eligibilite', 'children'),
         Output('health-conditions-frequentes', 'children'),
         Output('health-taux-indisponibilite', 'children'),
         Output('health-conditions-distribution', 'figure'),
         Output('health-eligibility-impact', 'figure'),
         Output('health-condition-correlation', 'figure'),
         Output('health-demographic-patterns', 'figure'),
         Output('health-temporal-trends', 'figure'),
         Output('health-risk-factors-heatmap', 'figure'),
         Output('health-eligibility-prediction', 'figure'),
         Output('health-key-statistics', 'children'),
         Output('health-medical-recommendations', 'children')],
        [Input('health-demographic-dropdown', 'value'),
         Input('health-condition-type-dropdown', 'value')]
    )
    def update_health_analysis(demographic, condition_type):
        # Sélectionner les conditions en fonction du type et qui existent dans le DataFrame
        if condition_type == 'chronic':
            conditions = [col for col in chronic_conditions if col in df.columns]
        elif condition_type == 'temporary':
            conditions = [col for col in temporary_conditions if col in df.columns]
        elif condition_type == 'risk':
            conditions = [col for col in risk_factors if col in df.columns]
        else:
            conditions = existing_columns
        
        if not conditions:  # Si aucune condition n'est disponible
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="Aucune donnée disponible pour cette sélection",
                annotations=[{"text": "Pas de données", "showarrow": False, "font": {"size": 28}}]
            )
            return "0", "0%", "0", "0%", empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "", ""
        
        # 1. Calculer les KPIs
        total_donneurs = len(df)
        taux_eligibilite = (df['ÉLIGIBILITÉ AU DON.'] == 'OUI').mean() * 100
        
        # Compter les conditions les plus fréquentes
        condition_counts = df[conditions].sum()
        conditions_frequentes = condition_counts.max()
        
        # Calculer le taux d'indisponibilité
        indispo_columns = [col for col in df.columns if col.startswith('indispo_')]
        taux_indisponibilite = (df[indispo_columns].any(axis=1)).mean() * 100
        
        # 2. Distribution des conditions médicales
        condition_data = pd.DataFrame({
            'Condition': [condition_mapping[col] for col in conditions],
            'Nombre': df[conditions].sum()
        }).sort_values('Nombre', ascending=True)
        
        distribution_fig = px.bar(condition_data,
                                x='Nombre',
                                y='Condition',
                                orientation='h',
                                title='Distribution des conditions médicales',
                                template='plotly_white')
        
        # 3. Impact sur l'éligibilité
        impact_data = []
        for condition in conditions:
            impact = pd.DataFrame({
                'Condition': condition_mapping[condition],
                'Statut': ['Avec condition', 'Sans condition'],
                'Taux_Eligibilite': [
                    (df[df[condition] == 1]['eligibilite_num']).mean() * 100,
                    (df[df[condition] == 0]['eligibilite_num']).mean() * 100
                ]
            })
            impact_data.append(impact)
        
        impact_data = pd.concat(impact_data)
        impact_fig = px.bar(impact_data,
                          x='Condition',
                          y='Taux_Eligibilite',
                          color='Statut',
                          barmode='group',
                          title="Impact des conditions sur l'éligibilité",
                          template='plotly_white')
        
        # 4. Corrélation entre conditions
        corr_matrix = df[conditions].corr()
        correlation_fig = px.imshow(corr_matrix,
                                  labels=dict(x='Condition', y='Condition'),
                                  x=[condition_mapping[col] for col in conditions],
                                  y=[condition_mapping[col] for col in conditions],
                                  title='Corrélation entre conditions médicales',
                                  color_continuous_scale='RdBu',
                                  template='plotly_white')
        
        # 5. Patterns démographiques
        if demographic == 'age':
            df['Age'] = pd.to_datetime('now').year - df['Date de naissance'].dt.year
            df['Groupe_Age'] = pd.cut(df['Age'], 
                                    bins=[0, 25, 35, 45, 55, 100],
                                    labels=['18-25', '26-35', '36-45', '46-55', '55+'])
            group_col = 'Groupe_Age'
        elif demographic == 'genre':
            group_col = 'Genre'
        elif demographic == 'profession':
            group_col = 'Profession'
        else:
            group_col = 'Arrondissement de résidence'
        
        pattern_data = []
        for condition in conditions:
            pattern = df.groupby(group_col)[condition].mean() * 100
            pattern_data.append(pd.DataFrame({
                'Groupe': pattern.index,
                'Condition': condition_mapping[condition],
                'Pourcentage': pattern.values
            }))
        
        pattern_data = pd.concat(pattern_data)
        patterns_fig = px.line(pattern_data,
                             x='Groupe',
                             y='Pourcentage',
                             color='Condition',
                             title=f'Patterns par {group_col}',
                             template='plotly_white')
        
        # 6. Tendances temporelles
        temporal_data = []
        for condition in conditions:
            temporal = df.groupby(pd.Grouper(key='Date de remplissage de la fiche', freq='M'))[condition].mean() * 100
            temporal_data.append(pd.DataFrame({
                'Date': temporal.index,
                'Condition': condition_mapping[condition],
                'Pourcentage': temporal.values
            }))
        
        temporal_data = pd.concat(temporal_data)
        temporal_fig = px.line(temporal_data,
                             x='Date',
                             y='Pourcentage',
                             color='Condition',
                             title='Évolution temporelle des conditions',
                             template='plotly_white')
        
        # 7. Heatmap des facteurs de risque
        risk_cols = [col for col in risk_factors if col in df.columns]
        if risk_cols:
            df_risk = df[risk_cols + ['eligibilite_num']].copy()
            risk_matrix = df_risk.corr()
            risk_fig = px.imshow(risk_matrix,
                               title='Corrélation avec les facteurs de risque',
                               color_continuous_scale='RdBu',
                               template='plotly_white')
        else:
            risk_fig = go.Figure()
            risk_fig.update_layout(
                title="Pas de facteurs de risque disponibles",
                annotations=[{"text": "Pas de données", "showarrow": False, "font": {"size": 28}}]
            )
        
        # 8. Prédiction d'éligibilité
        prediction_data = pd.DataFrame({
            'Condition': [condition_mapping[col] for col in conditions],
            'Impact': df.groupby(df[conditions].any(axis=1))['eligibilite_num'].mean().diff().iloc[-1] * 100
        }).sort_values('Impact')
        
        prediction_fig = px.bar(prediction_data,
                              x='Condition',
                              y='Impact',
                              title="Impact sur la probabilité d'éligibilité",
                              template='plotly_white')
        
        # 9. Statistiques clés
        stats_cards = []
        for condition_type, condition_list in [
            ('Maladies chroniques', [col for col in chronic_conditions if col in df.columns]),
            ('Conditions temporaires', [col for col in temporary_conditions if col in df.columns]),
            ('Facteurs de risque', [col for col in risk_factors if col in df.columns])
        ]:
            if condition_list:
                prevalence = (df[condition_list].any(axis=1)).mean() * 100
                impact = (df[df[condition_list].any(axis=1)]['eligibilite_num']).mean() * 100
                
                stats_cards.append(
                    dbc.Card([
                        dbc.CardHeader(condition_type),
                        dbc.CardBody([
                            html.P([
                                html.Strong("Prévalence: "), f"{prevalence:.1f}%"
                            ], className="mb-2"),
                            html.P([
                                html.Strong("Taux d'éligibilité: "), f"{impact:.1f}%"
                            ], className="mb-0")
                        ])
                    ], className="mb-3")
                )
        
        key_statistics = dbc.Row([dbc.Col(card, width=4) for card in stats_cards])
        
        # 10. Recommandations médicales
        high_impact_conditions = prediction_data.nlargest(3, 'Impact')
        recommendations = dbc.Row([
            dbc.Col([
                html.H5("Recommandations pour l'amélioration de l'éligibilité", className="mb-3"),
                html.Ul([
                    html.Li([
                        html.Strong("Conditions prioritaires : "),
                        "Focus sur le dépistage et la gestion de " + 
                        ", ".join(high_impact_conditions['Condition'].tolist())
                    ], className="mb-2"),
                    html.Li([
                        html.Strong("Groupe à risque : "),
                        f"Les {group_col}s montrant la plus haute prévalence de conditions médicales"
                    ], className="mb-2"),
                    html.Li([
                        html.Strong("Tendance : "),
                        f"Le taux d'éligibilité global est de {taux_eligibilite:.1f}%"
                    ], className="mb-2"),
                    html.Li([
                        html.Strong("Actions recommandées : "),
                        html.Ul([
                            html.Li("Renforcer le dépistage précoce des conditions chroniques"),
                            html.Li("Mettre en place un suivi personnalisé pour les donneurs à risque"),
                            html.Li("Développer des programmes de sensibilisation ciblés")
                        ], className="mt-2")
                    ])
                ])
            ])
        ])
        
        return (
            f"{total_donneurs:,}",
            f"{taux_eligibilite:.1f}%",
            f"{conditions_frequentes:,}",
            f"{taux_indisponibilite:.1f}%",
            distribution_fig,
            impact_fig,
            correlation_fig,
            patterns_fig,
            temporal_fig,
            risk_fig,
            prediction_fig,
            key_statistics,
            recommendations
        )
