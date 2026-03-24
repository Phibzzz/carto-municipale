"""
Module contenant la logique métier de l'application Streamlit
Gestion des filtres, visualisations et interface utilisateur
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple
from src.config import (
    VISUALIZATION_MODES,
    COLOR_SCALES,
    MAP_CONFIG,
    CRITERES_DISPONIBLES,
    DEFAULT_FILTERS,
    TEXTS
)
from src.data_loader import ElectoralDataLoader
from src.visualization import ElectoralMapVisualizer
from src.comparison_visualization import TourComparisonVisualizer, InterElectionComparisonVisualizer, Municipales2026T1T2Comparator
from src.export_manager import ExportManager
from src.vignot_analysis import VignotAnalyzer


def initialize_session_state():
    """Initialise les variables de session Streamlit"""
    if 'filters_applied' not in st.session_state:
        st.session_state.filters_applied = False
    
    if 'selected_mode' not in st.session_state:
        st.session_state.selected_mode = 'winner'


def render_sidebar(df_candidates: pd.DataFrame, geojson_enriched: Dict, loader: ElectoralDataLoader) -> Dict:
    """
    Affiche la sidebar avec tous les filtres et options
    
    Args:
        df_candidates: DataFrame des candidats
        geojson_enriched: GeoJSON enrichi
        loader: Instance du loader pour accès aux méthodes
        
    Returns:
        Dict: Dictionnaire contenant tous les filtres sélectionnés
    """
    with st.sidebar:
        st.header(TEXTS['sidebar_title'])
        
        # ========== SÉLECTION DU MODE DE VISUALISATION ==========
        st.subheader("📊 Mode de visualisation")
        
        mode_options = list(VISUALIZATION_MODES.keys())
        mode_labels = [VISUALIZATION_MODES[m]['label'] for m in mode_options]
        
        selected_mode_idx = st.radio(
            "Choisir un mode",
            range(len(mode_options)),
            format_func=lambda i: mode_labels[i],
            key='visualization_mode',
            label_visibility='collapsed'
        )
        selected_mode = mode_options[selected_mode_idx]
        st.session_state.selected_mode = selected_mode
        
        # Description du mode
        st.caption(VISUALIZATION_MODES[selected_mode]['description'])
        
        st.divider()
        
        # ========== FILTRES ==========
        st.subheader(TEXTS['filters_title'])
        
        filters = {
            'mode': selected_mode,
            'selected_candidates': [],
            'criteria_filters': {},
            'bureau_range': None,
            'min_voix': 0,
            'color_scale': DEFAULT_FILTERS['color_scale'],
            'opacity': DEFAULT_FILTERS['opacity']
        }
        
        # --- Filtre par candidats ---
        if selected_mode in ['by_candidate', 'comparison']:
            st.markdown("**👤 Candidats**")
            
            candidats_list = sorted(df_candidates['CANDIDAT'].unique())
            
            if selected_mode == 'by_candidate':
                # Mode multi-sélection
                selected_candidates = st.multiselect(
                    "Sélectionner un ou plusieurs candidats",
                    options=candidats_list,
                    default=[candidats_list[0]] if candidats_list else [],
                    key='selected_candidates_multi'
                )
                filters['selected_candidates'] = selected_candidates
                
            elif selected_mode == 'comparison':
                # Mode comparaison : exactement 2 candidats
                col1, col2 = st.columns(2)
                with col1:
                    candidat_1 = st.selectbox(
                        "Candidat 1",
                        options=candidats_list,
                        key='candidat_1'
                    )
                with col2:
                    candidat_2 = st.selectbox(
                        "Candidat 2",
                        options=candidats_list,
                        index=min(1, len(candidats_list) - 1),
                        key='candidat_2'
                    )
                filters['selected_candidates'] = [candidat_1, candidat_2]
        
        # --- Filtres par critères (participation, abstention, etc.) ---
        with st.expander("📊 Filtres par critères", expanded=False):
            
            # Participation
            st.markdown("**Taux de participation (%)**")
            participation_range = st.slider(
                "Plage de participation",
                min_value=0,
                max_value=100,
                value=(0, 100),
                key='participation_range',
                label_visibility='collapsed'
            )
            if participation_range != (0, 100):
                filters['criteria_filters']['taux_participation'] = participation_range
            
            # Abstention
            st.markdown("**Taux d'abstention (%)**")
            abstention_range = st.slider(
                "Plage d'abstention",
                min_value=0,
                max_value=100,
                value=(0, 100),
                key='abstention_range',
                label_visibility='collapsed'
            )
            if abstention_range != (0, 100):
                filters['criteria_filters']['taux_abstention'] = abstention_range
            
            # Inscrits
            bureau_data = df_candidates.groupby('NUM_BUREAU').first()
            min_inscrits = int(bureau_data['INSCRITS'].min())
            max_inscrits = int(bureau_data['INSCRITS'].max())
            
            st.markdown("**Nombre d'inscrits**")
            inscrits_range = st.slider(
                "Plage d'inscrits",
                min_value=min_inscrits,
                max_value=max_inscrits,
                value=(min_inscrits, max_inscrits),
                key='inscrits_range',
                label_visibility='collapsed'
            )
            if inscrits_range != (min_inscrits, max_inscrits):
                filters['criteria_filters']['inscrits'] = inscrits_range
            
            # Votants
            min_votants = int(bureau_data['VOTANTS'].min())
            max_votants = int(bureau_data['VOTANTS'].max())
            
            st.markdown("**Nombre de votants**")
            votants_range = st.slider(
                "Plage de votants",
                min_value=min_votants,
                max_value=max_votants,
                value=(min_votants, max_votants),
                key='votants_range',
                label_visibility='collapsed'
            )
            if votants_range != (min_votants, max_votants):
                filters['criteria_filters']['votants'] = votants_range
        
        # --- Filtre par bureaux ---
        with st.expander("🏢 Filtres par bureaux", expanded=False):
            bureaux_list = sorted(df_candidates['NUM_BUREAU'].unique())
            min_bureau = min(bureaux_list)
            max_bureau = max(bureaux_list)
            
            bureau_range = st.slider(
                "Plage de numéros de bureaux",
                min_value=min_bureau,
                max_value=max_bureau,
                value=(min_bureau, max_bureau),
                key='bureau_range'
            )
            
            if bureau_range != (min_bureau, max_bureau):
                filters['bureau_range'] = list(range(bureau_range[0], bureau_range[1] + 1))
        
        # --- Filtre par nombre de voix minimum ---
        if selected_mode == 'by_candidate':
            st.markdown("**Voix minimum**")
            min_voix = st.number_input(
                "Afficher uniquement si > X voix",
                min_value=0,
                max_value=1000,
                value=0,
                step=10,
                key='min_voix',
                label_visibility='collapsed'
            )
            filters['min_voix'] = min_voix
        
        st.divider()
        
        # ========== PARAMÈTRES D'AFFICHAGE ==========
        st.subheader(TEXTS['display_params_title'])
        
        # Palette de couleurs
        if selected_mode in ['by_candidate', 'participation']:
            color_scale_name = st.selectbox(
                "Palette de couleurs",
                options=list(COLOR_SCALES.keys()),
                index=0,
                key='color_scale_select'
            )
            filters['color_scale'] = COLOR_SCALES[color_scale_name]
        
        # Opacité
        opacity = st.slider(
            "Opacité des zones",
            min_value=MAP_CONFIG['min_opacity'],
            max_value=MAP_CONFIG['max_opacity'],
            value=MAP_CONFIG['default_opacity'],
            step=0.1,
            key='opacity_slider'
        )
        filters['opacity'] = opacity
        
        # Bouton de réinitialisation
        st.divider()
        if st.button("🔄 Réinitialiser les filtres", use_container_width=True):
            # Réinitialiser les clés de session
            for key in list(st.session_state.keys()):
                if key not in ['selected_election', 'selected_mode']:
                    del st.session_state[key]
            st.rerun()
        
        return filters


def render_export_section(
    df_candidates: pd.DataFrame,
    loader: ElectoralDataLoader,
    election_label: str,
    tour_mode: str = 't1',
    vignot_analyzer: Optional[VignotAnalyzer] = None
):
    """
    Affiche la section d'export de données dans la sidebar
    
    Args:
        df_candidates: DataFrame des candidats
        loader: Instance du loader
        election_label: Label de l'élection
        tour_mode: Mode du tour ('t1', 't2', 'comparison')
        vignot_analyzer: Optionnel, analyseur pour T1->T2
    """
    with st.sidebar:
        st.divider()
        st.subheader("📥 Exports de données")
        
        st.caption("Générez des fichiers CSV et la documentation complète des statistiques calculées.")
        
        # Bouton principal d'export
        if st.button("📊 Exporter toutes les statistiques", use_container_width=True, type="primary"):
            with st.spinner("Génération des exports en cours..."):
                try:
                    # Créer le gestionnaire d'exports
                    export_manager = ExportManager()
                    
                    # Exporter tous les fichiers
                    exports = export_manager.export_all(
                        df_candidates=df_candidates,
                        loader=loader,
                        election_label=election_label,
                        vignot_analyzer=vignot_analyzer
                    )
                    
                    # Afficher le succès
                    st.success(f"✅ {len(exports)} fichiers générés avec succès !")
                    
                    # Afficher la liste des fichiers
                    with st.expander("📁 Fichiers générés", expanded=True):
                        for name, path in exports.items():
                            st.text(f"• {path.name}")
                        
                        st.info(f"📂 Dossier : `{export_manager.export_folder.absolute()}`")
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'export : {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
        
        # Options d'export détaillées
        with st.expander("⚙️ Exports individuels"):
            st.caption("Exporter des fichiers spécifiques")
            
            export_manager = ExportManager()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Stats générales", use_container_width=True):
                    try:
                        path = export_manager.export_statistiques_generales(
                            df_candidates, loader, election_label
                        )
                        st.success(f"✅ {path.name}")
                    except Exception as e:
                        st.error(f"❌ {str(e)}")
                
                if st.button("🏢 Stats bureaux", use_container_width=True):
                    try:
                        path = export_manager.export_statistiques_par_bureau(
                            df_candidates, election_label
                        )
                        st.success(f"✅ {path.name}")
                    except Exception as e:
                        st.error(f"❌ {str(e)}")
                
                if st.button("👤 Stats candidats", use_container_width=True):
                    try:
                        path = export_manager.export_statistiques_par_candidat(
                            df_candidates, election_label
                        )
                        st.success(f"✅ {path.name}")
                    except Exception as e:
                        st.error(f"❌ {str(e)}")
            
            with col2:
                if st.button("📋 Résultats détaillés", use_container_width=True):
                    try:
                        path = export_manager.export_resultats_detailles(
                            df_candidates, election_label
                        )
                        st.success(f"✅ {path.name}")
                    except Exception as e:
                        st.error(f"❌ {str(e)}")
                
                if vignot_analyzer and st.button("🔄 Évolution T1→T2", use_container_width=True):
                    try:
                        path = export_manager.export_evolution_t1_t2(
                            vignot_analyzer, election_label
                        )
                        st.success(f"✅ {path.name}")
                    except Exception as e:
                        st.error(f"❌ {str(e)}")
                
                if st.button("📖 Documentation", use_container_width=True):
                    try:
                        path = export_manager.generate_documentation_markdown(
                            df_candidates, loader, election_label, vignot_analyzer
                        )
                        st.success(f"✅ {path.name}")
                    except Exception as e:
                        st.error(f"❌ {str(e)}")


def render_statistics_dashboard(df_candidates: pd.DataFrame, loader: ElectoralDataLoader, filters: Dict, tour_mode: str = 't1'):
    """
    Affiche le dashboard avec les statistiques principales
    
    Args:
        df_candidates: DataFrame des candidats
        loader: Instance du loader
        filters: Filtres appliqués
        tour_mode: Mode du tour ('t1', 't2', ou autre)
    """
    # Vérifier si c'est le Tour 2 (Anne VIGNOT uniquement)
    is_tour2 = tour_mode == 't2' or (df_candidates['CANDIDAT'].nunique() == 1 and 
                                       'Anne VIGNOT' in df_candidates['CANDIDAT'].values)
    
    if is_tour2:
        render_vignot_t2_dashboard(df_candidates, loader, filters)
    else:
        render_standard_dashboard(df_candidates, loader, filters)


def render_standard_dashboard(df_candidates: pd.DataFrame, loader: ElectoralDataLoader, filters: Dict):
    """Dashboard standard pour T1 avec plusieurs candidats"""
    st.subheader(TEXTS['stats_title'])
    
    # Calculer les statistiques
    stats = loader.get_statistics(df_candidates)
    
    # KPIs en colonnes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🏢 Bureaux de vote",
            f"{stats['nb_bureaux']:,}",
            help="Nombre total de bureaux de vote"
        )
    
    with col2:
        st.metric(
            "📝 Inscrits",
            f"{stats['total_inscrits']:,}",
            help="Nombre total d'électeurs inscrits"
        )
    
    with col3:
        st.metric(
            "✅ Votants",
            f"{stats['total_votants']:,}",
            help="Nombre total de votants"
        )
    
    with col4:
        st.metric(
            "📊 Participation",
            f"{stats['taux_participation_moyen']:.2f}%",
            help="Taux de participation moyen"
        )
    
    # Top candidats
    st.markdown("---")
    st.markdown("**🏆 Top 5 des candidats**")
    
    top_candidats = dict(list(stats['top_candidats'].items())[:5])
    
    for i, (candidat, voix) in enumerate(top_candidats.items(), 1):
        pourcentage = (voix / stats['total_exprimes']) * 100
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{i}. {candidat}**")
            st.progress(pourcentage / 100)
        with col2:
            st.markdown(f"**{voix:,}** voix")
            st.caption(f"{pourcentage:.2f}%")


def render_vignot_t2_dashboard(df_candidates: pd.DataFrame, loader: ElectoralDataLoader, filters: Dict):
    """Dashboard spécifique pour le Tour 2 (Anne VIGNOT uniquement)"""
    st.subheader("🏆 Résultats Anne VIGNOT - Tour 2")
    
    # Calculer les statistiques
    stats = loader.get_statistics(df_candidates)
    
    # Données spécifiques à Anne VIGNOT
    bureau_data = df_candidates.groupby('NUM_BUREAU').first()
    scores = df_candidates['POURCENTAGE_EXPRIMES']
    
    # Ligne 1 : KPIs généraux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🏢 Bureaux de vote",
            f"{stats['nb_bureaux']:,}",
            help="Nombre total de bureaux de vote"
        )
    
    with col2:
        st.metric(
            "📊 Participation",
            f"{stats['taux_participation_moyen']:.2f}%",
            help="Taux de participation moyen au T2"
        )
    
    with col3:
        st.metric(
            "✅ Votants",
            f"{stats['total_votants']:,}",
            help="Nombre total de votants au T2"
        )
    
    with col4:
        total_voix_vignot = int(df_candidates['VOIX'].sum())
        st.metric(
            "🗳️ Voix obtenues",
            f"{total_voix_vignot:,}",
            help="Total des voix pour Anne VIGNOT"
        )
    
    # Ligne 2 : Performance d'Anne VIGNOT
    st.markdown("---")
    st.markdown("### 📊 Performance d'Anne VIGNOT")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score_moyen = scores.mean()
        st.metric(
            "Score moyen",
            f"{score_moyen:.2f}%",
            help="Score moyen d'Anne VIGNOT sur tous les bureaux"
        )
    
    with col2:
        score_median = scores.median()
        st.metric(
            "Score médian",
            f"{score_median:.2f}%",
            help="Score médian d'Anne VIGNOT"
        )
    
    with col3:
        bureaux_majorite = (scores > 50).sum()
        st.metric(
            "🏆 Majorité absolue",
            f"{bureaux_majorite}/{stats['nb_bureaux']}",
            f"{(bureaux_majorite / stats['nb_bureaux'] * 100):.1f}%",
            help="Bureaux avec plus de 50% des voix"
        )
    
    with col4:
        ecart_type = scores.std()
        st.metric(
            "Dispersion",
            f"{ecart_type:.2f}",
            help="Écart-type des scores (mesure de dispersion)"
        )
    
    # Ligne 3 : Extrêmes
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        score_max = scores.max()
        bureau_max = df_candidates.loc[scores.idxmax(), 'NUM_BUREAU']
        st.success(f"**🔝 Meilleur score:** {score_max:.2f}% (Bureau {int(bureau_max)})")
    
    with col2:
        score_min = scores.min()
        bureau_min = df_candidates.loc[scores.idxmin(), 'NUM_BUREAU']
        st.info(f"**📉 Score le plus faible:** {score_min:.2f}% (Bureau {int(bureau_min)})")
    
    # Distribution des scores
    st.markdown("---")
    st.markdown("### 📈 Distribution des scores")
    
    # Créer des catégories de scores
    categories = {
        'Très fort (>60%)': (scores > 60).sum(),
        'Fort (50-60%)': ((scores >= 50) & (scores <= 60)).sum(),
        'Modéré (40-50%)': ((scores >= 40) & (scores < 50)).sum(),
        'Faible (<40%)': (scores < 40).sum()
    }
    
    col1, col2, col3, col4 = st.columns(4)
    
    for col, (label, count) in zip([col1, col2, col3, col4], categories.items()):
        with col:
            percentage = (count / stats['nb_bureaux'] * 100)
            st.metric(label, f"{count}", f"{percentage:.1f}%")


def render_visualization(
    visualizer: ElectoralMapVisualizer,
    loader: ElectoralDataLoader,
    df_candidates: pd.DataFrame,
    geojson_enriched: Dict,
    filters: Dict
):
    """
    Affiche la visualisation selon le mode sélectionné
    
    Args:
        visualizer: Instance du visualiseur
        loader: Instance du loader
        df_candidates: DataFrame des candidats
        geojson_enriched: GeoJSON enrichi
        filters: Filtres appliqués
    """
    mode = filters['mode']
    
    st.subheader(f"{VISUALIZATION_MODES[mode]['icon']} {VISUALIZATION_MODES[mode]['label']}")
    
    # Appliquer les filtres sur les données
    geojson_filtered = apply_filters_to_geojson(geojson_enriched, filters, loader)
    df_filtered = apply_filters_to_dataframe(df_candidates, filters, loader)
    
    # Afficher le nombre de bureaux après filtrage
    nb_bureaux_filtered = len(geojson_filtered['features'])
    nb_bureaux_total = len(geojson_enriched['features'])
    
    if nb_bureaux_filtered < nb_bureaux_total:
        st.info(f"📊 {nb_bureaux_filtered} bureaux affichés sur {nb_bureaux_total} (filtres appliqués)")
    
    # Vérifier qu'il reste des données
    if nb_bureaux_filtered == 0:
        st.warning("⚠️ Aucun bureau ne correspond aux filtres sélectionnés. Veuillez ajuster vos critères.")
        return
    
    # Créer un visualiseur avec les données filtrées
    visualizer_filtered = ElectoralMapVisualizer(geojson_filtered, df_filtered)
    
    # Rendu selon le mode
    if mode == 'winner':
        render_winner_mode(visualizer_filtered, filters)
    
    elif mode == 'participation':
        render_participation_mode(visualizer_filtered, filters)
    
    elif mode == 'by_candidate':
        render_by_candidate_mode(visualizer_filtered, filters)
    
    elif mode == 'comparison':
        render_comparison_mode(visualizer_filtered, filters)


def apply_filters_to_geojson(geojson: Dict, filters: Dict, loader: ElectoralDataLoader) -> Dict:
    """
    Applique les filtres au GeoJSON
    
    Args:
        geojson: GeoJSON original
        filters: Filtres à appliquer
        loader: Instance du loader
        
    Returns:
        Dict: GeoJSON filtré
    """
    # Construire les filtres de critères
    criteria_filters = filters.get('criteria_filters', {})
    bureau_range = filters.get('bureau_range')
    
    # Appliquer les filtres
    return loader.filter_geojson_by_criteria(
        geojson,
        criteria_filters=criteria_filters if criteria_filters else None,
        bureau_numbers=bureau_range
    )


def apply_filters_to_dataframe(df: pd.DataFrame, filters: Dict, loader: ElectoralDataLoader) -> pd.DataFrame:
    """
    Applique les filtres au DataFrame
    
    Args:
        df: DataFrame original
        filters: Filtres à appliquer
        loader: Instance du loader
        
    Returns:
        pd.DataFrame: DataFrame filtré
    """
    candidat_names = filters.get('selected_candidates')
    bureau_range = filters.get('bureau_range')
    min_voix = filters.get('min_voix', 0)
    
    return loader.filter_candidates_data(
        df,
        candidat_names=candidat_names if candidat_names else None,
        bureau_numbers=bureau_range,
        min_voix=min_voix
    )


# ========== MODES DE VISUALISATION ==========

def render_winner_mode(visualizer: ElectoralMapVisualizer, filters: Dict):
    """Affiche la carte du candidat en tête par bureau"""
    
    fig = visualizer.create_choropleth_winner()
    
    # Appliquer l'opacité
    for trace in fig.data:
        trace.marker.opacity = filters['opacity']
    
    st.plotly_chart(fig, use_container_width=True, key='winner_map')
    
    # Graphiques complémentaires
    with st.expander("📈 Graphiques complémentaires", expanded=False):
        render_winner_charts(visualizer)


def render_participation_mode(visualizer: ElectoralMapVisualizer, filters: Dict):
    """Affiche la carte du taux de participation"""
    
    fig = visualizer.create_choropleth_participation()
    
    # Appliquer l'opacité et la palette
    for trace in fig.data:
        trace.marker.opacity = filters['opacity']
        trace.colorscale = filters['color_scale']
    
    st.plotly_chart(fig, use_container_width=True, key='participation_map')
    
    # Graphiques complémentaires
    with st.expander("📈 Graphiques complémentaires", expanded=False):
        render_participation_charts(visualizer)


def render_by_candidate_mode(visualizer: ElectoralMapVisualizer, filters: Dict):
    """Affiche la carte par candidat(s)"""
    
    selected_candidates = filters.get('selected_candidates', [])
    
    if not selected_candidates:
        st.warning("⚠️ Veuillez sélectionner au moins un candidat dans la barre latérale.")
        return
    
    # Si plusieurs candidats, afficher en colonnes
    if len(selected_candidates) == 1:
        candidat = selected_candidates[0]
        fig = visualizer.create_choropleth_by_candidate(candidat, color_scale=filters['color_scale'])
        
        # Appliquer l'opacité
        for trace in fig.data:
            trace.marker.opacity = filters['opacity']
        
        st.plotly_chart(fig, use_container_width=True, key=f'candidate_map_{candidat}')
        
        # Graphiques complémentaires
        with st.expander("📈 Graphiques complémentaires", expanded=False):
            render_candidate_charts(visualizer, candidat)
    
    else:
        # Afficher plusieurs candidats en grille
        num_cols = min(2, len(selected_candidates))
        
        for i in range(0, len(selected_candidates), num_cols):
            cols = st.columns(num_cols)
            
            for j, col in enumerate(cols):
                if i + j < len(selected_candidates):
                    candidat = selected_candidates[i + j]
                    
                    with col:
                        st.markdown(f"**{candidat}**")
                        fig = visualizer.create_choropleth_by_candidate(
                            candidat,
                            color_scale=filters['color_scale']
                        )
                        
                        # Réduire la hauteur pour les multiples cartes
                        fig.update_layout(height=500)
                        
                        # Appliquer l'opacité
                        for trace in fig.data:
                            trace.marker.opacity = filters['opacity']
                        
                        st.plotly_chart(fig, use_container_width=True, key=f'candidate_map_{candidat}')


def render_comparison_mode(visualizer: ElectoralMapVisualizer, filters: Dict):
    """Affiche la comparaison entre deux candidats"""
    
    selected_candidates = filters.get('selected_candidates', [])
    
    if len(selected_candidates) != 2:
        st.warning("⚠️ Veuillez sélectionner exactement 2 candidats dans la barre latérale.")
        return
    
    candidat_1, candidat_2 = selected_candidates
    
    # Afficher les deux cartes côte à côte
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{candidat_1}**")
        fig1 = visualizer.create_choropleth_by_candidate(candidat_1, color_scale='Reds')
        fig1.update_layout(height=600)
        
        for trace in fig1.data:
            trace.marker.opacity = filters['opacity']
        
        st.plotly_chart(fig1, use_container_width=True, key=f'comparison_map_1')
    
    with col2:
        st.markdown(f"**{candidat_2}**")
        fig2 = visualizer.create_choropleth_by_candidate(candidat_2, color_scale='Blues')
        fig2.update_layout(height=600)
        
        for trace in fig2.data:
            trace.marker.opacity = filters['opacity']
        
        st.plotly_chart(fig2, use_container_width=True, key=f'comparison_map_2')
    
    # Graphiques de comparaison
    st.markdown("---")
    st.markdown("**📊 Analyse comparative**")
    render_comparison_charts(visualizer, candidat_1, candidat_2)


# ========== GRAPHIQUES COMPLÉMENTAIRES ==========

def render_winner_charts(visualizer: ElectoralMapVisualizer):
    """Graphiques complémentaires pour le mode 'candidat en tête'"""
    
    # Compter le nombre de bureaux gagnés par candidat
    bureaux_gagnes = {}
    
    for feature in visualizer.geojson['features']:
        candidat_tete = feature['properties'].get('candidat_tete', {})
        if candidat_tete:
            nom = candidat_tete['nom']
            bureaux_gagnes[nom] = bureaux_gagnes.get(nom, 0) + 1
    
    # Créer un graphique en barres
    df_chart = pd.DataFrame(list(bureaux_gagnes.items()), columns=['Candidat', 'Bureaux gagnés'])
    df_chart = df_chart.sort_values('Bureaux gagnés', ascending=True)
    
    fig = go.Figure(go.Bar(
        x=df_chart['Bureaux gagnés'],
        y=df_chart['Candidat'],
        orientation='h',
        marker=dict(color='#377eb8')
    ))
    
    fig.update_layout(
        title="Nombre de bureaux gagnés par candidat",
        xaxis_title="Nombre de bureaux",
        yaxis_title="Candidat",
        height=max(400, len(df_chart) * 30)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_participation_charts(visualizer: ElectoralMapVisualizer):
    """Graphiques complémentaires pour le mode 'participation'"""
    
    # Extraire les taux de participation
    taux_participation = []
    
    for feature in visualizer.geojson['features']:
        taux = 100 - feature['properties'].get('taux_abstention', 0)
        taux_participation.append(taux)
    
    # Histogramme de distribution
    fig = go.Figure(go.Histogram(
        x=taux_participation,
        nbinsx=20,
        marker=dict(color='#4daf4a'),
        name='Taux de participation'
    ))
    
    fig.update_layout(
        title="Distribution des taux de participation",
        xaxis_title="Taux de participation (%)",
        yaxis_title="Nombre de bureaux",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_candidate_charts(visualizer: ElectoralMapVisualizer, candidat: str):
    """Graphiques complémentaires pour un candidat spécifique"""
    
    # Extraire les pourcentages du candidat
    pourcentages = []
    bureaux = []
    
    for feature in visualizer.geojson['features']:
        num_bureau = feature['properties']['NUM_BUREAU']
        candidats_list = feature['properties'].get('candidats', [])
        
        for c in candidats_list:
            if c['nom'] == candidat:
                pourcentages.append(c['pourcentage_exprimes'])
                bureaux.append(num_bureau)
                break
    
    # Graphique en barres
    df_chart = pd.DataFrame({'Bureau': bureaux, 'Pourcentage': pourcentages})
    df_chart = df_chart.sort_values('Pourcentage', ascending=True)
    
    fig = go.Figure(go.Bar(
        x=df_chart['Pourcentage'],
        y=df_chart['Bureau'].astype(str),
        orientation='h',
        marker=dict(color='#e41a1c')
    ))
    
    fig.update_layout(
        title=f"Résultats de {candidat} par bureau",
        xaxis_title="Pourcentage (%)",
        yaxis_title="Bureau",
        height=max(400, len(df_chart) * 20)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_comparison_charts(visualizer: ElectoralMapVisualizer, candidat_1: str, candidat_2: str):
    """Graphiques de comparaison entre deux candidats"""
    
    # Extraire les données des deux candidats
    data_comparison = []
    
    for feature in visualizer.geojson['features']:
        num_bureau = feature['properties']['NUM_BUREAU']
        candidats_list = feature['properties'].get('candidats', [])
        
        voix_1 = 0
        voix_2 = 0
        
        for c in candidats_list:
            if c['nom'] == candidat_1:
                voix_1 = c['pourcentage_exprimes']
            elif c['nom'] == candidat_2:
                voix_2 = c['pourcentage_exprimes']
        
        data_comparison.append({
            'Bureau': num_bureau,
            candidat_1: voix_1,
            candidat_2: voix_2,
            'Écart': voix_1 - voix_2
        })
    
    df_comparison = pd.DataFrame(data_comparison)
    
    # Graphique 1: Comparaison côte à côte
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            name=candidat_1,
            x=df_comparison['Bureau'].astype(str),
            y=df_comparison[candidat_1],
            marker=dict(color='#e41a1c')
        ))
        fig1.add_trace(go.Bar(
            name=candidat_2,
            x=df_comparison['Bureau'].astype(str),
            y=df_comparison[candidat_2],
            marker=dict(color='#377eb8')
        ))
        
        fig1.update_layout(
            title="Comparaison par bureau",
            xaxis_title="Bureau",
            yaxis_title="Pourcentage (%)",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Graphique 2: Écart
        df_sorted = df_comparison.sort_values('Écart')
        
        fig2 = go.Figure(go.Bar(
            x=df_sorted['Écart'],
            y=df_sorted['Bureau'].astype(str),
            orientation='h',
            marker=dict(
                color=df_sorted['Écart'],
                colorscale='RdBu',
                cmid=0
            )
        ))
        
        fig2.update_layout(
            title=f"Écart {candidat_1} - {candidat_2}",
            xaxis_title="Écart (points %)",
            yaxis_title="Bureau",
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)


# ========== FONCTIONS POUR LA COMPARAISON ENTRE TOURS ==========

def render_comparison_dashboard(comparison_visualizer: TourComparisonVisualizer):
    """
    Affiche le dashboard comparatif centré sur Anne VIGNOT
    
    Args:
        comparison_visualizer: Instance du visualiseur comparatif
    """
    st.subheader("🏆 Évolution Anne VIGNOT : Tour 1 → Tour 2")
    
    # Obtenir les statistiques d'évolution
    vignot_stats = comparison_visualizer.vignot_analyzer.get_evolution_statistics()
    
    # Ligne 1 : Performance
    st.markdown("### 📊 Performance")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Score T1",
            f"{vignot_stats['score_moyen_t1']:.2f}%",
            help="Score moyen au premier tour"
        )
    
    with col2:
        st.metric(
            "Score T2",
            f"{vignot_stats['score_moyen_t2']:.2f}%",
            delta=f"{vignot_stats['evolution_moyenne_abs']:+.2f}%",
            help="Score moyen au second tour"
        )
    
    with col3:
        st.metric(
            "Ratio moyen",
            f"{vignot_stats['ratio_performance_moyen']:.2f}x",
            help="Ratio Score T2 / Score T1"
        )
    
    with col4:
        st.metric(
            "Évolution",
            f"{vignot_stats['evolution_moyenne_rel']:+.1f}%",
            help="Progression relative moyenne"
        )
    
    # Ligne 2 : Géographie
    st.markdown("### 🗺️ Géographie")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🏢 Bureaux totaux",
            f"{vignot_stats['bureaux_total']}"
        )
    
    with col2:
        st.metric(
            "🏆 Majorité T1",
            f"{vignot_stats['bureaux_majorite_t1']}",
            help="Bureaux avec >50% au T1"
        )
    
    with col3:
        st.metric(
            "🏆 Majorité T2",
            f"{vignot_stats['bureaux_majorite_t2']}",
            delta=f"{vignot_stats['bureaux_majorite_t2'] - vignot_stats['bureaux_majorite_t1']:+d}",
            help="Bureaux avec >50% au T2"
        )
    
    with col4:
        st.metric(
            "📈 Meilleur bureau",
            f"{vignot_stats['bureau_max_t2']}",
            f"{vignot_stats['score_max_t2']:.1f}%",
            help="Bureau avec le meilleur score au T2"
        )
    
    # Ligne 3 : Mobilisation
    st.markdown("### ⚡ Mobilisation")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Voix T1",
            f"{vignot_stats['total_voix_t1']:,}"
        )
    
    with col2:
        st.metric(
            "Voix T2",
            f"{vignot_stats['total_voix_t2']:,}",
            delta=f"{vignot_stats['total_voix_gagnees']:+,}",
            help="Nombre total de voix obtenues"
        )
    
    with col3:
        st.metric(
            "Participation T1",
            f"{vignot_stats['participation_moyenne_t1']:.2f}%"
        )
    
    with col4:
        st.metric(
            "Participation T2",
            f"{vignot_stats['participation_moyenne_t2']:.2f}%",
            delta=f"{vignot_stats['evolution_participation_moyenne']:+.2f}%"
        )
    
    # Ligne 4 : Extrêmes
    st.markdown("### 📊 Amplitude")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**🚀 Plus forte progression:** Bureau {vignot_stats['bureau_progression_max']} "
                f"({vignot_stats['progression_max']:+.2f} points)")
    
    with col2:
        if vignot_stats['progression_min'] < 0:
            st.warning(f"**📉 Plus forte régression:** Bureau {vignot_stats['bureau_progression_min']} "
                      f"({vignot_stats['progression_min']:+.2f} points)")
        else:
            st.success(f"**✅ Progression minimale:** Bureau {vignot_stats['bureau_progression_min']} "
                      f"({vignot_stats['progression_min']:+.2f} points)")


def render_comparison_visualization(
    comparison_visualizer: TourComparisonVisualizer,
    data_t1: Tuple,
    data_t2: Tuple
):
    """
    Affiche les visualisations comparatives centrées sur Anne VIGNOT
    
    Args:
        comparison_visualizer: Instance du visualiseur comparatif
        data_t1: Données du tour 1
        data_t2: Données du tour 2
    """
    st.subheader("🗺️ Analyses Comparatives - Anne VIGNOT")
    
    # Tabs pour organiser les visualisations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Évolution Scores",
        "💪 Ratios Performance",
        "🗺️ Bastions",
        "⚡ Impact Participation",
        "🎯 Analyses Avancées"
    ])
    
    with tab1:
        st.markdown("### 📈 Évolution du score d'Anne VIGNOT par bureau")
        
        # Carte d'évolution
        fig_evolution = comparison_visualizer.create_vignot_evolution_map()
        st.plotly_chart(fig_evolution, use_container_width=True, key='vignot_evolution_map')
        
        # Graphique des progressions/régressions
        st.markdown("---")
        st.markdown("### 📊 Top 10 progressions et régressions")
        
        fig_bars = comparison_visualizer.create_evolution_bars_chart(n=10)
        st.plotly_chart(fig_bars, use_container_width=True, key='evolution_bars')
        
        # Statistiques détaillées
        with st.expander("📋 Voir les statistiques détaillées"):
            stats = comparison_visualizer.vignot_analyzer.get_evolution_statistics()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Scores moyens**")
                st.write(f"• T1: {stats['score_moyen_t1']:.2f}%")
                st.write(f"• T2: {stats['score_moyen_t2']:.2f}%")
                st.write(f"• Médiane T1: {stats['score_median_t1']:.2f}%")
                st.write(f"• Médiane T2: {stats['score_median_t2']:.2f}%")
            
            with col2:
                st.markdown("**Dispersion**")
                st.write(f"• Écart-type T1: {stats['ecart_type_t1']:.2f}")
                st.write(f"• Écart-type T2: {stats['ecart_type_t2']:.2f}")
                st.write(f"• Progression max: {stats['progression_max']:+.2f}%")
                st.write(f"• Progression min: {stats['progression_min']:+.2f}%")
            
            with col3:
                st.markdown("**Extrêmes**")
                st.write(f"• Max T1: {stats['score_max_t1']:.2f}% (Bureau {stats['bureau_max_t1']})")
                st.write(f"• Max T2: {stats['score_max_t2']:.2f}% (Bureau {stats['bureau_max_t2']})")
                st.write(f"• Min T1: {stats['score_min_t1']:.2f}%")
                st.write(f"• Min T2: {stats['score_min_t2']:.2f}%")
    
    with tab2:
        st.markdown("### 💪 Ratios de Performance (T2/T1)")
        
        # Carte des ratios
        fig_ratio = comparison_visualizer.create_ratio_performance_map()
        st.plotly_chart(fig_ratio, use_container_width=True, key='ratio_map')
        
        # Statistiques des ratios
        st.markdown("---")
        st.markdown("### 📊 Distribution des ratios")
        
        evolution_data = comparison_visualizer.vignot_analyzer.evolution_data
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogramme des ratios
            fig_hist = go.Figure(go.Histogram(
                x=evolution_data['RATIO_PERFORMANCE'],
                nbinsx=20,
                marker=dict(color='#4daf4a'),
                name='Ratios'
            ))
            
            fig_hist.update_layout(
                title="Distribution des ratios de performance",
                xaxis_title="Ratio T2/T1",
                yaxis_title="Nombre de bureaux",
                height=400
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Box plot
            fig_box = go.Figure(go.Box(
                y=evolution_data['RATIO_PERFORMANCE'],
                name='Ratios',
                marker=dict(color='#377eb8')
            ))
            
            fig_box.update_layout(
                title="Statistiques des ratios",
                yaxis_title="Ratio T2/T1",
                height=400
            )
            
            st.plotly_chart(fig_box, use_container_width=True)
    
    with tab3:
        st.markdown("### 🗺️ Cartographie des Bastions")
        
        # Carte des bastions
        fig_bastions = comparison_visualizer.create_bastions_map()
        st.plotly_chart(fig_bastions, use_container_width=True, key='bastions_map')
        
        # Matrice quadrant
        st.markdown("---")
        st.markdown("### 📊 Matrice Score T1 vs Score T2")
        
        fig_quadrant = comparison_visualizer.create_quadrant_chart()
        st.plotly_chart(fig_quadrant, use_container_width=True, key='quadrant_chart')
        
        # Statistiques par catégorie
        st.markdown("---")
        st.markdown("### 📋 Statistiques par catégorie")
        
        stats_by_category = comparison_visualizer.vignot_analyzer.get_performance_by_category()
        
        # Afficher le tableau
        st.dataframe(
            stats_by_category.style.format({
                'Score_moyen_T1': '{:.2f}%',
                'Score_moyen_T2': '{:.2f}%',
                'Evolution_moyenne': '{:+.2f}%',
                'Ratio_moyen': '{:.2f}x',
                'Total_voix_gagnees': '{:+,.0f}'
            }),
            use_container_width=True
        )
        
        # Définitions des catégories
        with st.expander("ℹ️ Définition des catégories"):
            st.markdown("""
            - **Bastion** 🏰 : Fort au T1 (≥40%) et confirmé au T2 (≥50%)
            - **Conquête** 🚀 : Faible au T1 (<40%) mais fort au T2 (≥50%)
            - **Disputé** ⚖️ : Scores moyens aux deux tours (30-50% T1, 40-60% T2)
            - **Défavorable** 📉 : Faible aux deux tours
            """)
    
    with tab4:
        st.markdown("### ⚡ Impact de la Participation sur le Score")
        
        # Scatter plot de corrélation
        fig_correlation = comparison_visualizer.create_participation_correlation_scatter()
        st.plotly_chart(fig_correlation, use_container_width=True, key='correlation_scatter')
        
        # Analyse de la corrélation
        st.markdown("---")
        st.markdown("### 📊 Analyse de corrélation")
        
        correlation_data = comparison_visualizer.vignot_analyzer.calculate_participation_correlation()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Coefficient de corrélation**")
            st.metric(
                "Corrélation Pearson",
                f"{correlation_data['coefficient']:.3f}",
                help="Entre -1 et 1. Proche de 1 = forte corrélation positive"
            )
            st.info(f"**Interprétation:** {correlation_data['interpretation']}")
        
        with col2:
            st.markdown("**Répartition des bureaux**")
            st.write(f"• 📈📈 Participation ↗ et Score ↗ : **{correlation_data['bureaux_participation_hausse_score_hausse']}** bureaux")
            st.write(f"• 📈📉 Participation ↗ et Score ↘ : **{correlation_data['bureaux_participation_hausse_score_baisse']}** bureaux")
            st.write(f"• 📉📈 Participation ↘ et Score ↗ : **{correlation_data['bureaux_participation_baisse_score_hausse']}** bureaux")
            st.write(f"• 📉📉 Participation ↘ et Score ↘ : **{correlation_data['bureaux_participation_baisse_score_baisse']}** bureaux")
        
        # Carte d'évolution de la participation (legacy)
        st.markdown("---")
        st.markdown("### 🗺️ Carte d'évolution de la participation")
        
        fig_participation = comparison_visualizer.create_participation_evolution_map()
        st.plotly_chart(fig_participation, use_container_width=True, key='participation_map')
    
    with tab5:
        st.markdown("### 🎯 Analyses Avancées")
        
        # Graphique en cascade
        st.markdown("#### 💧 Décomposition de la progression")
        
        fig_waterfall = comparison_visualizer.create_waterfall_chart()
        st.plotly_chart(fig_waterfall, use_container_width=True, key='waterfall_chart')
        
        st.info("ℹ️ Ce graphique décompose la progression moyenne du score en différentes contributions estimées.")
        
        # Outliers
        st.markdown("---")
        st.markdown("#### 🎯 Bureaux atypiques (outliers)")
        
        outliers = comparison_visualizer.vignot_analyzer.identify_outliers(threshold_std=1.5)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🚀 Fortes progressions**")
            if len(outliers['forte_progression']) > 0:
                st.dataframe(
                    outliers['forte_progression'].style.format({
                        'SCORE_T1': '{:.2f}%',
                        'SCORE_T2': '{:.2f}%',
                        'EVOLUTION_ABS': '{:+.2f}%'
                    }),
                    use_container_width=True
                )
            else:
                st.write("Aucun outlier détecté")
        
        with col2:
            st.markdown("**📉 Fortes régressions**")
            if len(outliers['forte_regression']) > 0:
                st.dataframe(
                    outliers['forte_regression'].style.format({
                        'SCORE_T1': '{:.2f}%',
                        'SCORE_T2': '{:.2f}%',
                        'EVOLUTION_ABS': '{:+.2f}%'
                    }),
                    use_container_width=True
                )
            else:
                st.write("Aucun outlier détecté")
        
        # Comparaison cartes côte à côte (pour contexte)
        st.markdown("---")
        st.markdown("#### 🗺️ Comparaison visuelle : Cartes T1 vs T2")
        
        geojson_t1, df_t1, _ = data_t1
        geojson_t2, df_t2, _ = data_t2
        
        visualizer_t1 = ElectoralMapVisualizer(geojson_t1, df_t1)
        visualizer_t2 = ElectoralMapVisualizer(geojson_t2, df_t2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Tour 1 - Tous candidats**")
            fig_t1 = visualizer_t1.create_choropleth_winner()
            fig_t1.update_layout(height=500)
            st.plotly_chart(fig_t1, use_container_width=True, key='comparison_map_t1')
        
        with col2:
            st.markdown("**Tour 2 - Anne VIGNOT**")
            # Créer une carte du score d'Anne VIGNOT au T2
            df_vignot_t1 = df_t1[df_t1['CANDIDAT'] == 'Anne VIGNOT']
            fig_t2 = visualizer_t1.create_choropleth_by_candidate('Anne VIGNOT', color_scale='Greens')
            fig_t2.update_layout(height=500, title=dict(text='<b>Score Anne VIGNOT au T1</b>'))
            st.plotly_chart(fig_t2, use_container_width=True, key='comparison_vignot_t1')


# =============================================================================
# REPORT DE VOIX — Véziès & Friess → Vignot (T1 2026)
# =============================================================================

def _map_center_from_geojson(geojson: Dict) -> Dict:
    """Calcule le centre moyen de la carte à partir des features GeoJSON."""
    lons, lats = [], []
    for feature in geojson['features']:
        coords = feature['geometry']['coordinates']
        geom_type = feature['geometry']['type']
        if geom_type == 'Polygon':
            for ring in coords:
                for p in ring:
                    lons.append(p[0]); lats.append(p[1])
        elif geom_type == 'MultiPolygon':
            for polygon in coords:
                for ring in polygon:
                    for p in ring:
                        lons.append(p[0]); lats.append(p[1])
    return {'lat': sum(lats) / len(lats), 'lon': sum(lons) / len(lons)}


def render_vote_transfer_analysis(df_candidates: pd.DataFrame, geojson_enriched: Dict):
    """
    Visualisation interactive du report de voix de Séverine Véziès et Nicole Friess
    vers Anne Vignot au second tour de 2026.

    Un slider permet d'ajuster le taux de report (0–100 %) et recalcule en temps réel
    les scores projetés bureau par bureau.
    """
    st.subheader("🔁 Simulation de report de voix — Véziès & Friess → Vignot")
    st.caption(
        "Cette simulation estime le score d'Anne Vignot au second tour en supposant "
        "qu'un certain pourcentage des voix de Séverine Véziès et de Nicole Friess "
        "se reporterait en sa faveur."
    )

    NOM_VIGNOT = 'Anne Vignot'
    NOM_FAGAUT = 'Ludovic Fagaut'
    NOM_VEZIÈS = 'Séverine Véziès'
    NOM_FRIESS = 'Nicole Friess'

    candidats_dispo = set(df_candidates['CANDIDAT'].unique())
    if not {NOM_VIGNOT, NOM_FAGAUT}.issubset(candidats_dispo):
        st.warning("Données insuffisantes pour cette analyse (Vignot ou Fagaut absent).")
        return

    # --------------------------------------------------------
    # Construction du DataFrame de base bureau × candidat
    # --------------------------------------------------------
    bureaux_base = (
        df_candidates.groupby('NUM_BUREAU')
        .first()[['INSCRITS', 'VOTANTS', 'EXPRIMES']]
        .reset_index()
    )

    def _voix_bureau(nom, alias):
        sub = df_candidates[df_candidates['CANDIDAT'] == nom][
            ['NUM_BUREAU', 'VOIX', 'POURCENTAGE_EXPRIMES']
        ].copy()
        sub.columns = ['NUM_BUREAU', f'VOIX_{alias}', f'PCT_{alias}']
        return sub

    df_analysis = bureaux_base.copy()
    df_analysis = df_analysis.merge(_voix_bureau(NOM_VIGNOT, 'VIGNOT'), on='NUM_BUREAU', how='left')
    df_analysis = df_analysis.merge(_voix_bureau(NOM_FAGAUT, 'FAGAUT'), on='NUM_BUREAU', how='left')

    if NOM_VEZIÈS in candidats_dispo:
        df_analysis = df_analysis.merge(_voix_bureau(NOM_VEZIÈS, 'VEZIÈS'), on='NUM_BUREAU', how='left')
    else:
        df_analysis['VOIX_VEZIÈS'] = 0; df_analysis['PCT_VEZIÈS'] = 0.0

    if NOM_FRIESS in candidats_dispo:
        df_analysis = df_analysis.merge(_voix_bureau(NOM_FRIESS, 'FRIESS'), on='NUM_BUREAU', how='left')
    else:
        df_analysis['VOIX_FRIESS'] = 0; df_analysis['PCT_FRIESS'] = 0.0

    df_analysis = df_analysis.fillna(0)

    # --------------------------------------------------------
    # Slider de taux de report
    # --------------------------------------------------------
    taux_pct = st.slider(
        "Taux de report Véziès + Friess → Vignot (%)",
        min_value=0, max_value=100, value=50, step=5,
        help="50 % signifie que la moitié des voix de Véziès et Friess se reportent sur Vignot."
    )
    taux = taux_pct / 100.0

    # --------------------------------------------------------
    # Calculs projetés
    # --------------------------------------------------------
    df_analysis['VOIX_REPORT'] = (df_analysis['VOIX_VEZIÈS'] + df_analysis['VOIX_FRIESS']) * taux
    df_analysis['VOIX_VIGNOT_PROJ'] = df_analysis['VOIX_VIGNOT'] + df_analysis['VOIX_REPORT']
    df_analysis['PCT_VIGNOT_PROJ'] = df_analysis.apply(
        lambda r: r['VOIX_VIGNOT_PROJ'] / r['EXPRIMES'] * 100 if r['EXPRIMES'] > 0 else 0.0, axis=1
    )
    df_analysis['ECART_PROJ'] = df_analysis['PCT_VIGNOT_PROJ'] - df_analysis['PCT_FAGAUT']
    df_analysis['VIGNOT_EN_TETE'] = df_analysis['ECART_PROJ'] > 0
    df_analysis['VIGNOT_EN_TETE_ACTUEL'] = df_analysis['PCT_VIGNOT'] > df_analysis['PCT_FAGAUT']

    # Totaux
    total_exprimes  = df_analysis['EXPRIMES'].sum()
    total_vignot    = df_analysis['VOIX_VIGNOT'].sum()
    total_fagaut    = df_analysis['VOIX_FAGAUT'].sum()
    total_veziès    = df_analysis['VOIX_VEZIÈS'].sum()
    total_friess    = df_analysis['VOIX_FRIESS'].sum()
    total_report    = (total_veziès + total_friess) * taux
    total_vignot_p  = total_vignot + total_report

    score_actuel = total_vignot / total_exprimes * 100 if total_exprimes > 0 else 0
    score_proj   = total_vignot_p / total_exprimes * 100 if total_exprimes > 0 else 0
    score_fagaut = total_fagaut / total_exprimes * 100 if total_exprimes > 0 else 0
    ecart_global = score_proj - score_fagaut

    bv_en_tete_actuel = int(df_analysis['VIGNOT_EN_TETE_ACTUEL'].sum())
    bv_en_tete_proj   = int(df_analysis['VIGNOT_EN_TETE'].sum())
    nb_bureaux = len(df_analysis)
    voix_manquantes = max(0.0, total_fagaut - total_vignot_p)

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------
    st.markdown("### 📊 Résultats globaux projetés")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Score actuel Vignot", f"{score_actuel:.2f}%",
                  help="Score réel au T1 2026")
    with c2:
        st.metric("Score projeté Vignot", f"{score_proj:.2f}%",
                  delta=f"{score_proj - score_actuel:+.2f} pts")
    with c3:
        st.metric("Score Fagaut (inchangé)", f"{score_fagaut:.2f}%")
    with c4:
        label_ecart = "✅ Vignot en tête" if ecart_global > 0 else "❌ Vignot en retard"
        st.metric("Écart Vignot − Fagaut", f"{ecart_global:+.2f}%",
                  delta=label_ecart,
                  delta_color="normal" if ecart_global > 0 else "inverse")

    c5, c6, c7 = st.columns(3)
    with c5:
        st.metric("Bureaux Vignot en tête (actuel)",
                  f"{bv_en_tete_actuel} / {nb_bureaux}")
    with c6:
        st.metric("Bureaux Vignot en tête (projeté)",
                  f"{bv_en_tete_proj} / {nb_bureaux}",
                  delta=f"{bv_en_tete_proj - bv_en_tete_actuel:+d} bureaux")
    with c7:
        if voix_manquantes > 0:
            st.metric("Voix manquantes pour dépasser Fagaut",
                      f"{int(voix_manquantes):,}",
                      delta="Insuffisant",
                      delta_color="inverse")
        else:
            st.metric("Avance projetée sur Fagaut",
                      f"+{int(total_vignot_p - total_fagaut):,} voix",
                      delta="En tête",
                      delta_color="normal")

    # --------------------------------------------------------
    # Onglets de visualisation
    # --------------------------------------------------------
    st.markdown("---")
    map_center = _map_center_from_geojson(geojson_enriched)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Carte score projeté",
        "⚔️ Carte Vignot vs Fagaut",
        "📊 Résultats globaux",
        "📋 Bureaux pivots"
    ])

    # --- Tab 1 : Score projeté Vignot ---
    with tab1:
        st.markdown(f"**Score projeté d'Anne Vignot avec {taux_pct}% de report Véziès + Friess**")
        locations, z_proj, hovers = [], [], []
        for _, row in df_analysis.iterrows():
            num = int(row['NUM_BUREAU'])
            locations.append(num)
            z_proj.append(row['PCT_VIGNOT_PROJ'])
            hovers.append(
                f"<b>Bureau {num}</b><br><br>"
                f"<b>Anne Vignot :</b><br>"
                f"Score T1 réel : {row['PCT_VIGNOT']:.2f}%<br>"
                f"Voix reportées : +{int(row['VOIX_REPORT'])}<br>"
                f"<b>Score projeté : {row['PCT_VIGNOT_PROJ']:.2f}%</b><br><br>"
                f"<b>Ludovic Fagaut :</b> {row['PCT_FAGAUT']:.2f}%<br>"
                f"<b>Écart projeté : {row['ECART_PROJ']:+.2f}%</b>"
            )

        fig1 = go.Figure(go.Choroplethmapbox(
            geojson=geojson_enriched,
            locations=locations,
            z=z_proj,
            featureidkey="properties.NUM_BUREAU",
            colorscale='Greens',
            zmin=0,
            text=hovers,
            hovertemplate='%{text}<extra></extra>',
            marker_opacity=0.75,
            marker_line_width=1,
            marker_line_color='white',
            colorbar=dict(title="Score<br>projeté (%)", thickness=20, len=0.7, x=1.02),
        ))
        fig1.update_layout(
            mapbox=dict(style='open-street-map', center=map_center, zoom=11.5),
            title=dict(
                text=f'<b>Score projeté Anne Vignot — Report {taux_pct}% Véziès + Friess</b>',
                x=0.5, xanchor='center'
            ),
            height=700, margin={"r": 0, "t": 60, "l": 0, "b": 0},
        )
        st.plotly_chart(fig1, use_container_width=True, key='transfer_map_proj')

    # --- Tab 2 : Duel Vignot vs Fagaut ---
    with tab2:
        st.markdown("**Vert : Vignot en tête (projeté) — Rouge : Fagaut en tête**")
        locations2, z_ecart, hovers2 = [], [], []
        for _, row in df_analysis.iterrows():
            num = int(row['NUM_BUREAU'])
            locations2.append(num)
            z_ecart.append(row['ECART_PROJ'])
            vainqueur = "✅ Vignot" if row['VIGNOT_EN_TETE'] else "❌ Fagaut"
            hovers2.append(
                f"<b>Bureau {num}</b><br><br>"
                f"<b>Résultat projeté : {vainqueur}</b><br><br>"
                f"Vignot projeté : {row['PCT_VIGNOT_PROJ']:.2f}%<br>"
                f"Fagaut : {row['PCT_FAGAUT']:.2f}%<br>"
                f"<b>Écart : {row['ECART_PROJ']:+.2f}%</b>"
            )

        fig2 = go.Figure(go.Choroplethmapbox(
            geojson=geojson_enriched,
            locations=locations2,
            z=z_ecart,
            featureidkey="properties.NUM_BUREAU",
            colorscale=[[0, '#d73027'], [0.5, '#ffffbf'], [1, '#1a9850']],
            zmid=0,
            text=hovers2,
            hovertemplate='%{text}<extra></extra>',
            marker_opacity=0.75,
            marker_line_width=1,
            marker_line_color='white',
            colorbar=dict(title="Écart V−F<br>(pts %)", thickness=20, len=0.7, x=1.02),
        ))
        fig2.update_layout(
            mapbox=dict(style='open-street-map', center=map_center, zoom=11.5),
            title=dict(
                text=f'<b>Vignot vs Fagaut — Report {taux_pct}% (Vert = Vignot en tête)</b>',
                x=0.5, xanchor='center'
            ),
            height=700, margin={"r": 0, "t": 60, "l": 0, "b": 0},
        )
        st.plotly_chart(fig2, use_container_width=True, key='transfer_map_duel')

    # --- Tab 3 : Bar chart global ---
    with tab3:
        st.markdown("**Comparaison des votes totaux — Résultats réels vs projetés**")

        # Construire le tableau global
        all_candidats = df_candidates.groupby('CANDIDAT')['VOIX'].sum().sort_values(ascending=True)
        names = list(all_candidats.index)
        voix = list(all_candidats.values)
        colors = ['#4daf4a' if n == NOM_VIGNOT else '#377eb8' if n == NOM_FAGAUT
                  else '#bdbdbd' for n in names]

        fig3 = go.Figure()
        # Barres réelles
        fig3.add_trace(go.Bar(
            name='Voix réelles',
            x=voix, y=names,
            orientation='h',
            marker_color=colors,
            opacity=0.55,
            text=[f"{v:,}" for v in voix],
            textposition='auto',
        ))
        # Barre projetée Vignot uniquement
        voix_proj_list = []
        for n in names:
            if n == NOM_VIGNOT:
                voix_proj_list.append(int(total_vignot_p))
            else:
                voix_proj_list.append(0)

        fig3.add_trace(go.Bar(
            name=f'Vignot projeté (+{taux_pct}% report)',
            x=voix_proj_list, y=names,
            orientation='h',
            marker_color=['#1a7a1a' if n == NOM_VIGNOT else 'rgba(0,0,0,0)' for n in names],
            text=[f"{int(total_vignot_p):,}" if n == NOM_VIGNOT else '' for n in names],
            textposition='outside',
        ))

        # Ligne verticale pour Fagaut
        fig3.add_vline(
            x=total_fagaut, line_dash='dash', line_color='#377eb8',
            annotation_text=f"Fagaut : {int(total_fagaut):,}",
            annotation_position="top right"
        )

        fig3.update_layout(
            barmode='overlay',
            title=dict(text='<b>Votes totaux à Besançon — T1 2026</b>', x=0.5, xanchor='center'),
            xaxis_title='Nombre de voix',
            height=420,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )
        st.plotly_chart(fig3, use_container_width=True, key='transfer_bar_global')

        # Résumé chiffré
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(
                f"**Sources du report projeté :**\n"
                f"- Séverine Véziès : {int(total_veziès):,} voix × {taux_pct}% = **+{int(total_veziès * taux):,}**\n"
                f"- Nicole Friess : {int(total_friess):,} voix × {taux_pct}% = **+{int(total_friess * taux):,}**\n"
                f"- **Total reporté : +{int(total_report):,} voix**"
            )
        with col_b:
            if voix_manquantes > 0:
                pct_manquant = voix_manquantes / (total_veziès + total_friess) * 100 if (total_veziès + total_friess) > 0 else 0
                st.warning(
                    f"Il manquerait **{int(voix_manquantes):,} voix** à Vignot.\n"
                    f"Cela nécessiterait un report de **{pct_manquant + taux_pct:.0f}%** de Véziès + Friess."
                )
            else:
                st.success(
                    f"Avec {taux_pct}% de report, Vignot dépasserait Fagaut de "
                    f"**{int(total_vignot_p - total_fagaut):,} voix** ({ecart_global:+.2f}%)."
                )

    # --- Tab 4 : Bureaux pivots ---
    with tab4:
        st.markdown(
            "**Bureaux pivots** : bureaux où l'écart projeté Vignot−Fagaut est le plus serré "
            "(±5 points) — les plus susceptibles de basculer selon le taux réel de report."
        )
        df_pivots = df_analysis[df_analysis['ECART_PROJ'].abs() <= 5].copy()
        df_pivots = df_pivots.sort_values('ECART_PROJ')

        if df_pivots.empty:
            st.info("Aucun bureau avec un écart inférieur à 5 points au taux de report sélectionné.")
        else:
            df_display = df_pivots[[
                'NUM_BUREAU', 'EXPRIMES',
                'PCT_VIGNOT', 'PCT_VIGNOT_PROJ', 'VOIX_REPORT',
                'PCT_FAGAUT', 'ECART_PROJ'
            ]].copy()
            df_display.columns = [
                'Bureau', 'Exprimés',
                'Vignot réel (%)', 'Vignot projeté (%)', 'Voix reportées',
                'Fagaut (%)', 'Écart V−F (pts)'
            ]
            df_display['Voix reportées'] = df_display['Voix reportées'].astype(int)
            st.dataframe(
                df_display.style
                .format({
                    'Vignot réel (%)': '{:.2f}',
                    'Vignot projeté (%)': '{:.2f}',
                    'Fagaut (%)': '{:.2f}',
                    'Écart V−F (pts)': '{:+.2f}',
                })
                .applymap(
                    lambda v: 'color: #1a9850' if isinstance(v, float) and v > 0 else
                              ('color: #d73027' if isinstance(v, float) and v < 0 else ''),
                    subset=['Écart V−F (pts)']
                ),
                use_container_width=True, hide_index=True,
            )
            st.caption(f"{len(df_pivots)} bureau(x) dans une marge de ±5 points.")


def render_vote_transfer_analysis_fagaut(df_candidates: pd.DataFrame, geojson_enriched: Dict):
    """
    Visualisation interactive du report de voix de Jacques Ricciardetti et Eric Delabrousse
    vers Ludovic Fagaut au second tour de 2026.

    Un slider permet d'ajuster le taux de report (0–100 %) et recalcule en temps réel
    les scores projetés bureau par bureau.
    """
    st.subheader("🔁 Simulation de report de voix — Ricciardetti & Delabrousse → Fagaut")
    st.caption(
        "Cette simulation estime le score de Ludovic Fagaut au second tour en supposant "
        "qu'un certain pourcentage des voix de Jacques Ricciardetti et d'Eric Delabrousse "
        "se reporterait en sa faveur."
    )

    NOM_FAGAUT = 'Ludovic Fagaut'
    NOM_VIGNOT = 'Anne Vignot'
    NOM_RICCIARDETTI = 'Jacques Ricciardetti'
    NOM_DELABROUSSE = 'Eric Delabrousse'

    candidats_dispo = set(df_candidates['CANDIDAT'].unique())
    if not {NOM_FAGAUT, NOM_VIGNOT}.issubset(candidats_dispo):
        st.warning("Données insuffisantes pour cette analyse (Fagaut ou Vignot absent).")
        return

    # --------------------------------------------------------
    # Construction du DataFrame de base bureau × candidat
    # --------------------------------------------------------
    bureaux_base = (
        df_candidates.groupby('NUM_BUREAU')
        .first()[['INSCRITS', 'VOTANTS', 'EXPRIMES']]
        .reset_index()
    )

    def _voix_bureau(nom, alias):
        sub = df_candidates[df_candidates['CANDIDAT'] == nom][
            ['NUM_BUREAU', 'VOIX', 'POURCENTAGE_EXPRIMES']
        ].copy()
        sub.columns = ['NUM_BUREAU', f'VOIX_{alias}', f'PCT_{alias}']
        return sub

    df_analysis = bureaux_base.copy()
    df_analysis = df_analysis.merge(_voix_bureau(NOM_FAGAUT, 'FAGAUT'), on='NUM_BUREAU', how='left')
    df_analysis = df_analysis.merge(_voix_bureau(NOM_VIGNOT, 'VIGNOT'), on='NUM_BUREAU', how='left')

    if NOM_RICCIARDETTI in candidats_dispo:
        df_analysis = df_analysis.merge(_voix_bureau(NOM_RICCIARDETTI, 'RICC'), on='NUM_BUREAU', how='left')
    else:
        df_analysis['VOIX_RICC'] = 0; df_analysis['PCT_RICC'] = 0.0

    if NOM_DELABROUSSE in candidats_dispo:
        df_analysis = df_analysis.merge(_voix_bureau(NOM_DELABROUSSE, 'DELA'), on='NUM_BUREAU', how='left')
    else:
        df_analysis['VOIX_DELA'] = 0; df_analysis['PCT_DELA'] = 0.0

    df_analysis = df_analysis.fillna(0)

    # --------------------------------------------------------
    # Slider de taux de report
    # --------------------------------------------------------
    taux_pct = st.slider(
        "Taux de report Ricciardetti + Delabrousse → Fagaut (%)",
        min_value=0, max_value=100, value=50, step=5,
        help="50 % signifie que la moitié des voix de Ricciardetti et Delabrousse se reportent sur Fagaut.",
        key="slider_fagaut_transfer"
    )
    taux = taux_pct / 100.0

    # --------------------------------------------------------
    # Calculs projetés
    # --------------------------------------------------------
    df_analysis['VOIX_REPORT'] = (df_analysis['VOIX_RICC'] + df_analysis['VOIX_DELA']) * taux
    df_analysis['VOIX_FAGAUT_PROJ'] = df_analysis['VOIX_FAGAUT'] + df_analysis['VOIX_REPORT']
    df_analysis['PCT_FAGAUT_PROJ'] = df_analysis.apply(
        lambda r: r['VOIX_FAGAUT_PROJ'] / r['EXPRIMES'] * 100 if r['EXPRIMES'] > 0 else 0.0, axis=1
    )
    df_analysis['ECART_PROJ'] = df_analysis['PCT_FAGAUT_PROJ'] - df_analysis['PCT_VIGNOT']
    df_analysis['FAGAUT_EN_TETE'] = df_analysis['ECART_PROJ'] > 0
    df_analysis['FAGAUT_EN_TETE_ACTUEL'] = df_analysis['PCT_FAGAUT'] > df_analysis['PCT_VIGNOT']

    # Totaux
    total_exprimes   = df_analysis['EXPRIMES'].sum()
    total_fagaut     = df_analysis['VOIX_FAGAUT'].sum()
    total_vignot     = df_analysis['VOIX_VIGNOT'].sum()
    total_ricc       = df_analysis['VOIX_RICC'].sum()
    total_dela       = df_analysis['VOIX_DELA'].sum()
    total_report     = (total_ricc + total_dela) * taux
    total_fagaut_p   = total_fagaut + total_report

    score_actuel  = total_fagaut / total_exprimes * 100 if total_exprimes > 0 else 0
    score_proj    = total_fagaut_p / total_exprimes * 100 if total_exprimes > 0 else 0
    score_vignot  = total_vignot / total_exprimes * 100 if total_exprimes > 0 else 0
    ecart_global  = score_proj - score_vignot

    bv_en_tete_actuel = int(df_analysis['FAGAUT_EN_TETE_ACTUEL'].sum())
    bv_en_tete_proj   = int(df_analysis['FAGAUT_EN_TETE'].sum())
    nb_bureaux = len(df_analysis)
    voix_avance = total_fagaut_p - total_vignot  # always positive (Fagaut leads T1)

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------
    st.markdown("### 📊 Résultats globaux projetés")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Score actuel Fagaut", f"{score_actuel:.2f}%",
                  help="Score réel au T1 2026")
    with c2:
        st.metric("Score projeté Fagaut", f"{score_proj:.2f}%",
                  delta=f"{score_proj - score_actuel:+.2f} pts")
    with c3:
        st.metric("Score Vignot (inchangé)", f"{score_vignot:.2f}%")
    with c4:
        label_ecart = "✅ Fagaut en tête" if ecart_global > 0 else "❌ Fagaut en retard"
        st.metric("Écart Fagaut − Vignot", f"{ecart_global:+.2f}%",
                  delta=label_ecart,
                  delta_color="normal" if ecart_global > 0 else "inverse")

    c5, c6, c7 = st.columns(3)
    with c5:
        st.metric("Bureaux Fagaut en tête (actuel)",
                  f"{bv_en_tete_actuel} / {nb_bureaux}")
    with c6:
        st.metric("Bureaux Fagaut en tête (projeté)",
                  f"{bv_en_tete_proj} / {nb_bureaux}",
                  delta=f"{bv_en_tete_proj - bv_en_tete_actuel:+d} bureaux")
    with c7:
        st.metric("Avance projetée sur Vignot",
                  f"+{int(voix_avance):,} voix",
                  delta="En tête",
                  delta_color="normal")

    # --------------------------------------------------------
    # Onglets de visualisation
    # --------------------------------------------------------
    st.markdown("---")
    map_center = _map_center_from_geojson(geojson_enriched)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Carte score projeté",
        "⚔️ Carte Fagaut vs Vignot",
        "📊 Résultats globaux",
        "📋 Bureaux pivots"
    ])

    # --- Tab 1 : Score projeté Fagaut ---
    with tab1:
        st.markdown(f"**Score projeté de Ludovic Fagaut avec {taux_pct}% de report Ricciardetti + Delabrousse**")
        locations, z_proj, hovers = [], [], []
        for _, row in df_analysis.iterrows():
            num = int(row['NUM_BUREAU'])
            locations.append(num)
            z_proj.append(row['PCT_FAGAUT_PROJ'])
            hovers.append(
                f"<b>Bureau {num}</b><br><br>"
                f"<b>Ludovic Fagaut :</b><br>"
                f"Score T1 réel : {row['PCT_FAGAUT']:.2f}%<br>"
                f"Voix reportées : +{int(row['VOIX_REPORT'])}<br>"
                f"<b>Score projeté : {row['PCT_FAGAUT_PROJ']:.2f}%</b><br><br>"
                f"<b>Anne Vignot :</b> {row['PCT_VIGNOT']:.2f}%<br>"
                f"<b>Écart projeté : {row['ECART_PROJ']:+.2f}%</b>"
            )

        fig1 = go.Figure(go.Choroplethmapbox(
            geojson=geojson_enriched,
            locations=locations,
            z=z_proj,
            featureidkey="properties.NUM_BUREAU",
            colorscale='Blues',
            zmin=0,
            text=hovers,
            hovertemplate='%{text}<extra></extra>',
            marker_opacity=0.75,
            marker_line_width=1,
            marker_line_color='white',
            colorbar=dict(title="Score<br>projeté (%)", thickness=20, len=0.7, x=1.02),
        ))
        fig1.update_layout(
            mapbox=dict(style='open-street-map', center=map_center, zoom=11.5),
            title=dict(
                text=f'<b>Score projeté Ludovic Fagaut — Report {taux_pct}% Ricciardetti + Delabrousse</b>',
                x=0.5, xanchor='center'
            ),
            height=700, margin={"r": 0, "t": 60, "l": 0, "b": 0},
        )
        st.plotly_chart(fig1, use_container_width=True, key='fagaut_transfer_map_proj')

    # --- Tab 2 : Duel Fagaut vs Vignot ---
    with tab2:
        st.markdown("**Bleu : Fagaut en tête (projeté) — Rouge : Vignot en tête**")
        locations2, z_ecart, hovers2 = [], [], []
        for _, row in df_analysis.iterrows():
            num = int(row['NUM_BUREAU'])
            locations2.append(num)
            z_ecart.append(row['ECART_PROJ'])
            vainqueur = "✅ Fagaut" if row['FAGAUT_EN_TETE'] else "❌ Vignot"
            hovers2.append(
                f"<b>Bureau {num}</b><br><br>"
                f"<b>Résultat projeté : {vainqueur}</b><br><br>"
                f"Fagaut projeté : {row['PCT_FAGAUT_PROJ']:.2f}%<br>"
                f"Vignot : {row['PCT_VIGNOT']:.2f}%<br>"
                f"<b>Écart : {row['ECART_PROJ']:+.2f}%</b>"
            )

        fig2 = go.Figure(go.Choroplethmapbox(
            geojson=geojson_enriched,
            locations=locations2,
            z=z_ecart,
            featureidkey="properties.NUM_BUREAU",
            colorscale=[[0, '#d73027'], [0.5, '#ffffbf'], [1, '#2166ac']],
            zmid=0,
            text=hovers2,
            hovertemplate='%{text}<extra></extra>',
            marker_opacity=0.75,
            marker_line_width=1,
            marker_line_color='white',
            colorbar=dict(title="Écart F−V<br>(pts %)", thickness=20, len=0.7, x=1.02),
        ))
        fig2.update_layout(
            mapbox=dict(style='open-street-map', center=map_center, zoom=11.5),
            title=dict(
                text=f'<b>Fagaut vs Vignot — Report {taux_pct}% (Bleu = Fagaut en tête)</b>',
                x=0.5, xanchor='center'
            ),
            height=700, margin={"r": 0, "t": 60, "l": 0, "b": 0},
        )
        st.plotly_chart(fig2, use_container_width=True, key='fagaut_transfer_map_duel')

    # --- Tab 3 : Bar chart global ---
    with tab3:
        st.markdown("**Comparaison des votes totaux — Résultats réels vs projetés**")

        all_candidats = df_candidates.groupby('CANDIDAT')['VOIX'].sum().sort_values(ascending=True)
        names = list(all_candidats.index)
        voix = list(all_candidats.values)
        colors = ['#377eb8' if n == NOM_FAGAUT else '#4daf4a' if n == NOM_VIGNOT
                  else '#bdbdbd' for n in names]

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name='Voix réelles',
            x=voix, y=names,
            orientation='h',
            marker_color=colors,
            opacity=0.55,
            text=[f"{v:,}" for v in voix],
            textposition='auto',
        ))

        voix_proj_list = []
        for n in names:
            if n == NOM_FAGAUT:
                voix_proj_list.append(int(total_fagaut_p))
            else:
                voix_proj_list.append(0)

        fig3.add_trace(go.Bar(
            name=f'Fagaut projeté (+{taux_pct}% report)',
            x=voix_proj_list, y=names,
            orientation='h',
            marker_color=['#0c3d6e' if n == NOM_FAGAUT else 'rgba(0,0,0,0)' for n in names],
            text=[f"{int(total_fagaut_p):,}" if n == NOM_FAGAUT else '' for n in names],
            textposition='outside',
        ))

        fig3.add_vline(
            x=total_vignot, line_dash='dash', line_color='#4daf4a',
            annotation_text=f"Vignot : {int(total_vignot):,}",
            annotation_position="top right"
        )

        fig3.update_layout(
            barmode='overlay',
            title=dict(text='<b>Votes totaux à Besançon — T1 2026</b>', x=0.5, xanchor='center'),
            xaxis_title='Nombre de voix',
            height=420,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )
        st.plotly_chart(fig3, use_container_width=True, key='fagaut_transfer_bar_global')

        col_a, col_b = st.columns(2)
        with col_a:
            st.info(
                f"**Sources du report projeté :**\n"
                f"- Jacques Ricciardetti : {int(total_ricc):,} voix × {taux_pct}% = **+{int(total_ricc * taux):,}**\n"
                f"- Eric Delabrousse : {int(total_dela):,} voix × {taux_pct}% = **+{int(total_dela * taux):,}**\n"
                f"- **Total reporté : +{int(total_report):,} voix**"
            )
        with col_b:
            st.success(
                f"Avec {taux_pct}% de report, Fagaut dépasserait Vignot de "
                f"**{int(voix_avance):,} voix** ({ecart_global:+.2f}%)."
            )

    # --- Tab 4 : Bureaux pivots ---
    with tab4:
        st.markdown(
            "**Bureaux pivots** : bureaux où l'écart projeté Fagaut−Vignot est le plus serré "
            "(±5 points) — les plus susceptibles de basculer selon le taux réel de report."
        )
        df_pivots = df_analysis[df_analysis['ECART_PROJ'].abs() <= 5].copy()
        df_pivots = df_pivots.sort_values('ECART_PROJ')

        if df_pivots.empty:
            st.info("Aucun bureau avec un écart inférieur à 5 points au taux de report sélectionné.")
        else:
            df_display = df_pivots[[
                'NUM_BUREAU', 'EXPRIMES',
                'PCT_FAGAUT', 'PCT_FAGAUT_PROJ', 'VOIX_REPORT',
                'PCT_VIGNOT', 'ECART_PROJ'
            ]].copy()
            df_display.columns = [
                'Bureau', 'Exprimés',
                'Fagaut réel (%)', 'Fagaut projeté (%)', 'Voix reportées',
                'Vignot (%)', 'Écart F−V (pts)'
            ]
            df_display['Voix reportées'] = df_display['Voix reportées'].astype(int)
            st.dataframe(
                df_display.style
                .format({
                    'Fagaut réel (%)': '{:.2f}',
                    'Fagaut projeté (%)': '{:.2f}',
                    'Vignot (%)': '{:.2f}',
                    'Écart F−V (pts)': '{:+.2f}',
                })
                .applymap(
                    lambda v: 'color: #2166ac' if isinstance(v, float) and v > 0 else
                              ('color: #d73027' if isinstance(v, float) and v < 0 else ''),
                    subset=['Écart F−V (pts)']
                ),
                use_container_width=True, hide_index=True,
            )
            st.caption(f"{len(df_pivots)} bureau(x) dans une marge de ±5 points.")


# =============================================================================
# COMPARAISON INTER-ÉLECTIONS : T1 2020 vs T1 2026
# =============================================================================

def render_inter_election_comparison_dashboard(
    inter_viz: InterElectionComparisonVisualizer
):
    """Dashboard KPI pour la comparaison T1 2020 vs T1 2026."""
    st.subheader("📊 Comparaison Premier Tour 2020 → 2026")

    stats = inter_viz.get_global_statistics()

    # --- Participation ---
    st.markdown("### ⚡ Participation")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Participation 2020", f"{stats['participation_2020']:.2f}%")
    with col2:
        st.metric(
            "Participation 2026",
            f"{stats['participation_2026']:.2f}%",
            delta=f"{stats['evolution_participation']:+.2f}%",
        )
    with col3:
        st.metric(
            "Inscrits 2026",
            f"{stats['total_inscrits_2026']:,}",
            delta=f"{stats['total_inscrits_2026'] - stats['total_inscrits_2020']:+,}",
        )

    # --- Candidats communs ---
    st.markdown("### 👥 Candidats présents aux deux élections")
    candidats_stats = stats.get('candidats', {})
    if candidats_stats:
        cols = st.columns(len(candidats_stats))
        for idx, (candidat, cstats) in enumerate(candidats_stats.items()):
            with cols[idx]:
                delta_label = f"{cstats['evolution_moyenne']:+.2f} pts"
                st.metric(
                    candidat,
                    f"{cstats['score_moyen_2026']:.2f}%",
                    delta=delta_label,
                    help=f"2020 : {cstats['score_moyen_2020']:.2f}% → 2026 : {cstats['score_moyen_2026']:.2f}%",
                )

    # --- Tableau récapitulatif ---
    with st.expander("📋 Tableau récapitulatif des candidats communs"):
        recap_rows = []
        for candidat, cstats in candidats_stats.items():
            recap_rows.append({
                'Candidat': candidat,
                'Score moyen 2020 (%)': round(cstats['score_moyen_2020'], 2),
                'Score moyen 2026 (%)': round(cstats['score_moyen_2026'], 2),
                'Évolution (pts)': round(cstats['evolution_moyenne'], 2),
                'Total voix 2020': cstats['total_voix_2020'],
                'Total voix 2026': cstats['total_voix_2026'],
                'Variation voix': cstats['total_voix_2026'] - cstats['total_voix_2020'],
            })
        if recap_rows:
            df_recap = pd.DataFrame(recap_rows)
            st.dataframe(df_recap, use_container_width=True, hide_index=True)


def render_inter_election_comparison_visualization(
    inter_viz: InterElectionComparisonVisualizer,
):
    """Visualisations comparatives détaillées T1 2020 vs T1 2026."""
    st.subheader("🗺️ Analyses comparatives — 2020 vs 2026")

    candidats = list(inter_viz.COMMON_CANDIDATES.keys())

    tab_labels = [f"🔀 {c.split()[-1]}" for c in candidats]
    tab_labels.append("�️ Participation")
    tab_labels.append("�📊 Vue d'ensemble")
    tabs = st.tabs(tab_labels)

    for i, candidat in enumerate(candidats):
        with tabs[i]:
            st.markdown(f"### {candidat}")

            sub_tab1, sub_tab2, sub_tab3 = st.tabs(
                ["🗺️ Carte évolution", "📊 Barres par bureau", "🔵 Scatter 2020 vs 2026"]
            )

            with sub_tab1:
                fig_evo = inter_viz.create_candidate_evolution_map(candidat)
                st.plotly_chart(fig_evo, use_container_width=True,
                                key=f'inter_evo_map_{candidat}')

            with sub_tab2:
                fig_bars = inter_viz.create_evolution_bars_chart(candidat, n=20)
                st.plotly_chart(fig_bars, use_container_width=True,
                                key=f'inter_bars_{candidat}')

            with sub_tab3:
                fig_scatter = inter_viz.create_scatter_2020_vs_2026(candidat)
                st.plotly_chart(fig_scatter, use_container_width=True,
                                key=f'inter_scatter_{candidat}')

    # Onglet participation
    with tabs[-2]:
        st.markdown("### 🗳️ Participation — T1 2020 vs T1 2026")

        df_part = inter_viz.get_participation_data()
        total_inscrits_2020 = int(df_part['INSCRITS_2020'].sum())
        total_inscrits_2026 = int(df_part['INSCRITS_2026'].sum())
        total_votants_2020  = int(df_part['VOTANTS_2020'].sum())
        total_votants_2026  = int(df_part['VOTANTS_2026'].sum())
        taux_2020 = total_votants_2020 / total_inscrits_2020 * 100 if total_inscrits_2020 > 0 else 0
        taux_2026 = total_votants_2026 / total_inscrits_2026 * 100 if total_inscrits_2026 > 0 else 0
        evol_global = taux_2026 - taux_2020
        bv_hausse = int((df_part['EVOLUTION_ABS'] > 0).sum())
        bv_baisse = int((df_part['EVOLUTION_ABS'] < 0).sum())

        kc1, kc2, kc3, kc4 = st.columns(4)
        with kc1:
            st.metric("Participation 2020", f"{taux_2020:.2f}%",
                      help=f"{total_votants_2020:,} votants / {total_inscrits_2020:,} inscrits")
        with kc2:
            st.metric("Participation 2026", f"{taux_2026:.2f}%",
                      delta=f"{evol_global:+.2f} pts",
                      help=f"{total_votants_2026:,} votants / {total_inscrits_2026:,} inscrits")
        with kc3:
            st.metric("Bureaux en hausse", f"{bv_hausse} / {len(df_part)}")
        with kc4:
            st.metric("Bureaux en baisse", f"{bv_baisse} / {len(df_part)}")

        st.markdown("---")
        ptab1, ptab2, ptab3, ptab4 = st.tabs([
            "🗺️ Carte évolution",
            "🗺️ Cartes 2020 / 2026",
            "📊 Barres par bureau",
            "🔵 Scatter 2020 vs 2026"
        ])

        with ptab1:
            fig_pevo = inter_viz.create_participation_evolution_map()
            st.plotly_chart(fig_pevo, use_container_width=True, key='part_evo_map')

        with ptab2:
            col_a, col_b = st.columns(2)
            with col_a:
                fig_p2020 = inter_viz.create_participation_absolute_map(2020)
                fig_p2020.update_layout(height=500)
                st.plotly_chart(fig_p2020, use_container_width=True, key='part_abs_map_2020')
            with col_b:
                fig_p2026 = inter_viz.create_participation_absolute_map(2026)
                fig_p2026.update_layout(height=500)
                st.plotly_chart(fig_p2026, use_container_width=True, key='part_abs_map_2026')

        with ptab3:
            fig_pbars = inter_viz.create_participation_bars_chart(n=20)
            st.plotly_chart(fig_pbars, use_container_width=True, key='part_bars')

        with ptab4:
            fig_pscatter = inter_viz.create_participation_scatter()
            st.plotly_chart(fig_pscatter, use_container_width=True, key='part_scatter')

        # Tableau détaillé
        with st.expander("📋 Tableau détaillé par bureau de vote"):
            df_display = df_part.copy()
            df_display.columns = [
                'Bureau', 'Inscrits 2020', 'Votants 2020', 'Participation 2020 (%)',
                'Inscrits 2026', 'Votants 2026', 'Participation 2026 (%)',
                'Évolution (pts)', 'Évolution (%)'
            ]
            st.dataframe(
                df_display.style
                .format({
                    'Participation 2020 (%)': '{:.2f}',
                    'Participation 2026 (%)': '{:.2f}',
                    'Évolution (pts)': '{:+.2f}',
                    'Évolution (%)': '{:+.1f}',
                })
                .applymap(
                    lambda v: 'color: #1a9850' if isinstance(v, float) and v > 0 else
                              ('color: #d73027' if isinstance(v, float) and v < 0 else ''),
                    subset=['Évolution (pts)']
                ),
                use_container_width=True, hide_index=True,
            )

    # Onglet vue d'ensemble : cartes scores côte à côte pour tous les candidats
    with tabs[-1]:
        st.markdown("### 🗺️ Scores 2020 et 2026 par candidat")
        for candidat in candidats:
            st.markdown(f"#### {candidat}")
            col_a, col_b = st.columns(2)
            with col_a:
                fig_2020 = inter_viz.create_candidate_score_map(candidat, 2020)
                fig_2020.update_layout(height=500)
                st.plotly_chart(fig_2020, use_container_width=True,
                                key=f'inter_score_2020_{candidat}')
            with col_b:
                fig_2026 = inter_viz.create_candidate_score_map(candidat, 2026)
                fig_2026.update_layout(height=500)
                st.plotly_chart(fig_2026, use_container_width=True,
                                key=f'inter_score_2026_{candidat}')


# =============================================================================
# COMPARAISON T1 / T2 — Municipales 2026 Besancon
# =============================================================================

def render_2026_comparison_dashboard(comp: Municipales2026T1T2Comparator):
    """
    Dashboard KPI pour la comparaison T1 vs T2 des municipales 2026.
    """
    st.subheader("📊 Comparaison T1 → T2 — Municipales 2026 Besançon")

    stats = comp.get_comparison_stats()

    # --- Participation ---
    st.markdown("### ⚡ Participation")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Participation T1", f"{stats['participation_t1']:.2f}%",
                  help=f"{stats['total_votants_t1']:,} votants sur {stats['total_inscrits_t1']:,} inscrits")
    with c2:
        st.metric("Participation T2", f"{stats['participation_t2']:.2f}%",
                  delta=f"{stats['delta_participation']:+.2f} pts",
                  help=f"{stats['total_votants_t2']:,} votants sur {stats['total_inscrits_t2']:,} inscrits")
    with c3:
        st.metric("Bureaux analysés", f"{stats['nb_bureaux']}")
    with c4:
        st.metric("Voix de report disponibles", f"{stats['voix_report_total']:,}",
                  help="Total des voix des candidats présents uniquement au T1")

    # --- Résultats par candidat T2 ---
    st.markdown("### 🏆 Résultats T2 par candidat")
    candidats = stats.get('candidats', {})
    if candidats:
        cols = st.columns(len(candidats))
        for idx, (name, cstats) in enumerate(candidats.items()):
            with cols[idx]:
                st.metric(
                    name,
                    f"{cstats['score_moyen_t2']:.2f}%",
                    delta=f"{cstats['delta_moyen']:+.2f} pts vs T1",
                    help=(
                        f"T1 : {cstats['score_moyen_t1']:.2f}% "
                        f"({cstats['total_voix_t1']:,} voix) → "
                        f"T2 : {cstats['score_moyen_t2']:.2f}% "
                        f"({cstats['total_voix_t2']:,} voix)"
                    ),
                )
                st.caption(f"En tête dans {cstats['bureaux_en_tete_t2']} bureaux au T2")

    # --- Détail du report de voix ---
    report_details = stats.get('report_details', {})
    if report_details:
        st.markdown("### 🔄 Voix disponibles pour report (candidats T1 uniquement)")
        rd_rows = [
            {'Candidat': name, 'Voix T1': voix, '% du total de report': f"{voix / stats['voix_report_total'] * 100:.1f}%"}
            for name, voix in sorted(report_details.items(), key=lambda x: -x[1])
        ]
        st.dataframe(pd.DataFrame(rd_rows), use_container_width=True, hide_index=True)

    # --- Tableau détaillé par bureau ---
    with st.expander("📋 Tableau détaillé par bureau", expanded=False):
        df = comp.comparison_data.copy()
        cols_display = ['NUM_BUREAU', 'PARTICIPATION_T1', 'PARTICIPATION_T2', 'DELTA_PARTICIPATION']
        for key, name in [('FAGAUT', 'Fagaut'), ('VIGNOT', 'Vignot')]:
            for suffix in ['T1', 'T2']:
                for metric, label in [('SCORE', f'% {name} {suffix}'), ('VOIX', f'Voix {name} {suffix}')]:
                    col = f'{metric}_{key}_{suffix}'
                    if col in df.columns:
                        df = df.rename(columns={col: label})
                        cols_display.append(label)
            delta = f'DELTA_{key}'
            if delta in df.columns:
                df = df.rename(columns={delta: f'Delta {name} (pts)'})
                cols_display.append(f'Delta {name} (pts)')

        existing_cols = [c for c in cols_display if c in df.columns]
        df_show = df[existing_cols].round(2)
        df_show = df_show.rename(columns={
            'NUM_BUREAU': 'Bureau',
            'PARTICIPATION_T1': 'Participation T1 (%)',
            'PARTICIPATION_T2': 'Participation T2 (%)',
            'DELTA_PARTICIPATION': 'Delta participation (pts)',
        })
        st.dataframe(df_show, use_container_width=True, hide_index=True)


def render_2026_comparison_visualization(comp: Municipales2026T1T2Comparator):
    """
    Visualisations comparatives T1 vs T2 pour les municipales 2026.
    Fournit des cartes et graphiques organisés en onglets.
    """
    st.subheader("🗺️ Analyses comparatives — T1 vs T2 2026")

    tab_resultats, tab_part, tab_fagaut, tab_vignot, tab_report = st.tabs([
        "🗺️ Résultats T2",
        "⚡ Participation",
        "🔵 Fagaut T1→T2",
        "🟢 Vignot T1→T2",
        "🔄 Report de voix",
    ])

    # --- Onglet Résultats T2 ---
    with tab_resultats:
        st.markdown("### Carte des résultats au 2ème tour")
        fig_t2 = comp.create_results_map_t2()
        st.plotly_chart(fig_t2, use_container_width=True, key='t2_results_map')

    # --- Onglet Participation ---
    with tab_part:
        st.markdown("### Evolution de la participation T1 → T2")
        fig_part = comp.create_participation_evolution_map()
        st.plotly_chart(fig_part, use_container_width=True, key='part_evo_map')

    # --- Onglet Fagaut ---
    with tab_fagaut:
        candidat = 'Ludovic Fagaut'
        st.markdown(f"### {candidat} — Evolution T1 → T2")

        sub1, sub2, sub3 = st.tabs(["🗺️ Carte évolution", "📊 Barres par bureau", "🔵 Scatter T1 vs T2"])
        with sub1:
            fig = comp.create_candidate_delta_map(candidat)
            st.plotly_chart(fig, use_container_width=True, key='fagaut_delta_map')
        with sub2:
            fig = comp.create_score_evolution_bars(candidat)
            st.plotly_chart(fig, use_container_width=True, key='fagaut_evo_bars')
        with sub3:
            fig = comp.create_scatter_t1_vs_t2(candidat)
            st.plotly_chart(fig, use_container_width=True, key='fagaut_scatter')

    # --- Onglet Vignot ---
    with tab_vignot:
        candidat = 'Anne Vignot'
        st.markdown(f"### {candidat} — Evolution T1 → T2")

        sub1, sub2, sub3 = st.tabs(["🗺️ Carte évolution", "📊 Barres par bureau", "🔵 Scatter T1 vs T2"])
        with sub1:
            fig = comp.create_candidate_delta_map(candidat)
            st.plotly_chart(fig, use_container_width=True, key='vignot_delta_map')
        with sub2:
            fig = comp.create_score_evolution_bars(candidat)
            st.plotly_chart(fig, use_container_width=True, key='vignot_evo_bars')
        with sub3:
            fig = comp.create_scatter_t1_vs_t2(candidat)
            st.plotly_chart(fig, use_container_width=True, key='vignot_scatter')

    # --- Onglet Report de voix ---
    with tab_report:
        st.markdown("### Analyse du report de voix par bureau")
        st.caption(
            "Voix 'disponibles pour report' = total des voix obtenues au T1 "
            "par les candidats absents au T2 (Véziès, Delabrousse, Ricciardetti, Friess)."
        )
        fig_report = comp.create_vote_transfer_chart()
        st.plotly_chart(fig_report, use_container_width=True, key='vote_transfer_chart')
