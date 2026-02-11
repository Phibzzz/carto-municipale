"""
Application principale de visualisation des résultats électoraux
"""
from src.data_loader import ElectoralDataLoader
from src.visualization import ElectoralMapVisualizer


def main():
    """Fonction principale"""
    
    print("=" * 80)
    print("VISUALISATION DES RÉSULTATS ÉLECTORAUX - BESANÇON")
    print("=" * 80)
    print()
    
    # 1. Charger les données
    loader = ElectoralDataLoader()
    geojson_enriched, df_candidates, geojson_bureaux = loader.load_all_data()
    
    print()
    print("-" * 80)
    
    # 2. Créer le visualiseur
    visualizer = ElectoralMapVisualizer(geojson_enriched, df_candidates)
    
    # 3. Afficher les candidats disponibles
    candidats = visualizer.get_candidates_list()
    print(f"\nCandidats disponibles ({len(candidats)}):")
    for i, candidat in enumerate(candidats, 1):
        print(f"  {i}. {candidat}")
    
    print()
    print("-" * 80)
    print("\nGénération des visualisations...")
    print()
    
    # 4. Créer les différentes visualisations
    
    # Carte 1: Candidat en tête par bureau
    print("1. Carte du candidat en tete par bureau...")
    fig_winner = visualizer.create_choropleth_winner()
    fig_winner.write_html('carte_candidat_tete.html')
    print("   [OK] Sauvegardee: carte_candidat_tete.html")
    
    # Carte 2: Taux de participation
    print("2. Carte du taux de participation...")
    fig_participation = visualizer.create_choropleth_participation()
    fig_participation.write_html('carte_participation.html')
    print("   [OK] Sauvegardee: carte_participation.html")
    
    # Cartes 3+: Une carte par candidat principal (top 5)
    print("3. Cartes par candidat (top 5)...")
    
    # Calculer le total de voix par candidat
    candidats_voix = df_candidates.groupby('CANDIDAT')['VOIX'].sum().sort_values(ascending=False)
    top_candidats = candidats_voix.head(5)
    
    color_scales = ['Reds', 'Blues', 'Greens', 'Purples', 'Oranges']
    
    for i, (candidat, voix_total) in enumerate(top_candidats.items()):
        print(f"   - {candidat} ({voix_total:,} voix)...")
        fig_candidat = visualizer.create_choropleth_by_candidate(
            candidat, 
            color_scale=color_scales[i % len(color_scales)]
        )
        
        # Créer un nom de fichier sécurisé
        filename = f"carte_{candidat.replace(' ', '_').lower()}.html"
        fig_candidat.write_html(filename)
        print(f"     [OK] Sauvegardee: {filename}")
    
    print()
    print("=" * 80)
    print("VISUALISATIONS GÉNÉRÉES AVEC SUCCÈS!")
    print("=" * 80)
    print()
    print("Fichiers HTML créés dans le répertoire courant:")
    print("  • carte_candidat_tete.html - Vue d'ensemble des gagnants par bureau")
    print("  • carte_participation.html - Taux de participation par bureau")
    print("  • carte_[candidat].html - Résultats détaillés par candidat (top 5)")
    print()
    print("Ouvrez ces fichiers dans votre navigateur pour voir les cartes interactives.")
    print()
    
    # Optionnel: Afficher la première carte
    print("Affichage de la carte du candidat en tête...")
    fig_winner.show()


if __name__ == '__main__':
    main()
