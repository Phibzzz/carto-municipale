# 🚀 Guide de Démarrage Rapide - Application Streamlit

## ⚡ Lancement en 3 étapes

### 1. Activer l'environnement virtuel

```powershell
.venv\Scripts\activate
```

### 2. Vérifier les dépendances (optionnel)

Si c'est votre première fois ou en cas de problème :

```powershell
pip install -r requirements.txt
```

### 3. Lancer l'application

```powershell
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`

---

## 📊 Utilisation de l'Interface

### Sidebar (Barre latérale gauche)

#### 1. Mode de visualisation
Choisissez parmi 4 modes :
- **🏆 Candidat en tête** : Vue d'ensemble des gagnants par bureau
- **📊 Taux de participation** : Analyse de la participation électorale
- **👤 Par candidat** : Résultats détaillés d'un ou plusieurs candidats
- **⚖️ Comparaison** : Comparaison directe entre 2 candidats

#### 2. Filtres
- **Candidats** : Sélectionner les candidats à afficher (selon le mode)
- **Critères** : Filtrer par participation, abstention, inscrits, votants
- **Bureaux** : Sélectionner une plage de numéros de bureaux
- **Voix minimum** : Seuil de voix pour afficher un candidat

#### 3. Paramètres d'affichage
- **Palette de couleurs** : Choisir le schéma de couleurs de la carte
- **Opacité** : Ajuster la transparence des zones

### Zone Principale

#### Dashboard Statistiques (haut)
- Nombre de bureaux, inscrits, votants
- Taux de participation moyen
- Top 5 des candidats avec barres de progression

#### Carte Interactive (centre)
- **Zoom** : Molette de la souris ou boutons +/-
- **Déplacement** : Cliquer-glisser
- **Infobulles** : Survoler une zone pour voir les détails
- **Légende** : À droite de la carte

#### Graphiques Complémentaires (bas)
Cliquez sur "📈 Graphiques complémentaires" pour afficher des analyses supplémentaires

---

## 💡 Exemples d'Utilisation

### Exemple 1 : Voir les résultats d'Anne Vignot
1. Sélectionner le mode **👤 Par candidat**
2. Dans la sidebar, sélectionner "Anne VIGNOT" dans la liste des candidats
3. Ajuster éventuellement la palette de couleurs
4. Explorer la carte et les graphiques

### Exemple 2 : Comparer deux candidats
1. Sélectionner le mode **⚖️ Comparaison**
2. Choisir le Candidat 1 (ex: Anne VIGNOT)
3. Choisir le Candidat 2 (ex: Ludovic FAGAUT)
4. Observer les deux cartes côte à côte et l'analyse des écarts

### Exemple 3 : Analyser la participation
1. Sélectionner le mode **📊 Taux de participation**
2. Optionnel : Filtrer par plage de participation (ex: 40% - 60%)
3. Observer la distribution sur la carte et l'histogramme

### Exemple 4 : Filtrer les bureaux à forte participation
1. Choisir n'importe quel mode
2. Dans "📊 Filtres par critères", ajuster le slider de participation (ex: 50% - 100%)
3. La carte n'affiche que les bureaux correspondants
4. Le nombre de bureaux filtrés est indiqué sous le titre

---

## 🔄 Réinitialisation

Pour revenir aux paramètres par défaut :
- Cliquer sur **🔄 Réinitialiser les filtres** en bas de la sidebar

---

## 🛑 Arrêter l'Application

Dans le terminal :
- Appuyer sur `Ctrl + C`

---

## ❓ Questions Fréquentes

### L'application ne se lance pas
- Vérifier que l'environnement virtuel est activé
- Exécuter : `pip install -r requirements.txt`
- Vérifier que le port 8501 n'est pas déjà utilisé

### Les données ne s'affichent pas
- Vérifier que les fichiers sont présents dans le dossier `datas/`
- Les fichiers GeoJSON et Excel doivent correspondre aux noms configurés

### La carte est vide après filtrage
- Aucun bureau ne correspond aux filtres sélectionnés
- Utiliser le bouton **🔄 Réinitialiser les filtres**

### Comment ajouter une nouvelle élection ?
Voir la section "Ajouter une nouvelle élection" dans le README.md

---

## 📞 Support

Pour toute question ou problème, référez-vous à la documentation complète dans `README.md`.

---

**Bon usage de l'application ! 🎉**
