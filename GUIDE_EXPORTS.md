# Guide d'Utilisation des Exports

Ce guide explique comment utiliser le nouveau système d'export des statistiques électorales.

## 🎯 Objectif

Le système d'export permet de générer automatiquement :
- **Des fichiers CSV structurés** avec toutes les statistiques calculées
- **Une documentation Markdown complète** expliquant la méthodologie et les règles de calcul

## 📊 Fichiers Générés

### 1. Statistiques Générales
**Fichier** : `statistiques_generales_YYYYMMDD_HHMMSS.csv`

Contient les indicateurs globaux de l'élection :
- Nombre de bureaux, candidats
- Totaux : inscrits, votants, abstentions, exprimés
- Taux de participation et d'abstention

### 2. Statistiques par Bureau
**Fichier** : `statistiques_par_bureau_YYYYMMDD_HHMMSS.csv`

Données détaillées pour chaque bureau de vote :
- Participation et abstention
- Candidat en tête
- Nombre de voix et pourcentages

### 3. Statistiques par Candidat
**Fichier** : `statistiques_par_candidat_YYYYMMDD_HHMMSS.csv`

Performance de chaque candidat :
- Total de voix et moyennes
- Nombre de bureaux gagnés
- Scores min/max/médian
- Écart-type (dispersion)

### 4. Résultats Détaillés
**Fichier** : `resultats_detailles_YYYYMMDD_HHMMSS.csv`

Matrice complète Bureau × Candidat avec tous les résultats.

### 5. Évolution T1→T2 (si applicable)
**Fichier** : `evolution_t1_t2_YYYYMMDD_HHMMSS.csv`

Évolution des scores d'Anne VIGNOT entre les deux tours :
- Scores T1 et T2
- Évolutions absolue et relative
- Nombre de voix gagnées
- Impact de la participation

### 6. Classification des Bureaux (si applicable)
**Fichier** : `classification_bureaux_YYYYMMDD_HHMMSS.csv`

Typologie des bureaux selon leur évolution :
- **Bastions** : Fort au T1 et confirmé au T2
- **Conquêtes** : Faible au T1 mais fort au T2
- **Disputes** : Scores moyens aux deux tours
- **Défavorables** : Faibles scores aux deux tours

### 7. Documentation Markdown
**Fichier** : `DOCUMENTATION_EXPORTS_YYYYMMDD_HHMMSS.md`

Documentation complète comprenant :
- Vue d'ensemble des fichiers
- Règles de calcul pour chaque indicateur
- Formules mathématiques
- Guide d'interprétation
- Méthodologie
- Précautions d'usage

## 🚀 Comment Utiliser

### Via l'Application Streamlit

1. **Lancer l'application** :
   ```bash
   streamlit run app.py
   ```

2. **Dans la barre latérale**, descendre jusqu'à la section "📥 Exports de données"

3. **Export complet** :
   - Cliquer sur "📊 Exporter toutes les statistiques"
   - Tous les fichiers sont générés en une fois

4. **Exports individuels** :
   - Développer "⚙️ Exports individuels"
   - Cliquer sur le bouton du fichier souhaité

5. **Les fichiers sont créés** dans le dossier `exports/`

### Via Script Python

```python
from src.data_loader import ElectoralDataLoader
from src.export_manager import ExportManager

# Charger les données
loader = ElectoralDataLoader(election_key='municipales_2020_t1')
geojson, df_candidates, bureaux = loader.load_all_data()

# Créer le gestionnaire d'exports
export_manager = ExportManager(export_folder='exports')

# Export complet
exports = export_manager.export_all(
    df_candidates=df_candidates,
    loader=loader,
    election_label="Municipales 2020 - T1"
)

# Afficher les fichiers créés
for name, path in exports.items():
    print(f"✓ {path.name}")
```

### Exports Individuels

```python
# Statistiques générales
path = export_manager.export_statistiques_generales(
    df_candidates, loader, "Municipales 2020"
)

# Statistiques par bureau
path = export_manager.export_statistiques_par_bureau(
    df_candidates, "Municipales 2020"
)

# Statistiques par candidat
path = export_manager.export_statistiques_par_candidat(
    df_candidates, "Municipales 2020"
)

# Documentation
path = export_manager.generate_documentation_markdown(
    df_candidates, loader, "Municipales 2020"
)
```

### Avec Analyse T1/T2

```python
from src.vignot_analysis import VignotAnalyzer

# Charger T1 et T2
loader_t1 = ElectoralDataLoader(election_key='municipales_2020_t1')
_, df_t1, _ = loader_t1.load_all_data()

loader_t2 = ElectoralDataLoader(election_key='municipales_2020_t2')
_, df_t2, _ = loader_t2.load_all_data()

# Créer l'analyseur
vignot_analyzer = VignotAnalyzer(df_t1, df_t2)

# Export avec analyse
export_manager = ExportManager()
exports = export_manager.export_all(
    df_candidates=df_t2,
    loader=loader_t2,
    election_label="Municipales 2020",
    vignot_analyzer=vignot_analyzer
)
```

## 📁 Organisation des Fichiers

Les fichiers sont automatiquement horodatés :
```
exports/
├── README.md
├── statistiques_generales_20260214_013208.csv
├── statistiques_par_bureau_20260214_013208.csv
├── statistiques_par_candidat_20260214_013208.csv
├── resultats_detailles_20260214_013208.csv
├── evolution_t1_t2_20260214_013208.csv
├── classification_bureaux_20260214_013208.csv
└── DOCUMENTATION_EXPORTS_20260214_013208.md
```

## 💡 Bonnes Pratiques

### 1. Horodatage
Les fichiers sont automatiquement horodatés pour éviter les écrasements. Vous pouvez supprimer les anciens exports manuellement.

### 2. Format CSV
- **Encodage** : UTF-8 avec BOM (compatible Excel)
- **Séparateur** : Virgule (`,`)
- **Ouverture dans Excel** : Double-clic direct

### 3. Interprétation
Toujours consulter `DOCUMENTATION_EXPORTS_*.md` pour comprendre :
- Les formules de calcul
- Les précautions d'interprétation
- Les limites méthodologiques

### 4. Analyses Personnalisées
Les fichiers CSV peuvent être importés dans :
- **Excel/LibreOffice** : Tableaux croisés dynamiques
- **Python (pandas)** : Analyses statistiques avancées
- **R** : Modélisations
- **Power BI / Tableau** : Visualisations

## 🔍 Exemples d'Utilisation

### Exemple 1 : Analyse dans Excel
1. Ouvrir `statistiques_par_candidat.csv`
2. Créer un tableau croisé dynamique
3. Analyser la dispersion (SCORE_ECART_TYPE) vs performance (TOTAL_VOIX)

### Exemple 2 : Analyse Python
```python
import pandas as pd

# Charger les statistiques par bureau
df = pd.read_csv('exports/statistiques_par_bureau_*.csv')

# Analyser la corrélation participation/score
correlation = df[['TAUX_PARTICIPATION', 'PCT_TETE']].corr()
print(correlation)

# Visualiser
import matplotlib.pyplot as plt
plt.scatter(df['TAUX_PARTICIPATION'], df['PCT_TETE'])
plt.xlabel('Taux de Participation (%)')
plt.ylabel('Score du Candidat en Tête (%)')
plt.show()
```

### Exemple 3 : Comparaison T1/T2
```python
# Charger l'évolution
df_evol = pd.read_csv('exports/evolution_t1_t2_*.csv')

# Bureaux avec plus forte progression
top_progression = df_evol.nlargest(10, 'EVOLUTION_ABS')
print(top_progression[['NUM_BUREAU', 'SCORE_T1', 'SCORE_T2', 'EVOLUTION_ABS']])
```

## ⚠️ Précautions

### Moyennes Non Pondérées
Les moyennes par bureau ne tiennent **pas compte de la taille** des bureaux. Pour une moyenne pondérée :

```python
moyenne_ponderee = (df['VOIX'].sum() / df['EXPRIMES'].sum()) * 100
```

### Comparaisons Inter-Tours
Attention à l'évolution de la participation qui peut biaiser les comparaisons de voix absolues.

### Bulletins Blancs/Nuls
Les pourcentages sont calculés sur les **exprimés** (hors blancs et nuls).

## 🛠️ Personnalisation

### Modifier le Dossier d'Export
```python
export_manager = ExportManager(export_folder='mes_exports')
```

### Désactiver l'Horodatage
Modifier dans `src/export_manager.py` :
```python
def _get_export_path(self, filename: str, with_timestamp: bool = False):
    # ... avec with_timestamp=False par défaut
```

## 📞 Support

Pour toute question :
- Consulter `DOCUMENTATION_EXPORTS_*.md`
- Voir le code source : `src/export_manager.py`
- Examiner les tests : `test_exports.py`

---

**Dernière mise à jour** : 14 février 2026
