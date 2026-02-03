"""
Dashboard Smart Care - Pitié-Salpêtrière
Gestion et prédiction des ressources hospitalières
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from pathlib import Path
import sys

# Ajouter le dossier pages au path pour pouvoir importer les modules
sys.path.insert(0, str(Path(__file__).parent / "pages"))
# Ajouter le dossier ml pour le package smartcare_model
ml_path = Path(__file__).parent.parent / "ml"
if ml_path.exists():
    sys.path.insert(0, str(ml_path))

# Configuration de la page
st.set_page_config(
    page_title="Smart Care Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar cachée par défaut
)

# CSS personnalisé - Style Smart Care Dark
st.markdown("""
<style>
    /* Import de la police */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Variables Smart Care - Style sobre */
    :root {
        --sc-black: #000000;
        --sc-dark: #1a1a1a;
        --sc-card: #2a2a2a;
        --sc-white: #FFFFFF;
        --sc-orange: #FF5500;
        --sc-gray: #999999;
        --sc-light-gray: #cccccc;
        --sc-text: #f5f5f5;
    }
    
    /* Style général - Dark */
    .main {
        background: var(--sc-black);
        font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
        color: var(--sc-light-gray);
    }
    
    /* Masquer complètement le header Streamlit */
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
    }
    
    /* Réduire l'espace en haut */
    .block-container {
        padding-top: 0rem !important;
        max-width: 100%;
    }
    
    /* Masquer le menu hamburger et toolbar */
    button[kind="header"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* Navigation horizontale - FIXE en haut */
    .navbar-container {
        background: var(--sc-dark);
        padding: 0;
        margin: 0;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        border-bottom: 1px solid #2F2F2F;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    
    /* Ajouter de l'espace en haut du contenu pour compenser la navbar fixe */
    .main .block-container {
        padding-top: 90px !important;
        padding-bottom: 2rem;
    }
    
    
    .navbar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        flex-wrap: wrap;
    }
    
    .navbar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .navbar-logo h1 {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--sc-white);
        margin: 0;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .navbar-subtitle {
        font-size: 0.7rem;
        color: var(--sc-gray);
        font-weight: 400;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 2px;
    }
    
    .navbar-nav {
        display: flex;
        gap: 18px;
        flex-wrap: wrap;
    }

    .navbar-nav a {
        text-decoration: none;
    }
    
    .nav-item {
        background: transparent;
        color: var(--sc-gray);
        padding: 10px 18px;
        border-radius: 0;
        border: none;
        border-bottom: 2px solid transparent;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        cursor: pointer;
        white-space: nowrap;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .nav-item:hover {
        border-bottom-color: var(--sc-orange);
        color: var(--sc-white);
    }
    
    .nav-item.active {
        background: transparent;
        color: var(--sc-orange);
        border-bottom-color: var(--sc-orange);
        font-weight: 600;
    }
    
    /* Info tooltip */
    .info-tooltip {
        position: relative;
        display: inline-block;
        width: 18px;
        height: 18px;
        background: var(--sc-card);
        border-radius: 50%;
        color: var(--sc-white);
        font-size: 11px;
        font-weight: 700;
        text-align: center;
        line-height: 18px;
        cursor: help;
        margin-left: 8px;
        border: 1px solid var(--sc-gray);
    }
    
    .info-tooltip:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background: var(--sc-dark);
        color: var(--sc-white);
        padding: 12px 16px;
        border-radius: 4px;
        border-left: 3px solid var(--sc-orange);
        white-space: normal;
        width: 280px;
        font-size: 0.85rem;
        font-weight: 400;
        z-index: 1000;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        line-height: 1.5;
    }
    
    .info-tooltip:hover::before {
        content: '';
        position: absolute;
        bottom: 115%;
        left: 50%;
        transform: translateX(-50%);
        border: 6px solid transparent;
        border-top-color: var(--sc-dark);
        z-index: 1000;
    }
    
    /* Description sous graphiques */
    .chart-description {
        background: var(--sc-card);
        border-left: 3px solid var(--sc-orange);
        padding: 14px 18px;
        border-radius: 4px;
        margin-top: 12px;
        font-size: 0.9rem;
        color: var(--sc-light-gray);
        line-height: 1.7;
    }
    
    .chart-description strong {
        color: var(--sc-white);
        font-weight: 700;
    }
    
    /* Header principal */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--sc-white);
        margin-bottom: 1rem;
        letter-spacing: 0.5px;
        text-transform: none;
        padding-bottom: 0;
        display: block;
    }
    
    /* Carte métrique */
    .metric-card {
        background: var(--sc-card);
        padding: 2rem;
        border-radius: 4px;
        border: 1px solid #333333;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 0%;
        background: var(--sc-orange);
        transition: height 0.3s ease;
    }
    
    .metric-card:hover::before {
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #444444;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    }
    
    /* Alertes */
    .alert-warning {
        background: rgba(255, 85, 0, 0.1);
        border-left: 3px solid var(--sc-orange);
        padding: 1.2rem;
        border-radius: 2px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        color: var(--sc-text);
        font-weight: 500;
    }
    
    .alert-danger {
        background: rgba(211, 47, 47, 0.1);
        border-left: 4px solid #D32F2F;
        padding: 1.2rem;
        border-radius: 4px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        color: #ff6b6b;
        font-weight: 700;
    }
    
    .alert-success {
        background: rgba(56, 142, 60, 0.1);
        border-left: 4px solid #388E3C;
        padding: 1.2rem;
        border-radius: 4px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        color: #69db7c;
        font-weight: 600;
    }
    
    /* Cache la sidebar complètement */
    [data-testid="stSidebar"] {
        display: none !important;
        background: var(--sc-dark);
        border-right: 1px solid #2a2f3e;
    }
    
    /* Métriques Streamlit */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 900;
        color: var(--sc-white);
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--sc-gray);
    }
    
    /* Boutons */
    .stButton>button {
        background: var(--sc-card);
        color: var(--sc-white);
        border: 1px solid #333333;
        border-radius: 2px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        width: 100%;
    }
    
    .stButton>button:hover {
        background: var(--sc-orange);
        color: var(--sc-white);
        border-color: var(--sc-orange);
        box-shadow: 0 2px 12px rgba(255, 85, 0, 0.3);
    }
    
    /* Bouton actif (primary) */
    .stButton>button[kind="primary"],
    .stButton>button[data-baseweb="button"][kind="primary"] {
        background: var(--sc-orange) !important;
        color: var(--sc-white) !important;
        border: 1px solid var(--sc-orange);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        padding: 0;
        border-bottom: 2px solid #2a2f3e;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-bottom: 3px solid transparent;
        border-radius: 0;
        color: var(--sc-gray);
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--sc-white);
        border-bottom-color: var(--sc-orange);
    }
    
    .stTabs [aria-selected="true"] {
        background: transparent;
        color: var(--sc-white);
        border-bottom-color: var(--sc-orange);
        font-weight: 700;
    }
    
    /* Sliders */
    .stSlider [data-baseweb="slider"] {
        background: transparent;
    }
    
    .stSlider [role="slider"] {
        background: var(--sc-orange) !important;
        border: 2px solid var(--sc-orange) !important;
        box-shadow: 0 0 8px rgba(255, 85, 0, 0.6);
    }
    
    .stSlider [data-baseweb="slider-track"] {
        background: #444444 !important;
    }
    
    .stSlider input[type="range"]::-webkit-slider-thumb {
        background: var(--sc-orange);
        border: 2px solid var(--sc-white);
        box-shadow: 0 0 8px rgba(255, 85, 0, 0.6);
    }
    
    .stSlider input[type="range"]::-moz-range-thumb {
        background: var(--sc-orange);
        border: 2px solid var(--sc-white);
        box-shadow: 0 0 8px rgba(255, 85, 0, 0.6);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--sc-card);
        border: 1px solid #2a2f3e;
        border-radius: 4px;
        font-weight: 600;
        color: var(--sc-white);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--sc-white);
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    h2 {
        font-size: 1.5rem;
        color: var(--sc-white);
    }
    
    h3 {
        font-size: 1.2rem;
        font-weight: 500;
        color: var(--sc-light-gray);
    }
    
    /* Texte général */
    p, label, span {
        color: var(--sc-light-gray);
    }
    
    /* Dataframe style */
    .dataframe {
        background: var(--sc-card);
        border: 1px solid #2a2f3e;
        border-radius: 4px;
        overflow: hidden;
        color: var(--sc-white);
    }
    
    /* Input fields */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>div,
    .stDateInput>div>div>input,
    .stNumberInput>div>div>input {
        background: var(--sc-card);
        color: var(--sc-white);
        border: 1px solid #2a2f3e;
        border-radius: 4px;
    }
    
    /* Scroll bar custom */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--sc-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--sc-orange);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--sc-gold);
    }
</style>
""", unsafe_allow_html=True)

pd.options.mode.string_storage = "python"

# Chargement des données
@st.cache_data
def load_data():
    """Charge les données hospitalières"""
    base_path = Path(__file__).parent.parent
    df = pd.read_csv(
        base_path / "data" / "raw" / "Jeu de données - Smart Care - daily_hospital_context_2022-2024_generated.csv",
        decimal=',',
        skipinitialspace=True  # Ignore les espaces après les virgules
    )
    
    # Nettoyage des colonnes
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].astype("string[python]").str.strip()
    
    # Conversion des types
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    
    # Conversion des colonnes numériques
    numeric_cols = [
        'temperature_moyenne', 'temperature_min', 'temperature_max',
        'indice_chaleur', 'indice_froid', 'taux_occupation_lits',
        'taux_couverture_personnel', 'impact_evenement_estime'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

# Chargement du modèle ML (si disponible)
@st.cache_resource
def load_ml_model():
    """Charge le modèle ML de prédiction si disponible"""
    try:
        base_path = Path(__file__).parent.parent

        # Tentative 1 : pipeline SmartCare (ML/)
        try:
            from smartcare_model import (
                load_raw_dataframe,
                build_feature_dataframe,
                load_artifacts,
            )
            raw_df = load_raw_dataframe()
            feature_df = build_feature_dataframe(raw_df)
            model, feature_cols = load_artifacts()
            return {
                "model": model,
                "feature_cols": feature_cols,
                "feature_df": feature_df,
                "source": "smartcare_model",
            }, True
        except Exception:
            pass

        # Tentative 2 : fichiers .joblib directs
        import joblib
        candidates = [
            base_path / "model_prediction.joblib",
            base_path / "ml" / "artifacts" / "gradient_boosting.joblib",
            base_path / "ml" / "artifacts" / "random_forest.joblib",
        ]

        for model_path in candidates:
            if model_path.exists():
                model = joblib.load(model_path)
                return model, True

        # Fallback ancien format .pkl si encore présent
        legacy_path = base_path / "model_prediction.pkl"
        if legacy_path.exists():
            import pickle
            with open(legacy_path, 'rb') as f:
                model = pickle.load(f)
            return model, True

        return None, False
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle : {e}")
        return None, False

# Initialisation
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = None
    st.session_state.model = None
    st.session_state.model_available = False

# Chargement initial
if not st.session_state.data_loaded:
    with st.spinner("Chargement des données..."):
        st.session_state.df = load_data()
        st.session_state.model, st.session_state.model_available = load_ml_model()
        st.session_state.data_loaded = True

df = st.session_state.df

# Initialiser la page active dans session_state
if 'active_page' not in st.session_state:
    st.session_state.active_page = "Accueil"

# Lire la page depuis les query params (navigation fixe HTML)
try:
    page_param = st.query_params.get("page")
except Exception:
    params = st.experimental_get_query_params()
    page_param = params.get("page", [None])[0]

valid_pages = ["Accueil", "Analyse", "Simulation", "Prédiction", "Recommandations"]
if page_param in valid_pages:
    st.session_state.active_page = page_param

# Navigation horizontale en haut (liens HTML fixes)
page = st.session_state.active_page
nav_html = f"""
<div class=\"navbar-container\">
    <div class=\"navbar-header\">
        <div class=\"navbar-logo\">
            <div>
                <h1>SMART CARE</h1>
                <div class=\"navbar-subtitle\">Pitié-Salpêtrière • Dashboard v2.0</div>
            </div>
        </div>
        <div class=\"navbar-nav\">
            <a class=\"nav-item {'active' if page=='Accueil' else ''}\" href=\"?page=Accueil\" target=\"_self\">Accueil</a>
            <a class=\"nav-item {'active' if page=='Analyse' else ''}\" href=\"?page=Analyse\" target=\"_self\">Analyse</a>
            <a class=\"nav-item {'active' if page=='Simulation' else ''}\" href=\"?page=Simulation\" target=\"_self\">Simulation</a>
            <a class=\"nav-item {'active' if page=='Prédiction' else ''}\" href=\"?page=Prédiction\" target=\"_self\">Prédiction</a>
            <a class=\"nav-item {'active' if page=='Recommandations' else ''}\" href=\"?page=Recommandations\" target=\"_self\">Recommandations</a>
        </div>
    </div>
</div>
"""
st.markdown(nav_html, unsafe_allow_html=True)

page = st.session_state.active_page

# ========================================
# PAGE : ACCUEIL
# ========================================
if page == "Accueil":
    st.markdown('<h1 class="main-header">Tableau de Bord</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: var(--sc-gray); text-align: left; margin-bottom: 2rem;">Vue d\'ensemble des indicateurs clés et alertes en temps réel</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # KPIs principaux
    st.markdown("""
        <h2 style="color: #FFD700; font-size: 1.3rem; font-weight: 600; margin-bottom: 15px;">
            Indicateurs Clés
            <span class="info-tooltip" data-tooltip="Ces métriques représentent les moyennes calculées sur l'ensemble de la période. Les deltas indiquent la variation entre les 7 derniers jours et la semaine précédente.">ⓘ</span>
        </h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_occupation = df['taux_occupation_lits'].mean() * 100
        st.metric(
            "Occupation Moyenne",
            f"{avg_occupation:.1f}%",
            delta=f"{(df['taux_occupation_lits'].iloc[-7:].mean() - df['taux_occupation_lits'].iloc[-14:-7].mean()) * 100:.1f}%"
        )
    
    with col2:
        avg_admissions = df['nombre_admissions'].mean()
        st.metric(
            "Admissions/Jour",
            f"{avg_admissions:.0f}",
            delta=f"{df['nombre_admissions'].iloc[-7:].mean() - df['nombre_admissions'].iloc[-14:-7].mean():.0f}"
        )
    
    with col3:
        avg_urgences = df['nombre_passages_urgences'].mean()
        st.metric(
            "Urgences/Jour",
            f"{avg_urgences:.0f}",
            delta=f"{df['nombre_passages_urgences'].iloc[-7:].mean() - df['nombre_passages_urgences'].iloc[-14:-7].mean():.0f}"
        )
    
    with col4:
        avg_personnel = df['taux_couverture_personnel'].mean() * 100
        st.metric(
            "Couverture Personnel",
            f"{avg_personnel:.1f}%",
            delta=f"{(df['taux_couverture_personnel'].iloc[-7:].mean() - df['taux_couverture_personnel'].iloc[-14:-7].mean()) * 100:.1f}%"
        )
    
    st.markdown("---")
    
    # Graphiques de synthèse
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Évolution des admissions (2022-2024)")
        df_monthly = df.groupby(df['date'].dt.to_period('M')).agg({
            'nombre_admissions': 'sum',
            'nombre_passages_urgences': 'sum'
        }).reset_index()
        df_monthly['date'] = df_monthly['date'].dt.to_timestamp()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_monthly['date'],
            y=df_monthly['nombre_admissions'],
            name='Admissions',
            line=dict(color='#2E3FE8', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=df_monthly['date'],
            y=df_monthly['nombre_passages_urgences'],
            name='Passages urgences',
            line=dict(color='#FFD700', width=3)
        ))
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'),
            legend=dict(
                bgcolor='rgba(46, 63, 232, 0.1)',
                bordercolor='rgba(46, 63, 232, 0.3)',
                borderwidth=1
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🛏️ Taux d'occupation des lits")
        df['occupation_pct'] = df['taux_occupation_lits'] * 100
        # Agrégation mensuelle pour une meilleure lisibilité
        df_monthly_occupation = df.groupby(df['date'].dt.to_period('M')).agg({
            'occupation_pct': 'mean'
        }).reset_index()
        df_monthly_occupation['date'] = df_monthly_occupation['date'].dt.to_timestamp()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_monthly_occupation['date'],
            y=df_monthly_occupation['occupation_pct'],
            name='Taux d\'occupation',
            line=dict(color='#2E3FE8', width=3),
            fill='tozeroy',
            fillcolor='rgba(46, 63, 232, 0.2)'
        ))
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'),
            xaxis_title='Date',
            yaxis_title='Taux d\'occupation (%)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Alertes et événements avec style moderne
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; margin: 30px 0 20px 0;">
            <h2 style="color: #FFD700; font-size: 1.5rem; font-weight: 700; letter-spacing: 2px;">
                🚨 CENTRE D'ALERTES • SURVEILLANCE ACTIVE
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Dernière semaine
    last_week = df[df['date'] >= df['date'].max() - timedelta(days=7)]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_occupation = last_week[last_week['taux_occupation_lits'] > 0.85]
        if not high_occupation.empty:
            st.markdown(f"""
            <div class="alert-danger">
                <strong>🔴 Occupation critique</strong><br>
                {len(high_occupation)} jour(s) avec occupation > 85%
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-success">
                <strong>✅ Occupation normale</strong><br>
                Aucun jour critique cette semaine
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        events = last_week[last_week['evenement_special'] != ''].copy()
        if not events.empty:
            event_types = events['evenement_special'].value_counts()
            st.markdown(f"""
            <div class="alert-warning">
                <strong>⚠️ Événements actifs</strong><br>
                {', '.join([f"{k}: {v}j" for k, v in event_types.items()])}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-success">
                <strong>✅ Aucun événement</strong><br>
                Activité normale
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        low_staff = last_week[last_week['taux_couverture_personnel'] < 0.85]
        if not low_staff.empty:
            st.markdown(f"""
            <div class="alert-warning">
                <strong>⚠️ Personnel insuffisant</strong><br>
                {len(low_staff)} jour(s) sous le seuil de 85%
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-success">
                <strong>✅ Personnel suffisant</strong><br>
                Couverture adéquate
            </div>
            """, unsafe_allow_html=True)

# ========================================
# PAGE : ANALYSE EXPLORATOIRE
# ========================================
elif page == "Analyse":
    st.markdown('<p class="main-header">Analyse Exploratoire des Données</p>', unsafe_allow_html=True)
    
    # Filtres
    st.sidebar.markdown("### 🔍 Filtres")
    
    date_range = st.sidebar.date_input(
        "Période d'analyse",
        value=(df['date'].min(), df['date'].max()),
        min_value=df['date'].min(),
        max_value=df['date'].max()
    )
    
    if len(date_range) == 2:
        mask = (df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
    
    saison_options = sorted(df["saison"].dropna().unique().tolist())
    saison_filter = st.sidebar.multiselect(
        "Saison",
        options=saison_options,
        default=saison_options,
    )
    
    if saison_filter:
        df_filtered = df_filtered[df_filtered['saison'].isin(saison_filter)]
    
    # Onglets d'analyse
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Tendances Temporelles",
        "🔗 Corrélations",
        "🌡️ Impact Météo",
        "📊 Statistiques Descriptives"
    ])
    
    with tab1:
        st.subheader("Évolution des indicateurs clés")
        
        metric = st.selectbox(
            "Sélectionnez un indicateur",
            ['nombre_admissions', 'nombre_passages_urgences', 'nombre_hospitalisations',
             'taux_occupation_lits', 'taux_couverture_personnel']
        )
        
        granularity = st.radio(
            "Granularité",
            ['Quotidien', 'Hebdomadaire', 'Mensuel'],
            horizontal=True
        )
        
        if granularity == 'Hebdomadaire':
            df_agg = df_filtered.set_index('date').resample('W')[metric].mean().reset_index()
        elif granularity == 'Mensuel':
            df_agg = df_filtered.set_index('date').resample('ME')[metric].mean().reset_index()
        else:
            df_agg = df_filtered[['date', metric]].copy()
        
        fig = px.line(
            df_agg,
            x='date',
            y=metric,
            title=f"Évolution de {metric.replace('_', ' ').title()}",
            labels={'date': 'Date', metric: metric.replace('_', ' ').title()}
        )
        
        # Ajout de la moyenne et tendance
        avg_value = df_agg[metric].mean()
        fig.add_hline(y=avg_value, line_dash="dash", line_color="red",
                     annotation_text=f"Moyenne: {avg_value:.2f}")
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse par jour de semaine
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 Variation par jour de semaine")
            df_dow = df_filtered.groupby('jour_semaine')[metric].mean().reset_index()
            
            jour_order = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            df_dow['jour_semaine'] = pd.Categorical(df_dow['jour_semaine'], categories=jour_order, ordered=True)
            df_dow = df_dow.sort_values('jour_semaine')
            
            fig = px.bar(
                df_dow,
                x='jour_semaine',
                y=metric,
                color=metric,
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🌤️ Variation par saison")
            df_season = df_filtered.groupby('saison')[metric].mean().reset_index()
            
            fig = px.bar(
                df_season,
                x='saison',
                y=metric,
                color=metric,
                color_continuous_scale='Oranges'
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Matrice de corrélation")
        
        numeric_cols = [
            'nombre_admissions', 'nombre_passages_urgences', 'nombre_hospitalisations',
            'taux_occupation_lits', 'taux_couverture_personnel',
            'temperature_moyenne', 'lits_occupes'
        ]
        
        corr_matrix = df_filtered[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.around(corr_matrix.values, decimals=2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Corrélation")
        ))
        
        fig.update_layout(
            title="Corrélations entre variables",
            height=600,
            xaxis={'side': 'bottom'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top corrélations
        st.markdown("#### 🔗 Top 10 des corrélations")
        
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_pairs.append({
                    'Variable 1': corr_matrix.columns[i],
                    'Variable 2': corr_matrix.columns[j],
                    'Corrélation': corr_matrix.iloc[i, j]
                })
        
        df_corr = pd.DataFrame(corr_pairs)
        df_corr = df_corr.sort_values('Corrélation', key=abs, ascending=False).head(10)
        
        df_corr_display = df_corr.copy()
        df_corr_display.index = df_corr_display.index.astype("string[python]")
        st.dataframe(df_corr_display, use_container_width=True)
    
    with tab3:
        st.subheader("Impact de la météo sur l'activité hospitalière")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌡️ Température vs Admissions")
            fig = px.scatter(
                df_filtered,
                x='temperature_moyenne',
                y='nombre_admissions',
                color='meteo_principale',
                labels={
                    'temperature_moyenne': 'Température moyenne (°C)',
                    'nombre_admissions': 'Nombre d\'admissions'
                }
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### ❄️ Conditions météo et urgences")
            df_meteo = df_filtered.groupby('meteo_principale').agg({
                'nombre_passages_urgences': 'mean',
                'nombre_admissions': 'mean'
            }).reset_index()
            
            fig = px.bar(
                df_meteo,
                x='meteo_principale',
                y=['nombre_passages_urgences', 'nombre_admissions'],
                barmode='group',
                labels={'value': 'Nombre moyen', 'variable': 'Type'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Statistiques descriptives")
        
        # Sélection des colonnes numériques pertinentes
        cols_to_describe = [
            'nombre_admissions', 'nombre_passages_urgences', 'nombre_hospitalisations',
            'nombre_sorties', 'lits_occupes', 'taux_occupation_lits',
            'nb_medecins_disponibles', 'nb_infirmiers_disponibles',
            'nb_aides_soignants_disponibles', 'taux_couverture_personnel',
            'temperature_moyenne'
        ]
        
        stats_df = df_filtered[cols_to_describe].describe().T
        stats_df['cv'] = (stats_df['std'] / stats_df['mean'] * 100).round(2)
        stats_df.index = stats_df.index.astype("string[python]")
        
        st.dataframe(
            stats_df.style.format("{:.2f}"),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Distribution des variables
        st.markdown("#### 📊 Distribution d'une variable")
        
        var_to_plot = st.selectbox(
            "Choisir une variable",
            cols_to_describe
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(
                df_filtered,
                x=var_to_plot,
                nbins=50,
                title="Histogramme",
                marginal='box'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.box(
                df_filtered,
                y=var_to_plot,
                x='saison',
                title="Distribution par saison",
                color='saison'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

# ========================================
# ========================================
# PAGE : SIMULATION SCÉNARIOS
# ========================================
elif page == "Simulation":
    from pages import simulation
    simulation.show(df)

# ========================================
# PAGE : PRÉDICTION
# ========================================
elif page == "Prédiction":
    from pages import prediction
    prediction.show(df, st.session_state.model, st.session_state.model_available)

# ========================================
# PAGE : RECOMMANDATIONS
# ========================================
elif page == "Recommandations":
    from pages import recommandations
    recommandations.show(df)
