# Cartographie Électorale - Besançon

Application de visualisation cartographique des résultats électoraux par bureau de vote à Besançon.

## 📊 Description

Cette application permet de visualiser les résultats électoraux du premier tour sur une carte interactive basée sur les périmètres géographiques des bureaux de vote.

## 🗂️ Données utilisées

- **Résultats électoraux** : Fichier Excel contenant les résultats par bureau de vote
- **Bureaux de vote** : Fichier GeoJSON avec la localisation des bureaux (points)
- **Périmètres** : Fichier GeoJSON avec les zones de couverture de chaque bureau (polygones)

## 🛠️ Installation

### Prérequis

- Python 3.8+
- Les dépendances sont déjà installées dans l'environnement virtuel `.venv`

### Vérification des dépendances

```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

### Mode 1 : Application Interactive Streamlit (Recommandé)

L'application interactive offre des filtres dynamiques et une exploration en temps réel des données :

```bash
# Activer l'environnement virtuel (si nécessaire)
.venv\Scripts\activate

# Lancer l'application Streamlit
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`.

#### Fonctionnalités de l'application Streamlit

- **4 modes de visualisation** :
  - 🏆 Candidat en tête par bureau
  - 📊 Taux de participation
  - 👤 Résultats par candidat(s)
  - ⚖️ Comparaison entre 2 candidats

- **Filtres dynamiques** :
  - Par candidat (sélection multiple)
  - Par critères (participation, abstention, inscrits, votants)
  - Par plage de bureaux
  - Par nombre de voix minimum

- **Paramètres d'affichage** :
  - Choix de la palette de couleurs
  - Ajustement de l'opacité
  - Graphiques complémentaires

- **Dashboard statistiques** :
  - KPIs globaux (bureaux, inscrits, votants, participation)
  - Top 5 des candidats avec barres de progression

- **📥 Exports de données** :
  - Export CSV de toutes les statistiques calculées
  - Documentation Markdown complète avec règles de calcul
  - Horodatage automatique des fichiers
  - Voir [GUIDE_EXPORTS.md](GUIDE_EXPORTS.md) pour plus de détails

### Mode 2 : Génération de fichiers HTML statiques

Pour générer des fichiers HTML statiques (ancienne méthode) :

```bash
# Activer l'environnement virtuel (si nécessaire)
.venv\Scripts\activate

# Exécuter l'application en mode batch
python main.py
```

### Résultats (mode batch)

L'application génère plusieurs fichiers HTML contenant des cartes interactives :

1. **`carte_candidat_tete.html`** - Carte montrant le candidat arrivé en tête dans chaque bureau
2. **`carte_participation.html`** - Carte du taux de participation par bureau
3. **`carte_[candidat].html`** - Une carte par candidat principal montrant ses résultats détaillés

Ouvrez ces fichiers dans votre navigateur web pour explorer les cartes de manière interactive.

## 📁 Structure du projet

```
cartographie-electorale/
├── datas/                          # Données sources
│   ├── 2020-05-18-resultats-...xlsx
│   ├── Bureaux_de_Vote_de_Besancon.json
│   └── Perimetre_Bureaux_de_Vote_de_Besancon.json
├── src/                            # Code source
│   ├── __init__.py
│   ├── config.py                  # Configuration de l'application
│   ├── data_loader.py             # Chargement et fusion des données
│   ├── visualization.py           # Création des cartes Plotly
│   ├── export_manager.py          # Gestion des exports CSV/Markdown
│   └── streamlit_app.py           # Logique métier Streamlit
├── exports/                       # Dossier des exports générés
│   └── README.md                  # Documentation du dossier
├── app.py                         # Point d'entrée Streamlit
├── main.py                        # Point d'entrée batch (génération HTML)
├── requirements.txt               # Dépendances Python
├── GUIDE_EXPORTS.md               # Guide d'utilisation des exports
└── README.md                      # Cette documentation
```

## 🎨 Fonctionnalités

### Cartes interactives

- **Zoom et navigation** : Explorez la carte librement
- **Infobulles détaillées** : Survolez un périmètre pour voir :
  - Numéro du bureau
  - Statistiques de participation (inscrits, votants, abstentions)
  - Top 5 des candidats avec leurs résultats
- **Couleurs adaptées** : Visualisation claire des résultats

### Types de visualisation (Application Streamlit)

1. **Carte du gagnant** : Chaque périmètre est coloré selon le candidat en tête
2. **Carte de participation** : Gradient de couleur selon le taux de participation
3. **Cartes par candidat** : Visualisation des résultats d'un ou plusieurs candidats
4. **Comparaison** : Affichage côte à côte de deux candidats avec analyse des écarts

### Filtres avancés (Application Streamlit)

- **Par candidat** : Sélection simple ou multiple
- **Par critères électoraux** :
  - Taux de participation (min/max)
  - Taux d'abstention (min/max)
  - Nombre d'inscrits (min/max)
  - Nombre de votants (min/max)
- **Par bureaux** : Sélection de plages de numéros
- **Par seuil de voix** : Afficher uniquement si > X voix

### Extensibilité multi-élections

L'architecture de l'application est conçue pour supporter facilement l'ajout de nouvelles élections :
- Municipales 2020 - Tour 2
- Élections européennes
- Élections législatives
- Etc.

Il suffit d'ajouter la configuration dans `src/config.py` et de placer le fichier Excel correspondant dans le dossier `datas/`.

## 📊 Technologies utilisées

- **Streamlit** : Framework d'application web interactive
- **Plotly** : Bibliothèque de visualisation interactive
- **Pandas** : Manipulation et analyse de données
- **OpenPyXL** : Lecture des fichiers Excel
- **GeoJSON** : Format de données géospatiales

## 🔧 Personnalisation

### Modifier les visualisations

Éditez `src/visualization.py` pour :
- Changer les échelles de couleurs
- Ajuster le zoom et le centre de la carte
- Personnaliser les infobulles

### Ajouter d'autres visualisations

Créez de nouvelles méthodes dans la classe `ElectoralMapVisualizer` et appelez-les depuis `src/streamlit_app.py`.

### Ajouter une nouvelle élection

1. Placez le fichier Excel dans `datas/`
2. Ajoutez la configuration dans `src/config.py` dans le dictionnaire `ELECTIONS_CONFIG`
3. Relancez l'application Streamlit

Exemple de configuration :

```python
'municipales_2020_t2': {
    'label': 'Municipales 2020 - Tour 2',
    'date': '2020-06-28',
    'excel_file': 'nom_du_fichier.xlsx',
    'description': 'Second tour des élections municipales'
}
```

## 📝 Notes techniques

- Les données sont fusionnées via le champ `NUM_BUREAU` présent dans les trois sources
- Le fond de carte utilisé est OpenStreetMap (gratuit, sans token requis)
- Les cartes sont entièrement interactives et fonctionnent hors ligne une fois générées

## 👤 Auteur

Développé pour l'analyse des résultats électoraux de Besançon.
