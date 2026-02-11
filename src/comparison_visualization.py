"""
Module de visualisation comparative entre les tours d'élection
Focalisé sur l'analyse de la performance d'Anne VIGNOT (T1 → T2)
"""
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from plotly.subplots import make_subplots
from src.vignot_analysis import VignotAnalyzer


class TourComparisonVisualizer:
    """Classe pour créer des visualisations comparatives entre deux tours d'élection"""
    
    CANDIDAT_NAME = "Anne VIGNOT"
    
    def __init__(self, data_t1: Tuple, data_t2: Tuple):
        """
        Initialise le visualiseur comparatif
        
        Args:
            data_t1: Tuple (geojson_enriched, df_candidates, geojson_bureaux) pour le tour 1
            data_t2: Tuple (geojson_enriched, df_candidates, geojson_bureaux) pour le tour 2
        """
        self.geojson_t1, self.df_t1, self.geojson_bureaux_t1 = data_t1
        self.geojson_t2, self.df_t2, self.geojson_bureaux_t2 = data_t2
        
        # Créer l'analyseur Anne VIGNOT
        self.vignot_analyzer = VignotAnalyzer(self.df_t1, self.df_t2)
        
        # Extraire les candidats communs (legacy - pour compatibilité)
        self.common_candidates = self._get_common_candidates()
        
        # Calculer le centre de la carte
        self.map_center = self._calculate_map_center()
    
    def _calculate_map_center(self):
        """Calcule le centre de la carte basé sur les géométries du T1"""
        lons = []
        lats = []
        
        for feature in self.geojson_t1['features']:
            coords = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                for ring in coords:
                    for point in ring:
                        lons.append(point[0])
                        lats.append(point[1])
            elif feature['geometry']['type'] == 'MultiPolygon':
                for polygon in coords:
                    for ring in polygon:
                        for point in ring:
                            lons.append(point[0])
                            lats.append(point[1])
        
        return {
            'lat': sum(lats) / len(lats),
            'lon': sum(lons) / len(lons)
        }
    
    def _get_common_candidates(self) -> List[str]:
        """Retourne la liste des candidats présents aux deux tours"""
        candidats_t1 = set(self.df_t1['CANDIDAT'].unique())
        candidats_t2 = set(self.df_t2['CANDIDAT'].unique())
        return sorted(list(candidats_t1 & candidats_t2))
    
    def create_participation_evolution_map(self):
        """
        Crée une carte montrant l'évolution de la participation entre T1 et T2
        
        Returns:
            plotly.graph_objects.Figure
        """
        # Calculer l'évolution de la participation pour chaque bureau
        evolution_data = []
        locations = []
        hover_texts = []
        
        # Créer un dictionnaire des données T1 par bureau
        t1_data = {}
        for feature in self.geojson_t1['features']:
            num_bureau = feature['properties']['NUM_BUREAU']
            taux_participation_t1 = 100 - feature['properties'].get('taux_abstention', 0)
            t1_data[num_bureau] = {
                'participation': taux_participation_t1,
                'inscrits': feature['properties'].get('inscrits', 0),
                'votants': feature['properties'].get('votants', 0)
            }
        
        # Calculer l'évolution pour chaque bureau T2
        for feature in self.geojson_t2['features']:
            num_bureau = feature['properties']['NUM_BUREAU']
            taux_participation_t2 = 100 - feature['properties'].get('taux_abstention', 0)
            
            if num_bureau in t1_data:
                taux_participation_t1 = t1_data[num_bureau]['participation']
                evolution = taux_participation_t2 - taux_participation_t1
                
                evolution_data.append(evolution)
                locations.append(num_bureau)
                
                # Créer le texte d'infobulle
                hover_text = f"<b>Bureau {num_bureau}</b><br>"
                hover_text += f"<br><b>Participation:</b><br>"
                hover_text += f"Tour 1: {taux_participation_t1:.2f}%<br>"
                hover_text += f"Tour 2: {taux_participation_t2:.2f}%<br>"
                hover_text += f"<b>Évolution: {evolution:+.2f}%</b><br>"
                hover_texts.append(hover_text)
        
        # Créer la carte
        fig = go.Figure(go.Choroplethmapbox(
            geojson=self.geojson_t2,
            locations=locations,
            z=evolution_data,
            featureidkey="properties.NUM_BUREAU",
            colorscale='RdBu',
            zmid=0,  # Centre de l'échelle à 0
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>',
            marker_opacity=0.7,
            marker_line_width=1,
            marker_line_color='white',
            colorbar=dict(
                title="Évolution<br>participation (%)",
                thickness=20,
                len=0.7,
                x=1.02
            )
        ))
        
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=self.map_center,
                zoom=11.5
            ),
            title=dict(
                text='<b>Évolution de la participation entre T1 et T2</b>',
                x=0.5,
                xanchor='center'
            ),
            height=800,
            margin={"r": 0, "t": 60, "l": 0, "b": 0}
        )
        
        return fig
    
    def create_candidate_evolution_chart(self, candidat_name: str):
        """
        Crée un graphique montrant l'évolution des résultats d'un candidat entre T1 et T2
        
        Args:
            candidat_name: Nom du candidat
            
        Returns:
            plotly.graph_objects.Figure
        """
        if candidat_name not in self.common_candidates:
            return None
        
        # Extraire les données T1 et T2 pour ce candidat
        bureaux_data = []
        
        # Données T1
        df_t1_candidat = self.df_t1[self.df_t1['CANDIDAT'] == candidat_name]
        t1_by_bureau = df_t1_candidat.set_index('NUM_BUREAU')['POURCENTAGE_EXPRIMES'].to_dict()
        
        # Données T2
        df_t2_candidat = self.df_t2[self.df_t2['CANDIDAT'] == candidat_name]
        t2_by_bureau = df_t2_candidat.set_index('NUM_BUREAU')['POURCENTAGE_EXPRIMES'].to_dict()
        
        # Fusionner les données
        all_bureaux = sorted(set(t1_by_bureau.keys()) & set(t2_by_bureau.keys()))
        
        for bureau in all_bureaux:
            bureaux_data.append({
                'Bureau': bureau,
                'T1': t1_by_bureau.get(bureau, 0),
                'T2': t2_by_bureau.get(bureau, 0),
                'Evolution': t2_by_bureau.get(bureau, 0) - t1_by_bureau.get(bureau, 0)
            })
        
        df_evolution = pd.DataFrame(bureaux_data)
        df_evolution = df_evolution.sort_values('Evolution')
        
        # Créer le graphique
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Tour 1',
            x=df_evolution['Bureau'].astype(str),
            y=df_evolution['T1'],
            marker=dict(color='#377eb8'),
            text=df_evolution['T1'].round(2),
            texttemplate='%{text}%',
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='Tour 2',
            x=df_evolution['Bureau'].astype(str),
            y=df_evolution['T2'],
            marker=dict(color='#e41a1c'),
            text=df_evolution['T2'].round(2),
            texttemplate='%{text}%',
            textposition='outside'
        ))
        
        fig.update_layout(
            title=f'<b>Évolution des résultats de {candidat_name}</b>',
            xaxis_title='Bureau',
            yaxis_title='Pourcentage (%)',
            barmode='group',
            height=500,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            )
        )
        
        return fig
    
    def create_participation_comparison_chart(self):
        """
        Crée un graphique comparant la participation entre T1 et T2 par bureau
        
        Returns:
            plotly.graph_objects.Figure
        """
        # Extraire les données de participation
        bureaux_data = []
        
        # Données T1
        t1_participation = {}
        for feature in self.geojson_t1['features']:
            num_bureau = feature['properties']['NUM_BUREAU']
            taux = 100 - feature['properties'].get('taux_abstention', 0)
            t1_participation[num_bureau] = taux
        
        # Données T2
        t2_participation = {}
        for feature in self.geojson_t2['features']:
            num_bureau = feature['properties']['NUM_BUREAU']
            taux = 100 - feature['properties'].get('taux_abstention', 0)
            t2_participation[num_bureau] = taux
        
        # Fusionner
        all_bureaux = sorted(set(t1_participation.keys()) & set(t2_participation.keys()))
        
        for bureau in all_bureaux:
            t1 = t1_participation.get(bureau, 0)
            t2 = t2_participation.get(bureau, 0)
            bureaux_data.append({
                'Bureau': bureau,
                'T1': t1,
                'T2': t2,
                'Evolution': t2 - t1
            })
        
        df_participation = pd.DataFrame(bureaux_data)
        
        # Créer le graphique
        fig = go.Figure()
        
        # Scatter plot avec ligne de référence
        fig.add_trace(go.Scatter(
            x=df_participation['T1'],
            y=df_participation['T2'],
            mode='markers',
            marker=dict(
                size=10,
                color=df_participation['Evolution'],
                colorscale='RdBu',
                cmid=0,
                showscale=True,
                colorbar=dict(title='Évolution (%)')
            ),
            text=[f"Bureau {b}<br>T1: {t1:.1f}%<br>T2: {t2:.1f}%<br>Évol: {e:+.1f}%" 
                  for b, t1, t2, e in zip(df_participation['Bureau'], 
                                          df_participation['T1'],
                                          df_participation['T2'],
                                          df_participation['Evolution'])],
            hovertemplate='%{text}<extra></extra>',
            name='Bureaux'
        ))
        
        # Ligne de référence (pas de changement)
        min_val = min(df_participation['T1'].min(), df_participation['T2'].min())
        max_val = max(df_participation['T1'].max(), df_participation['T2'].max())
        
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            line=dict(color='gray', dash='dash'),
            name='Pas de changement',
            showlegend=True
        ))
        
        fig.update_layout(
            title='<b>Comparaison de la participation T1 vs T2</b>',
            xaxis_title='Participation Tour 1 (%)',
            yaxis_title='Participation Tour 2 (%)',
            height=600,
            showlegend=True
        )
        
        return fig
    
    def get_statistics_comparison(self) -> Dict:
        """
        Calcule les statistiques comparatives entre T1 et T2
        
        Returns:
            Dict: Statistiques comparatives
        """
        # Statistiques T1
        bureau_t1 = self.df_t1.groupby('NUM_BUREAU').first()
        stats_t1 = {
            'nb_bureaux': self.df_t1['NUM_BUREAU'].nunique(),
            'nb_candidats': self.df_t1['CANDIDAT'].nunique(),
            'total_inscrits': int(bureau_t1['INSCRITS'].sum()),
            'total_votants': int(bureau_t1['VOTANTS'].sum()),
            'taux_participation': float(100 - bureau_t1['TAUX_ABSTENTION'].mean())
        }
        
        # Statistiques T2
        bureau_t2 = self.df_t2.groupby('NUM_BUREAU').first()
        stats_t2 = {
            'nb_bureaux': self.df_t2['NUM_BUREAU'].nunique(),
            'nb_candidats': self.df_t2['CANDIDAT'].nunique(),
            'total_inscrits': int(bureau_t2['INSCRITS'].sum()),
            'total_votants': int(bureau_t2['VOTANTS'].sum()),
            'taux_participation': float(100 - bureau_t2['TAUX_ABSTENTION'].mean())
        }
        
        # Évolution
        evolution = {
            'participation': stats_t2['taux_participation'] - stats_t1['taux_participation'],
            'votants': stats_t2['total_votants'] - stats_t1['total_votants'],
            'candidats_t1_only': stats_t1['nb_candidats'] - len(self.common_candidates),
            'candidats_t2_only': stats_t2['nb_candidats'] - len(self.common_candidates),
            'candidats_communs': len(self.common_candidates)
        }
        
        return {
            't1': stats_t1,
            't2': stats_t2,
            'evolution': evolution
        }
    
    # ========== NOUVELLES MÉTHODES CENTRÉES SUR ANNE VIGNOT ==========
    
    def create_vignot_evolution_map(self):
        """
        Crée une carte montrant l'évolution du score d'Anne VIGNOT entre T1 et T2
        Gradient : Vert (forte progression) → Jaune (modérée) → Rouge (régression)
        
        Returns:
            plotly.graph_objects.Figure
        """
        evolution_data = self.vignot_analyzer.evolution_data
        
        # Préparer les données pour la carte
        locations = []
        z_values = []
        hover_texts = []
        
        for idx, row in evolution_data.iterrows():
            num_bureau = int(row['NUM_BUREAU'])
            locations.append(num_bureau)
            z_values.append(row['EVOLUTION_ABS'])
            
            # Créer le texte d'infobulle
            hover_text = f"<b>Bureau {num_bureau}</b><br>"
            hover_text += f"<br><b>Scores Anne VIGNOT:</b><br>"
            hover_text += f"Tour 1: {row['SCORE_T1']:.2f}%<br>"
            hover_text += f"Tour 2: {row['SCORE_T2']:.2f}%<br>"
            hover_text += f"<b>Évolution: {row['EVOLUTION_ABS']:+.2f} points</b><br>"
            hover_text += f"Ratio: {row['RATIO_PERFORMANCE']:.2f}x<br>"
            hover_text += f"<br><b>Voix:</b><br>"
            hover_text += f"T1: {int(row['VOIX_T1'])} → T2: {int(row['VOIX_T2'])}<br>"
            hover_text += f"Gain: {int(row['VOIX_GAGNEES']):+d} voix ({row['VOIX_GAGNEES_PCT']:+.1f}%)"
            hover_texts.append(hover_text)
        
        # Créer la carte
        fig = go.Figure(go.Choroplethmapbox(
            geojson=self.geojson_t2,
            locations=locations,
            z=z_values,
            featureidkey="properties.NUM_BUREAU",
            colorscale=[
                [0, '#d73027'],    # Rouge (régression)
                [0.3, '#fee08b'],  # Jaune (stagnation)
                [0.5, '#ffffbf'],  # Blanc-jaune (légère progression)
                [0.7, '#d9ef8b'],  # Vert clair (progression)
                [1, '#1a9850']     # Vert foncé (forte progression)
            ],
            zmid=0,
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>',
            marker_opacity=0.7,
            marker_line_width=1,
            marker_line_color='white',
            colorbar=dict(
                title="Évolution<br>score (%)",
                thickness=20,
                len=0.7,
                x=1.02
            )
        ))
        
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=self.map_center,
                zoom=11.5
            ),
            title=dict(
                text='<b>Évolution du score d\'Anne VIGNOT (T1 → T2)</b>',
                x=0.5,
                xanchor='center'
            ),
            height=800,
            margin={"r": 0, "t": 60, "l": 0, "b": 0}
        )
        
        return fig
    
    def create_ratio_performance_map(self):
        """
        Crée une carte montrant le ratio de performance T2/T1
        
        Returns:
            plotly.graph_objects.Figure
        """
        evolution_data = self.vignot_analyzer.evolution_data
        
        locations = []
        z_values = []
        hover_texts = []
        
        for idx, row in evolution_data.iterrows():
            num_bureau = int(row['NUM_BUREAU'])
            locations.append(num_bureau)
            z_values.append(row['RATIO_PERFORMANCE'])
            
            hover_text = f"<b>Bureau {num_bureau}</b><br>"
            hover_text += f"<br><b>Ratio de performance: {row['RATIO_PERFORMANCE']:.2f}x</b><br>"
            hover_text += f"Score T1: {row['SCORE_T1']:.2f}%<br>"
            hover_text += f"Score T2: {row['SCORE_T2']:.2f}%<br>"
            hover_text += f"Progression: {row['EVOLUTION_ABS']:+.2f} points"
            hover_texts.append(hover_text)
        
        fig = go.Figure(go.Choroplethmapbox(
            geojson=self.geojson_t2,
            locations=locations,
            z=z_values,
            featureidkey="properties.NUM_BUREAU",
            colorscale='YlOrRd',
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>',
            marker_opacity=0.7,
            marker_line_width=1,
            marker_line_color='white',
            colorbar=dict(
                title="Ratio<br>T2/T1",
                thickness=20,
                len=0.7,
                x=1.02
            )
        ))
        
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=self.map_center,
                zoom=11.5
            ),
            title=dict(
                text='<b>Ratio de performance Anne VIGNOT (T2/T1)</b>',
                x=0.5,
                xanchor='center'
            ),
            height=800,
            margin={"r": 0, "t": 60, "l": 0, "b": 0}
        )
        
        return fig
    
    def create_bastions_map(self):
        """
        Crée une carte montrant la typologie des bureaux
        (bastions, conquêtes, disputés, défavorables)
        
        Returns:
            plotly.graph_objects.Figure
        """
        df_classified = self.vignot_analyzer.classify_bureaux()
        
        # Couleurs par catégorie
        color_map = {
            'bastion': '#1a9850',      # Vert foncé
            'conquete': '#91cf60',     # Vert clair
            'dispute': '#fee08b',      # Jaune
            'defavorable': '#d73027'   # Rouge
        }
        
        fig = go.Figure()
        
        # Ajouter une trace pour chaque catégorie
        for categorie, color in color_map.items():
            df_cat = df_classified[df_classified['CATEGORIE'] == categorie]
            
            if len(df_cat) > 0:
                # Créer un sous-ensemble du GeoJSON
                geojson_subset = {
                    'type': 'FeatureCollection',
                    'features': [f for f in self.geojson_t2['features'] 
                                if f['properties']['NUM_BUREAU'] in df_cat['NUM_BUREAU'].values]
                }
                
                locations = df_cat['NUM_BUREAU'].tolist()
                hover_texts = []
                
                for idx, row in df_cat.iterrows():
                    hover_text = f"<b>Bureau {int(row['NUM_BUREAU'])}</b><br>"
                    hover_text += f"<b>Catégorie: {categorie.upper()}</b><br>"
                    hover_text += f"<br>Score T1: {row['SCORE_T1']:.2f}%<br>"
                    hover_text += f"Score T2: {row['SCORE_T2']:.2f}%<br>"
                    hover_text += f"Évolution: {row['EVOLUTION_ABS']:+.2f} points"
                    hover_texts.append(hover_text)
                
                fig.add_trace(go.Choroplethmapbox(
                    geojson=geojson_subset,
                    locations=locations,
                    z=[1] * len(locations),
                    featureidkey="properties.NUM_BUREAU",
                    colorscale=[[0, color], [1, color]],
                    showscale=False,
                    text=hover_texts,
                    hovertemplate='%{text}<extra></extra>',
                    marker_opacity=0.7,
                    marker_line_width=1,
                    marker_line_color='white',
                    name=categorie.capitalize()
                ))
        
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=self.map_center,
                zoom=11.5
            ),
            title=dict(
                text='<b>Typologie des bureaux - Anne VIGNOT</b>',
                x=0.5,
                xanchor='center'
            ),
            height=800,
            margin={"r": 0, "t": 60, "l": 0, "b": 0},
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255, 255, 255, 0.8)"
            )
        )
        
        return fig
    
    def create_evolution_bars_chart(self, n: int = 10):
        """
        Crée un graphique en barres des évolutions (top N progressions et régressions)
        
        Args:
            n: Nombre de bureaux à afficher de chaque côté
            
        Returns:
            plotly.graph_objects.Figure
        """
        # Top progressions
        top_progressions = self.vignot_analyzer.get_top_evolutions(n=n, ascending=False)
        # Top régressions
        top_regressions = self.vignot_analyzer.get_top_evolutions(n=n, ascending=True)
        
        # Combiner et trier
        df_combined = pd.concat([top_regressions, top_progressions])
        df_combined = df_combined.sort_values('EVOLUTION_ABS')
        
        fig = go.Figure(go.Bar(
            x=df_combined['EVOLUTION_ABS'],
            y=df_combined['NUM_BUREAU'].astype(str),
            orientation='h',
            marker=dict(
                color=df_combined['EVOLUTION_ABS'],
                colorscale='RdYlGn',
                cmid=0,
                colorbar=dict(title='Évolution (%)')
            ),
            text=df_combined['EVOLUTION_ABS'].round(2),
            texttemplate='%{text:+.2f}%',
            textposition='outside',
            hovertemplate='<b>Bureau %{y}</b><br>Évolution: %{x:+.2f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'<b>Top {n} progressions et régressions du score d\'Anne VIGNOT</b>',
            xaxis_title='Évolution (points de %)',
            yaxis_title='Bureau',
            height=max(400, len(df_combined) * 25),
            xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='gray')
        )
        
        return fig
    
    def create_participation_correlation_scatter(self):
        """
        Crée un scatter plot montrant la corrélation entre
        évolution de la participation et évolution du score
        
        Returns:
            plotly.graph_objects.Figure
        """
        evolution_data = self.vignot_analyzer.evolution_data
        correlation_data = self.vignot_analyzer.calculate_participation_correlation()
        
        fig = go.Figure()
        
        # Scatter plot
        fig.add_trace(go.Scatter(
            x=evolution_data['EVOLUTION_PARTICIPATION'],
            y=evolution_data['EVOLUTION_ABS'],
            mode='markers',
            marker=dict(
                size=10,
                color=evolution_data['RATIO_PERFORMANCE'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Ratio T2/T1')
            ),
            text=[f"Bureau {int(b)}<br>Δ Participation: {p:+.2f}%<br>Δ Score: {s:+.2f}%<br>Ratio: {r:.2f}" 
                  for b, p, s, r in zip(evolution_data['NUM_BUREAU'],
                                        evolution_data['EVOLUTION_PARTICIPATION'],
                                        evolution_data['EVOLUTION_ABS'],
                                        evolution_data['RATIO_PERFORMANCE'])],
            hovertemplate='%{text}<extra></extra>',
            name='Bureaux'
        ))
        
        # Ligne de tendance (régression linéaire)
        z = np.polyfit(evolution_data['EVOLUTION_PARTICIPATION'], 
                      evolution_data['EVOLUTION_ABS'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(evolution_data['EVOLUTION_PARTICIPATION'].min(),
                             evolution_data['EVOLUTION_PARTICIPATION'].max(), 100)
        
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            line=dict(color='red', dash='dash', width=2),
            name=f'Tendance (r={correlation_data["coefficient"]:.3f})'
        ))
        
        fig.update_layout(
            title=f'<b>Corrélation : Évolution Participation vs Évolution Score Anne VIGNOT</b><br>'
                  f'<sup>{correlation_data["interpretation"]} (r = {correlation_data["coefficient"]:.3f})</sup>',
            xaxis_title='Évolution de la participation (points de %)',
            yaxis_title='Évolution du score Anne VIGNOT (points de %)',
            height=600,
            showlegend=True,
            xaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor='gray'),
            yaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor='gray')
        )
        
        return fig
    
    def create_quadrant_chart(self):
        """
        Crée un graphique quadrant (matrice 2x2) Score T1 vs Score T2
        
        Returns:
            plotly.graph_objects.Figure
        """
        evolution_data = self.vignot_analyzer.evolution_data
        df_classified = self.vignot_analyzer.classify_bureaux()
        
        # Couleurs par catégorie
        color_map = {
            'bastion': '#1a9850',
            'conquete': '#91cf60',
            'dispute': '#fee08b',
            'defavorable': '#d73027'
        }
        
        fig = go.Figure()
        
        # Ajouter les points par catégorie
        for categorie, color in color_map.items():
            df_cat = df_classified[df_classified['CATEGORIE'] == categorie]
            
            if len(df_cat) > 0:
                fig.add_trace(go.Scatter(
                    x=df_cat['SCORE_T1'],
                    y=df_cat['SCORE_T2'],
                    mode='markers',
                    marker=dict(size=10, color=color),
                    text=[f"Bureau {int(b)}<br>T1: {t1:.2f}%<br>T2: {t2:.2f}%" 
                          for b, t1, t2 in zip(df_cat['NUM_BUREAU'],
                                               df_cat['SCORE_T1'],
                                               df_cat['SCORE_T2'])],
                    hovertemplate='%{text}<extra></extra>',
                    name=categorie.capitalize()
                ))
        
        # Ligne de référence (pas de changement)
        min_val = min(evolution_data['SCORE_T1'].min(), evolution_data['SCORE_T2'].min())
        max_val = max(evolution_data['SCORE_T1'].max(), evolution_data['SCORE_T2'].max())
        
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            line=dict(color='gray', dash='dash', width=2),
            name='Pas de changement',
            showlegend=True
        ))
        
        # Lignes de seuil (40% et 50%)
        fig.add_hline(y=50, line_dash="dot", line_color="blue", 
                     annotation_text="Seuil 50% (T2)", annotation_position="right")
        fig.add_vline(x=40, line_dash="dot", line_color="blue",
                     annotation_text="Seuil 40% (T1)", annotation_position="top")
        
        fig.update_layout(
            title='<b>Matrice Score T1 vs Score T2 - Anne VIGNOT</b>',
            xaxis_title='Score Tour 1 (%)',
            yaxis_title='Score Tour 2 (%)',
            height=600,
            showlegend=True
        )
        
        return fig
    
    def create_waterfall_chart(self):
        """
        Crée un graphique en cascade expliquant la progression moyenne
        
        Returns:
            plotly.graph_objects.Figure
        """
        waterfall_data = self.vignot_analyzer.get_waterfall_data()
        
        fig = go.Figure(go.Waterfall(
            name="Évolution",
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Score T1", "Impact<br>participation", "Reports<br>de voix", "Score T2"],
            textposition="outside",
            text=[f"{waterfall_data['base']:.2f}%",
                  f"+{waterfall_data['participation']:.2f}%",
                  f"+{waterfall_data['reports_voix']:.2f}%",
                  f"{waterfall_data['final']:.2f}%"],
            y=[waterfall_data['base'],
               waterfall_data['participation'],
               waterfall_data['reports_voix'],
               waterfall_data['final']],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="<b>Décomposition de la progression du score moyen d'Anne VIGNOT</b>",
            showlegend=False,
            height=500,
            yaxis_title="Score (%)"
        )
        
        return fig