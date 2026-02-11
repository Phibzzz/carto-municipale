# Changelog - Cartographie Électorale

## Version 2.1.0 - Refonte Analyse Anne VIGNOT (2026-02-11)

### 🎯 Contexte
Suite à la constatation que le fichier T2 ne contient que les résultats d'Anne VIGNOT (candidate gagnante), refonte complète de l'approche comparative pour se centrer sur l'analyse de sa performance entre T1 et T2.

### ✨ Nouvelles fonctionnalités majeures

#### 📊 Module d'Analyse Spécialisé
- **Nouveau module** : `src/vignot_analysis.py`
- **Classe `VignotAnalyzer`** : Analyse approfondie de la performance d'Anne VIGNOT
- **Métriques calculées** :
  - Évolution absolue et relative des scores
  - Ratios de performance (T2/T1)
  - Classification des bureaux (bastions, conquêtes, disputés, défavorables)
  - Corrélation participation/score
  - Identification des outliers
  - Analyse des voix gagnées/perdues

#### 🗺️ Visualisations Enrichies (8 nouveaux graphiques)
1. **Carte d'évolution des scores** : Gradient vert/rouge par bureau
2. **Carte des ratios de performance** : Visualisation des multiplicateurs T2/T1
3. **Carte des bastions** : Typologie géographique en 4 catégories
4. **Graphique des progressions** : Top 10 évolutions positives/négatives
5. **Scatter plot de corrélation** : Participation vs Score
6. **Matrice quadrant** : Score T1 vs Score T2
7. **Graphique en cascade** : Décomposition de la progression
8. **Histogrammes et box plots** : Distribution des performances

#### 📱 Interface Refactorée

**Dashboard Tour 2 (revisité)** :
- Performance d'Anne VIGNOT (score moyen, médian, dispersion)
- Géographie (bureaux avec majorité absolue)
- Distribution des scores par catégories
- Extrêmes (meilleur/plus faible bureau)

**Dashboard Comparaison (refonte complète)** :
- 4 sections de KPIs : Performance, Géographie, Mobilisation, Amplitude
- **5 onglets thématiques** :
  - 📈 Évolution Scores
  - 💪 Ratios Performance
  - 🗺️ Bastions
  - ⚡ Impact Participation
  - 🎯 Analyses Avancées

### 🔧 Améliorations techniques

#### Architecture
- **Séparation des préoccupations** : Logique d'analyse isolée dans `vignot_analysis.py`
- **Détection automatique** : Le système détecte si le dataset ne contient qu'Anne VIGNOT
- **Dashboards adaptatifs** : Affichage différencié selon T1 (multi-candidats) ou T2 (Anne VIGNOT)

#### Méthodes ajoutées
**VignotAnalyzer** :
- `get_evolution_statistics()` : 25+ métriques d'évolution
- `classify_bureaux()` : Classification en 4 catégories
- `get_top_evolutions()` : Top progressions/régressions
- `calculate_participation_correlation()` : Analyse causale
- `get_performance_by_category()` : Stats par catégorie
- `identify_outliers()` : Détection des anomalies
- `get_waterfall_data()` : Données pour graphique cascade

**TourComparisonVisualizer** :
- `create_vignot_evolution_map()` : Carte d'évolution
- `create_ratio_performance_map()` : Carte des ratios
- `create_bastions_map()` : Carte typologique
- `create_evolution_bars_chart()` : Barres progressions
- `create_participation_correlation_scatter()` : Scatter corrélation
- `create_quadrant_chart()` : Matrice 2x2
- `create_waterfall_chart()` : Graphique cascade

#### Performance
- **Calculs optimisés** : Toutes les métriques calculées une seule fois
- **Cache préservé** : Mise en cache Streamlit maintenue
- **Chargement progressif** : Onglets chargés à la demande

### 📊 Analyses Disponibles

#### Typologie des Bureaux
- **Bastion** 🏰 : Fort au T1 (≥40%) et confirmé au T2 (≥50%)
- **Conquête** 🚀 : Faible au T1 (<40%) mais fort au T2 (≥50%)
- **Disputé** ⚖️ : Scores moyens aux deux tours
- **Défavorable** 📉 : Faible aux deux tours

#### Métriques Calculées
- Scores moyens, médians, écart-types T1 et T2
- Évolution absolue (points) et relative (%)
- Ratios de performance (multiplicateurs)
- Corrélation participation/score (Pearson)
- Voix gagnées/perdues par bureau
- Distribution des performances

### 🔐 Compatibilité
- ✅ **100% rétrocompatible** : Mode T1 inchangé
- ✅ **Détection intelligente** : Adaptation automatique selon les données
- ✅ **Extensible** : Support facile d'autres candidats si fichier T2 complet

### 📝 Documentation
- **REFONTE_V2.1.md** : Documentation complète de la refonte
- **Code commenté** : Toutes les nouvelles fonctions documentées
- **Guide utilisateur** : Interprétation des visualisations

### 🐛 Corrections
- Adaptation du dashboard T2 pour un seul candidat
- Suppression des références inadaptées aux "candidats communs"
- Logique de comparaison recentrée sur Anne VIGNOT

---

## Version 2.0.0 - Intégration du Second Tour (2026-02-11)

### ✨ Nouvelles fonctionnalités

#### 🔄 Sélection du mode d'analyse
- **Tour 1 uniquement** : Visualisation des résultats du premier tour (mode existant)
- **Tour 2 uniquement** : Visualisation des résultats du second tour
- **Comparaison T1/T2** : Analyse comparative entre les deux tours

#### 🗺️ Visualisations comparatives
- **Cartes côte à côte** : Comparaison visuelle des résultats des deux tours
- **Évolution de la participation** : Carte choroplèthe montrant l'évolution bureau par bureau
- **Graphique de comparaison** : Scatter plot comparant la participation T1 vs T2
- **Évolution des candidats** : Graphiques d'évolution pour les candidats présents aux deux tours

#### 📊 Dashboard comparatif
- Statistiques détaillées pour chaque tour
- Métriques d'évolution (participation, nombre de votants)
- Analyse des candidats (communs, éliminés, nouveaux)

#### 🔍 Analyses supplémentaires
- Répartition des candidats entre les tours
- Graphiques de comparaison de la participation moyenne
- Identification des bureaux ayant changé de candidat en tête

### 🔧 Améliorations techniques

#### Configuration (`src/config.py`)
- Ajout de la configuration pour le Tour 2
- Nouveau paramètre `format` pour gérer différents formats de données ('wide' vs 'long')
- Ajout de `TOUR_MODES` pour la gestion des modes de tour

#### Data Loader (`src/data_loader.py`)
- Prise en charge de plusieurs formats de fichiers Excel :
  - **Format 'wide'** : Tous les candidats sur une ligne (100 colonnes - Tour 1)
  - **Format 'long'** : Une ligne par candidat et bureau (28 colonnes - Tour 2)
- Méthode `load_multiple_elections()` pour charger plusieurs tours simultanément
- Méthode `get_common_candidates()` pour identifier les candidats présents aux deux tours
- Adaptation dynamique du parsing selon le format configuré

#### Nouveau module (`src/comparison_visualization.py`)
- Classe `TourComparisonVisualizer` pour les visualisations comparatives
- Méthodes de génération de cartes d'évolution
- Méthodes de calcul de statistiques comparatives
- Support des graphiques d'évolution par candidat

#### Interface Streamlit (`app.py` & `src/streamlit_app.py`)
- Sélecteur de mode de tour avec boutons interactifs
- Nouvelles fonctions de rendu :
  - `render_comparison_dashboard()`
  - `render_comparison_visualization()`
- Système d'onglets pour organiser les visualisations comparatives
- Gestion du cache Streamlit pour optimiser les performances

### 📁 Structure des données

#### Fichiers Excel pris en charge
- **Tour 1** : `2020-05-18-resultats-par-niveau-burvot-t1-france-entiere-nettoye.xlsx`
  - Format: Wide (100 colonnes)
  - Candidats: Multiples candidats par ligne avec suffixes (.1, .2, etc.)
  
- **Tour 2** : `resultats-par-niveau-burvot-t2-france-entiere.xlsx-nettoye.xlsx`
  - Format: Long (28 colonnes)
  - Candidats: Une ligne par bureau (actuellement 1 seul candidat : Anne VIGNOT)

### 🔐 Compatibilité
- ✅ Le mode "Tour 1" conserve exactement le comportement précédent
- ✅ Aucune régression sur les fonctionnalités existantes
- ✅ Support des filtres existants pour chaque tour individuellement
- ✅ Architecture extensible pour ajouter d'autres élections futures

### 📝 Notes importantes

#### Limitation actuelle
Le fichier du Tour 2 fourni ne contient actuellement qu'un seul candidat (Anne VIGNOT).
Le système est néanmoins conçu pour gérer plusieurs candidats et pourra être enrichi
ultérieurement avec des données complètes.

#### Performance
- Utilisation du cache Streamlit (`@st.cache_data`) pour optimiser le chargement
- Chargement des données du T2 uniquement lorsque nécessaire
- Mode comparaison : chargement parallèle des deux tours

### 🚀 Utilisation

```bash
# Lancer l'application
streamlit run app.py

# Sélectionner le mode d'analyse souhaité :
# - 📊 Tour 1 : Analyse du premier tour
# - 📊 Tour 2 : Analyse du second tour
# - 🔀 Comparaison T1/T2 : Analyse comparative
```

### 🔮 Évolutions futures possibles
- [ ] Support de fichiers T2 avec plusieurs candidats
- [ ] Analyse des transferts de voix entre candidats
- [ ] Carte animée montrant l'évolution progressive
- [ ] Export des analyses comparatives en PDF
- [ ] Ajout d'autres élections (Européennes, Législatives, etc.)

---

## Version 1.0.0 - Version initiale

### Fonctionnalités
- Visualisation des résultats du Tour 1
- 4 modes de visualisation (Candidat en tête, Participation, Par candidat, Comparaison)
- Système de filtres avancé
- Dashboard de statistiques
- Cartes interactives avec Plotly
