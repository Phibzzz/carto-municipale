# Guide Rapide d'Utilisation

## Démarrage rapide

### 1. Activer l'environnement virtuel

```bash
.venv\Scripts\activate
```

### 2. Lancer l'application

```bash
python main.py
```

### 3. Résultats

L'application génère automatiquement plusieurs cartes HTML :

- **`carte_candidat_tete.html`** : Vue d'ensemble des gagnants par bureau
- **`carte_participation.html`** : Taux de participation
- **`carte_[candidat].html`** : Résultats par candidat (top 5)

### 4. Visualiser

Ouvrez les fichiers HTML dans votre navigateur (double-clic ou glisser-déposer).

## Fonctionnalités des cartes

### Navigation
- **Zoom** : Molette de la souris ou boutons +/-
- **Déplacement** : Cliquer-glisser sur la carte
- **Réinitialiser** : Bouton "Reset" en haut à droite

### Informations
- **Survolez** un périmètre pour voir :
  - Numéro du bureau
  - Statistiques de participation
  - Top 5 des candidats avec résultats détaillés

### Légende
- **Carte du gagnant** : Légende à gauche avec liste des candidats
- **Autres cartes** : Échelle de couleurs à droite

## Structure des données

### Sources
```
datas/
├── 2020-05-18-resultats-par-niveau-burvot-t1-france-entiere-nettoye.xlsx
├── Bureaux_de_Vote_de_Besancon.json (67 bureaux)
└── Perimetre_Bureaux_de_Vote_de_Besancon.json (67 périmètres)
```

### Statistiques
- **67 bureaux de vote** à Besançon
- **9 candidats** au premier tour
- **Jointure** via `NUM_BUREAU`

## Personnalisation

### Modifier les couleurs

Éditez `src/visualization.py` :

```python
# Changer l'échelle de couleurs pour un candidat
fig = visualizer.create_choropleth_by_candidate(
    'Anne VIGNOT', 
    color_scale='Purples'  # Blues, Greens, Reds, etc.
)
```

### Ajouter un candidat

Éditez `main.py` pour générer une carte supplémentaire :

```python
fig = visualizer.create_choropleth_by_candidate('NOM CANDIDAT', 'Blues')
fig.write_html('carte_mon_candidat.html')
```

### Changer le zoom initial

Éditez `src/visualization.py` :

```python
fig.update_layout(
    mapbox=dict(
        style='open-street-map',
        center=self.map_center,
        zoom=12  # Augmenter pour zoomer plus
    )
)
```

## Dépannage

### Problème d'encodage
Si vous voyez des caractères bizarres, c'est normal sur Windows. Les fichiers HTML générés sont corrects.

### Pas de carte affichée
Vérifiez :
- Les fichiers HTML sont générés dans le répertoire courant
- Votre navigateur autorise les fichiers locaux
- Une connexion internet est disponible (pour le fond de carte)

### Erreur de données manquantes
Vérifiez que tous les fichiers sont présents dans `datas/` :
```bash
dir datas
```

## Support des fonds de carte

Fonds de carte disponibles sans token :
- `open-street-map` (par défaut)
- `carto-positron`
- `carto-darkmatter`
- `stamen-terrain`
- `stamen-toner`

Pour changer, éditez `src/visualization.py` :
```python
mapbox=dict(
    style='carto-positron',  # Changez ici
    ...
)
```
