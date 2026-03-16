# Dossier des Exports

Ce dossier contient les exports de statistiques et de données générés par l'application de cartographie électorale.

## 📁 Structure des fichiers

Les exports sont automatiquement horodatés au format `YYYYMMDD_HHMMSS` pour garantir la traçabilité.

### Fichiers CSV générés

- **`statistiques_generales_*.csv`** : Indicateurs globaux de l'élection
- **`statistiques_par_bureau_*.csv`** : Données détaillées par bureau de vote
- **`statistiques_par_candidat_*.csv`** : Performance de chaque candidat
- **`resultats_detailles_*.csv`** : Matrice bureau × candidat avec tous les résultats
- **`evolution_t1_t2_*.csv`** : Évolution des scores entre les deux tours (si applicable)
- **`classification_bureaux_*.csv`** : Typologie des bureaux selon leur évolution (si applicable)

### Documentation

- **`DOCUMENTATION_EXPORTS_*.md`** : Documentation complète avec :
  - Règles de calcul pour chaque indicateur
  - Méthodologie d'analyse
  - Interprétation des métriques
  - Contexte des données

## 🚀 Comment générer les exports

1. Lancer l'application Streamlit : `streamlit run app.py`
2. Dans la barre latérale, descendre jusqu'à la section "📥 Exports de données"
3. Cliquer sur "📊 Exporter toutes les statistiques" pour générer tous les fichiers
4. Ou utiliser les boutons individuels pour des exports spécifiques

## 📊 Format des fichiers

- **Encodage** : UTF-8 avec BOM (compatible Excel)
- **Séparateur** : Virgule (`,`)
- **Décimale** : Point (`.`)
- **Format des pourcentages** : 0-100 avec 2 décimales

## 💡 Utilisation

Les fichiers CSV peuvent être ouverts avec :
- Microsoft Excel
- LibreOffice Calc
- Google Sheets
- Python (pandas)
- R
- Tout outil d'analyse de données

## 🗑️ Nettoyage

Ce dossier peut contenir de nombreux fichiers horodatés. Vous pouvez supprimer les anciens exports pour libérer de l'espace.

---

*Ce dossier est géré automatiquement par le module `src/export_manager.py`*
