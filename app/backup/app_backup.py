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

# Configuration de la page
st.set_page_config(
    page_title="Smart Care Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar cachée par défaut
)

# CSS personnalisé - Style Karmine Corp Élégant avec Navigation Horizontale
st.markdown("""
<style>
    /* Import de la police ronde et sobre - Poppins */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    /* Variables de couleur Karmine Corp */
    :root {
        --kc-primary: #2E3FE8;
        --kc-secondary: #1a237e;
        --kc-gold: #FFD700;
        --kc-light: #f8f9fa;
        --kc-dark: #0a0e27;
        --kc-gradient: linear-gradient(135deg, #2E3FE8 0%, #1a237e 100%);
        --kc-gradient-gold: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    }
    
    /* Style général */
    .main {
        background: linear-gradient(to bottom, #0a0e27 0%, #1a1f3a 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Cache la sidebar par défaut */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Réduit l'espace en haut */
    .block-container {
        padding-top: 1rem;
    }
    
    /* Navigation horizontale */
    .navbar-container {
        background: linear-gradient(135deg, rgba(46, 63, 232, 0.95) 0%, rgba(26, 35, 126, 0.95) 100%);
        backdrop-filter: blur(10px);
        padding: 0;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin: -1rem -1rem 2rem -1rem;
        position: sticky;
        top: 0;
        z-index: 999;
        border-bottom: 2px solid rgba(255, 215, 0, 0.3);
    }
    
    .navbar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.2rem 2rem;
        flex-wrap: wrap;
    }
    
    .navbar-logo {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .navbar-logo h1 {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #FFD700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: 1px;
    }
    
    .navbar-subtitle {
        font-size: 0.75rem;
        color: #FFD700;
        font-weight: 500;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 2px;
    }
    
    .navbar-nav {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    
    .nav-item {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        border: 2px solid transparent;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        cursor: pointer;
        white-space: nowrap;
    }
    
    .nav-item:hover {
        background: rgba(255, 215, 0, 0.2);
        border-color: #FFD700;
        transform: translateY(-2px);
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #0a0e27;
        border-color: #FFD700;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
    }
    
    /* Info tooltip */
    .info-tooltip {
        position: relative;
        display: inline-block;
        width: 18px;
        height: 18px;
        background: linear-gradient(135deg, #2E3FE8 0%, #1a237e 100%);
        border-radius: 50%;
        color: white;
        font-size: 12px;
        font-weight: bold;
        text-align: center;
        line-height: 18px;
        cursor: help;
        margin-left: 8px;
        border: 2px solid #FFD700;
    }
    
    .info-tooltip:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(10, 14, 39, 0.98);
        color: #FFD700;
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid rgba(46, 63, 232, 0.5);
        white-space: normal;
        width: 280px;
        font-size: 0.85rem;
        font-weight: 500;
        z-index: 1000;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        line-height: 1.4;
    }
    
    .info-tooltip:hover::before {
        content: '';
        position: absolute;
        bottom: 115%;
        left: 50%;
        transform: translateX(-50%);
        border: 8px solid transparent;
        border-top-color: rgba(10, 14, 39, 0.98);
        z-index: 1000;
    }
    
    /* Description sous graphiques */
    .chart-description {
        background: linear-gradient(135deg, rgba(46, 63, 232, 0.1) 0%, rgba(26, 35, 126, 0.1) 100%);
        border-left: 3px solid #2E3FE8;
        padding: 12px 16px;
        border-radius: 8px;
        margin-top: 10px;
        font-size: 0.9rem;
        color: #b0b0b0;
        line-height: 1.6;
    }
    
    .chart-description strong {
        color: #FFD700;
        font-weight: 600;
    }
    
    /* Header principal avec effet néon */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2E3FE8 0%, #FFD700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1.5rem;
        letter-spacing: 0px;
    }
    
    /* Carte métrique style gaming */
    .metric-card {
        background: linear-gradient(135deg, rgba(46, 63, 232, 0.1) 0%, rgba(26, 35, 126, 0.1) 100%);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(46, 63, 232, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent 30%, rgba(255, 215, 0, 0.1) 50%, transparent 70%);
        transform: rotate(45deg);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #FFD700;
        box-shadow: 0 12px 48px rgba(46, 63, 232, 0.4);
    }
    
    /* Alertes style moderne */
    .alert-warning {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.15) 100%);
        border-left: 4px solid #FFD700;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(255, 193, 7, 0.2);
        color: #FFD700;
        font-weight: 600;
    }
    
    .alert-danger {
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(229, 57, 53, 0.15) 100%);
        border-left: 4px solid #f44336;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(244, 67, 54, 0.3);
        color: #ff6b6b;
        font-weight: 600;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 4px 16px rgba(244, 67, 54, 0.3); }
        50% { box-shadow: 0 4px 24px rgba(244, 67, 54, 0.6); }
    }
    
    .alert-success {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(67, 160, 71, 0.15) 100%);
        border-left: 4px solid #4caf50;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(76, 175, 80, 0.2);
        color: #4caf50;
        font-weight: 600;
    }
    
    /* Style pour les métriques Streamlit */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2E3FE8 0%, #FFD700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.95rem;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Sidebar style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e27 0%, #1a237e 100%);
        border-right: 2px solid rgba(46, 63, 232, 0.3);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ffffff;
    }
    
    /* Boutons style gaming */
    .stButton>button {
        background: linear-gradient(135deg, #2E3FE8 0%, #1a237e 100%);
        color: white;
        border: 2px solid #FFD700;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(46, 63, 232, 0.4);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #0a0e27;
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(255, 215, 0, 0.6);
    }
    
    /* Tabs style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(10, 14, 39, 0.5);
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: 2px solid rgba(46, 63, 232, 0.3);
        border-radius: 8px;
        color: #ffffff;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(46, 63, 232, 0.2);
        border-color: #FFD700;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2E3FE8 0%, #1a237e 100%);
        border-color: #FFD700;
        box-shadow: 0 4px 15px rgba(46, 63, 232, 0.5);
    }
    
    /* Sliders */
    .stSlider [data-baseweb="slider"] {
        background: linear-gradient(135deg, #2E3FE8 0%, #1a237e 100%);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(46, 63, 232, 0.1) 0%, rgba(26, 35, 126, 0.1) 100%);
        border: 1px solid rgba(46, 63, 232, 0.3);
        border-radius: 10px;
        font-weight: 600;
        color: #FFD700;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #FFD700;
        font-weight: 600;
        letter-spacing: 0px;
    }
    
    h2 {
        font-size: 1.5rem;
    }
    
    h3 {
        font-size: 1.2rem;
        font-weight: 500;
    }
    
    /* Texte général */
    p, label, span {
        color: #e0e0e0;
    }
    
    /* Dataframe style */
    .dataframe {
        border: 1px solid rgba(46, 63, 232, 0.3);
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Logo/Badge effet */
    .kc-badge {
        display: inline-block;
        background: linear-gradient(135deg, #2E3FE8 0%, #FFD700 100%);
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        color: white;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(46, 63, 232, 0.4);
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
    }
    
    /* Scroll bar custom */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(10, 14, 39, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #2E3FE8 0%, #FFD700 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #FFD700 0%, #2E3FE8 100%);
    }
</style>
""", unsafe_allow_html=True)

# Chargement des données
@st.cache_data
def load_data():
    """Charge les données hospitalières"""
    base_path = Path(__file__).parent
    df = pd.read_csv(
        base_path / "Jeu de données - Smart Care - daily_hospital_context_2022-2024_generated.csv",
        decimal=',',
        skipinitialspace=True  # Ignore les espaces après les virgules
    )
    
    # Nettoyage des colonnes
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()
    
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
        import pickle
        model_path = Path(__file__).parent / "model_prediction.pkl"
        if model_path.exists():
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            return model, True
        else:
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

# Navigation horizontale en haut
st.markdown("""
<div class="navbar-container">
    <div class="navbar-header">
        <div class="navbar-logo">
            <div>
                <h1>SMART CARE</h1>
                <div class="navbar-subtitle">Pitié-Salpêtrière • Dashboard v2.0</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Boutons de navigation
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🏠 Accueil", width="stretch", key="nav_accueil"):
        st.session_state.active_page = "Accueil"

with col2:
    if st.button("📊 Analyse", width="stretch", key="nav_analyse"):
        st.session_state.active_page = "Analyse"

with col3:
    if st.button("🎯 Simulation", width="stretch", key="nav_simulation"):
        st.session_state.active_page = "Simulation"

with col4:
    if st.button("🔮 Prédiction", width="stretch", key="nav_prediction"):
        st.session_state.active_page = "Prédiction"

with col5:
    if st.button("💡 Recommandations", width="stretch", key="nav_recommandations"):
        st.session_state.active_page = "Recommandations"

st.markdown("---")

page = st.session_state.active_page

# ========================================
# PAGE : ACCUEIL
# ========================================
if page == "Accueil":
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #2E3FE8 0%, #FFD700 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
            ">Tableau de Bord</h1>
            <p style="
                color: #b0b0b0;
                font-size: 1rem;
                font-weight: 400;
                margin-top: 10px;
            ">Vue d'ensemble des indicateurs clés et alertes en temps réel</p>
        </div>
    """, unsafe_allow_html=True)
    
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
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.subheader("🛏️ Taux d'occupation des lits")
        df['occupation_pct'] = df['taux_occupation_lits'] * 100
        fig = px.histogram(
            df,
            x='occupation_pct',
            nbins=50,
            labels={'occupation_pct': 'Taux d\'occupation (%)'},
            color_discrete_sequence=['#2E3FE8']
        )
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0')
        )
        st.plotly_chart(fig, width="stretch")
    
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
elif page == "📊 Analyse Exploratoire":
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
    
    saison_filter = st.sidebar.multiselect(
        "Saison",
        options=df['saison'].unique(),
        default=df['saison'].unique()
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
            df_agg = df_filtered.set_index('date').resample('M')[metric].mean().reset_index()
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
        st.plotly_chart(fig, width="stretch")
        
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
            st.plotly_chart(fig, width="stretch")
        
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
            st.plotly_chart(fig, width="stretch")
    
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
        
        st.plotly_chart(fig, width="stretch")
        
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
        
        st.dataframe(df_corr, width="stretch", hide_index=True)
    
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
            st.plotly_chart(fig, width="stretch")
        
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
            st.plotly_chart(fig, width="stretch")
    
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
        
        st.dataframe(
            stats_df.style.format("{:.2f}"),
            width="stretch"
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
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            fig = px.box(
                df_filtered,
                y=var_to_plot,
                x='saison',
                title="Distribution par saison",
                color='saison'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, width="stretch")

# ========================================
# PAGE : SIMULATION SCÉNARIOS (suite dans le prochain fichier)
# ========================================
elif page == "🎯 Simulation Scénarios":
    from pages import simulation
    simulation.show(df)

elif page == "🔮 Prédiction":
    from pages import prediction
    prediction.show(df, st.session_state.model, st.session_state.model_available)

elif page == "💡 Recommandations":
    from pages import recommandations
    recommandations.show(df)
