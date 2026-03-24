"""
Configuration de l'application de cartographie électorale
"""
from pathlib import Path
from typing import Dict, List

# Chemins de base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'datas'

# Configuration des élections disponibles
ELECTIONS_CONFIG = {
    'municipales_2020_t1': {
        'label': 'Municipales 2020 - Tour 1',
        'date': '2020-05-18',
        'excel_file': '2020-05-18-resultats-par-niveau-burvot-t1-france-entiere-nettoye.xlsx',
        'description': 'Premier tour des élections municipales de Besançon',
        'format': 'wide'  # Format avec tous les candidats sur une ligne
    },
    'municipales_2020_t2': {
        'label': 'Municipales 2020 - Tour 2',
        'date': '2020-06-28',
        'excel_file': 'resultats-par-niveau-burvot-t2-france-entiere.xlsx-nettoye.xlsx',
        'description': 'Second tour des élections municipales de Besançon',
        'format': 'long'  # Format avec une ligne par bureau
    },
    'municipales_2026_t1': {
        'label': 'Municipales 2026 - Tour 1',
        'date': '2026-03-15',
        'excel_file': 'elections-municipales-1er-tour-resultats-2026.xlsx',
        'description': 'Premier tour des élections municipales de Besançon 2026',
        'format': 'besancon_2026'  # Format spécifique : une ligne par bureau, colonnes candidats textuelles
    },
    'municipales_2026_t2': {
        'label': 'Municipales 2026 - Tour 2',
        'date': '2026-03-29',
        'excel_file': 'resultats-bureaux-de-votes-2eme-tour.xlsx',
        'description': 'Second tour des élections municipales de Besançon 2026',
        'format': 'besancon_2026_t2'  # Format national filtré Besançon, candidats numérotés
    },
}

# Fichiers GeoJSON (communs à toutes les élections)
GEOJSON_PERIMETRES = 'Perimetre_Bureaux_de_Vote_de_Besancon.json'
GEOJSON_BUREAUX = 'Bureaux_de_Vote_de_Besancon.json'

# Configuration Streamlit
APP_CONFIG = {
    'page_title': '🗳️ Cartographie Électorale - Besançon',
    'page_icon': '🗳️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Palettes de couleurs pour les visualisations
COLOR_SCALES = {
    'rouge': 'Reds',
    'bleu': 'Blues',
    'vert': 'Greens',
    'violet': 'Purples',
    'orange': 'Oranges',
    'viridis': 'Viridis',
    'plasma': 'Plasma',
    'turbo': 'Turbo'
}

# Couleurs pour les candidats (carte "en tête")
CANDIDATE_COLORS = [
    '#e41a1c',  # Rouge
    '#377eb8',  # Bleu
    '#4daf4a',  # Vert
    '#984ea3',  # Violet
    '#ff7f00',  # Orange
    '#ffff33',  # Jaune
    '#a65628',  # Marron
    '#f781bf',  # Rose
    '#999999',  # Gris
    '#66c2a5',  # Turquoise
]

# Critères disponibles pour les filtres
CRITERES_DISPONIBLES = {
    'inscrits': {
        'label': 'Inscrits',
        'description': 'Nombre d\'électeurs inscrits',
        'type': 'int',
        'format': '{:,}'
    },
    'votants': {
        'label': 'Votants',
        'description': 'Nombre de personnes ayant voté',
        'type': 'int',
        'format': '{:,}'
    },
    'abstentions': {
        'label': 'Abstentions',
        'description': 'Nombre d\'abstentions',
        'type': 'int',
        'format': '{:,}'
    },
    'taux_abstention': {
        'label': 'Taux d\'abstention (%)',
        'description': 'Pourcentage d\'abstention',
        'type': 'float',
        'format': '{:.2f}%'
    },
    'taux_participation': {
        'label': 'Taux de participation (%)',
        'description': 'Pourcentage de participation',
        'type': 'float',
        'format': '{:.2f}%',
        'computed': True  # Indique que ce critère est calculé
    },
    'exprimes': {
        'label': 'Exprimés',
        'description': 'Nombre de votes exprimés',
        'type': 'int',
        'format': '{:,}'
    },
}

# Modes de visualisation
VISUALIZATION_MODES = {
    'winner': {
        'label': '🏆 Candidat en tête',
        'description': 'Affiche le candidat arrivé en tête dans chaque bureau',
        'icon': '🏆'
    },
    'participation': {
        'label': '📊 Taux de participation',
        'description': 'Visualise le taux de participation par bureau',
        'icon': '📊'
    },
    'by_candidate': {
        'label': '👤 Par candidat',
        'description': 'Affiche les résultats d\'un ou plusieurs candidats',
        'icon': '👤'
    },
    'comparison': {
        'label': '⚖️ Comparaison',
        'description': 'Compare deux candidats côte à côte',
        'icon': '⚖️'
    },
    'comparison_tours': {
        'label': '🔀 Comparaison T1/T2',
        'description': 'Compare les résultats entre le premier et le second tour',
        'icon': '🔀'
    }
}

# Modes de sélection de tour
TOUR_MODES = {
    't1': {
        'label': '📊 T1 - 2020',
        'description': 'Premier tour des élections municipales 2020',
        'election_key': 'municipales_2020_t1'
    },
    't2': {
        'label': '📊 T2 - 2020',
        'description': 'Second tour des élections municipales 2020',
        'election_key': 'municipales_2020_t2'
    },
    'comparison': {
        'label': '🔀 T1/T2 - 2020',
        'description': 'Comparaison entre le premier et le second tour 2020',
        'election_keys': ['municipales_2020_t1', 'municipales_2020_t2']
    },
    '2026_t1': {
        'label': '📊 T1 - 2026',
        'description': 'Premier tour des élections municipales 2026',
        'election_key': 'municipales_2026_t1'
    },
    'comparison_2020_2026': {
        'label': '🔀 Évol. 2020→2026',
        'description': 'Comparaison du premier tour 2020 vs premier tour 2026',
        'election_keys': ['municipales_2020_t1', 'municipales_2026_t1']
    },
    '2026_t2': {
        'label': '📊 T2 - 2026',
        'description': 'Second tour des élections municipales 2026 (Besançon)',
        'election_key': 'municipales_2026_t2'
    },
    'comparison_2026': {
        'label': '🔀 T1/T2 - 2026',
        'description': 'Comparaison T1 vs T2 des élections municipales 2026',
        'election_keys': ['municipales_2026_t1', 'municipales_2026_t2']
    },
}

# Configuration de la carte
MAP_CONFIG = {
    'default_zoom': 11.5,
    'min_zoom': 10,
    'max_zoom': 15,
    'default_opacity': 0.7,
    'min_opacity': 0.3,
    'max_opacity': 1.0,
    'map_style': 'open-street-map',
    'map_height': 800
}

# Textes de l'interface
TEXTS = {
    'sidebar_title': '⚙️ Configuration',
    'filters_title': '🔍 Filtres',
    'display_params_title': '🎨 Paramètres d\'affichage',
    'stats_title': '📊 Statistiques',
    'no_data': 'Aucune donnée disponible',
    'loading': 'Chargement des données...',
    'error_load': 'Erreur lors du chargement des données',
}

# Valeurs par défaut des filtres
DEFAULT_FILTERS = {
    'participation_min': 0,
    'participation_max': 100,
    'voix_min': 0,
    'top_n_candidates': 10,
    'opacity': 0.7,
    'color_scale': 'Reds'
}


def get_election_file_path(election_key: str) -> Path:
    """
    Retourne le chemin complet du fichier Excel pour une élection donnée
    
    Args:
        election_key: Clé de l'élection dans ELECTIONS_CONFIG
        
    Returns:
        Path: Chemin complet du fichier
    """
    if election_key not in ELECTIONS_CONFIG:
        raise ValueError(f"Élection inconnue: {election_key}")
    
    return DATA_DIR / ELECTIONS_CONFIG[election_key]['excel_file']


def get_geojson_path(geojson_type: str) -> Path:
    """
    Retourne le chemin complet d'un fichier GeoJSON
    
    Args:
        geojson_type: 'perimetres' ou 'bureaux'
        
    Returns:
        Path: Chemin complet du fichier
    """
    if geojson_type == 'perimetres':
        return DATA_DIR / GEOJSON_PERIMETRES
    elif geojson_type == 'bureaux':
        return DATA_DIR / GEOJSON_BUREAUX
    else:
        raise ValueError(f"Type de GeoJSON inconnu: {geojson_type}")


def get_available_elections() -> List[str]:
    """Retourne la liste des clés d'élections disponibles"""
    return list(ELECTIONS_CONFIG.keys())


def get_election_label(election_key: str) -> str:
    """Retourne le label d'affichage d'une élection"""
    return ELECTIONS_CONFIG.get(election_key, {}).get('label', election_key)
