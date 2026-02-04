"""
Page de recommandations automatiques
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def show(df):
    """Affiche la page de recommandations"""
    
    st.markdown('<p class="main-header">Recommandations Automatiques</p>', unsafe_allow_html=True)
    st.markdown("### 💡 Optimisez la gestion de vos ressources hospitalières")
    
    st.markdown("---")
    
    # Onglets
    tab1, tab2, tab3 = st.tabs([
        "🎯 Recommandations du Jour",
        "📅 Planification Hebdomadaire",
        "📈 Optimisation Stratégique"
    ])
    
    # ========================================
    # TAB 1: Recommandations du jour
    # ========================================
    with tab1:
        st.subheader("Recommandations pour aujourd'hui")
        
        # Analyse des derniers jours
        last_7_days = df.tail(7)
        last_30_days = df.tail(30)
        
        # KPIs actuels
        current_occupation = last_7_days['taux_occupation_lits'].mean()
        current_staff = last_7_days['taux_couverture_personnel'].mean()
        current_admissions = last_7_days['nombre_admissions'].mean()
        current_urgences = last_7_days['nombre_passages_urgences'].mean()
        
        # Tendances
        trend_occupation = (last_7_days['taux_occupation_lits'].iloc[-3:].mean() - 
                           last_7_days['taux_occupation_lits'].iloc[:3].mean())
        trend_admissions = (last_7_days['nombre_admissions'].iloc[-3:].mean() - 
                           last_7_days['nombre_admissions'].iloc[:3].mean())
        
        # État général
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if current_occupation > 0.85:
                status = "🔴 CRITIQUE"
                status_color = "danger"
            elif current_occupation > 0.75:
                status = "🟠 ATTENTION"
                status_color = "warning"
            else:
                status = "🟢 NORMAL"
                status_color = "success"
            
            st.markdown(f"""
            <div class="alert-{status_color}">
                <strong>État d'occupation</strong><br>
                <h2>{status}</h2>
                {current_occupation*100:.1f}%
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if current_staff < 0.85:
                staff_status = "🔴 INSUFFISANT"
                staff_color = "danger"
            elif current_staff < 0.90:
                staff_status = "🟠 JUSTE"
                staff_color = "warning"
            else:
                staff_status = "🟢 SUFFISANT"
                staff_color = "success"
            
            st.markdown(f"""
            <div class="alert-{staff_color}">
                <strong>Personnel disponible</strong><br>
                <h2>{staff_status}</h2>
                {current_staff*100:.1f}%
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if trend_admissions > 50:
                trend_status = "📈 HAUSSE FORTE"
                trend_color = "warning"
            elif trend_admissions > 10:
                trend_status = "📈 HAUSSE"
                trend_color = "warning"
            elif trend_admissions < -10:
                trend_status = "📉 BAISSE"
                trend_color = "success"
            else:
                trend_status = "➡️ STABLE"
                trend_color = "success"
            
            st.markdown(f"""
            <div class="alert-{trend_color}">
                <strong>Tendance admissions</strong><br>
                <h2>{trend_status}</h2>
                {trend_admissions:+.0f}/jour
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Génération des recommandations
        recommendations = generate_recommendations(
            current_occupation, current_staff, current_admissions,
            current_urgences, trend_occupation, trend_admissions, last_7_days
        )
        
        # Affichage des recommandations par priorité
        st.subheader("🎯 Actions recommandées")
        
        # Priorité CRITIQUE
        critical_recs = [r for r in recommendations if r['priority'] == 'CRITIQUE']
        if critical_recs:
            st.markdown("### 🔴 PRIORITÉ CRITIQUE - Action immédiate requise")
            for i, rec in enumerate(critical_recs, 1):
                with st.expander(f"**{i}. {rec['title']}**", expanded=True):
                    st.markdown(rec['description'])
                    st.markdown(f"**Impact attendu:** {rec['impact']}")
                    st.markdown(f"**Délai:** {rec['delay']}")
                    if rec.get('actions'):
                        st.markdown("**Actions concrètes:**")
                        for action in rec['actions']:
                            st.markdown(f"- {action}")
        
        # Priorité HAUTE
        high_recs = [r for r in recommendations if r['priority'] == 'HAUTE']
        if high_recs:
            st.markdown("### 🟠 PRIORITÉ HAUTE - À traiter rapidement")
            for i, rec in enumerate(high_recs, 1):
                with st.expander(f"**{i}. {rec['title']}**"):
                    st.markdown(rec['description'])
                    st.markdown(f"**Impact attendu:** {rec['impact']}")
                    st.markdown(f"**Délai:** {rec['delay']}")
                    if rec.get('actions'):
                        st.markdown("**Actions concrètes:**")
                        for action in rec['actions']:
                            st.markdown(f"- {action}")
        
        # Priorité MOYENNE
        medium_recs = [r for r in recommendations if r['priority'] == 'MOYENNE']
        if medium_recs:
            st.markdown("### 🟡 PRIORITÉ MOYENNE - Planification conseillée")
            for i, rec in enumerate(medium_recs, 1):
                with st.expander(f"**{i}. {rec['title']}**"):
                    st.markdown(rec['description'])
                    st.markdown(f"**Impact attendu:** {rec['impact']}")
                    st.markdown(f"**Délai:** {rec['delay']}")
                    if rec.get('actions'):
                        st.markdown("**Actions concrètes:**")
                        for action in rec['actions']:
                            st.markdown(f"- {action}")
        
        # Optimisations
        optim_recs = [r for r in recommendations if r['priority'] == 'OPTIMISATION']
        if optim_recs:
            st.markdown("### 🟢 OPTIMISATIONS - Améliorations continues")
            for i, rec in enumerate(optim_recs, 1):
                with st.expander(f"**{i}. {rec['title']}**"):
                    st.markdown(rec['description'])
                    st.markdown(f"**Impact attendu:** {rec['impact']}")
                    if rec.get('actions'):
                        st.markdown("**Actions concrètes:**")
                        for action in rec['actions']:
                            st.markdown(f"- {action}")
    
    # ========================================
    # TAB 2: Planification Hebdomadaire
    # ========================================
    with tab2:
        st.subheader("Planification de la semaine à venir")
        
        # Analyse par jour de semaine
        st.markdown("#### 📅 Prévisions par jour")
        
        # Calculer les moyennes par jour de semaine
        jour_order = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        dow_stats = df.groupby('jour_semaine').agg({
            'nombre_admissions': ['mean', 'std'],
            'nombre_passages_urgences': ['mean', 'std'],
            'taux_occupation_lits': ['mean', 'std'],
            'taux_couverture_personnel': ['mean', 'std']
        }).reset_index()
        
        dow_stats.columns = ['jour_semaine', 'adm_mean', 'adm_std', 'urg_mean', 'urg_std',
                             'occ_mean', 'occ_std', 'staff_mean', 'staff_std']
        
        # Ordonner
        dow_stats['jour_semaine'] = pd.Categorical(
            dow_stats['jour_semaine'],
            categories=jour_order,
            ordered=True
        )
        dow_stats = dow_stats.sort_values('jour_semaine')
        
        # Visualisation
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=dow_stats['jour_semaine'],
                y=dow_stats['adm_mean'],
                name='Admissions',
                marker_color='lightblue',
                error_y=dict(type='data', array=dow_stats['adm_std'])
            ))
            
            fig.update_layout(
                title="Admissions moyennes par jour",
                yaxis_title="Nombre",
                height=300
            )
            
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=dow_stats['jour_semaine'],
                y=dow_stats['occ_mean'] * 100,
                name='Occupation',
                marker_color='purple',
                error_y=dict(type='data', array=dow_stats['occ_std'] * 100)
            ))
            
            fig.add_hline(y=85, line_dash="dash", line_color="red",
                         annotation_text="Seuil critique")
            
            fig.update_layout(
                title="Taux d'occupation moyen par jour (%)",
                yaxis_title="Taux (%)",
                height=300
            )
            
            st.plotly_chart(fig, width="stretch")
        
        st.markdown("---")
        
        # Recommandations par jour
        st.markdown("#### 💡 Recommandations par jour de la semaine")
        
        for _, row in dow_stats.iterrows():
            jour = row['jour_semaine']
            occ = row['occ_mean']
            staff = row['staff_mean']
            adm = row['adm_mean']
            
            # Déterminer le niveau de risque
            if occ > 0.80 or staff < 0.88:
                color = "warning"
                icon = "⚠️"
            elif occ > 0.85 or staff < 0.85:
                color = "danger"
                icon = "🔴"
            else:
                color = "success"
                icon = "✅"
            
            with st.expander(f"{icon} **{jour}** - Occupation: {occ*100:.1f}% | Personnel: {staff*100:.1f}%"):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Indicateurs:**")
                    st.metric("Admissions moyennes", f"{adm:.0f}")
                    st.metric("Occupation moyenne", f"{occ*100:.1f}%")
                    st.metric("Personnel moyen", f"{staff*100:.1f}%")
                
                with col2:
                    st.markdown("**Actions recommandées:**")
                    
                    if occ > 0.85:
                        st.markdown("- 🛏️ Préparer lits supplémentaires")
                        st.markdown("- 📋 Planifier sorties anticipées si possible")
                    
                    if staff < 0.88:
                        st.markdown("- 👥 Renforcer l'équipe (intérimaires, astreintes)")
                        st.markdown("- 📅 Éviter les congés ce jour")
                    
                    if adm > dow_stats['adm_mean'].mean() * 1.1:
                        st.markdown("- 🚨 Renforcer l'accueil et les admissions")
                        st.markdown("- 📞 Prévoir communication flux patients")
                    
                    if occ < 0.70 and staff > 0.92:
                        st.markdown("- ✅ Opportunité pour interventions programmées")
                        st.markdown("- 🔧 Planifier maintenance/formations")
    
    # ========================================
    # TAB 3: Optimisation Stratégique
    # ========================================
    with tab3:
        st.subheader("Optimisation stratégique à moyen/long terme")
        
        # Analyse des patterns
        st.markdown("#### 📊 Analyse des patterns d'activité")
        
        # Analyse mensuelle
        df_monthly = df.groupby(df['date'].dt.to_period('M')).agg({
            'nombre_admissions': 'mean',
            'taux_occupation_lits': 'mean',
            'nombre_passages_urgences': 'mean'
        }).reset_index()
        df_monthly['date'] = df_monthly['date'].dt.to_timestamp()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                df_monthly,
                x='date',
                y='taux_occupation_lits',
                title="Évolution du taux d'occupation",
                labels={'taux_occupation_lits': 'Taux (%)', 'date': 'Mois'}
            )
            fig.update_yaxes(tickformat=".0%")
            fig.add_hline(y=0.85, line_dash="dash", line_color="red")
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            # Saisonnalité
            df_season = df.groupby('saison')['nombre_admissions'].mean().reset_index()
            fig = px.bar(
                df_season,
                x='saison',
                y='nombre_admissions',
                title="Admissions par saison",
                color='nombre_admissions',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, width="stretch")
        
        st.markdown("---")
        
        # Recommandations stratégiques
        st.markdown("#### 🎯 Recommandations stratégiques")
        
        # Analyse des événements
        events_impact = df[df['evenement_special'] != ''].groupby('evenement_special').agg({
            'nombre_admissions': 'mean',
            'impact_evenement_estime': 'mean',
            'taux_occupation_lits': 'mean'
        }).sort_values('impact_evenement_estime', ascending=False)
        
        if not events_impact.empty:
            st.markdown("##### 🦠 Gestion des événements récurrents")
            
            for event, data in events_impact.head(3).iterrows():
                impact = data['impact_evenement_estime']
                adm = data['nombre_admissions']
                occ = data['taux_occupation_lits']
                
                with st.expander(f"**{event}** - Impact moyen: {impact*100:.1f}%"):
                    st.markdown(f"""
                    **Statistiques:**
                    - Admissions moyennes pendant l'événement: {adm:.0f}/jour
                    - Taux d'occupation moyen: {occ*100:.1f}%
                    - Impact estimé: {impact*100:.1f}%
                    
                    **Recommandations:**
                    """)
                    
                    if 'Epidemie' in event or 'grippe' in event.lower():
                        st.markdown("""
                        - 💉 Renforcer campagnes de vaccination
                        - 🏥 Préparer unités d'isolement
                        - 📦 Stock anticipé EPI et matériel
                        - 👥 Former personnel protocoles sanitaires
                        """)
                    elif 'Canicule' in event:
                        st.markdown("""
                        - 🌡️ Plan canicule activable rapidement
                        - ❄️ Zones rafraîchies pour patients fragiles
                        - 💧 Stock hydratation
                        - 📞 Communication populations à risque
                        """)
                    elif 'froid' in event.lower():
                        st.markdown("""
                        - 🏥 Renforcer lits médecine/gériatrie
                        - 🚑 Plan grand froid
                        - 🔥 Accueil personnes vulnérables
                        """)
        
        st.markdown("---")
        
        # Optimisation capacités
        st.markdown("##### 🛏️ Optimisation des capacités")
        
        # Analyse utilisation lits
        avg_occupation = df['taux_occupation_lits'].mean()
        max_occupation = df['taux_occupation_lits'].max()
        days_critical = len(df[df['taux_occupation_lits'] > 0.85])
        days_low = len(df[df['taux_occupation_lits'] < 0.60])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Occupation moyenne", f"{avg_occupation*100:.1f}%")
            st.metric("Jours critiques (>85%)", f"{days_critical} ({days_critical/len(df)*100:.1f}%)")
        
        with col2:
            st.metric("Occupation maximale", f"{max_occupation*100:.1f}%")
            st.metric("Jours faible charge (<60%)", f"{days_low} ({days_low/len(df)*100:.1f}%)")
        
        with col3:
            # Capacité optimale recommandée
            optimal_capacity = int(df['lits_occupes'].quantile(0.95))
            current_capacity = df['lits_total'].iloc[-1]
            
            st.metric("Capacité actuelle", f"{current_capacity}")
            st.metric("Capacité recommandée (P95)", f"{optimal_capacity}")
        
        st.markdown("**Recommandations:**")
        
        if days_critical / len(df) > 0.10:  # Plus de 10% de jours critiques
            st.warning(f"""
            ⚠️ **Tension capacitaire forte** ({days_critical/len(df)*100:.1f}% jours >85%)
            
            Actions recommandées:
            - 🏗️ Augmenter capacité de {optimal_capacity - current_capacity} lits
            - 🔄 Améliorer rotation patients (réduire durée séjour)
            - 🏥 Développer médecine ambulatoire
            - 🤝 Conventions établissements partenaires
            """)
        else:
            st.success("""
            ✅ **Capacité généralement suffisante**
            
            Optimisations possibles:
            - 📊 Affiner planification interventions programmées
            - 🔄 Lissage charge semaine (reporter sur jours creux)
            """)
        
        st.markdown("---")
        
        # Optimisation personnel
        st.markdown("##### 👥 Optimisation des ressources humaines")
        
        avg_staff = df['taux_couverture_personnel'].mean()
        days_low_staff = len(df[df['taux_couverture_personnel'] < 0.85])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Couverture moyenne", f"{avg_staff*100:.1f}%")
            st.metric("Jours sous-effectif (<85%)", f"{days_low_staff} ({days_low_staff/len(df)*100:.1f}%)")
        
        with col2:
            # Analyse par type de personnel
            avg_doctors = df['nb_medecins_disponibles'].mean()
            avg_nurses = df['nb_infirmiers_disponibles'].mean()
            avg_aides = df['nb_aides_soignants_disponibles'].mean()
            
            st.metric("Médecins moyens", f"{avg_doctors:.0f}")
            st.metric("Infirmiers moyens", f"{avg_nurses:.0f}")
            st.metric("Aides-soignants moyens", f"{avg_aides:.0f}")
        
        st.markdown("**Recommandations:**")
        
        if days_low_staff / len(df) > 0.15:
            st.error(f"""
            🔴 **Tension RH forte** ({days_low_staff/len(df)*100:.1f}% jours <85%)
            
            Actions prioritaires:
            - 📝 Campagne recrutement
            - 🤝 Développer pool intérimaires qualifiés
            - 📚 Formation personnel polyvalent
            - ⏰ Revoir organisation temps travail
            - 💰 Primes fidélisation/attractivité
            """)
        else:
            st.success("""
            ✅ **RH globalement adéquates**
            
            Pistes d'amélioration:
            - 🎯 Ajustement fin planning selon charge prévisionnelle
            - 📊 Anticipation congés périodes creuses
            - 🔄 Mutualisation ressources inter-services
            """)
        
        st.markdown("---")
        
        # ROI des optimisations
        st.markdown("#### 💰 Retour sur investissement des optimisations")
        
        # Calculs d'économies potentielles
        avg_daily_admissions = df['nombre_admissions'].mean()
        
        # Réduction durée séjour
        avg_stay = 7  # jours (estimation)
        cost_per_day = 1000  # €
        
        if st.checkbox("Voir l'analyse coût-bénéfice"):
            
            st.markdown("##### Scénario 1: Réduction durée de séjour moyenne")
            
            col1, col2 = st.columns(2)
            
            with col1:
                reduction_days = st.slider("Réduction durée séjour (jours)", 0.0, 2.0, 0.5, 0.1)
                
                annual_admissions = avg_daily_admissions * 365
                savings_per_patient = reduction_days * cost_per_day
                annual_savings = annual_admissions * savings_per_patient
                
                st.metric("Économies/patient", f"{savings_per_patient:,.0f} €")
                st.metric("Économies annuelles", f"{annual_savings:,.0f} €")
            
            with col2:
                investment = st.number_input(
                    "Investissement nécessaire (€)",
                    value=500000,
                    step=50000
                )
                
                roi_years = investment / annual_savings if annual_savings > 0 else 999
                
                st.metric("ROI (années)", f"{roi_years:.1f}")
                
                if roi_years < 2:
                    st.success("✅ ROI excellent")
                elif roi_years < 5:
                    st.info("ℹ️ ROI acceptable")
                else:
                    st.warning("⚠️ ROI long")
            
            st.markdown(f"""
            **Exemple d'actions:**
            - 🏠 Développement hospitalisation à domicile (HAD)
            - 🚑 Renforcement soins ambulatoires
            - 💻 Optimisation parcours patient (digital)
            - 🤝 Coordination ville-hôpital améliorée
            """)


def generate_recommendations(occ, staff, adm, urg, trend_occ, trend_adm, recent_data):
    """Génère les recommandations basées sur l'analyse"""
    
    recommendations = []
    
    # CRITIQUE: Occupation très haute
    if occ > 0.85:
        recommendations.append({
            'priority': 'CRITIQUE',
            'title': 'Saturation des lits - Plan blanc à envisager',
            'description': f"Le taux d'occupation actuel ({occ*100:.1f}%) dépasse le seuil critique de 85%. Risque élevé de refus d'admission.",
            'impact': "Réduction des refus d'admission, amélioration qualité soins",
            'delay': 'Immédiat (0-4h)',
            'actions': [
                'Activer le plan blanc niveau 1',
                'Identifier lits mobilisables (chirurgie ambulatoire, court séjour)',
                'Préparer ouverture lits supplémentaires',
                'Accélérer sorties patients stabilisés',
                'Communication SAMU/régulation pour répartition patients'
            ]
        })
    
    # CRITIQUE: Personnel insuffisant
    if staff < 0.85:
        recommendations.append({
            'priority': 'CRITIQUE',
            'title': 'Sous-effectif critique - Mobilisation nécessaire',
            'description': f"La couverture personnel ({staff*100:.1f}%) est en dessous du seuil de sécurité (85%). Risque sur qualité des soins.",
            'impact': 'Sécurisation soins patients, réduction risques',
            'delay': 'Immédiat (0-24h)',
            'actions': [
                'Rappel personnel d\'astreinte',
                'Contact liste intérimaires disponibles',
                'Annulation congés non validés cette semaine',
                'Réorganisation équipes (fusion unités faible charge)',
                'Limitation admissions programmées non urgentes'
            ]
        })
    
    # HAUTE: Tendance occupation à la hausse
    if trend_occ > 0.05:
        recommendations.append({
            'priority': 'HAUTE',
            'title': 'Tendance haussière occupation - Anticipation nécessaire',
            'description': f"L'occupation augmente de {trend_occ*100:.1f}% sur les derniers jours. Risque de saturation à court terme.",
            'impact': 'Prévention saturation, maintien flux',
            'delay': '24-48h',
            'actions': [
                'Surveillance renforcée indicateurs quotidiens',
                'Planification sorties anticipées faisables',
                'Préparation lits supplémentaires',
                'Information cadres de santé pour réorganisation',
                'Reporter interventions programmées non urgentes si possible'
            ]
        })
    
    # HAUTE: Forte hausse admissions
    if trend_adm > 50:
        recommendations.append({
            'priority': 'HAUTE',
            'title': 'Pic d\'admissions - Renforcement accueil',
            'description': f"Les admissions augmentent fortement ({trend_adm:+.0f}/jour). Tension sur accueil et urgences.",
            'impact': 'Fluidité parcours patient, réduction attente',
            'delay': '12-24h',
            'actions': [
                'Renforcer personnel bureau admissions',
                'Ouvrir box supplémentaires urgences',
                'Activer circuit court pour patients légers',
                'Communication aux patients (délais)',
                'Mobiliser équipe administrative support'
            ]
        })
    
    # MOYENNE: Occupation modérément haute
    if 0.75 < occ <= 0.85:
        recommendations.append({
            'priority': 'MOYENNE',
            'title': 'Occupation soutenue - Surveillance renforcée',
            'description': f"L'occupation ({occ*100:.1f}%) est élevée sans être critique. Vigilance nécessaire.",
            'impact': 'Prévention dégradation, maintien capacité réaction',
            'delay': '2-3 jours',
            'actions': [
                'Monitoring quotidien taux occupation',
                'Préparation plan B (lits mobilisables)',
                'Communication interne état tension',
                'Optimisation durées de séjour',
                'Priorisation admissions programmées'
            ]
        })
    
    # MOYENNE: Personnel juste
    if 0.85 <= staff < 0.90:
        recommendations.append({
            'priority': 'MOYENNE',
            'title': 'Personnel en limite - Planification prudente',
            'description': f"La couverture ({staff*100:.1f}%) est limite. Marge de manœuvre réduite.",
            'impact': 'Sécurisation effectifs, prévention épuisement',
            'delay': '3-5 jours',
            'actions': [
                'Validation congés au compte-gouttes',
                'Anticipation besoins intérim semaine suivante',
                'Report formations non critiques',
                'Mutualisation ressources inter-services',
                'Communication transparente équipes sur situation'
            ]
        })
    
    # Analyse événements
    active_events = recent_data[recent_data['evenement_special'] != '']
    if not active_events.empty:
        main_event = active_events['evenement_special'].mode()[0] if len(active_events) > 0 else ""
        
        if main_event:
            recommendations.append({
                'priority': 'HAUTE',
                'title': f'Événement actif: {main_event}',
                'description': f"Un événement spécial ({main_event}) est en cours. Adaptation protocoles nécessaire.",
                'impact': 'Gestion adaptée événement, limitation propagation',
                'delay': 'En cours',
                'actions': get_event_specific_actions(main_event)
            })
    
    # OPTIMISATIONS: Situation favorable
    if occ < 0.70 and staff > 0.90:
        recommendations.append({
            'priority': 'OPTIMISATION',
            'title': 'Période favorable - Opportunités d\'amélioration',
            'description': f"Situation confortable (occ: {occ*100:.1f}%, staff: {staff*100:.1f}%). Moment propice optimisations.",
            'impact': 'Amélioration continue, préparation périodes tendues',
            'actions': [
                'Planifier interventions programmées en attente',
                'Organiser formations personnel',
                'Maintenance équipements',
                'Réunions amélioration processus',
                'Valorisation équipes (reconnaissance)'
            ]
        })
    
    # Toujours: Optimisation prévisionnelle
    recommendations.append({
        'priority': 'OPTIMISATION',
        'title': 'Amélioration outils prédictifs',
        'description': "Affiner les capacités de prédiction pour anticiper encore mieux les variations.",
        'impact': 'Meilleure anticipation, réduction situations critiques',
        'actions': [
            'Enrichissement base données (météo, événements locaux)',
            'Amélioration modèles prédictifs (ML)',
            'Formation équipes utilisation dashboard',
            'Retours d\'expérience réguliers',
            'Ajustement seuils alertes'
        ]
    })
    
    return recommendations


def get_event_specific_actions(event):
    """Retourne actions spécifiques selon type événement"""
    
    if 'Epidemie' in event or 'grippe' in event.lower() or 'gastro' in event.lower():
        return [
            'Activation protocole épidémie',
            'Isolement patients contagieux',
            'Renforcement mesures hygiène (SHA, masques)',
            'Limitation visites si nécessaire',
            'Communication personnel protocoles',
            'Surveillance stock EPI',
            'Cellule de crise quotidienne'
        ]
    
    elif 'Canicule' in event or 'chaleur' in event.lower():
        return [
            'Activation plan canicule',
            'Surveillance personnes âgées/fragiles',
            'Hydratation renforcée',
            'Climatisation zones critiques',
            'Report activités non urgentes',
            'Communication populations à risque',
            'Coordination avec SAMU/médecine ville'
        ]
    
    elif 'froid' in event.lower():
        return [
            'Activation plan grand froid',
            'Accueil renforcé personnes vulnérables',
            'Surveillance pathologies respiratoires',
            'Coordination avec services sociaux',
            'Stock couvertures/boissons chaudes',
            'Communication risques populations'
        ]
    
    elif 'pollution' in event.lower():
        return [
            'Information patients pathologies respiratoires',
            'Limitation activités extérieures',
            'Renforcement consultations pneumologie',
            'Communication recommandations sanitaires',
            'Surveillance indicateurs respiratoires'
        ]
    
    else:
        return [
            'Activation cellule de crise',
            'Évaluation impact sur services',
            'Communication interne renforcée',
            'Adaptation organisation selon besoin',
            'Coordination avec autorités'
        ]
