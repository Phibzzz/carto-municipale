"""
Module de gestion des exports de données et statistiques électorales
Génère des fichiers CSV et de la documentation Markdown
"""
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from src.data_loader import ElectoralDataLoader
from src.visualization import ElectoralMapVisualizer
from src.vignot_analysis import VignotAnalyzer


class ExportManager:
    """Classe pour gérer l'export des statistiques électorales"""
    
    def __init__(self, export_folder: str = 'exports'):
        """
        Initialise le gestionnaire d'exports
        
        Args:
            export_folder: Dossier de destination des exports
        """
        self.export_folder = Path(export_folder)
        self.export_folder.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def _get_export_path(self, filename: str, with_timestamp: bool = True) -> Path:
        """
        Construit le chemin complet d'un fichier d'export
        
        Args:
            filename: Nom du fichier
            with_timestamp: Si True, ajoute un timestamp au nom
            
        Returns:
            Path: Chemin complet du fichier
        """
        if with_timestamp:
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                filename = f"{name_parts[0]}_{self.timestamp}.{name_parts[1]}"
            else:
                filename = f"{filename}_{self.timestamp}"
        
        return self.export_folder / filename
    
    def export_statistiques_generales(
        self,
        df_candidates: pd.DataFrame,
        loader: ElectoralDataLoader,
        election_label: str = "Municipales 2020"
    ) -> Path:
        """
        Exporte les statistiques générales de l'élection en CSV
        
        Args:
            df_candidates: DataFrame des candidats
            loader: Instance du loader
            election_label: Label de l'élection
            
        Returns:
            Path: Chemin du fichier généré
        """
        stats = loader.get_statistics(df_candidates)
        
        # Créer un DataFrame avec les statistiques générales
        data = {
            'Indicateur': [
                'Nombre de bureaux de vote',
                'Nombre de candidats',
                'Total inscrits',
                'Total votants',
                'Total abstentions',
                'Total exprimés',
                'Taux de participation moyen (%)',
                'Taux d\'abstention moyen (%)',
            ],
            'Valeur': [
                stats['nb_bureaux'],
                stats['nb_candidats'],
                stats['total_inscrits'],
                stats['total_votants'],
                stats['total_abstentions'],
                stats['total_exprimes'],
                round(stats['taux_participation_moyen'], 2),
                round(stats['taux_abstention_moyen'], 2),
            ],
            'Type': [
                'Comptage',
                'Comptage',
                'Comptage',
                'Comptage',
                'Comptage',
                'Comptage',
                'Pourcentage',
                'Pourcentage',
            ]
        }
        
        df_stats = pd.DataFrame(data)
        
        # Ajouter métadonnées
        df_stats['Election'] = election_label
        df_stats['Date_export'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Sauvegarder
        filepath = self._get_export_path('statistiques_generales.csv')
        df_stats.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def export_statistiques_par_bureau(
        self,
        df_candidates: pd.DataFrame,
        election_label: str = "Municipales 2020"
    ) -> Path:
        """
        Exporte les statistiques détaillées par bureau en CSV
        
        Args:
            df_candidates: DataFrame des candidats
            election_label: Label de l'élection
            
        Returns:
            Path: Chemin du fichier généré
        """
        # Regrouper par bureau pour obtenir les statistiques de base
        bureau_stats = df_candidates.groupby('NUM_BUREAU').agg({
            'INSCRITS': 'first',
            'VOTANTS': 'first',
            'ABSTENTIONS': 'first',
            'TAUX_ABSTENTION': 'first',
            'EXPRIMES': 'first',
            'COMMUNE': 'first'
        }).reset_index()
        
        # Calculer le taux de participation
        bureau_stats['TAUX_PARTICIPATION'] = 100 - bureau_stats['TAUX_ABSTENTION']
        
        # Trouver le candidat en tête par bureau
        candidat_tete = df_candidates.loc[
            df_candidates.groupby('NUM_BUREAU')['VOIX'].idxmax()
        ][['NUM_BUREAU', 'CANDIDAT', 'VOIX', 'POURCENTAGE_EXPRIMES']]
        candidat_tete.columns = ['NUM_BUREAU', 'CANDIDAT_TETE', 'VOIX_TETE', 'PCT_TETE']
        
        # Fusionner
        bureau_stats = bureau_stats.merge(candidat_tete, on='NUM_BUREAU', how='left')
        
        # Ajouter métadonnées
        bureau_stats['Election'] = election_label
        bureau_stats['Date_export'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Réorganiser les colonnes
        cols = ['NUM_BUREAU', 'COMMUNE', 'INSCRITS', 'VOTANTS', 'ABSTENTIONS', 
                'TAUX_PARTICIPATION', 'TAUX_ABSTENTION', 'EXPRIMES', 
                'CANDIDAT_TETE', 'VOIX_TETE', 'PCT_TETE', 'Election', 'Date_export']
        bureau_stats = bureau_stats[cols]
        
        # Sauvegarder
        filepath = self._get_export_path('statistiques_par_bureau.csv')
        bureau_stats.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def export_statistiques_par_candidat(
        self,
        df_candidates: pd.DataFrame,
        election_label: str = "Municipales 2020"
    ) -> Path:
        """
        Exporte les statistiques par candidat en CSV
        
        Args:
            df_candidates: DataFrame des candidats
            election_label: Label de l'élection
            
        Returns:
            Path: Chemin du fichier généré
        """
        # Calculer les statistiques par candidat
        candidat_stats = df_candidates.groupby('CANDIDAT').agg({
            'VOIX': 'sum',
            'POURCENTAGE_EXPRIMES': 'mean',
            'POURCENTAGE_INSCRITS': 'mean',
            'NUM_BUREAU': 'count'
        }).reset_index()
        
        candidat_stats.columns = [
            'CANDIDAT', 'TOTAL_VOIX', 'PCT_EXPRIMES_MOYEN', 
            'PCT_INSCRITS_MOYEN', 'NB_BUREAUX'
        ]
        
        # Calculer le nombre de bureaux gagnés
        bureaux_gagnes = df_candidates.loc[
            df_candidates.groupby('NUM_BUREAU')['VOIX'].idxmax()
        ]['CANDIDAT'].value_counts().to_dict()
        
        candidat_stats['BUREAUX_GAGNES'] = candidat_stats['CANDIDAT'].map(
            lambda x: bureaux_gagnes.get(x, 0)
        )
        
        # Calculer le score minimum, maximum et écart-type
        score_stats = df_candidates.groupby('CANDIDAT')['POURCENTAGE_EXPRIMES'].agg([
            ('SCORE_MIN', 'min'),
            ('SCORE_MAX', 'max'),
            ('SCORE_MEDIAN', 'median'),
            ('SCORE_ECART_TYPE', 'std')
        ]).reset_index()
        
        candidat_stats = candidat_stats.merge(score_stats, on='CANDIDAT', how='left')
        
        # Trier par nombre de voix décroissant
        candidat_stats = candidat_stats.sort_values('TOTAL_VOIX', ascending=False)
        
        # Ajouter le rang
        candidat_stats.insert(0, 'RANG', range(1, len(candidat_stats) + 1))
        
        # Ajouter métadonnées
        candidat_stats['Election'] = election_label
        candidat_stats['Date_export'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Arrondir les valeurs
        candidat_stats['PCT_EXPRIMES_MOYEN'] = candidat_stats['PCT_EXPRIMES_MOYEN'].round(2)
        candidat_stats['PCT_INSCRITS_MOYEN'] = candidat_stats['PCT_INSCRITS_MOYEN'].round(2)
        candidat_stats['SCORE_MIN'] = candidat_stats['SCORE_MIN'].round(2)
        candidat_stats['SCORE_MAX'] = candidat_stats['SCORE_MAX'].round(2)
        candidat_stats['SCORE_MEDIAN'] = candidat_stats['SCORE_MEDIAN'].round(2)
        candidat_stats['SCORE_ECART_TYPE'] = candidat_stats['SCORE_ECART_TYPE'].round(2)
        
        # Sauvegarder
        filepath = self._get_export_path('statistiques_par_candidat.csv')
        candidat_stats.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def export_evolution_t1_t2(
        self,
        vignot_analyzer: VignotAnalyzer,
        election_label: str = "Municipales 2020"
    ) -> Path:
        """
        Exporte l'évolution T1->T2 pour Anne VIGNOT en CSV
        
        Args:
            vignot_analyzer: Instance de VignotAnalyzer
            election_label: Label de l'élection
            
        Returns:
            Path: Chemin du fichier généré
        """
        # Récupérer les données d'évolution
        df_evolution = vignot_analyzer.evolution_data.copy()
        
        # Arrondir les valeurs
        numeric_cols = df_evolution.select_dtypes(include=['float64']).columns
        df_evolution[numeric_cols] = df_evolution[numeric_cols].round(2)
        
        # Ajouter métadonnées
        df_evolution['Election'] = election_label
        df_evolution['Date_export'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Réorganiser les colonnes
        cols = ['NUM_BUREAU', 'SCORE_T1', 'SCORE_T2', 'EVOLUTION_ABS', 'EVOLUTION_REL',
                'RATIO_PERFORMANCE', 'VOIX_T1', 'VOIX_T2', 'VOIX_GAGNEES', 'VOIX_GAGNEES_PCT',
                'PARTICIPATION_T1', 'PARTICIPATION_T2', 'EVOLUTION_PARTICIPATION',
                'Election', 'Date_export']
        df_evolution = df_evolution[cols]
        
        # Sauvegarder
        filepath = self._get_export_path('evolution_t1_t2.csv')
        df_evolution.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def export_classification_bureaux(
        self,
        vignot_analyzer: VignotAnalyzer,
        election_label: str = "Municipales 2020"
    ) -> Path:
        """
        Exporte la classification des bureaux en CSV
        
        Args:
            vignot_analyzer: Instance de VignotAnalyzer
            election_label: Label de l'élection
            
        Returns:
            Path: Chemin du fichier généré
        """
        # Classifier les bureaux
        df_classified = vignot_analyzer.classify_bureaux()
        
        # Sélectionner les colonnes pertinentes
        cols = ['NUM_BUREAU', 'SCORE_T1', 'SCORE_T2', 'EVOLUTION_ABS', 
                'CATEGORIE', 'VOIX_T1', 'VOIX_T2']
        df_export = df_classified[cols].copy()
        
        # Arrondir
        df_export['SCORE_T1'] = df_export['SCORE_T1'].round(2)
        df_export['SCORE_T2'] = df_export['SCORE_T2'].round(2)
        df_export['EVOLUTION_ABS'] = df_export['EVOLUTION_ABS'].round(2)
        
        # Ajouter métadonnées
        df_export['Election'] = election_label
        df_export['Date_export'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Sauvegarder
        filepath = self._get_export_path('classification_bureaux.csv')
        df_export.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def export_resultats_detailles(
        self,
        df_candidates: pd.DataFrame,
        election_label: str = "Municipales 2020"
    ) -> Path:
        """
        Exporte les résultats détaillés (bureau x candidat) en CSV
        
        Args:
            df_candidates: DataFrame des candidats
            election_label: Label de l'élection
            
        Returns:
            Path: Chemin du fichier généré
        """
        df_export = df_candidates.copy()
        
        # Sélectionner les colonnes pertinentes
        cols = ['NUM_BUREAU', 'CANDIDAT', 'VOIX', 'POURCENTAGE_EXPRIMES', 
                'POURCENTAGE_INSCRITS', 'INSCRITS', 'VOTANTS', 'EXPRIMES']
        df_export = df_export[cols].copy()
        
        # Arrondir
        df_export['POURCENTAGE_EXPRIMES'] = df_export['POURCENTAGE_EXPRIMES'].round(2)
        df_export['POURCENTAGE_INSCRITS'] = df_export['POURCENTAGE_INSCRITS'].round(2)
        
        # Ajouter métadonnées
        df_export['Election'] = election_label
        df_export['Date_export'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Trier
        df_export = df_export.sort_values(['NUM_BUREAU', 'VOIX'], ascending=[True, False])
        
        # Sauvegarder
        filepath = self._get_export_path('resultats_detailles.csv')
        df_export.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def generate_documentation_markdown(
        self,
        df_candidates: pd.DataFrame,
        loader: ElectoralDataLoader,
        election_label: str = "Municipales 2020",
        vignot_analyzer: Optional[VignotAnalyzer] = None
    ) -> Path:
        """
        Génère un fichier Markdown de documentation des exports
        
        Args:
            df_candidates: DataFrame des candidats
            loader: Instance du loader
            election_label: Label de l'élection
            vignot_analyzer: Optionnel, pour l'analyse T1->T2
            
        Returns:
            Path: Chemin du fichier généré
        """
        stats = loader.get_statistics(df_candidates)
        
        # Construire le contenu Markdown
        md_content = f"""# Documentation des Exports - {election_label}

**Date de génération** : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}

---

## 📊 Vue d'ensemble

Cette documentation fournit le contexte d'interprétation de tous les fichiers CSV exportés lors de l'analyse électorale.

### Fichiers générés

1. `statistiques_generales_{self.timestamp}.csv` - Indicateurs globaux de l'élection
2. `statistiques_par_bureau_{self.timestamp}.csv` - Données détaillées par bureau de vote
3. `statistiques_par_candidat_{self.timestamp}.csv` - Performance de chaque candidat
4. `resultats_detailles_{self.timestamp}.csv` - Matrice bureau × candidat avec tous les résultats
"""

        if vignot_analyzer:
            md_content += f"""5. `evolution_t1_t2_{self.timestamp}.csv` - Évolution des scores entre les deux tours
6. `classification_bureaux_{self.timestamp}.csv` - Typologie des bureaux selon leur évolution
"""

        md_content += f"""
---

## 📈 Statistiques Générales

### Indicateurs de base

- **Nombre de bureaux** : {stats['nb_bureaux']} bureaux de vote analysés
- **Nombre de candidats** : {stats['nb_candidats']} candidats en lice
- **Inscrits** : {stats['total_inscrits']:,} électeurs inscrits
- **Votants** : {stats['total_votants']:,} électeurs ayant voté
- **Abstentions** : {stats['total_abstentions']:,} abstentions
- **Exprimés** : {stats['total_exprimes']:,} votes exprimés

### Taux calculés

- **Taux de participation** : {stats['taux_participation_moyen']:.2f}%
  - *Formule* : `(Votants / Inscrits) × 100`
  - *Interprétation* : Proportion d'inscrits ayant exprimé leur vote

- **Taux d'abstention** : {stats['taux_abstention_moyen']:.2f}%
  - *Formule* : `(Abstentions / Inscrits) × 100`
  - *Interprétation* : Proportion d'inscrits n'ayant pas voté

---

## 🏢 Statistiques par Bureau

### Colonnes du fichier

| Colonne | Description | Type | Règle de calcul |
|---------|-------------|------|-----------------|
| `NUM_BUREAU` | Numéro du bureau de vote | Entier | Identifiant unique |
| `COMMUNE` | Nom de la commune | Texte | Besançon |
| `INSCRITS` | Nombre d'inscrits | Entier | Données source |
| `VOTANTS` | Nombre de votants | Entier | Données source |
| `ABSTENTIONS` | Nombre d'abstentions | Entier | Données source |
| `TAUX_PARTICIPATION` | Taux de participation (%) | Décimal | `100 - TAUX_ABSTENTION` |
| `TAUX_ABSTENTION` | Taux d'abstention (%) | Décimal | `(ABSTENTIONS / INSCRITS) × 100` |
| `EXPRIMES` | Votes exprimés | Entier | Données source |
| `CANDIDAT_TETE` | Candidat arrivé en tête | Texte | Candidat avec le plus de voix |
| `VOIX_TETE` | Voix du candidat en tête | Entier | Maximum de voix dans le bureau |
| `PCT_TETE` | Pourcentage du candidat en tête | Décimal | `(VOIX_TETE / EXPRIMES) × 100` |

### Utilisation

Ce fichier permet d'analyser :
- La répartition géographique de la participation
- Les bastions de chaque candidat
- Les disparités entre bureaux

---

## 👤 Statistiques par Candidat

### Colonnes du fichier

| Colonne | Description | Type | Règle de calcul |
|---------|-------------|------|-----------------|
| `RANG` | Position finale | Entier | Classement par nombre de voix |
| `CANDIDAT` | Nom complet du candidat | Texte | Prénom + Nom |
| `TOTAL_VOIX` | Total des voix obtenues | Entier | Somme sur tous les bureaux |
| `PCT_EXPRIMES_MOYEN` | Score moyen sur les exprimés (%) | Décimal | Moyenne des pourcentages par bureau |
| `PCT_INSCRITS_MOYEN` | Score moyen sur les inscrits (%) | Décimal | Moyenne des pourcentages par bureau |
| `NB_BUREAUX` | Nombre de bureaux présents | Entier | Décompte des bureaux |
| `BUREAUX_GAGNES` | Bureaux arrivés en tête | Entier | Nombre de victoires |
| `SCORE_MIN` | Score minimum obtenu (%) | Décimal | Minimum sur tous les bureaux |
| `SCORE_MAX` | Score maximum obtenu (%) | Décimal | Maximum sur tous les bureaux |
| `SCORE_MEDIAN` | Score médian (%) | Décimal | Médiane des scores |
| `SCORE_ECART_TYPE` | Dispersion des scores | Décimal | Écart-type des pourcentages |

### Interprétation

- **SCORE_ECART_TYPE élevé** : Performance très variable selon les bureaux (candidat clivant géographiquement)
- **SCORE_ECART_TYPE faible** : Performance homogène sur le territoire
- **Ratio BUREAUX_GAGNES / NB_BUREAUX** : Indicateur de domination territoriale

---

## 📋 Résultats Détaillés

### Structure

Matrice complète **Bureau × Candidat** avec toutes les données de performance.

### Colonnes

- `NUM_BUREAU` : Identifiant du bureau
- `CANDIDAT` : Nom du candidat
- `VOIX` : Nombre de voix obtenues
- `POURCENTAGE_EXPRIMES` : % sur les exprimés du bureau
- `POURCENTAGE_INSCRITS` : % sur les inscrits du bureau
- `INSCRITS`, `VOTANTS`, `EXPRIMES` : Contexte du bureau

### Utilisation

Ce fichier permet :
- Des analyses croisées bureau × candidat
- La création de tableaux croisés dynamiques
- L'identification de corrélations spatiales

---
"""

        if vignot_analyzer:
            vignot_stats = vignot_analyzer.get_evolution_statistics()
            
            md_content += f"""## 🔄 Évolution T1 → T2 (Anne VIGNOT)

### Vue d'ensemble

- **Score moyen T1** : {vignot_stats['score_moyen_t1']:.2f}%
- **Score moyen T2** : {vignot_stats['score_moyen_t2']:.2f}%
- **Évolution absolue moyenne** : {vignot_stats['evolution_moyenne_abs']:.2f} points
- **Évolution relative moyenne** : {vignot_stats['evolution_moyenne_rel']:.2f}%
- **Ratio de performance moyen** : {vignot_stats['ratio_performance_moyen']:.2f}

### Colonnes du fichier evolution_t1_t2

| Colonne | Description | Formule |
|---------|-------------|---------|
| `SCORE_T1` | Score au premier tour (%) | `(VOIX_T1 / EXPRIMES_T1) × 100` |
| `SCORE_T2` | Score au second tour (%) | `(VOIX_T2 / EXPRIMES_T2) × 100` |
| `EVOLUTION_ABS` | Évolution absolue (points) | `SCORE_T2 - SCORE_T1` |
| `EVOLUTION_REL` | Évolution relative (%) | `((SCORE_T2 / SCORE_T1) - 1) × 100` |
| `RATIO_PERFORMANCE` | Ratio de performance | `SCORE_T2 / SCORE_T1` |
| `VOIX_GAGNEES` | Voix gagnées | `VOIX_T2 - VOIX_T1` |
| `VOIX_GAGNEES_PCT` | % de voix gagnées | `((VOIX_T2 - VOIX_T1) / VOIX_T1) × 100` |
| `EVOLUTION_PARTICIPATION` | Δ Participation (points) | `PARTICIPATION_T2 - PARTICIPATION_T1` |

### Interprétation

- **EVOLUTION_ABS > 0** : Progression entre les tours
- **RATIO_PERFORMANCE > 1** : Performance améliorée au T2
- **Corrélation EVOLUTION_PARTICIPATION / EVOLUTION_ABS** : Impact de la mobilisation

---

## 🏆 Classification des Bureaux

### Méthodologie

Les bureaux sont classés en 4 catégories selon leur performance T1 et T2 :

#### 1. **Bastions** 
- *Critères* : Score T1 ≥ 40% ET Score T2 ≥ 50%
- *Interprétation* : Territoires acquis, confirmés au second tour
- *Stratégie* : Consolidation

#### 2. **Conquêtes**
- *Critères* : Score T1 < 40% ET Score T2 ≥ 50%
- *Interprétation* : Réussites majeures, territoires retournés
- *Stratégie* : Analyser les facteurs de succès

#### 3. **Disputes**
- *Critères* : Score T1 entre 30-50% ET Score T2 entre 40-60%
- *Interprétation* : Zones contestées, équilibrées
- *Stratégie* : Mobilisation ciblée

#### 4. **Défavorables**
- *Critères* : Autres cas (scores faibles aux deux tours)
- *Interprétation* : Territoires difficiles
- *Stratégie* : Analyse des freins

### Statistiques des catégories

"""
            # Calculer les stats par catégorie
            df_classified = vignot_analyzer.classify_bureaux()
            categorie_counts = df_classified['CATEGORIE'].value_counts()
            
            for cat in ['bastion', 'conquete', 'dispute', 'defavorable']:
                count = categorie_counts.get(cat, 0)
                pct = (count / len(df_classified) * 100) if len(df_classified) > 0 else 0
                md_content += f"- **{cat.capitalize()}** : {count} bureaux ({pct:.1f}%)\n"

        md_content += f"""

---

## 🔧 Méthodologie Générale

### Sources des données

- **Fichiers Excel** : Résultats officiels par bureau de vote
- **GeoJSON** : Périmètres géographiques des bureaux (Open Data Besançon)
- **Traitement** : Pandas, Python 3.8+

### Règles de calcul communes

1. **Pourcentages** : Toujours arrondis à 2 décimales
2. **Totaux** : Sommes directes sans pondération
3. **Moyennes** : Moyennes arithmétiques simples (non pondérées par taille de bureau)
4. **Taux** : Exprimés en pourcentage (0-100)

### Précautions d'interprétation

⚠️ **Moyennes non pondérées** : Les moyennes par bureau ne tiennent pas compte de la taille des bureaux. Pour une moyenne pondérée, utilisez `(Total / Somme)`.

⚠️ **Bulletins blancs/nuls** : Les pourcentages sont calculés sur les exprimés (hors blancs/nuls).

⚠️ **Comparaisons inter-tours** : Attention à l'évolution de la participation qui peut biaiser les interprétations.

---

## 📞 Informations Complémentaires

### Génération

- **Script** : `src/export_manager.py`
- **Application** : Streamlit
- **Version** : 2.1

### Formats

- **CSV** : Encodage UTF-8 avec BOM (compatible Excel)
- **Séparateur** : Virgule (`,`)
- **Décimale** : Point (`.`)

### Contact

Pour toute question sur la méthodologie ou les calculs, consulter la documentation technique du projet.

---

*Document généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}*
"""

        # Sauvegarder
        filepath = self._get_export_path('DOCUMENTATION_EXPORTS.md', with_timestamp=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filepath
    
    def export_all(
        self,
        df_candidates: pd.DataFrame,
        loader: ElectoralDataLoader,
        election_label: str = "Municipales 2020",
        vignot_analyzer: Optional[VignotAnalyzer] = None
    ) -> Dict[str, Path]:
        """
        Exporte tous les fichiers (CSV + Markdown)
        
        Args:
            df_candidates: DataFrame des candidats
            loader: Instance du loader
            election_label: Label de l'élection
            vignot_analyzer: Optionnel, pour l'analyse T1->T2
            
        Returns:
            Dict: Dictionnaire {nom_fichier: chemin}
        """
        exports = {}
        
        # CSV de base
        exports['statistiques_generales'] = self.export_statistiques_generales(
            df_candidates, loader, election_label
        )
        exports['statistiques_par_bureau'] = self.export_statistiques_par_bureau(
            df_candidates, election_label
        )
        exports['statistiques_par_candidat'] = self.export_statistiques_par_candidat(
            df_candidates, election_label
        )
        exports['resultats_detailles'] = self.export_resultats_detailles(
            df_candidates, election_label
        )
        
        # CSV spécifiques T1->T2
        if vignot_analyzer:
            exports['evolution_t1_t2'] = self.export_evolution_t1_t2(
                vignot_analyzer, election_label
            )
            exports['classification_bureaux'] = self.export_classification_bureaux(
                vignot_analyzer, election_label
            )
        
        # Documentation Markdown
        exports['documentation'] = self.generate_documentation_markdown(
            df_candidates, loader, election_label, vignot_analyzer
        )
        
        return exports
