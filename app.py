"""
Application Streamlit de cartographie électorale interactive
Point d'entrée principal
"""
import streamlit as st
from src.config import APP_CONFIG, ELECTIONS_CONFIG, TOUR_MODES, get_available_elections, get_election_label
from src.data_loader import ElectoralDataLoader
from src.visualization import ElectoralMapVisualizer
from src.comparison_visualization import TourComparisonVisualizer
from src.streamlit_app import (
    render_sidebar,
    render_statistics_dashboard,
    render_visualization,
    render_comparison_dashboard,
    render_comparison_visualization,
    initialize_session_state
)

# Configuration de la page
st.set_page_config(**APP_CONFIG)


@st.cache_data(show_spinner="Chargement des données...", hash_funcs={type(None): lambda _: None})
def load_data(election_key: str):
    """
    Charge les données pour une élection donnée (avec cache)
    
    Le cache est différencié par election_key, garantissant que T1 et T2
    utilisent des données séparées.
    
    Args:
        election_key: Clé de l'élection à charger ('municipales_2020_t1' ou 'municipales_2020_t2')
        
    Returns:
        tuple: (geojson_enriched, df_candidates, geojson_bureaux)
    """
    loader = ElectoralDataLoader(election_key=election_key)
    geojson_enriched, df_candidates, geojson_bureaux = loader.load_all_data()
    
    # Log pour vérification (visible dans la console Streamlit)
    candidats_list = df_candidates['CANDIDAT'].unique()
    st.write(f"🔄 [DEBUG] Données chargées pour **{election_key}**")
    st.write(f"   - Candidats: {len(candidats_list)}")
    st.write(f"   - Lignes: {len(df_candidates)}")
    if len(candidats_list) <= 3:
        st.write(f"   - Noms: {', '.join(candidats_list)}")
    
    return geojson_enriched, df_candidates, geojson_bureaux

@st.cache_data(show_spinner="Chargement des données de comparaison...")
def load_comparison_data():
    """
    Charge les données des deux tours pour la comparaison (avec cache)
    
    Returns:
        Dict: {election_key: (geojson_enriched, df_candidates, geojson_bureaux)}
    """
    results = ElectoralDataLoader.load_multiple_elections([
        'municipales_2020_t1',
        'municipales_2020_t2'
    ])
    
    # Afficher un message de confirmation dans les logs
    for key, (_, df, _) in results.items():
        print(f"[CACHE] Comparaison - {key}: {df['CANDIDAT'].nunique()} candidats, {len(df)} lignes")
    
    return results


def main():
    """Fonction principale de l'application"""
    
    # Initialiser l'état de session
    initialize_session_state()
    
    # Titre principal
    st.title("🗳️ Cartographie Électorale - Besançon")
    
    # ========== SÉLECTION DU MODE DE TOUR ==========
    st.markdown("### 🔄 Sélection du mode d'analyse")
    
    tour_mode_options = list(TOUR_MODES.keys())
    tour_mode_labels = [TOUR_MODES[m]['label'] for m in tour_mode_options]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tour_t1_selected = st.button(
            TOUR_MODES['t1']['label'],
            use_container_width=True,
            type='primary' if st.session_state.get('tour_mode', 't1') == 't1' else 'secondary'
        )
        if tour_t1_selected:
            st.session_state.tour_mode = 't1'
    
    with col2:
        tour_t2_selected = st.button(
            TOUR_MODES['t2']['label'],
            use_container_width=True,
            type='primary' if st.session_state.get('tour_mode', 't1') == 't2' else 'secondary'
        )
        if tour_t2_selected:
            st.session_state.tour_mode = 't2'
    
    with col3:
        tour_comparison_selected = st.button(
            TOUR_MODES['comparison']['label'],
            use_container_width=True,
            type='primary' if st.session_state.get('tour_mode', 't1') == 'comparison' else 'secondary'
        )
        if tour_comparison_selected:
            st.session_state.tour_mode = 'comparison'
    
    # Récupérer le mode sélectionné
    tour_mode = st.session_state.get('tour_mode', 't1')
    
    st.caption(TOUR_MODES[tour_mode]['description'])
    
    # Bouton pour vider le cache (utile en développement)
    with st.expander("⚙️ Options avancées"):
        if st.button("🗑️ Vider le cache et recharger", help="Utile si les données ne se mettent pas à jour"):
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    # ========== CHARGEMENT DES DONNÉES SELON LE MODE ==========
    if tour_mode == 'comparison':
        # Mode comparaison : charger les deux tours
        with st.spinner("Chargement des données des deux tours..."):
            try:
                all_data = load_comparison_data()
                data_t1 = all_data['municipales_2020_t1']
                data_t2 = all_data['municipales_2020_t2']
                
                # Créer le visualiseur comparatif
                comparison_visualizer = TourComparisonVisualizer(data_t1, data_t2)
                
                # Afficher le dashboard comparatif
                with st.container():
                    render_comparison_dashboard(comparison_visualizer)
                
                st.divider()
                
                # Afficher les visualisations comparatives
                with st.container():
                    render_comparison_visualization(comparison_visualizer, data_t1, data_t2)
                
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
                import traceback
                st.error(traceback.format_exc())
                st.stop()
    
    else:
        # Mode tour unique (T1 ou T2)
        selected_election = TOUR_MODES[tour_mode]['election_key']
        
        with st.spinner(f"Chargement des données du {TOUR_MODES[tour_mode]['label']}..."):
            try:
                geojson_enriched, df_candidates, geojson_bureaux = load_data(selected_election)
                
                # Créer le visualiseur
                visualizer = ElectoralMapVisualizer(geojson_enriched, df_candidates)
                
                # Créer le loader pour les statistiques et filtres
                loader = ElectoralDataLoader(election_key=selected_election)
                
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
                import traceback
                st.error(traceback.format_exc())
                st.stop()
        
        # Afficher la sidebar avec les filtres
        filters = render_sidebar(df_candidates, geojson_enriched, loader)
        
        # Séparer l'interface en sections
        st.divider()
        
        # 1. Dashboard statistiques (en haut)
        with st.container():
            render_statistics_dashboard(df_candidates, loader, filters, tour_mode=tour_mode)
        
        st.divider()
        
        # 2. Visualisation principale (carte + graphiques)
        with st.container():
            render_visualization(
                visualizer=visualizer,
                loader=loader,
                df_candidates=df_candidates,
                geojson_enriched=geojson_enriched,
                filters=filters
            )
    
    # Footer
    st.divider()
    st.caption("💡 Application développée par Philippe Haag")
    st.caption("📍 Données : Élections municipales de Besançon 2020")


if __name__ == '__main__':
    main()
