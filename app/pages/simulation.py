"""
Page de simulation de scénarios
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

def show(df):
    """Affiche la page de simulation de scénarios"""
    
    st.markdown('<p class="main-header">Simulation de Scénarios Hospitaliers</p>', unsafe_allow_html=True)
    st.markdown("### Anticipez l'impact d'événements sur vos ressources")
    
    # Sélection du scénario
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Configuration du scénario")
        
        scenario_type = st.selectbox(
            "Type de scénario",
            [
                "🦠 Épidémie (Grippe/Covid)",
                "🔥 Canicule",
                "❄️ Vague de froid",
                "🚫 Grève du personnel",
                "🚨 Afflux massif (accident)",
                "📅 Période de vacances",
                "🎯 Personnalisé"
            ]
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
        st.subheader("📊 Paramètres d'impact")
        
        # Paramètres selon le type de scénario
        if "Épidémie" in scenario_type:
            st.info("🦠 **Scénario Épidémie**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    0, 200, int(50 + intensity * 100)
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    0, 300, int(80 + intensity * 120)
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    0, 50, int(intensity * 30),
                    help="Personnel malade"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    0, 100, int(60 + intensity * 40)
                )
        
        elif "Canicule" in scenario_type:
            st.warning("🔥 **Scénario Canicule**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    0, 150, int(30 + intensity * 70)
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    0, 200, int(40 + intensity * 80)
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    0, 30, int(intensity * 15),
                    help="Congés d'été"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    0, 80, int(40 + intensity * 30)
                )
        
        elif "Vague de froid" in scenario_type:
            st.info("❄️ **Scénario Vague de Froid**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    0, 120, int(25 + intensity * 60)
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    0, 150, int(35 + intensity * 70)
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    0, 25, int(intensity * 15),
                    help="Difficultés de transport"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    0, 70, int(35 + intensity * 35)
                )
        
        elif "Grève" in scenario_type:
            st.error("🚫 **Scénario Grève**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Variation admissions (%)",
                    -50, 50, int(-20 + intensity * 20),
                    help="Peut diminuer si report d'interventions"
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    0, 100, int(20 + intensity * 50),
                    help="Patients se reportant aux urgences"
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    0, 80, int(30 + intensity * 50)
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    -30, 50, int(intensity * 30)
                )
        
        elif "Afflux massif" in scenario_type:
            st.error("🚨 **Scénario Afflux Massif**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Augmentation admissions (%)",
                    0, 500, int(100 + intensity * 300)
                )
                urgence_increase = st.slider(
                    "Augmentation urgences (%)",
                    0, 1000, int(200 + intensity * 600)
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    0, 20, 0,
                    help="Personnel en rappel possible"
                )
                bed_pressure = st.slider(
                    "Pression sur les lits (%)",
                    0, 150, int(80 + intensity * 70)
                )
        
        elif "Vacances" in scenario_type:
            st.success("📅 **Scénario Période de Vacances**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Variation admissions (%)",
                    -30, 30, int(-10 + intensity * 20)
                )
                urgence_increase = st.slider(
                    "Variation urgences (%)",
                    -20, 40, int(-5 + intensity * 25)
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Réduction personnel (%)",
                    0, 50, int(20 + intensity * 20)
                )
                bed_pressure = st.slider(
                    "Variation lits (%)",
                    -20, 30, int(-5 + intensity * 20)
                )
        
        else:  # Personnalisé
            st.info("🎯 **Scénario Personnalisé**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                admission_increase = st.slider(
                    "Variation admissions (%)",
                    -50, 500, 0
                )
                urgence_increase = st.slider(
                    "Variation urgences (%)",
                    -50, 1000, 0
                )
            
            with col_b:
                staff_decrease = st.slider(
                    "Variation personnel (%)",
                    -50, 80, 0
                )
                bed_pressure = st.slider(
                    "Variation lits (%)",
                    -50, 150, 0
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
            st.subheader("📈 Résultats de la simulation")
            
            # Métriques comparatives
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                delta_adm = sim_admissions - baseline_admissions
                st.metric(
                    "Admissions/jour",
                    f"{sim_admissions:.0f}",
                    delta=f"{delta_adm:+.0f} ({admission_increase:+.0f}%)",
                    delta_color="inverse"
                )
            
            with col2:
                delta_urg = sim_urgences - baseline_urgences
                st.metric(
                    "Passages urgences/jour",
                    f"{sim_urgences:.0f}",
                    delta=f"{delta_urg:+.0f} ({urgence_increase:+.0f}%)",
                    delta_color="inverse"
                )
            
            with col3:
                delta_occ = (sim_occupation - baseline_occupation) * 100
                st.metric(
                    "Taux occupation lits",
                    f"{sim_occupation*100:.1f}%",
                    delta=f"{delta_occ:+.1f}%",
                    delta_color="inverse"
                )
            
            with col4:
                delta_staff = (sim_staff - baseline_staff) * 100
                st.metric(
                    "Couverture personnel",
                    f"{sim_staff*100:.1f}%",
                    delta=f"{delta_staff:+.1f}%",
                    delta_color="normal"
                )
            
            # Graphique de projection
            st.markdown("---")
            st.subheader("📊 Projection sur la période")
            
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
