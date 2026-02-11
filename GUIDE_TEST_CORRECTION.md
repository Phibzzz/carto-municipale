# 🔧 Guide de Test - Correction du Bug de Chargement

## ⚠️ Problème Identifié

Le cache de Streamlit ne différenciait pas correctement les données entre Tour 1 et Tour 2, affichant les données du T1 (avec Claire ARNOUX) même quand on sélectionnait le Tour 2.

---

## ✅ Corrections Apportées

### 1. Suppression des @st.cache_data sur les méthodes internes
**Fichier** : `src/data_loader.py`

**Problème** : Les méthodes `load_electoral_results()`, `load_geojson_perimetres()` et `load_geojson_bureaux()` utilisaient `@st.cache_data` avec le paramètre `_self` qui empêchait Streamlit de différencier les appels selon l'instance du loader.

**Solution** : Suppression de ces décorateurs. Le cache est maintenant uniquement au niveau de `load_data()` dans `app.py`, ce qui permet à Streamlit de différencier les appels par `election_key`.

### 2. Ajout de logs de débogage
**Fichier** : `app.py`

Des messages de debug s'affichent maintenant dans l'interface pour confirmer quel dataset est chargé :
```
🔄 [DEBUG] Données chargées pour municipales_2020_t2
   - Candidats: 1
   - Lignes: 67
   - Noms: Anne VIGNOT
```

### 3. Bouton de vidage du cache
**Fichier** : `app.py`

Un bouton "🗑️ Vider le cache et recharger" a été ajouté dans un expander "⚙️ Options avancées" pour forcer le rechargement des données si nécessaire.

---

## 🧪 Procédure de Test

### Étape 1 : Accéder à l'Application
```
http://localhost:8501
```

### Étape 2 : Tester le Tour 1
1. Cliquer sur le bouton **"📊 Tour 1"**
2. **Vérifier les messages de debug** qui s'affichent :
   ```
   🔄 [DEBUG] Données chargées pour municipales_2020_t1
      - Candidats: 9
      - Lignes: 603
   ```
3. **Descendre au dashboard** et vérifier :
   - "Top 5 des candidats" doit afficher plusieurs candidats
   - Claire ARNOUX, Anne VIGNOT, Jacques RICCIARDETTI, etc.
4. **Observer la carte** : Plusieurs couleurs (chaque candidat en tête dans différents bureaux)

### Étape 3 : Tester le Tour 2
1. Cliquer sur le bouton **"📊 Tour 2"**
2. **Vérifier les messages de debug** qui s'affichent :
   ```
   🔄 [DEBUG] Données chargées pour municipales_2020_t2
      - Candidats: 1
      - Lignes: 67
      - Noms: Anne VIGNOT
   ```
3. **Descendre au dashboard** et vérifier :
   - Titre : "🏆 Résultats Anne VIGNOT - Tour 2"
   - Performance d'Anne VIGNOT (score moyen, médian, etc.)
   - **Aucune mention de Claire ARNOUX ou autres candidats**
4. **Observer la carte** : Une seule couleur (gradient) représentant Anne VIGNOT

### Étape 4 : Tester le Mode Comparaison
1. Cliquer sur le bouton **"🔀 Comparaison T1/T2"**
2. **Vérifier le dashboard** :
   - Titre : "🏆 Évolution Anne VIGNOT : Tour 1 → Tour 2"
   - Score T1 : ~30-40% → Score T2 : ~50-60%
3. **Explorer les onglets** :
   - 📈 Évolution Scores : Carte avec gradient vert/rouge
   - 💪 Ratios : Carte des multiplicateurs
   - 🗺️ Bastions : 4 catégories de bureaux

---

## ✅ Résultats Attendus

### Tour 1 (Correct)
- **Candidats** : 9 (Claire ARNOUX, Anne VIGNOT, Jacques RICCIARDETTI, etc.)
- **Lignes** : 603 (9 candidats × 67 bureaux)
- **Carte** : Multicolore (différents candidats en tête)
- **Dashboard** : Top 5 avec plusieurs noms

### Tour 2 (Correct)
- **Candidats** : 1 (Anne VIGNOT uniquement)
- **Lignes** : 67 (1 candidat × 67 bureaux)
- **Carte** : Gradient de couleur unique (scores d'Anne VIGNOT)
- **Dashboard** : Données d'Anne VIGNOT uniquement

### Comparaison (Correct)
- **Dashboard** : Évolution Anne VIGNOT T1 → T2
- **Cartes** : Évolution, ratios, bastions
- **Pas de mention** d'autres candidats dans le mode comparaison

---

## 🔧 Si le Problème Persiste

### Solution 1 : Vider le Cache Manuel
1. Dans l'application, cliquer sur **"⚙️ Options avancées"**
2. Cliquer sur **"🗑️ Vider le cache et recharger"**
3. L'application va se recharger avec un cache vide

### Solution 2 : Vider le Cache Streamlit Complet
```bash
# Dans le terminal
streamlit cache clear
```

### Solution 3 : Forcer le Rechargement
1. Fermer complètement l'onglet du navigateur
2. Rouvrir `http://localhost:8501`
3. Tester à nouveau

### Solution 4 : Redémarrer l'Application
```bash
# Arrêter l'application (Ctrl+C dans le terminal)
# Puis relancer
streamlit run app.py
```

---

## 📊 Vérification Technique

Pour vérifier manuellement que les fichiers sont bien différents :

```python
# Test rapide en Python
from src.data_loader import ElectoralDataLoader

# Tour 1
loader_t1 = ElectoralDataLoader(election_key='municipales_2020_t1')
_, df_t1, _ = loader_t1.load_all_data()
print(f"T1: {df_t1['CANDIDAT'].nunique()} candidats")
print(f"Premiers candidats T1: {df_t1['CANDIDAT'].unique()[:5]}")

# Tour 2
loader_t2 = ElectoralDataLoader(election_key='municipales_2020_t2')
_, df_t2, _ = loader_t2.load_all_data()
print(f"T2: {df_t2['CANDIDAT'].nunique()} candidats")
print(f"Candidats T2: {df_t2['CANDIDAT'].unique()}")
```

**Résultat attendu** :
```
T1: 9 candidats
Premiers candidats T1: ['Claire ARNOUX' 'Alexandra CORDIER' 'Jacques RICCIARDETTI'
 'Anne VIGNOT' 'Eric ALAUZET']
T2: 1 candidats
Candidats T2: ['Anne VIGNOT']
```

---

## 📝 Modifications Effectuées

| Fichier | Type | Description |
|---------|------|-------------|
| `src/data_loader.py` | Correction | Suppression @st.cache_data des méthodes internes |
| `app.py` | Ajout | Messages de debug + bouton vidage cache |
| `GUIDE_TEST_CORRECTION.md` | Création | Ce guide de test |

---

## 🎯 Prochaine Action

**Testez l'application maintenant** :
1. Ouvrez http://localhost:8501
2. Suivez la procédure de test ci-dessus
3. Vérifiez que le Tour 2 affiche bien Anne VIGNOT uniquement
4. Si Claire ARNOUX apparaît encore, utilisez le bouton "Vider le cache"

---

**Le problème devrait maintenant être résolu ! 🎉**

Si vous observez toujours des anomalies, merci de noter :
- Quel bouton vous avez cliqué
- Quels candidats s'affichent
- Ce que disent les messages de debug
