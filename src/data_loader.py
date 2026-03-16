"""
Module de chargement et de préparation des données électorales et géographiques
"""
import pandas as pd
import json
from pathlib import Path
import streamlit as st
from typing import Dict, List, Tuple, Optional
from src.config import ELECTIONS_CONFIG


class ElectoralDataLoader:
    """Classe pour charger et fusionner les données électorales et géographiques"""
    
    def __init__(self, data_folder='datas', election_key='municipales_2020_t1'):
        self.data_folder = Path(data_folder)
        self.election_key = election_key
        self.election_config = ELECTIONS_CONFIG.get(election_key, ELECTIONS_CONFIG['municipales_2020_t1'])
        self.excel_file = self.data_folder / self.election_config['excel_file']
        self.data_format = self.election_config.get('format', 'wide')
        self.bureaux_file = self.data_folder / 'Bureaux_de_Vote_de_Besancon.json'
        self.perimetres_file = self.data_folder / 'Perimetre_Bureaux_de_Vote_de_Besancon.json'
        
    def load_electoral_results(self):
        """
        Charge les résultats électoraux depuis le fichier Excel
        
        Returns:
            pd.DataFrame: DataFrame avec les résultats par bureau
        """
        print(f"Chargement des résultats électoraux depuis {self.excel_file.name}...")
        df = pd.read_excel(self.excel_file)
        
        # Renommer la colonne clé pour cohérence
        if 'Code B.Vote' in df.columns:
            df = df.rename(columns={'Code B.Vote': 'NUM_BUREAU'})
        
        return df
    
    def extract_candidates_data(self, df):
        """
        Extrait les données des candidats depuis le DataFrame Excel
        Gère automatiquement les formats 'wide' et 'long'
        
        Args:
            df: DataFrame des résultats
            
        Returns:
            pd.DataFrame: DataFrame restructuré avec une ligne par bureau et candidat
        """
        if self.data_format == 'long':
            return self._extract_candidates_data_long_format(df)
        elif self.data_format == 'besancon_2026':
            return self._extract_candidates_data_besancon_2026_format(df)
        else:
            return self._extract_candidates_data_wide_format(df)
    
    def _extract_candidates_data_long_format(self, df):
        """
        Extrait les données au format 'long' (une ligne par bureau, un candidat par ligne)
        
        Args:
            df: DataFrame des résultats
            
        Returns:
            pd.DataFrame: DataFrame standardisé
        """
        candidates_data = []
        
        for idx, row in df.iterrows():
            # Utiliser 'Code B.Vote' si disponible, sinon 'NUM_BUREAU'
            bureau_num = row.get('Code B.Vote', row.get('NUM_BUREAU'))
            
            candidat_info = {
                'NUM_BUREAU': bureau_num,
                'COMMUNE': row.get('Libellé de la commune', 'Besançon'),
                'INSCRITS': row.get('Inscrits', 0),
                'VOTANTS': row.get('Votants', 0),
                'ABSTENTIONS': row.get('Abstentions', 0),
                'TAUX_ABSTENTION': row.get('% Abs/Ins', 0),
                'EXPRIMES': row.get('Exprimés', 0),
                'CANDIDAT': f"{row.get('Prénom', '')} {row.get('Nom', '')}".strip(),
                'NOM': row.get('Nom', ''),
                'PRENOM': row.get('Prénom', ''),
                'VOIX': row.get('Voix', 0),
                'POURCENTAGE_INSCRITS': row.get('% Voix/Ins', 0),
                'POURCENTAGE_EXPRIMES': row.get('% Voix/Exp', 0)
            }
            candidates_data.append(candidat_info)
        
        return pd.DataFrame(candidates_data)
    
    def _extract_candidates_data_wide_format(self, df):
        """
        Extrait les données au format 'wide' (tous les candidats sur une ligne par bureau)
        Transforme le format wide en format long pour faciliter l'analyse
        
        Args:
            df: DataFrame des résultats
            
        Returns:
            pd.DataFrame: DataFrame restructuré avec une ligne par bureau et candidat
        """
        candidates_data = []
        
        for idx, row in df.iterrows():
            bureau_num = row['NUM_BUREAU']
            
            # Données de base du bureau
            bureau_data = {
                'NUM_BUREAU': bureau_num,
                'COMMUNE': row['Libellé de la commune'],
                'INSCRITS': row['Inscrits'],
                'VOTANTS': row['Votants'],
                'ABSTENTIONS': row['Abstentions'],
                'TAUX_ABSTENTION': row['% Abs/Ins'],
                'EXPRIMES': row['Exprimés']
            }
            
            # Premier candidat (colonnes sans suffixe)
            if pd.notna(row['Nom']):
                candidat_info = bureau_data.copy()
                candidat_info.update({
                    'CANDIDAT': f"{row['Prénom']} {row['Nom']}",
                    'NOM': row['Nom'],
                    'PRENOM': row['Prénom'],
                    'VOIX': row['Voix'],
                    'POURCENTAGE_INSCRITS': row['% Voix/Ins'],
                    'POURCENTAGE_EXPRIMES': row['% Voix/Exp']
                })
                candidates_data.append(candidat_info)
            
            # Candidats suivants (avec suffixes .1, .2, etc.)
            # Augmenté à 50 pour gérer tous les candidats possibles
            for i in range(1, 50):
                suffix = f'.{i}'
                nom_col = f'Nom{suffix}'
                
                if nom_col not in row.index:
                    break  # Sortir si la colonne n'existe plus
                    
                if pd.notna(row[nom_col]):
                    candidat_info = bureau_data.copy()
                    candidat_info.update({
                        'CANDIDAT': f"{row[f'Prénom{suffix}']} {row[nom_col]}",
                        'NOM': row[nom_col],
                        'PRENOM': row[f'Prénom{suffix}'],
                        'VOIX': row[f'Voix{suffix}'],
                        'POURCENTAGE_INSCRITS': row[f'% Voix/Ins{suffix}'],
                        'POURCENTAGE_EXPRIMES': row[f'% Voix/Exp{suffix}']
                    })
                    candidates_data.append(candidat_info)
        
        return pd.DataFrame(candidates_data)

    def _extract_candidates_data_besancon_2026_format(self, df):
        """
        Extrait les données au format spécifique Besançon 2026.
        
        Ce format a une ligne par bureau de vote, avec :
        - 'Bureau de vote' : texte "101 - Nom du bureau"
        - Colonnes candidats : "Prénom Nom - NOM DE LISTE" (voix directement)
        - Ligne "Total scrutin" à ignorer
        - Pas de colonnes % ni d'abstentions déjà calculées
        
        Args:
            df: DataFrame brut chargé depuis Excel
            
        Returns:
            pd.DataFrame: DataFrame standardisé (même structure que les autres formats)
        """
        # Filtrer la ligne de total
        df = df[~df['Bureau de vote'].str.contains('Total', na=True)].copy()

        # Extraire le numéro de bureau depuis le texte "101 - Nom du bureau"
        df['NUM_BUREAU'] = df['Bureau de vote'].str.extract(r'^(\d+)').astype(int)

        # Identifier les colonnes candidats : toutes les colonnes après 'Procurations'
        cols_before_candidats = ['Bureau de vote', 'Inscrits', 'Emargements', 'Votants',
                                  'Blancs', 'Nuls', 'Exprimés', 'Procurations', 'NUM_BUREAU']
        candidat_cols = [c for c in df.columns if c not in cols_before_candidats]

        candidates_data = []

        for _, row in df.iterrows():
            inscrits = int(row['Inscrits']) if pd.notna(row['Inscrits']) else 0
            votants = int(row['Votants']) if pd.notna(row['Votants']) else 0
            exprimes = int(row['Exprimés']) if pd.notna(row['Exprimés']) else 0
            abstentions = inscrits - votants
            taux_abstention = (abstentions / inscrits * 100) if inscrits > 0 else 0.0

            bureau_data = {
                'NUM_BUREAU': row['NUM_BUREAU'],
                'COMMUNE': 'Besançon',
                'INSCRITS': inscrits,
                'VOTANTS': votants,
                'ABSTENTIONS': abstentions,
                'TAUX_ABSTENTION': taux_abstention,
                'EXPRIMES': exprimes,
            }

            for col in candidat_cols:
                voix = int(row[col]) if pd.notna(row[col]) else 0
                # Extraire "Prénom Nom" depuis "Prénom Nom - NOM DE LISTE"
                candidat_full = col.split(' - ')[0].strip()
                # Décomposer prénom/nom : dernier mot = NOM, reste = prénom
                parts = candidat_full.split()
                if len(parts) >= 2:
                    prenom = ' '.join(parts[:-1])
                    nom = parts[-1]
                else:
                    prenom = ''
                    nom = candidat_full

                pct_exprimes = (voix / exprimes * 100) if exprimes > 0 else 0.0
                pct_inscrits = (voix / inscrits * 100) if inscrits > 0 else 0.0

                candidat_info = bureau_data.copy()
                candidat_info.update({
                    'CANDIDAT': candidat_full,
                    'NOM': nom,
                    'PRENOM': prenom,
                    'VOIX': voix,
                    'POURCENTAGE_INSCRITS': pct_inscrits,
                    'POURCENTAGE_EXPRIMES': pct_exprimes,
                })
                candidates_data.append(candidat_info)

        return pd.DataFrame(candidates_data)

    def load_geojson_perimetres(self):
        """
        Charge le fichier GeoJSON des périmètres de bureaux de vote
        
        Returns:
            dict: Structure GeoJSON
        """
        print("Chargement des périmètres...")
        with open(self.perimetres_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_geojson_bureaux(self):
        """
        Charge le fichier GeoJSON des localisations des bureaux de vote
        
        Returns:
            dict: Structure GeoJSON
        """
        print("Chargement des bureaux de vote...")
        with open(self.bureaux_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def merge_data_with_geojson(self, df_candidates, geojson_perimetres):
        """
        Fusionne les données électorales avec le GeoJSON des périmètres
        
        Args:
            df_candidates: DataFrame des candidats
            geojson_perimetres: GeoJSON des périmètres
            
        Returns:
            dict: GeoJSON enrichi avec les données électorales
        """
        print("Fusion des données électorales avec les périmètres...")
        
        # Créer un dictionnaire des résultats par bureau
        bureaux_dict = {}
        for num_bureau in df_candidates['NUM_BUREAU'].unique():
            bureau_data = df_candidates[df_candidates['NUM_BUREAU'] == num_bureau]
            
            # Créer la liste des candidats avec leurs résultats
            candidats_list = []
            for _, row in bureau_data.iterrows():
                candidats_list.append({
                    'nom': row['CANDIDAT'],
                    'voix': int(row['VOIX']),
                    'pourcentage_exprimes': float(row['POURCENTAGE_EXPRIMES']),
                    'pourcentage_inscrits': float(row['POURCENTAGE_INSCRITS'])
                })
            
            # Trier par nombre de voix décroissant
            candidats_list.sort(key=lambda x: x['voix'], reverse=True)
            
            # Données du bureau
            first_row = bureau_data.iloc[0]
            bureaux_dict[num_bureau] = {
                'inscrits': int(first_row['INSCRITS']),
                'votants': int(first_row['VOTANTS']),
                'abstentions': int(first_row['ABSTENTIONS']),
                'taux_abstention': float(first_row['TAUX_ABSTENTION']),
                'exprimes': int(first_row['EXPRIMES']),
                'candidats': candidats_list,
                'candidat_tete': candidats_list[0] if candidats_list else None
            }
        
        # Enrichir le GeoJSON
        enriched_geojson = geojson_perimetres.copy()
        
        for feature in enriched_geojson['features']:
            num_bureau = feature['properties']['NUM_BUREAU']
            
            if num_bureau in bureaux_dict:
                # Ajouter les données électorales aux propriétés
                feature['properties'].update(bureaux_dict[num_bureau])
            else:
                print(f"Attention: Aucune donnée électorale pour le bureau {num_bureau}")
        
        return enriched_geojson
    
    def load_all_data(self):
        """
        Charge et fusionne toutes les données pour l'élection configurée
        
        Returns:
            tuple: (GeoJSON enrichi, DataFrame candidats, GeoJSON bureaux)
        """
        # Charger les résultats électoraux
        df_results = self.load_electoral_results()
        
        # Extraire les données des candidats
        df_candidates = self.extract_candidates_data(df_results)
        
        # Charger les GeoJSON
        geojson_perimetres = self.load_geojson_perimetres()
        geojson_bureaux = self.load_geojson_bureaux()
        
        # Fusionner
        enriched_geojson = self.merge_data_with_geojson(df_candidates, geojson_perimetres)
        
        print(f"Données chargées ({self.election_key}): {len(enriched_geojson['features'])} périmètres")
        print(f"Candidats: {df_candidates['CANDIDAT'].nunique()} candidats uniques")
        
        return enriched_geojson, df_candidates, geojson_bureaux
    
    @staticmethod
    def load_multiple_elections(election_keys: List[str], data_folder='datas'):
        """
        Charge les données pour plusieurs élections (utile pour la comparaison)
        
        Args:
            election_keys: Liste des clés d'élection à charger
            data_folder: Dossier contenant les données
            
        Returns:
            Dict: {election_key: (geojson_enriched, df_candidates, geojson_bureaux)}
        """
        results = {}
        for election_key in election_keys:
            loader = ElectoralDataLoader(data_folder=data_folder, election_key=election_key)
            results[election_key] = loader.load_all_data()
        return results
    
    @staticmethod
    def get_common_candidates(df_t1: pd.DataFrame, df_t2: pd.DataFrame) -> List[str]:
        """
        Retourne la liste des candidats présents dans les deux tours
        
        Args:
            df_t1: DataFrame des candidats du tour 1
            df_t2: DataFrame des candidats du tour 2
            
        Returns:
            List[str]: Liste des noms de candidats communs
        """
        candidats_t1 = set(df_t1['CANDIDAT'].unique())
        candidats_t2 = set(df_t2['CANDIDAT'].unique())
        return sorted(list(candidats_t1 & candidats_t2))
    
    # ========== MÉTHODES AJOUTÉES POUR STREAMLIT ==========
    
    def get_statistics(self, df_candidates: pd.DataFrame) -> Dict:
        """
        Calcule les statistiques globales des données électorales
        
        Args:
            df_candidates: DataFrame des candidats
            
        Returns:
            Dict: Dictionnaire des statistiques
        """
        # Données uniques par bureau (première ligne de chaque bureau)
        bureau_data = df_candidates.groupby('NUM_BUREAU').first()
        
        stats = {
            'nb_bureaux': df_candidates['NUM_BUREAU'].nunique(),
            'nb_candidats': df_candidates['CANDIDAT'].nunique(),
            'total_inscrits': int(bureau_data['INSCRITS'].sum()),
            'total_votants': int(bureau_data['VOTANTS'].sum()),
            'total_abstentions': int(bureau_data['ABSTENTIONS'].sum()),
            'total_exprimes': int(bureau_data['EXPRIMES'].sum()),
            'taux_participation_moyen': float(100 - bureau_data['TAUX_ABSTENTION'].mean()),
            'taux_abstention_moyen': float(bureau_data['TAUX_ABSTENTION'].mean()),
        }
        
        # Top candidats par voix totales
        candidats_voix = df_candidates.groupby('CANDIDAT')['VOIX'].sum().sort_values(ascending=False)
        stats['top_candidats'] = candidats_voix.to_dict()
        
        return stats
    
    def get_available_criteria(self, df_candidates: pd.DataFrame) -> List[str]:
        """
        Retourne la liste des critères disponibles pour les filtres
        
        Args:
            df_candidates: DataFrame des candidats
            
        Returns:
            List[str]: Liste des noms de colonnes utilisables comme critères
        """
        # Colonnes de critères (exclure les colonnes de candidats)
        criteria_cols = ['INSCRITS', 'VOTANTS', 'ABSTENTIONS', 'TAUX_ABSTENTION', 'EXPRIMES']
        return [col for col in criteria_cols if col in df_candidates.columns]
    
    def filter_geojson_by_criteria(
        self, 
        geojson_enriched: Dict,
        criteria_filters: Optional[Dict[str, Tuple[float, float]]] = None,
        bureau_numbers: Optional[List[int]] = None
    ) -> Dict:
        """
        Filtre le GeoJSON selon des critères spécifiques
        
        Args:
            geojson_enriched: GeoJSON enrichi avec données électorales
            criteria_filters: Dictionnaire {critère: (min, max)} pour filtrer
            bureau_numbers: Liste de numéros de bureaux à inclure (None = tous)
            
        Returns:
            Dict: GeoJSON filtré
        """
        filtered_features = []
        
        for feature in geojson_enriched['features']:
            props = feature['properties']
            num_bureau = props['NUM_BUREAU']
            
            # Filtre par numéro de bureau
            if bureau_numbers is not None and num_bureau not in bureau_numbers:
                continue
            
            # Filtre par critères
            if criteria_filters:
                include = True
                for criterion, (min_val, max_val) in criteria_filters.items():
                    # Mapper les noms de critères
                    prop_name = criterion.lower()
                    
                    # Gérer le taux de participation (calculé)
                    if criterion == 'taux_participation':
                        value = 100 - props.get('taux_abstention', 0)
                    else:
                        value = props.get(prop_name, 0)
                    
                    if not (min_val <= value <= max_val):
                        include = False
                        break
                
                if not include:
                    continue
            
            filtered_features.append(feature)
        
        # Créer un nouveau GeoJSON avec les features filtrées
        filtered_geojson = {
            'type': 'FeatureCollection',
            'features': filtered_features
        }
        
        return filtered_geojson
    
    def filter_candidates_data(
        self,
        df_candidates: pd.DataFrame,
        candidat_names: Optional[List[str]] = None,
        bureau_numbers: Optional[List[int]] = None,
        min_voix: int = 0
    ) -> pd.DataFrame:
        """
        Filtre le DataFrame des candidats selon différents critères
        
        Args:
            df_candidates: DataFrame des candidats
            candidat_names: Liste de noms de candidats à inclure (None = tous)
            bureau_numbers: Liste de numéros de bureaux à inclure (None = tous)
            min_voix: Nombre minimum de voix
            
        Returns:
            pd.DataFrame: DataFrame filtré
        """
        df_filtered = df_candidates.copy()
        
        # Filtre par candidat
        if candidat_names:
            df_filtered = df_filtered[df_filtered['CANDIDAT'].isin(candidat_names)]
        
        # Filtre par bureau
        if bureau_numbers:
            df_filtered = df_filtered[df_filtered['NUM_BUREAU'].isin(bureau_numbers)]
        
        # Filtre par nombre de voix
        if min_voix > 0:
            df_filtered = df_filtered[df_filtered['VOIX'] >= min_voix]
        
        return df_filtered