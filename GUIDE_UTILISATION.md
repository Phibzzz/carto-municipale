# 📖 Guide d'Utilisation - Cartographie Électorale v2.0

## 🚀 Lancement de l'Application

```bash
# Activer l'environnement virtuel (si nécessaire)
.\.venv\Scripts\Activate.ps1

# Lancer l'application
streamlit run app.py
```

L'application sera accessible à l'adresse : **http://localhost:8501**

---

## 🎯 Vue d'Ensemble des Fonctionnalités

### 🔄 Sélection du Mode d'Analyse

Au lancement de l'application, trois boutons vous permettent de choisir le mode d'analyse :

1. **📊 Tour 1** : Analyse complète des résultats du premier tour
2. **📊 Tour 2** : Analyse des résultats du second tour
3. **🔀 Comparaison T1/T2** : Analyse comparative entre les deux tours

---

## 📊 Mode Tour 1 / Tour 2

### Interface
Lorsque vous sélectionnez le mode "Tour 1" ou "Tour 2", vous accédez à :

#### 1. Sidebar - Filtres et Options
- **📊 Mode de visualisation**
  - 🏆 Candidat en tête
  - 📊 Taux de participation
  - 👤 Par candidat
  - ⚖️ Comparaison (entre 2 candidats)

- **🔍 Filtres**
  - Par candidats (sélection multiple)
  - Par critères (participation, abstention, inscrits, votants)
  - Par bureaux (plage de numéros)
  - Par nombre de voix minimum

- **🎨 Paramètres d'affichage**
  - Palette de couleurs
  - Opacité des zones

#### 2. Dashboard de Statistiques
Affiche les KPIs principaux :
- 🏢 Nombre de bureaux de vote
- 📝 Nombre d'inscrits
- ✅ Nombre de votants
- 📊 Taux de participation moyen
- 🏆 Top 5 des candidats

#### 3. Visualisation Principale
Carte interactive avec :
- Zones colorées selon le mode sélectionné
- Infobulles détaillées au survol
- Graphiques complémentaires (dépliables)

### Exemples d'Utilisation

#### Exemple 1 : Voir le candidat en tête par bureau
1. Sélectionner "📊 Tour 1" (ou Tour 2)
2. Choisir le mode "🏆 Candidat en tête"
3. La carte affiche chaque bureau coloré selon le candidat arrivé en tête
4. La légende montre les candidats avec leur couleur respective

#### Exemple 2 : Analyser la participation dans un quartier
1. Sélectionner "📊 Tour 1"
2. Choisir le mode "📊 Taux de participation"
3. Dans la sidebar, ouvrir "🏢 Filtres par bureaux"
4. Ajuster le slider pour sélectionner une plage de bureaux (ex: 201-210)
5. La carte affiche uniquement ces bureaux avec un gradient de couleur

#### Exemple 3 : Comparer deux candidats
1. Sélectionner "📊 Tour 1"
2. Choisir le mode "⚖️ Comparaison"
3. Dans la sidebar, sélectionner les 2 candidats à comparer
4. Deux cartes s'affichent côte à côte
5. Des graphiques comparatifs apparaissent en dessous

---

## 🔀 Mode Comparaison T1/T2

### Interface
Le mode comparaison offre une vue complète de l'évolution entre les deux tours.

#### 1. Dashboard Comparatif
Trois sections de métriques :

**📊 Tour 1**
- Bureaux, Candidats, Votants, Participation

**📊 Tour 2**
- Mêmes métriques avec indicateurs d'évolution (deltas)

**🔀 Évolution**
- Candidats communs aux deux tours
- Candidats éliminés (présents au T1 uniquement)
- Indicateur visuel de l'évolution de la participation

#### 2. Visualisations par Onglets

##### 🗺️ Onglet "Cartes côte à côte"
- Carte du Tour 1 à gauche
- Carte du Tour 2 à droite
- Permet de visualiser les changements de candidat en tête

##### 📈 Onglet "Évolution Participation"
- **Carte d'évolution** : Choroplèthe montrant l'évolution bureau par bureau
  - Rouge : Baisse de participation
  - Bleu : Hausse de participation
  - Blanc : Participation stable
- **Graphique scatter** : Chaque point représente un bureau
  - Axe X : Participation au T1
  - Axe Y : Participation au T2
  - Ligne diagonale : Référence (pas de changement)

##### 👤 Onglet "Évolution Candidats"
- Sélecteur de candidat (uniquement ceux présents aux deux tours)
- Graphique en barres groupées montrant l'évolution par bureau
  - Barres bleues : Résultats Tour 1
  - Barres rouges : Résultats Tour 2

##### 📊 Onglet "Analyses"
- **Graphique en camembert** : Répartition des candidats
  - Candidats communs
  - Candidats éliminés
  - Nouveaux candidats (si applicable)
- **Graphique en barres** : Comparaison de la participation moyenne

### Exemples d'Utilisation

#### Exemple 1 : Identifier les bureaux où la participation a augmenté
1. Cliquer sur "🔀 Comparaison T1/T2"
2. Aller dans l'onglet "📈 Évolution Participation"
3. Observer la carte d'évolution :
   - Les zones bleues indiquent une hausse
   - Les zones rouges indiquent une baisse
4. Survoler les bureaux pour voir les valeurs exactes

#### Exemple 2 : Analyser l'évolution d'un candidat
1. Cliquer sur "🔀 Comparaison T1/T2"
2. Aller dans l'onglet "👤 Évolution Candidats"
3. Sélectionner un candidat dans le menu déroulant
4. Observer le graphique en barres :
   - Comparer les hauteurs des barres bleues (T1) et rouges (T2)
   - Identifier les bureaux où le candidat a progressé/régressé

#### Exemple 3 : Vue d'ensemble des changements
1. Cliquer sur "🔀 Comparaison T1/T2"
2. Consulter le dashboard comparatif en haut :
   - Vérifier l'évolution globale de la participation (delta affiché)
   - Noter le nombre de candidats éliminés
3. Aller dans l'onglet "🗺️ Cartes côte à côte"
4. Comparer visuellement les deux cartes pour voir les bureaux ayant changé de couleur

---

## 🔍 Filtres Avancés (Modes Tour 1/Tour 2)

### Filtres par Critères
Accessibles via l'expander "📊 Filtres par critères" :

- **Taux de participation** : Slider de 0 à 100%
  - Affiche uniquement les bureaux dans la plage sélectionnée
  
- **Taux d'abstention** : Slider de 0 à 100%
  
- **Nombre d'inscrits** : Slider avec min/max automatiques
  - Utile pour filtrer les petits/grands bureaux
  
- **Nombre de votants** : Slider avec min/max automatiques

### Filtres par Bureaux
Accessibles via l'expander "🏢 Filtres par bureaux" :

- **Plage de numéros de bureaux** : Slider de min à max
  - Exemple : Bureaux 201 à 210 (quartier spécifique)

### Filtres par Candidats
Visibles selon le mode sélectionné :

- **Mode "Par candidat"** : Multi-sélection de candidats
- **Mode "Comparaison"** : Sélection de 2 candidats précis

### Réinitialisation
Bouton "🔄 Réinitialiser les filtres" en bas de la sidebar pour revenir à l'état initial.

---

## 🎨 Personnalisation de l'Affichage

### Palettes de Couleurs
Disponibles dans "🎨 Paramètres d'affichage" :
- Rouge (Reds)
- Bleu (Blues)
- Vert (Greens)
- Violet (Purples)
- Orange (Oranges)
- Viridis
- Plasma
- Turbo

### Opacité
Slider permettant d'ajuster la transparence des zones (0.3 à 1.0)
- Utile pour voir la carte de fond en transparence

---

## 💡 Astuces et Bonnes Pratiques

### Performance
- Les données sont mises en cache : le chargement initial peut prendre quelques secondes
- Les changements de filtres sont instantanés
- Le mode comparaison charge les deux tours : temps de chargement légèrement plus long

### Navigation
- Utilisez les onglets dans le mode comparaison pour organiser votre analyse
- Les graphiques sont interactifs : survolez, zoomez, téléchargez
- La sidebar reste accessible en permanence

### Analyse Efficace
1. **Vue d'ensemble** : Commencez par le mode "Candidat en tête"
2. **Détails** : Basculez en mode "Par candidat" pour analyser chaque candidat
3. **Comparaison** : Utilisez le mode "🔀 Comparaison T1/T2" pour l'analyse d'évolution
4. **Approfondissement** : Appliquez des filtres pour affiner votre analyse

### Interprétation des Couleurs
- **Mode Candidat en tête** : Chaque couleur = un candidat
- **Mode Participation** : Gradient du clair au foncé (faible à forte participation)
- **Mode Évolution** : Rouge/Bleu avec blanc au centre (baisse/hausse)

---

## ❓ FAQ

### Q: Pourquoi le Tour 2 n'affiche-t-il qu'un seul candidat ?
**R:** Le fichier de données fourni pour le Tour 2 ne contient actuellement que les résultats d'Anne VIGNOT. Le système est conçu pour supporter plusieurs candidats ; il suffit d'enrichir le fichier Excel.

### Q: Puis-je exporter les graphiques ?
**R:** Oui ! Survolez n'importe quel graphique Plotly et cliquez sur l'icône 📷 en haut à droite pour télécharger en PNG.

### Q: Comment ajouter d'autres élections ?
**R:** Consultez le fichier `src/config.py` et ajoutez une nouvelle entrée dans `ELECTIONS_CONFIG` avec le chemin du fichier Excel et le format approprié.

### Q: L'application ne démarre pas ?
**R:** Vérifiez que :
1. L'environnement virtuel est activé
2. Les dépendances sont installées (`pip install -r requirements.txt`)
3. Les fichiers de données sont présents dans le dossier `datas/`

### Q: Comment changer les couleurs des candidats ?
**R:** Modifiez le paramètre `CANDIDATE_COLORS` dans `src/config.py`.

---

## 📞 Support

Pour toute question ou problème :
1. Consultez le fichier `CHANGELOG.md` pour les notes de version
2. Vérifiez les logs dans le terminal Streamlit
3. Examinez la structure des fichiers de données Excel

---

## 🔧 Configuration Avancée

### Fichiers de Configuration
- `src/config.py` : Configuration globale (élections, couleurs, modes)
- `src/data_loader.py` : Gestion du chargement des données
- `src/visualization.py` : Visualisations pour un tour unique
- `src/comparison_visualization.py` : Visualisations comparatives
- `src/streamlit_app.py` : Logique de l'interface utilisateur

### Structure des Données
Les fichiers Excel doivent contenir au minimum :
- `Code B.Vote` ou `NUM_BUREAU` : Numéro du bureau
- `Inscrits`, `Votants`, `Abstentions` : Données de participation
- `Nom`, `Prénom`, `Voix`, `% Voix/Exp` : Données des candidats

---

**Application développée avec ❤️ par l'équipe de Cartographie Électorale**
