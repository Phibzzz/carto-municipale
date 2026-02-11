"""
Module d'analyse spécifique de la performance d'Anne VIGNOT
entre le premier et le second tour des municipales 2020
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class VignotAnalyzer:
    """Classe pour analyser la performance d'Anne VIGNOT entre T1 et T2"""
    
    CANDIDAT_NAME = "Anne VIGNOT"
    
    def __init__(self, df_t1: pd.DataFrame, df_t2: pd.DataFrame):
        """
        Initialise l'analyseur
        
        Args:
            df_t1: DataFrame des candidats du tour 1
            df_t2: DataFrame des candidats du tour 2
        """
        self.df_t1 = df_t1
        self.df_t2 = df_t2
        
        # Extraire les données d'Anne VIGNOT
        self.vignot_t1 = df_t1[df_t1['CANDIDAT'] == self.CANDIDAT_NAME].copy()
        self.vignot_t2 = df_t2.copy()  # T2 contient uniquement Anne VIGNOT
        
        # Calculer les métriques d'évolution
        self.evolution_data = self._calculate_evolution_data()
    
    def _calculate_evolution_data(self) -> pd.DataFrame:
        """
        Calcule les données d'évolution bureau par bureau
        
        Returns:
            pd.DataFrame avec les colonnes : NUM_BUREAU, SCORE_T1, SCORE_T2, 
            EVOLUTION_ABS, EVOLUTION_REL, VOIX_T1, VOIX_T2, VOIX_GAGNEES, etc.
        """
        # Créer un DataFrame avec les données T1
        df_evolution = self.vignot_t1[['NUM_BUREAU', 'POURCENTAGE_EXPRIMES', 'VOIX', 
                                        'INSCRITS', 'VOTANTS', 'TAUX_ABSTENTION']].copy()
        df_evolution.columns = ['NUM_BUREAU', 'SCORE_T1', 'VOIX_T1', 
                                'INSCRITS_T1', 'VOTANTS_T1', 'TAUX_ABSTENTION_T1']
        
        # Ajouter les données T2
        df_t2_data = self.vignot_t2[['NUM_BUREAU', 'POURCENTAGE_EXPRIMES', 'VOIX',
                                      'INSCRITS', 'VOTANTS', 'TAUX_ABSTENTION']].copy()
        df_t2_data.columns = ['NUM_BUREAU', 'SCORE_T2', 'VOIX_T2',
                              'INSCRITS_T2', 'VOTANTS_T2', 'TAUX_ABSTENTION_T2']
        
        # Fusionner sur NUM_BUREAU
        df_evolution = df_evolution.merge(df_t2_data, on='NUM_BUREAU', how='inner')
        
        # Calculer les évolutions
        df_evolution['EVOLUTION_ABS'] = df_evolution['SCORE_T2'] - df_evolution['SCORE_T1']
        df_evolution['EVOLUTION_REL'] = (df_evolution['SCORE_T2'] / df_evolution['SCORE_T1']) - 1
        df_evolution['RATIO_PERFORMANCE'] = df_evolution['SCORE_T2'] / df_evolution['SCORE_T1']
        
        # Évolution des voix
        df_evolution['VOIX_GAGNEES'] = df_evolution['VOIX_T2'] - df_evolution['VOIX_T1']
        df_evolution['VOIX_GAGNEES_PCT'] = ((df_evolution['VOIX_T2'] - df_evolution['VOIX_T1']) / 
                                            df_evolution['VOIX_T1'] * 100)
        
        # Évolution de la participation
        df_evolution['PARTICIPATION_T1'] = 100 - df_evolution['TAUX_ABSTENTION_T1']
        df_evolution['PARTICIPATION_T2'] = 100 - df_evolution['TAUX_ABSTENTION_T2']
        df_evolution['EVOLUTION_PARTICIPATION'] = (df_evolution['PARTICIPATION_T2'] - 
                                                   df_evolution['PARTICIPATION_T1'])
        
        return df_evolution
    
    def get_evolution_statistics(self) -> Dict:
        """
        Calcule les statistiques globales d'évolution
        
        Returns:
            Dict contenant les statistiques clés
        """
        stats = {
            # Scores moyens
            'score_moyen_t1': float(self.evolution_data['SCORE_T1'].mean()),
            'score_moyen_t2': float(self.evolution_data['SCORE_T2'].mean()),
            'score_median_t1': float(self.evolution_data['SCORE_T1'].median()),
            'score_median_t2': float(self.evolution_data['SCORE_T2'].median()),
            
            # Évolution
            'evolution_moyenne_abs': float(self.evolution_data['EVOLUTION_ABS'].mean()),
            'evolution_moyenne_rel': float(self.evolution_data['EVOLUTION_REL'].mean() * 100),
            'ratio_performance_moyen': float(self.evolution_data['RATIO_PERFORMANCE'].mean()),
            
            # Dispersion
            'ecart_type_t1': float(self.evolution_data['SCORE_T1'].std()),
            'ecart_type_t2': float(self.evolution_data['SCORE_T2'].std()),
            
            # Extrêmes
            'score_max_t1': float(self.evolution_data['SCORE_T1'].max()),
            'score_max_t2': float(self.evolution_data['SCORE_T2'].max()),
            'score_min_t1': float(self.evolution_data['SCORE_T1'].min()),
            'score_min_t2': float(self.evolution_data['SCORE_T2'].min()),
            
            'bureau_max_t1': int(self.evolution_data.loc[self.evolution_data['SCORE_T1'].idxmax(), 'NUM_BUREAU']),
            'bureau_max_t2': int(self.evolution_data.loc[self.evolution_data['SCORE_T2'].idxmax(), 'NUM_BUREAU']),
            
            # Progression
            'progression_max': float(self.evolution_data['EVOLUTION_ABS'].max()),
            'progression_min': float(self.evolution_data['EVOLUTION_ABS'].min()),
            'bureau_progression_max': int(self.evolution_data.loc[self.evolution_data['EVOLUTION_ABS'].idxmax(), 'NUM_BUREAU']),
            'bureau_progression_min': int(self.evolution_data.loc[self.evolution_data['EVOLUTION_ABS'].idxmin(), 'NUM_BUREAU']),
            
            # Voix
            'total_voix_t1': int(self.evolution_data['VOIX_T1'].sum()),
            'total_voix_t2': int(self.evolution_data['VOIX_T2'].sum()),
            'total_voix_gagnees': int(self.evolution_data['VOIX_GAGNEES'].sum()),
            
            # Victoire
            'bureaux_majorite_t1': int((self.evolution_data['SCORE_T1'] > 50).sum()),
            'bureaux_majorite_t2': int((self.evolution_data['SCORE_T2'] > 50).sum()),
            'bureaux_total': len(self.evolution_data),
            
            # Participation
            'participation_moyenne_t1': float(self.evolution_data['PARTICIPATION_T1'].mean()),
            'participation_moyenne_t2': float(self.evolution_data['PARTICIPATION_T2'].mean()),
            'evolution_participation_moyenne': float(self.evolution_data['EVOLUTION_PARTICIPATION'].mean()),
        }
        
        return stats
    
    def classify_bureaux(self) -> pd.DataFrame:
        """
        Classifie les bureaux en 4 catégories selon leur évolution
        
        Catégories :
        - 'bastion' : Fort au T1 (>40%) et confirmé au T2 (>50%)
        - 'conquete' : Faible au T1 (<40%) mais fort au T2 (>50%)
        - 'dispute' : Moyens aux deux tours (30-50%)
        - 'defavorable' : Faible aux deux tours (<40%)
        
        Returns:
            pd.DataFrame avec colonne 'CATEGORIE' ajoutée
        """
        df_classified = self.evolution_data.copy()
        
        def classify_bureau(row):
            t1 = row['SCORE_T1']
            t2 = row['SCORE_T2']
            
            if t1 >= 40 and t2 >= 50:
                return 'bastion'
            elif t1 < 40 and t2 >= 50:
                return 'conquete'
            elif 30 <= t1 <= 50 and 40 <= t2 <= 60:
                return 'dispute'
            else:
                return 'defavorable'
        
        df_classified['CATEGORIE'] = df_classified.apply(classify_bureau, axis=1)
        
        return df_classified
    
    def get_top_evolutions(self, n: int = 10, ascending: bool = False) -> pd.DataFrame:
        """
        Retourne les bureaux avec les plus fortes/faibles évolutions
        
        Args:
            n: Nombre de bureaux à retourner
            ascending: Si True, retourne les plus faibles évolutions
            
        Returns:
            pd.DataFrame trié par évolution
        """
        return self.evolution_data.nlargest(n, 'EVOLUTION_ABS') if not ascending \
               else self.evolution_data.nsmallest(n, 'EVOLUTION_ABS')
    
    def calculate_participation_correlation(self) -> Dict:
        """
        Calcule la corrélation entre évolution de la participation et évolution du score
        
        Returns:
            Dict avec coefficient de corrélation et analyse
        """
        correlation = self.evolution_data['EVOLUTION_PARTICIPATION'].corr(
            self.evolution_data['EVOLUTION_ABS']
        )
        
        # Analyse de la corrélation
        if correlation > 0.5:
            interpretation = "forte corrélation positive"
        elif correlation > 0.3:
            interpretation = "corrélation positive modérée"
        elif correlation > 0:
            interpretation = "faible corrélation positive"
        elif correlation > -0.3:
            interpretation = "faible corrélation négative"
        elif correlation > -0.5:
            interpretation = "corrélation négative modérée"
        else:
            interpretation = "forte corrélation négative"
        
        return {
            'coefficient': float(correlation),
            'interpretation': interpretation,
            'bureaux_participation_hausse_score_hausse': int(
                ((self.evolution_data['EVOLUTION_PARTICIPATION'] > 0) & 
                 (self.evolution_data['EVOLUTION_ABS'] > 0)).sum()
            ),
            'bureaux_participation_hausse_score_baisse': int(
                ((self.evolution_data['EVOLUTION_PARTICIPATION'] > 0) & 
                 (self.evolution_data['EVOLUTION_ABS'] < 0)).sum()
            ),
            'bureaux_participation_baisse_score_hausse': int(
                ((self.evolution_data['EVOLUTION_PARTICIPATION'] < 0) & 
                 (self.evolution_data['EVOLUTION_ABS'] > 0)).sum()
            ),
            'bureaux_participation_baisse_score_baisse': int(
                ((self.evolution_data['EVOLUTION_PARTICIPATION'] < 0) & 
                 (self.evolution_data['EVOLUTION_ABS'] < 0)).sum()
            ),
        }
    
    def get_performance_by_category(self) -> pd.DataFrame:
        """
        Retourne les statistiques par catégorie de bureau
        
        Returns:
            pd.DataFrame avec statistiques par catégorie
        """
        df_classified = self.classify_bureaux()
        
        stats_by_category = df_classified.groupby('CATEGORIE').agg({
            'NUM_BUREAU': 'count',
            'SCORE_T1': 'mean',
            'SCORE_T2': 'mean',
            'EVOLUTION_ABS': 'mean',
            'RATIO_PERFORMANCE': 'mean',
            'VOIX_GAGNEES': 'sum',
        }).round(2)
        
        stats_by_category.columns = [
            'Nombre_bureaux',
            'Score_moyen_T1',
            'Score_moyen_T2',
            'Evolution_moyenne',
            'Ratio_moyen',
            'Total_voix_gagnees'
        ]
        
        return stats_by_category
    
    def identify_outliers(self, threshold_std: float = 2.0) -> Dict[str, pd.DataFrame]:
        """
        Identifie les bureaux atypiques (outliers)
        
        Args:
            threshold_std: Nombre d'écarts-types pour définir un outlier
            
        Returns:
            Dict avec les outliers pour différentes métriques
        """
        mean_evolution = self.evolution_data['EVOLUTION_ABS'].mean()
        std_evolution = self.evolution_data['EVOLUTION_ABS'].std()
        
        outliers = {}
        
        # Outliers pour l'évolution absolue
        outliers['forte_progression'] = self.evolution_data[
            self.evolution_data['EVOLUTION_ABS'] > mean_evolution + threshold_std * std_evolution
        ][['NUM_BUREAU', 'SCORE_T1', 'SCORE_T2', 'EVOLUTION_ABS']].copy()
        
        outliers['forte_regression'] = self.evolution_data[
            self.evolution_data['EVOLUTION_ABS'] < mean_evolution - threshold_std * std_evolution
        ][['NUM_BUREAU', 'SCORE_T1', 'SCORE_T2', 'EVOLUTION_ABS']].copy()
        
        # Outliers pour le ratio de performance
        mean_ratio = self.evolution_data['RATIO_PERFORMANCE'].mean()
        std_ratio = self.evolution_data['RATIO_PERFORMANCE'].std()
        
        outliers['ratio_eleve'] = self.evolution_data[
            self.evolution_data['RATIO_PERFORMANCE'] > mean_ratio + threshold_std * std_ratio
        ][['NUM_BUREAU', 'RATIO_PERFORMANCE', 'SCORE_T1', 'SCORE_T2']].copy()
        
        return outliers
    
    def get_waterfall_data(self) -> Dict:
        """
        Prépare les données pour un graphique en cascade
        expliquant la progression moyenne du score
        
        Returns:
            Dict avec les contributions de différents facteurs
        """
        stats = self.get_evolution_statistics()
        
        # Calcul simplifié des contributions
        # Note : Ces calculs sont des approximations pour la visualisation
        
        base = stats['score_moyen_t1']
        target = stats['score_moyen_t2']
        total_evolution = target - base
        
        # Contribution de l'augmentation de la participation
        # (hypothèse : les nouveaux votants votent proportionnellement)
        participation_contrib = stats['evolution_participation_moyenne'] * 0.3  # Facteur estimé
        
        # Le reste est attribué aux reports de voix
        reports_contrib = total_evolution - participation_contrib
        
        waterfall_data = {
            'base': base,
            'participation': participation_contrib,
            'reports_voix': reports_contrib,
            'final': target,
            'steps': [
                {'label': 'Score T1', 'value': base, 'type': 'base'},
                {'label': 'Impact participation', 'value': participation_contrib, 'type': 'increase'},
                {'label': 'Reports de voix', 'value': reports_contrib, 'type': 'increase'},
                {'label': 'Score T2', 'value': target, 'type': 'final'},
            ]
        }
        
        return waterfall_data
