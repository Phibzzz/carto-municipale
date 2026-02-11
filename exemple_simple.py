"""
Exemple simple : génère et affiche une carte dans le navigateur
"""
from src.data_loader import ElectoralDataLoader
from src.visualization import ElectoralMapVisualizer

print("Chargement des donnees electorales...")

# Charger les données
loader = ElectoralDataLoader()
geojson_enriched, df_candidates, _ = loader.load_all_data()

print("\nCreation de la carte...")

# Créer le visualiseur
visualizer = ElectoralMapVisualizer(geojson_enriched, df_candidates)

# Générer la carte du candidat en tête
fig = visualizer.create_choropleth_winner()

# Sauvegarder
print("\nSauvegarde: exemple_carte.html")
fig.write_html('exemple_carte.html')

# Afficher dans le navigateur
print("Ouverture dans le navigateur...")
fig.show()

print("\nTermine!")
