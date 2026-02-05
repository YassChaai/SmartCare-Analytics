"""
Page de simulation de scénarios
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

from pages.ui_helpers import metric_with_info, render_title

def show(df):
    """Affiche la page de simulation de scénarios"""
    
    st.markdown('<p class="main-header">Simulation de Scénarios Hospitaliers</p>', unsafe_allow_html=True)
    st.markdown("### Anticipez l'impact d'événements sur vos ressources")
    
    # Sélection du scénario
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    scenario_presets = {
        "🦠 Épidémie (Grippe/Covid)": {
            "admissions": (0, 200, 100),
            "urgences": (0, 300, 140),
            "staff": (0, 50, 15),
            "lits": (0, 100, 80),
        },
        "🔥 Canicule": {
            "admissions": (0, 150, 65),
            "urgences": (0, 200, 80),
            "staff": (0, 30, 8),
            "lits": (0, 80, 55),
        },
        "❄️ Vague de froid": {
            "admissions": (0, 120, 55),
            "urgences": (0, 150, 70),
            "staff": (0, 25, 10),
            "lits": (0, 70, 50),
        },
        "🏥 Plan blanc / Tension hivernale": {
            "admissions": (0, 200, 120),
            "urgences": (0, 250, 160),
            "staff": (0, 40, 20),
            "lits": (0, 120, 90),
        },
        "🚫 Grève du personnel": {
            "admissions": (-50, 50, -10),
            "urgences": (0, 100, 45),
            "staff": (0, 80, 40),
            "lits": (-30, 50, 15),
        },
        "🚨 Afflux massif (accident)": {
            "admissions": (0, 500, 250),
            "urgences": (0, 1000, 500),
            "staff": (0, 20, 0),
            "lits": (0, 150, 110),
        },
        "🌫️ Pic pollution": {
            "admissions": (0, 80, 25),
            "urgences": (0, 120, 40),
            "staff": (0, 20, 5),
            "lits": (0, 60, 30),
        },
        "🏉 Coupe du monde Rugby 2023": {
            "admissions": (0, 80, 20),
            "urgences": (0, 120, 35),
            "staff": (0, 15, 5),
            "lits": (0, 60, 25),
        },
        "🥇 JO Paris 2024": {
            "admissions": (0, 80, 25),
            "urgences": (0, 120, 45),
            "staff": (0, 15, 5),
            "lits": (0, 60, 30),
        },
        "🌞 Tension été": {
            "admissions": (0, 60, 20),
            "urgences": (0, 80, 30),
            "staff": (0, 35, 20),
            "lits": (0, 70, 35),
        },
        "📅 Période de vacances": {
            "admissions": (-30, 30, -5),
            "urgences": (-20, 40, 5),
            "staff": (0, 50, 25),
            "lits": (-20, 30, 5),
        },
        "🎯 Personnalisé": {
            "admissions": (-50, 500, 0),
            "urgences": (-50, 1000, 0),
            "staff": (-50, 80, 0),
            "lits": (-50, 150, 0),
        },
    }

    def _apply_preset():
        preset = scenario_presets.get(st.session_state.scenario_type)
        if not preset:
            return
        st.session_state.admission_increase = preset["admissions"][2]
        st.session_state.urgence_increase = preset["urgences"][2]
        st.session_state.staff_decrease = preset["staff"][2]
        st.session_state.bed_pressure = preset["lits"][2]

    with col1:
        render_title(
            "⚙️ Configuration du scénario",
            "Choisissez le type de scénario, la date de début, la durée et l'intensité.",
            heading="###",
        )
        
        scenario_type = st.selectbox(
            "Type de scénario",
            [
                "🦠 Épidémie (Grippe/Covid)",
                "🔥 Canicule",
                "❄️ Vague de froid",
                "🏥 Plan blanc / Tension hivernale",
                "🚫 Grève du personnel",
                "🚨 Afflux massif (accident)",
                "🌫️ Pic pollution",
                "🏉 Coupe du monde Rugby 2023",
                "🥇 JO Paris 2024",
                "🌞 Tension été",
                "📅 Période de vacances",
                "🎯 Personnalisé"
            ],
            key="scenario_type",
            on_change=_apply_preset
        )
        
        start_date = st.date_input(
            "Date de début",
            value=datetime.now(),
            min_value=datetime.now(),
            max_value=datetime.now() + timedelta(days=365)
        )
        
        duration = st.slider(
            "Durée (jours)",
            min_value=1,
            max_value=90,
            value=14
        )
        
        intensity = st.slider(
            "Intensité de l'événement",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="0 = faible impact, 1 = impact maximal"
        )
    
    with col2:
        render_title(
            "📊 Paramètres d'impact",
            "Paramètres qui modulent admissions, urgences, personnel et lits.",
            heading="###",
        )
        
        # Paramètres selon le type de scénario
        preset = scenario_presets.get(scenario_type, scenario_presets["🎯 Personnalisé"])
        if "Épidémie" in scenario_type:
            st.info("🦠 **Scénario Épidémie**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    preset["admissions"][0], preset["admissions"][1],
                    int(preset["admissions"][2] + intensity * 100),
                    key="admission_increase"
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    preset["urgences"][0], preset["urgences"][1],
                    int(preset["urgences"][2] + intensity * 120),
                    key="urgence_increase"
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    preset["staff"][0], preset["staff"][1],
                    int(preset["staff"][2] + intensity * 30),
                    help="Personnel malade",
                    key="staff_decrease"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    preset["lits"][0], preset["lits"][1],
                    int(preset["lits"][2] + intensity * 40),
                    key="bed_pressure"
                )
        
        elif "Canicule" in scenario_type:
            st.warning("🔥 **Scénario Canicule**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    preset["admissions"][0], preset["admissions"][1],
                    int(preset["admissions"][2] + intensity * 70),
                    key="admission_increase"
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    preset["urgences"][0], preset["urgences"][1],
                    int(preset["urgences"][2] + intensity * 80),
                    key="urgence_increase"
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    preset["staff"][0], preset["staff"][1],
                    int(preset["staff"][2] + intensity * 15),
                    help="Congés d'été",
                    key="staff_decrease"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    preset["lits"][0], preset["lits"][1],
                    int(preset["lits"][2] + intensity * 30),
                    key="bed_pressure"
                )
        
        elif "Vague de froid" in scenario_type:
            st.info("❄️ **Scénario Vague de Froid**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    preset["admissions"][0], preset["admissions"][1],
                    int(preset["admissions"][2] + intensity * 60),
                    key="admission_increase"
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    preset["urgences"][0], preset["urgences"][1],
                    int(preset["urgences"][2] + intensity * 70),
                    key="urgence_increase"
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    preset["staff"][0], preset["staff"][1],
                    int(preset["staff"][2] + intensity * 15),
                    help="Difficultés de transport",
                    key="staff_decrease"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    preset["lits"][0], preset["lits"][1],
                    int(preset["lits"][2] + intensity * 35),
                    key="bed_pressure"
                )

        elif "Plan blanc" in scenario_type or "Tension hivernale" in scenario_type:
            st.error("🏥 **Scénario Plan blanc / Tension hivernale**")

            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    preset["admissions"][0], preset["admissions"][1],
                    int(preset["admissions"][2] + intensity * 80),
                    key="admission_increase"
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    preset["urgences"][0], preset["urgences"][1],
                    int(preset["urgences"][2] + intensity * 100),
                    key="urgence_increase"
                )

            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    preset["staff"][0], preset["staff"][1],
                    int(preset["staff"][2] + intensity * 20),
                    key="staff_decrease"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    preset["lits"][0], preset["lits"][1],
                    int(preset["lits"][2] + intensity * 40),
                    key="bed_pressure"
                )
        
        elif "Grève" in scenario_type:
            st.error("🚫 **Scénario Grève**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Variation admissions (%)",
                    preset["admissions"][0], preset["admissions"][1],
                    int(preset["admissions"][2] + intensity * 20),
                    help="Peut diminuer si report d'interventions",
                    key="admission_increase"
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    preset["urgences"][0], preset["urgences"][1],
                    int(preset["urgences"][2] + intensity * 50),
                    help="Patients se reportant aux urgences",
                    key="urgence_increase"
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    preset["staff"][0], preset["staff"][1],
                    int(preset["staff"][2] + intensity * 50),
                    key="staff_decrease"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    preset["lits"][0], preset["lits"][1],
                    int(preset["lits"][2] + intensity * 30),
                    key="bed_pressure"
                )
        
        elif "Afflux massif" in scenario_type:
            st.error("🚨 **Scénario Afflux Massif**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    preset["admissions"][0], preset["admissions"][1],
                    int(preset["admissions"][2] + intensity * 300),
                    key="admission_increase"
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    preset["urgences"][0], preset["urgences"][1],
                    int(preset["urgences"][2] + intensity * 600),
                    key="urgence_increase"
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    preset["staff"][0], preset["staff"][1],
                    int(preset["staff"][2] + intensity * 0),
                    help="Personnel en rappel possible",
                    key="staff_decrease"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    preset["lits"][0], preset["lits"][1],
                    int(preset["lits"][2] + intensity * 70),
                    key="bed_pressure"
                )

        elif "pollution" in scenario_type.lower():
            st.warning("🌫️ **Scénario Pic Pollution**")

            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    preset["admissions"][0], preset["admissions"][1],
                    int(preset["admissions"][2] + intensity * 30),
                    key="admission_increase"
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    preset["urgences"][0], preset["urgences"][1],
                    int(preset["urgences"][2] + intensity * 40),
                    key="urgence_increase"
                )

            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    preset["staff"][0], preset["staff"][1],
                    int(preset["staff"][2] + intensity * 10),
                    key="staff_decrease"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    preset["lits"][0], preset["lits"][1],
                    int(preset["lits"][2] + intensity * 20),
                    key="bed_pressure"
                )

        elif "Rugby" in scenario_type or "JO" in scenario_type:
            st.info("🎟️ **Scénario Grand Événement**")

            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    preset["admissions"][0], preset["admissions"][1],
                    int(preset["admissions"][2] + intensity * 20),
                    key="admission_increase"
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    preset["urgences"][0], preset["urgences"][1],
                    int(preset["urgences"][2] + intensity * 30),
                    key="urgence_increase"
                )

            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    preset["staff"][0], preset["staff"][1],
                    int(preset["staff"][2] + intensity * 5),
                    key="staff_decrease"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    preset["lits"][0], preset["lits"][1],
                    int(preset["lits"][2] + intensity * 20),
                    key="bed_pressure"
                )

        elif "Tension été" in scenario_type or "été" in scenario_type:
            st.warning("🌞 **Scénario Tension Été**")

            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    preset["admissions"][0], preset["admissions"][1],
                    int(preset["admissions"][2] + intensity * 15),
                    key="admission_increase"
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    preset["urgences"][0], preset["urgences"][1],
                    int(preset["urgences"][2] + intensity * 20),
                    key="urgence_increase"
                )

            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    preset["staff"][0], preset["staff"][1],
                    int(preset["staff"][2] + intensity * 15),
                    key="staff_decrease"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    preset["lits"][0], preset["lits"][1],
                    int(preset["lits"][2] + intensity * 25),
                    key="bed_pressure"
                )
        
        elif "Vacances" in scenario_type:
            st.success("📅 **Scénario Période de Vacances**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Variation admissions (%)",
                    preset["admissions"][0], preset["admissions"][1],
                    int(preset["admissions"][2] + intensity * 20),
                    key="admission_increase"
                )
                urgence_increase = st.slider(
                    "Variation urgences (%)",
                    preset["urgences"][0], preset["urgences"][1],
                    int(preset["urgences"][2] + intensity * 25),
                    key="urgence_increase"
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    preset["staff"][0], preset["staff"][1],
                    int(preset["staff"][2] + intensity * 20),
                    key="staff_decrease"
                )
                bed_pressure = st.slider(
                    "Variation lits (%)",
                    preset["lits"][0], preset["lits"][1],
                    int(preset["lits"][2] + intensity * 20),
                    key="bed_pressure"
                )
        
        else:  # Personnalisé
            st.info("🎯 **Scénario Personnalisé**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Variation admissions (%)",
                    preset["admissions"][0], preset["admissions"][1],
                    preset["admissions"][2],
                    key="admission_increase"
                )
                urgence_increase = st.slider(
                    "Variation urgences (%)",
                    preset["urgences"][0], preset["urgences"][1],
                    preset["urgences"][2],
                    key="urgence_increase"
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Variation personnel (%)",
                    preset["staff"][0], preset["staff"][1],
                    preset["staff"][2],
                    key="staff_decrease"
                )
                bed_pressure = st.slider(
                    "Variation lits (%)",
                    preset["lits"][0], preset["lits"][1],
                    preset["lits"][2],
                    key="bed_pressure"
                )
    
    # Bouton de simulation
    st.markdown("---")
    
    if st.button("🚀 Lancer la Simulation", type="primary", width="stretch"):
        
        with st.spinner("Simulation en cours..."):
            # Calcul baseline (moyenne des derniers 30 jours dans les données)
            recent_data = df.tail(30)
            
            baseline_admissions = recent_data['nombre_admissions'].mean()
            baseline_urgences = recent_data['nombre_passages_urgences'].mean()
            baseline_occupation = recent_data['taux_occupation_lits'].mean()
            baseline_staff = recent_data['taux_couverture_personnel'].mean()
            
            # Calcul des valeurs simulées
            sim_admissions = baseline_admissions * (1 + admission_increase/100)
            sim_urgences = baseline_urgences * (1 + urgence_increase/100)
            sim_staff = baseline_staff * (1 - staff_decrease/100)
            sim_occupation = min(1.0, baseline_occupation * (1 + bed_pressure/100))
            
            # Résultats
            st.success("✅ Simulation terminée")
            
            st.markdown("---")
            render_title(
                "📈 Résultats de la simulation",
                "Comparaison entre la situation récente (baseline) et le scénario simulé.",
                heading="###",
            )
            
            # Métriques comparatives
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                delta_adm = sim_admissions - baseline_admissions
                metric_with_info(
                    "Admissions/jour",
                    "Baseline = moyenne des 30 derniers jours. Scénario = baseline × (1 + % admissions).",
                    f"{sim_admissions:.0f}",
                    delta=f"{delta_adm:+.0f} ({admission_increase:+.0f}%)",
                    delta_color="inverse",
                )
            
            with col2:
                delta_urg = sim_urgences - baseline_urgences
                metric_with_info(
                    "Passages urgences/jour",
                    "Baseline = moyenne des 30 derniers jours. Scénario = baseline × (1 + % urgences).",
                    f"{sim_urgences:.0f}",
                    delta=f"{delta_urg:+.0f} ({urgence_increase:+.0f}%)",
                    delta_color="inverse",
                )
            
            with col3:
                delta_occ = (sim_occupation - baseline_occupation) * 100
                metric_with_info(
                    "Taux occupation lits",
                    "Baseline = moyenne des 30 derniers jours. Scénario = baseline × (1 + % pression lits).",
                    f"{sim_occupation*100:.1f}%",
                    delta=f"{delta_occ:+.1f}%",
                    delta_color="inverse",
                )
            
            with col4:
                delta_staff = (sim_staff - baseline_staff) * 100
                metric_with_info(
                    "Couverture personnel",
                    "Baseline = moyenne des 30 derniers jours. Scénario = baseline × (1 - % réduction personnel).",
                    f"{sim_staff*100:.1f}%",
                    delta=f"{delta_staff:+.1f}%",
                    delta_color="normal",
                )
            
            # Graphique de projection
            st.markdown("---")
            render_title(
                "📊 Projection sur la période",
                "Projection journalière avec montée/descente progressive selon l'intensité.",
                heading="###",
            )
            
            # Créer des données de projection
            dates = pd.date_range(start=start_date, periods=duration, freq='D')
            
            # Variation progressive (courbe réaliste)
            progression = np.array([
                np.sin((i / duration) * np.pi) * intensity for i in range(duration)
            ])
            
            projection_data = pd.DataFrame({
                'Date': dates,
                'Admissions_baseline': baseline_admissions,
                'Admissions_scenario': baseline_admissions * (1 + (admission_increase/100) * progression),
                'Urgences_baseline': baseline_urgences,
                'Urgences_scenario': baseline_urgences * (1 + (urgence_increase/100) * progression),
                'Occupation_baseline': baseline_occupation * 100,
                'Occupation_scenario': np.clip(baseline_occupation * (1 + (bed_pressure/100) * progression) * 100, 0, 100),
                'Personnel_baseline': baseline_staff * 100,
                'Personnel_scenario': np.clip(baseline_staff * (1 - (staff_decrease/100) * progression) * 100, 0, 100)
            })
            
            # Graphique admissions
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=projection_data['Date'],
                    y=projection_data['Admissions_baseline'],
                    name='Baseline',
                    line=dict(color='lightblue', dash='dash')
                ))
                fig.add_trace(go.Scatter(
                    x=projection_data['Date'],
                    y=projection_data['Admissions_scenario'],
                    name='Scénario',
                    line=dict(color='red', width=2),
                    fill='tonexty'
                ))
                fig.update_layout(
                    title="Admissions quotidiennes",
                    height=300,
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=projection_data['Date'],
                    y=projection_data['Urgences_baseline'],
                    name='Baseline',
                    line=dict(color='lightgreen', dash='dash')
                ))
                fig.add_trace(go.Scatter(
                    x=projection_data['Date'],
                    y=projection_data['Urgences_scenario'],
                    name='Scénario',
                    line=dict(color='orange', width=2),
                    fill='tonexty'
                ))
                fig.update_layout(
                    title="Passages aux urgences",
                    height=300,
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                st.plotly_chart(fig, width="stretch")
            
            # Graphique occupation et personnel
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=projection_data['Date'],
                    y=projection_data['Occupation_baseline'],
                    name='Baseline',
                    line=dict(color='lightblue', dash='dash')
                ))
                fig.add_trace(go.Scatter(
                    x=projection_data['Date'],
                    y=projection_data['Occupation_scenario'],
                    name='Scénario',
                    line=dict(color='purple', width=2),
                    fill='tonexty'
                ))
                fig.add_hline(y=85, line_dash="dot", line_color="red", 
                             annotation_text="Seuil critique (85%)")
                fig.update_layout(
                    title="Taux d'occupation des lits (%)",
                    height=300,
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=projection_data['Date'],
                    y=projection_data['Personnel_baseline'],
                    name='Baseline',
                    line=dict(color='lightgreen', dash='dash')
                ))
                fig.add_trace(go.Scatter(
                    x=projection_data['Date'],
                    y=projection_data['Personnel_scenario'],
                    name='Scénario',
                    line=dict(color='darkgreen', width=2),
                    fill='tonexty'
                ))
                fig.add_hline(y=85, line_dash="dot", line_color="red",
                             annotation_text="Seuil minimum (85%)")
                fig.update_layout(
                    title="Couverture personnel (%)",
                    height=300,
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                st.plotly_chart(fig, width="stretch")
            
            # Analyse des risques
            st.markdown("---")
            st.subheader("⚠️ Analyse des risques et impacts")
            
            risk_level = "🟢 FAIBLE"
            risk_color = "success"
            
            if sim_occupation > 0.85 or sim_staff < 0.85:
                risk_level = "🔴 CRITIQUE"
                risk_color = "danger"
            elif sim_occupation > 0.75 or sim_staff < 0.9:
                risk_level = "🟠 MODÉRÉ"
                risk_color = "warning"
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if risk_color == "danger":
                    st.markdown(f"""
                    <div class="alert-danger">
                        <strong>{risk_level}</strong><br>
                        Niveau de risque : <strong>CRITIQUE</strong><br>
                        Mesures d'urgence nécessaires
                    </div>
                    """, unsafe_allow_html=True)
                elif risk_color == "warning":
                    st.markdown(f"""
                    <div class="alert-warning">
                        <strong>{risk_level}</strong><br>
                        Niveau de risque : <strong>MODÉRÉ</strong><br>
                        Surveillance renforcée requise
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="alert-success">
                        <strong>{risk_level}</strong><br>
                        Niveau de risque : <strong>FAIBLE</strong><br>
                        Situation gérable
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Besoins supplémentaires
                beds_needed = max(0, int((sim_occupation - 0.80) * df['lits_total'].iloc[-1]))
                staff_needed = max(0, int((0.90 - sim_staff) * (
                    df['nb_medecins_disponibles'].iloc[-1] +
                    df['nb_infirmiers_disponibles'].iloc[-1] +
                    df['nb_aides_soignants_disponibles'].iloc[-1]
                )))
                
                st.markdown(f"""
                <div class="alert-warning">
                    <strong>🛏️ Besoins supplémentaires</strong><br>
                    Lits : <strong>+{beds_needed}</strong><br>
                    Personnel : <strong>+{staff_needed}</strong><br>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # Coût estimé
                cost_per_bed = 500  # €/jour
                cost_per_staff = 300  # €/jour
                daily_cost = beds_needed * cost_per_bed + staff_needed * cost_per_staff
                total_cost = daily_cost * duration
                
                st.markdown(f"""
                <div class="alert-warning">
                    <strong>💰 Coût estimé</strong><br>
                    Par jour : <strong>{daily_cost:,.0f} €</strong><br>
                    Total ({duration}j) : <strong>{total_cost:,.0f} €</strong>
                </div>
                """, unsafe_allow_html=True)
            
            # Recommandations
            st.markdown("---")
            st.subheader("💡 Recommandations")
            
            recommendations = []
            
            if sim_occupation > 0.85:
                recommendations.append("🛏️ **Augmenter la capacité d'accueil** : Préparer des lits supplémentaires et activer le plan blanc si nécessaire.")
            
            if sim_staff < 0.85:
                recommendations.append("👥 **Renforcer le personnel** : Recruter du personnel temporaire, annuler les congés non critiques, activer les astreintes.")
            
            if sim_urgences > baseline_urgences * 1.5:
                recommendations.append("🚨 **Renforcer les urgences** : Ouvrir des box supplémentaires, prépositionner du matériel, activer le circuit court.")
            
            if admission_increase > 100:
                recommendations.append("📋 **Gestion des admissions** : Prioriser les urgences vitales, reporter les interventions programmées non urgentes.")
            
            if "Épidémie" in scenario_type:
                recommendations.append("🦠 **Mesures sanitaires** : Activer le protocole épidémie, isoler les cas, renforcer l'hygiène, prévoir stocks de matériel.")
            
            if "Grève" in scenario_type:
                recommendations.append("🚫 **Plan de continuité** : Service minimum garanti, réorganisation des équipes, communication aux usagers.")
            
            if not recommendations:
                recommendations.append("✅ **Situation maîtrisée** : La situation reste gérable avec les ressources actuelles. Maintenir la surveillance.")
            
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
            
            # Export des résultats
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export CSV
                csv_data = projection_data.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger les données (CSV)",
                    data=csv_data,
                    file_name=f"simulation_{start_date.strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Résumé texte
                summary = f"""
SIMULATION - {scenario_type}
Date: {start_date.strftime('%d/%m/%Y')}
Durée: {duration} jours
Intensité: {intensity}

RÉSULTATS:
- Admissions/jour: {sim_admissions:.0f} ({admission_increase:+.0f}%)
- Urgences/jour: {sim_urgences:.0f} ({urgence_increase:+.0f}%)
- Occupation lits: {sim_occupation*100:.1f}%
- Couverture personnel: {sim_staff*100:.1f}%

NIVEAU DE RISQUE: {risk_level}

BESOINS:
- Lits supplémentaires: +{beds_needed}
- Personnel supplémentaire: +{staff_needed}
- Coût total estimé: {total_cost:,.0f} €
"""
                st.download_button(
                    label="📄 Télécharger le résumé (TXT)",
                    data=summary,
                    file_name=f"resume_simulation_{start_date.strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
            
            with col3:
                st.info("💾 Résultats sauvegardés")
