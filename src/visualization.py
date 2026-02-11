"""
Module de visualisation cartographique des résultats électoraux avec Plotly
"""
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List


class ElectoralMapVisualizer:
    """Classe pour créer des visualisations cartographiques des résultats électoraux"""
    
    def __init__(self, geojson_enriched, df_candidates):
        """
        Initialise le visualiseur
        
        Args:
            geojson_enriched: GeoJSON des périmètres enrichi avec données électorales
            df_candidates: DataFrame des candidats
        """
        self.geojson = geojson_enriched
        self.df_candidates = df_candidates
        
        # Extraire la liste unique des candidats
        self.candidats_list = sorted(df_candidates['CANDIDAT'].unique())
        
        # Calculer le centre de la carte (moyenne des coordonnées)
        self.map_center = self._calculate_map_center()
    
    def _calculate_map_center(self):
        """Calcule le centre de la carte basé sur les géométries"""
        lons = []
        lats = []
        
        for feature in self.geojson['features']:
            coords = feature['geometry']['coordinates']
            # Les polygones peuvent avoir plusieurs niveaux d'imbrication
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
    
    def _create_hover_text(self, feature):
        """
        Crée le texte d'infobulle pour un périmètre
        
        Args:
            feature: Feature GeoJSON
            
        Returns:
            str: Texte HTML formaté pour l'infobulle
        """
        props = feature['properties']
        num_bureau = props['NUM_BUREAU']
        
        hover_text = f"<b>Bureau {num_bureau}</b><br>"
        hover_text += f"<br><b>Participation:</b><br>"
        hover_text += f"Inscrits: {props.get('inscrits', 'N/A')}<br>"
        hover_text += f"Votants: {props.get('votants', 'N/A')}<br>"
        hover_text += f"Abstentions: {props.get('abstentions', 'N/A')} ({props.get('taux_abstention', 'N/A'):.2f}%)<br>"
        hover_text += f"Exprimés: {props.get('exprimes', 'N/A')}<br>"
        
        if 'candidats' in props:
            hover_text += f"<br><b>Résultats:</b><br>"
            for i, candidat in enumerate(props['candidats'][:5]):  # Top 5
                hover_text += f"{i+1}. {candidat['nom']}: {candidat['voix']} voix ({candidat['pourcentage_exprimes']:.2f}%)<br>"
        
        return hover_text
    
    def create_choropleth_by_candidate(self, candidat_name, color_scale='Reds'):
        """
        Crée une carte choroplèthe colorée selon le pourcentage de voix d'un candidat
        
        Args:
            candidat_name: Nom du candidat à visualiser
            color_scale: Échelle de couleurs Plotly (ex: 'Reds', 'Blues', 'Greens')
            
        Returns:
            plotly.graph_objects.Figure
        """
        # Extraire les valeurs pour la colorisation
        z_values = []  # Pourcentages du candidat choisi
        hover_texts = []
        locations = []
        
        for feature in self.geojson['features']:
            props = feature['properties']
            num_bureau = props['NUM_BUREAU']
            locations.append(num_bureau)
            
            # Trouver le pourcentage du candidat dans ce bureau
            pourcentage = 0.0
            if 'candidats' in props:
                for candidat in props['candidats']:
                    if candidat['nom'] == candidat_name:
                        pourcentage = candidat['pourcentage_exprimes']
                        break
            
            z_values.append(pourcentage)
            hover_texts.append(self._create_hover_text(feature))
        
        # Créer la figure
        fig = go.Figure(go.Choroplethmapbox(
            geojson=self.geojson,
            locations=locations,
            z=z_values,
            featureidkey="properties.NUM_BUREAU",
            colorscale=color_scale,
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>',
            marker_opacity=0.7,
            marker_line_width=1,
            marker_line_color='white',
            colorbar=dict(
                title=f"% voix<br>{candidat_name}",
                thickness=20,
                len=0.7,
                x=1.02
            )
        ))
        
        # Configuration de la carte
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=self.map_center,
                zoom=11.5
            ),
            title=dict(
                text=f'<b>Résultats électoraux par bureau de vote</b><br><sup>{candidat_name}</sup>',
                x=0.5,
                xanchor='center'
            ),
            height=800,
            margin={"r": 0, "t": 60, "l": 0, "b": 0}
        )
        
        return fig
    
    def create_choropleth_winner(self, color_map=None):
        """
        Crée une carte choroplèthe colorée selon le candidat en tête dans chaque bureau
        
        Args:
            color_map: Dictionnaire {nom_candidat: couleur} optionnel
            
        Returns:
            plotly.graph_objects.Figure
        """
        # Si pas de color_map fournie, en créer une automatique
        if color_map is None:
            colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', 
                     '#ffff33', '#a65628', '#f781bf', '#999999', '#66c2a5']
            color_map = {candidat: colors[i % len(colors)] 
                        for i, candidat in enumerate(self.candidats_list)}
        
        # Extraire les données
        hover_texts = []
        locations = []
        colors_list = []
        candidat_gagnants = []
        num_bureaux_list = []
        
        for feature in self.geojson['features']:
            props = feature['properties']
            num_bureau = props['NUM_BUREAU']
            num_bureaux_list.append(num_bureau)
            locations.append(num_bureau)
            hover_texts.append(self._create_hover_text(feature))
            
            # Trouver le candidat en tête
            if 'candidat_tete' in props and props['candidat_tete']:
                candidat_gagnant = props['candidat_tete']['nom']
                candidat_gagnants.append(candidat_gagnant)
                colors_list.append(color_map.get(candidat_gagnant, '#cccccc'))
            else:
                candidat_gagnants.append('Aucun')
                colors_list.append('#cccccc')
        
        # Créer la figure avec Choroplethmapbox
        # Note: Pour une carte avec couleurs discrètes, on utilise un workaround
        fig = go.Figure()
        
        # Ajouter une trace pour chaque candidat
        for candidat in self.candidats_list:
            # Filtrer les bureaux où ce candidat est en tête
            indices_candidat = [i for i, c in enumerate(candidat_gagnants) if c == candidat]
            
            if indices_candidat:
                # Sous-ensemble du GeoJSON pour ce candidat
                geojson_subset = {
                    'type': 'FeatureCollection',
                    'features': [self.geojson['features'][i] for i in indices_candidat]
                }
                
                # Locations correspondantes (NUM_BUREAU)
                locations_subset = [num_bureaux_list[i] for i in indices_candidat]
                
                fig.add_trace(go.Choroplethmapbox(
                    geojson=geojson_subset,
                    locations=locations_subset,
                    z=[1] * len(indices_candidat),  # Valeur constante
                    featureidkey="properties.NUM_BUREAU",
                    colorscale=[[0, color_map[candidat]], [1, color_map[candidat]]],
                    showscale=False,
                    text=[hover_texts[i] for i in indices_candidat],
                    hovertemplate='%{text}<extra></extra>',
                    marker_opacity=0.7,
                    marker_line_width=1,
                    marker_line_color='white',
                    name=candidat
                ))
        
        # Configuration de la carte
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=self.map_center,
                zoom=11.5
            ),
            title=dict(
                text='<b>Candidat en tête par bureau de vote</b>',
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
    
    def create_choropleth_participation(self):
        """
        Crée une carte choroplèthe colorée selon le taux de participation
        
        Returns:
            plotly.graph_objects.Figure
        """
        # Extraire les taux de participation
        z_values = []
        hover_texts = []
        locations = []
        
        for feature in self.geojson['features']:
            props = feature['properties']
            num_bureau = props['NUM_BUREAU']
            locations.append(num_bureau)
            
            # Taux de participation = 100 - taux d'abstention
            taux_participation = 100 - props.get('taux_abstention', 0)
            z_values.append(taux_participation)
            hover_texts.append(self._create_hover_text(feature))
        
        # Créer la figure
        fig = go.Figure(go.Choroplethmapbox(
            geojson=self.geojson,
            locations=locations,
            z=z_values,
            featureidkey="properties.NUM_BUREAU",
            colorscale='Viridis',
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>',
            marker_opacity=0.7,
            marker_line_width=1,
            marker_line_color='white',
            colorbar=dict(
                title="Taux de<br>participation (%)",
                thickness=20,
                len=0.7,
                x=1.02
            )
        ))
        
        # Configuration de la carte
        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=self.map_center,
                zoom=11.5
            ),
            title=dict(
                text='<b>Taux de participation par bureau de vote</b>',
                x=0.5,
                xanchor='center'
            ),
            height=800,
            margin={"r": 0, "t": 60, "l": 0, "b": 0}
        )
        
        return fig
    
    def get_candidates_list(self):
        """Retourne la liste des candidats disponibles"""
        return self.candidats_list
