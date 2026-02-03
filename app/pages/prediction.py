"""
Page de prédiction avec modèle ML
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

try:
    from smartcare_model import (
        prepare_prediction_row,
        apply_overrides,
        predict_from_features,
    )
except Exception:
    prepare_prediction_row = None
    apply_overrides = None
    predict_from_features = None

def show(df, model, model_available):
    """Affiche la page de prédiction"""

    pipeline_ready = (
        model_available
        and isinstance(model, dict)
        and "feature_cols" in model
        and "feature_df" in model
        and prepare_prediction_row is not None
        and apply_overrides is not None
        and predict_from_features is not None
    )
    
    st.markdown('<p class="main-header">Prédiction des Besoins Hospitaliers</p>', unsafe_allow_html=True)
    
    # Statut du modèle
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🔮 Anticipez les flux et optimisez vos ressources")
    
    with col2:
        if model_available:
            st.success("✅ Modèle ML chargé")
        else:
            st.warning("⏳ Modèle en attente")
            st.info("📁 Placez `ml/artifacts/gradient_boosting.joblib` + `feature_columns.json` + `data/raw/` dans le projet")
    
    st.markdown("---")
    
    # Onglets
    tab1, tab2, tab3 = st.tabs([
        "🎯 Prédiction Simple",
        "📈 Prédiction Multi-jours",
        "🔧 Uploader Modèle ML"
    ])
    
    # ========================================
    # TAB 1: Prédiction Simple
    # ========================================
    with tab1:
        st.subheader("Prédiction pour une journée spécifique")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 Paramètres temporels")
            
            pred_date = st.date_input(
                "Date à prédire",
                value=datetime.now() + timedelta(days=7),
                min_value=datetime.now(),
                max_value=datetime.now() + timedelta(days=365)
            )
            
            day_of_week = pred_date.strftime('%A')
            day_of_week_fr = {
                'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
                'Thursday': 'Jeudi', 'Friday': 'Vendredi', 'Saturday': 'Samedi', 'Sunday': 'Dimanche'
            }
            
            st.info(f"📆 {day_of_week_fr.get(day_of_week, day_of_week)}")
            
            # Saison
            month = pred_date.month
            if month in [12, 1, 2]:
                saison = "Hiver"
            elif month in [3, 4, 5]:
                saison = "Printemps"
            elif month in [6, 7, 8]:
                saison = "Été"
            else:
                saison = "Automne"
            
            st.info(f"🌤️ {saison}")
            
            vacances = st.checkbox("Vacances scolaires")
        
        with col2:
            st.markdown("#### 🌡️ Paramètres contextuels")
            
            temperature = st.slider(
                "Température moyenne (°C)",
                min_value=-10.0,
                max_value=40.0,
                value=15.0,
                step=0.5
            )
            
            if pipeline_ready:
                meteo_options = sorted({
                    c.replace("meteo_", "")
                    for c in model["feature_cols"]
                    if c.startswith("meteo_")
                })
                meteo = st.selectbox(
                    "Conditions météo",
                    ["Aucun"] + meteo_options
                )
            else:
                meteo = st.selectbox(
                    "Conditions météo",
                    ['Ensoleillé', 'Nuageux', 'Pluie', 'Neige', 'Orage', 'Canicule', 'Grand froid']
                )
            
            if pipeline_ready:
                event_options = sorted({
                    c.replace("event_", "")
                    for c in model["feature_cols"]
                    if c.startswith("event_")
                })
                evenement = st.selectbox(
                    "Événement spécial",
                    ["Aucun"] + event_options
                )
            else:
                evenement = st.selectbox(
                    "Événement spécial",
                    ['Aucun', 'Épidémie grippe', 'Épidémie gastro', 'Covid-19', 
                     'Canicule', 'Grand froid', 'Pic pollution']
                )
        
        st.markdown("---")
        
        if st.button("🚀 Calculer la Prédiction", type="primary", use_container_width=True):
            
            with st.spinner("Calcul en cours..."):
                
                if pipeline_ready:
                    st.info("🤖 Utilisation du modèle ML SmartCare")
                    try:
                        meteo_override = None if meteo == "Aucun" else meteo
                        event_override = None if evenement == "Aucun" else evenement

                        try:
                            row = prepare_prediction_row(
                                model["feature_df"],
                                model["feature_cols"],
                                target_date=pred_date
                            )
                        except Exception:
                            row = prepare_prediction_row(
                                model["feature_df"],
                                model["feature_cols"],
                                target_date=None
                            )
                            st.info("ℹ️ Date hors historique ML : utilisation de la dernière date disponible")
                        row = apply_overrides(
                            row,
                            model["feature_cols"],
                            meteo=meteo_override,
                            event=event_override
                        )
                        result = predict_from_features(
                            row,
                            model["model"],
                            model["feature_cols"],
                            safety_margin=0.10
                        )

                        pred_admissions = result["prediction"]
                        urg_ratio = df["nombre_passages_urgences"].mean() / df["nombre_admissions"].mean()
                        pred_urgences = pred_admissions * urg_ratio
                        pred_occupation = df["taux_occupation_lits"].mean()

                    except Exception as e:
                        st.error(f"Erreur avec le modèle ML : {e}")
                        st.warning("Passage au modèle statistique de secours")
                        pred_admissions, pred_urgences, pred_occupation = predict_with_stats(
                            df, day_of_week_fr.get(day_of_week, day_of_week),
                            saison, vacances, temperature, evenement
                        )
                elif model_available and model is not None:
                    # Utiliser un modèle ML simple si fourni
                    st.info("🤖 Utilisation du modèle ML")
                    try:
                        features = prepare_features_for_model(
                            pred_date, day_of_week, saison, vacances,
                            temperature, meteo, evenement
                        )
                        predictions = model.predict([features])
                        pred_admissions = predictions[0]
                        pred_urgences = predictions[1] if len(predictions) > 1 else predictions[0] * 3.5
                        pred_occupation = predictions[2] if len(predictions) > 2 else 0.75
                    except Exception as e:
                        st.error(f"Erreur avec le modèle ML : {e}")
                        st.warning("Passage au modèle statistique de secours")
                        pred_admissions, pred_urgences, pred_occupation = predict_with_stats(
                            df, day_of_week_fr.get(day_of_week, day_of_week),
                            saison, vacances, temperature, evenement
                        )
                else:
                    # Utiliser le modèle statistique de base
                    st.info("📊 Utilisation du modèle statistique")
                    pred_admissions, pred_urgences, pred_occupation = predict_with_stats(
                        df, day_of_week_fr.get(day_of_week, day_of_week),
                        saison, vacances, temperature, evenement
                    )
                
                # Calculs dérivés
                pred_hospitalisations = int(pred_admissions * 0.65)
                pred_sorties = int(pred_admissions * 0.95)
                pred_lits_occupes = int(1650 * pred_occupation)
                
                # Affichage des résultats
                st.success("✅ Prédiction calculée")
                
                st.markdown("---")
                st.subheader("📊 Résultats de la prédiction")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # Comparaison avec baseline
                    baseline_adm = df[df['jour_semaine'] == day_of_week_fr.get(day_of_week, day_of_week)]['nombre_admissions'].mean()
                    delta_adm = pred_admissions - baseline_adm
                    
                    st.metric(
                        "Admissions",
                        f"{pred_admissions:.0f}",
                        delta=f"{delta_adm:+.0f}",
                        delta_color="inverse"
                    )
                
                with col2:
                    baseline_urg = df[df['jour_semaine'] == day_of_week_fr.get(day_of_week, day_of_week)]['nombre_passages_urgences'].mean()
                    delta_urg = pred_urgences - baseline_urg
                    
                    st.metric(
                        "Passages urgences",
                        f"{pred_urgences:.0f}",
                        delta=f"{delta_urg:+.0f}",
                        delta_color="inverse"
                    )
                
                with col3:
                    st.metric(
                        "Hospitalisations",
                        f"{pred_hospitalisations:.0f}"
                    )
                
                with col4:
                    color = "normal" if pred_occupation < 0.85 else "inverse"
                    st.metric(
                        "Taux occupation",
                        f"{pred_occupation*100:.1f}%",
                        delta="Critique" if pred_occupation > 0.85 else "Normal",
                        delta_color=color
                    )
                
                # Détails supplémentaires
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🛏️ Besoins en lits")
                    st.metric("Lits occupés prévus", f"{pred_lits_occupes} / 1650")
                    st.metric("Lits disponibles", f"{1650 - pred_lits_occupes}")
                    
                    if pred_occupation > 0.85:
                        st.error(f"⚠️ Risque de saturation ({pred_occupation*100:.1f}%)")
                    elif pred_occupation > 0.75:
                        st.warning(f"⚠️ Surveillance nécessaire ({pred_occupation*100:.1f}%)")
                    else:
                        st.success(f"✅ Capacité suffisante ({pred_occupation*100:.1f}%)")
                
                with col2:
                    st.markdown("#### 👥 Besoins en personnel")
                    
                    # Estimation besoins personnel
                    ratio_patient_staff = 3.5
                    staff_needed = int(pred_lits_occupes / ratio_patient_staff)
                    
                    baseline_staff = int((
                        df['nb_medecins_disponibles'].mean() +
                        df['nb_infirmiers_disponibles'].mean() +
                        df['nb_aides_soignants_disponibles'].mean()
                    ))
                    
                    st.metric("Personnel nécessaire", f"{staff_needed}")
                    st.metric("Personnel disponible moyen", f"{baseline_staff}")
                    
                    if staff_needed > baseline_staff * 1.1:
                        st.error("⚠️ Renfort nécessaire")
                    elif staff_needed > baseline_staff:
                        st.warning("⚠️ Mobilisation complète")
                    else:
                        st.success("✅ Effectifs suffisants")
                
                # Intervalle de confiance
                st.markdown("---")
                st.subheader("📏 Intervalle de confiance")
                
                # Calcul IC (95%)
                std_admissions = df['nombre_admissions'].std()
                ic_low_adm = max(0, pred_admissions - 1.96 * std_admissions)
                ic_high_adm = pred_admissions + 1.96 * std_admissions
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=['Prédiction'],
                        y=[pred_admissions],
                        mode='markers',
                        marker=dict(size=15, color='red'),
                        name='Prédiction',
                        error_y=dict(
                            type='data',
                            symmetric=False,
                            array=[ic_high_adm - pred_admissions],
                            arrayminus=[pred_admissions - ic_low_adm]
                        )
                    ))
                    
                    fig.update_layout(
                        title="Admissions (IC 95%)",
                        yaxis_title="Nombre",
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption(f"Intervalle: [{ic_low_adm:.0f} - {ic_high_adm:.0f}]")
                
                with col2:
                    # Distribution historique comparée
                    fig = go.Figure()
                    
                    hist_data = df[df['jour_semaine'] == day_of_week_fr.get(day_of_week, day_of_week)]['nombre_admissions']
                    
                    fig.add_trace(go.Histogram(
                        x=hist_data,
                        name='Historique',
                        opacity=0.7,
                        marker_color='lightblue'
                    ))
                    
                    fig.add_vline(
                        x=pred_admissions,
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Prédiction"
                    )
                    
                    fig.update_layout(
                        title=f"Distribution historique ({day_of_week_fr.get(day_of_week, day_of_week)})",
                        xaxis_title="Admissions",
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    # ========================================
    # TAB 2: Prédiction Multi-jours
    # ========================================
    with tab2:
        st.subheader("Prédiction sur plusieurs jours")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Date de début",
                value=datetime.now() + timedelta(days=1),
                min_value=datetime.now(),
                max_value=datetime.now() + timedelta(days=365)
            )
        
        with col2:
            n_days = st.slider(
                "Nombre de jours à prédire",
                min_value=1,
                max_value=90,
                value=30
            )
        
        # Options avancées
        with st.expander("⚙️ Options avancées"):
            include_seasonality = st.checkbox("Inclure la saisonnalité", value=True)
            include_trend = st.checkbox("Inclure la tendance", value=True)
            confidence_level = st.slider("Niveau de confiance (%)", 80, 99, 95)
        
        if st.button("🚀 Générer les Prédictions", type="primary", use_container_width=True):
            
            with st.spinner(f"Calcul des prédictions pour {n_days} jours..."):
                
                # Générer les prédictions jour par jour
                predictions = []
                dates = pd.date_range(start=start_date, periods=n_days, freq='D')
                
                for date in dates:
                    day_name = date.strftime('%A')
                    day_fr = {
                        'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
                        'Thursday': 'Jeudi', 'Friday': 'Vendredi', 'Saturday': 'Samedi', 
                        'Sunday': 'Dimanche'
                    }.get(day_name, day_name)
                    
                    month = date.month
                    if month in [12, 1, 2]:
                        saison = "Hiver"
                    elif month in [3, 4, 5]:
                        saison = "Printemps"
                    elif month in [6, 7, 8]:
                        saison = "Été"
                    else:
                        saison = "Automne"
                    
                    # Prédiction simple (à améliorer avec le modèle ML)
                    pred_adm, pred_urg, pred_occ = predict_with_stats(
                        df, day_fr, saison, False, 15.0, 'Aucun'
                    )
                    
                    predictions.append({
                        'date': date,
                        'admissions': pred_adm,
                        'urgences': pred_urg,
                        'occupation': pred_occ * 100
                    })
                
                pred_df = pd.DataFrame(predictions)
                
                # Affichage
                st.success(f"✅ {n_days} jours prédits")
                
                st.markdown("---")
                
                # Graphiques
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=pred_df['date'],
                        y=pred_df['admissions'],
                        name='Admissions',
                        mode='lines+markers',
                        line=dict(color='blue', width=2)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=pred_df['date'],
                        y=pred_df['urgences'],
                        name='Urgences',
                        mode='lines+markers',
                        line=dict(color='orange', width=2)
                    ))
                    
                    fig.update_layout(
                        title="Prédiction des flux",
                        xaxis_title="Date",
                        yaxis_title="Nombre",
                        height=350
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=pred_df['date'],
                        y=pred_df['occupation'],
                        mode='lines+markers',
                        fill='tozeroy',
                        line=dict(color='purple', width=2),
                        name='Occupation'
                    ))
                    
                    fig.add_hline(
                        y=85,
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Seuil critique"
                    )
                    
                    fig.update_layout(
                        title="Taux d'occupation prévisionnel",
                        xaxis_title="Date",
                        yaxis_title="Taux (%)",
                        height=350
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Statistiques
                st.markdown("---")
                st.subheader("📊 Statistiques de la période")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Admissions moyennes/jour",
                        f"{pred_df['admissions'].mean():.0f}"
                    )
                
                with col2:
                    st.metric(
                        "Urgences moyennes/jour",
                        f"{pred_df['urgences'].mean():.0f}"
                    )
                
                with col3:
                    st.metric(
                        "Occupation moyenne",
                        f"{pred_df['occupation'].mean():.1f}%"
                    )
                
                with col4:
                    critical_days = len(pred_df[pred_df['occupation'] > 85])
                    st.metric(
                        "Jours critiques",
                        f"{critical_days}",
                        delta=f"{critical_days/n_days*100:.0f}%"
                    )
                
                # Alertes
                if critical_days > 0:
                    st.error(f"⚠️ {critical_days} jour(s) avec risque de saturation détecté(s)")
                    
                    critical_dates = pred_df[pred_df['occupation'] > 85]['date'].dt.strftime('%d/%m/%Y').tolist()
                    st.warning(f"Dates concernées : {', '.join(critical_dates[:5])}{'...' if len(critical_dates) > 5 else ''}")
                
                # Export
                st.markdown("---")
                
                csv_export = pred_df.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger les prédictions (CSV)",
                    data=csv_export,
                    file_name=f"predictions_{start_date.strftime('%Y%m%d')}_{n_days}j.csv",
                    mime="text/csv"
                )
    
    # ========================================
    # TAB 3: Upload Modèle
    # ========================================
    with tab3:
        st.subheader("📁 Uploader un modèle ML personnalisé")
        
        st.info("""
        **Instructions pour votre collègue :**
        
        1. Le modèle doit être au format `.joblib`
        2. Il doit prédire au minimum : `nombre_admissions`, `nombre_passages_urgences`, `taux_occupation_lits`
        3. Les features attendues seront affichées ci-dessous
        """)
        
        uploaded_file = st.file_uploader(
            "Choisir un fichier .joblib",
            type=['joblib'],
            help="Modèle ML entraîné et sauvegardé avec joblib"
        )
        
        if uploaded_file is not None:
            try:
                from pathlib import Path
                import joblib
                
                # Sauvegarder le fichier
                model_path = Path(__file__).parent.parent / "model_prediction.joblib"
                
                with open(model_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                
                st.success("✅ Modèle uploadé avec succès!")
                st.info("🔄 Rechargez la page pour utiliser le nouveau modèle")
                
                # Bouton de rechargement
                if st.button("🔄 Recharger l'application", type="primary"):
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erreur lors de l'upload : {e}")
        
        st.markdown("---")
        st.markdown("#### 📋 Features attendues par le modèle")
        
        features_expected = {
            "Temporelles": [
                "jour_semaine (str: Lundi-Dimanche)",
                "jour_mois (int: 1-31)",
                "semaine_annee (int: 1-53)",
                "mois (int: 1-12)",
                "annee (int)",
                "saison (str: Hiver/Printemps/Été/Automne)"
            ],
            "Contextuelles": [
                "vacances_scolaires (bool: 0/1)",
                "temperature_moyenne (float)",
                "temperature_min (float)",
                "temperature_max (float)",
                "meteo_principale (str)",
                "evenement_special (str)"
            ],
            "Hospitalières (optionnel)": [
                "lits_total (int)",
                "nb_medecins_disponibles (int)",
                "nb_infirmiers_disponibles (int)",
                "nb_aides_soignants_disponibles (int)"
            ]
        }
        
        for category, features in features_expected.items():
            with st.expander(f"📌 {category}"):
                for feature in features:
                    st.markdown(f"- `{feature}`")
        
        st.markdown("---")
        
        # Exemple de code pour le collègue
        with st.expander("💻 Exemple de code pour sauvegarder le modèle"):
            st.code("""
import joblib
from sklearn.ensemble import RandomForestRegressor

# Votre modèle entraîné
model = RandomForestRegressor()  # ou votre modèle
# model.fit(X_train, y_train)

# Sauvegarder
joblib.dump(model, 'model_prediction.joblib')

print("Modèle sauvegardé!")
            """, language='python')


def predict_with_stats(df, jour_semaine, saison, vacances, temperature, evenement):
    """
    Modèle statistique de base pour les prédictions
    Sera remplacé par le modèle ML quand disponible
    """
    
    # Filtrer les données similaires
    mask = (df['jour_semaine'] == jour_semaine) & (df['saison'] == saison)
    similar_days = df[mask]
    
    if len(similar_days) == 0:
        similar_days = df[df['saison'] == saison]
    
    if len(similar_days) == 0:
        similar_days = df
    
    # Baseline
    base_admissions = similar_days['nombre_admissions'].mean()
    base_urgences = similar_days['nombre_passages_urgences'].mean()
    base_occupation = similar_days['taux_occupation_lits'].mean()
    
    # Ajustements
    
    # Vacances
    if vacances:
        base_admissions *= 0.85
        base_urgences *= 0.90
    
    # Température
    if temperature > 30:  # Canicule
        base_admissions *= 1.25
        base_urgences *= 1.35
        base_occupation *= 1.15
    elif temperature < 0:  # Grand froid
        base_admissions *= 1.15
        base_urgences *= 1.20
        base_occupation *= 1.10
    
    # Événements
    if evenement != 'Aucun':
        if 'Épidémie' in evenement or 'Covid' in evenement:
            base_admissions *= 1.40
            base_urgences *= 1.60
            base_occupation *= 1.30
        elif 'Canicule' in evenement:
            base_admissions *= 1.30
            base_urgences *= 1.40
        elif 'froid' in evenement:
            base_admissions *= 1.20
            base_urgences *= 1.25
        elif 'pollution' in evenement:
            base_urgences *= 1.15
    
    # Ajouter variabilité réaliste
    base_admissions *= np.random.normal(1.0, 0.05)
    base_urgences *= np.random.normal(1.0, 0.05)
    base_occupation = min(1.0, base_occupation * np.random.normal(1.0, 0.03))
    
    return base_admissions, base_urgences, base_occupation


def prepare_features_for_model(pred_date, day_of_week, saison, vacances, temperature, meteo, evenement):
    """
    Prépare les features pour le modèle ML
    À adapter selon le format attendu par le modèle du collègue
    """
    
    # Exemple de préparation - à personnaliser
    features = {
        'jour_semaine': day_of_week,
        'jour_mois': pred_date.day,
        'semaine_annee': pred_date.isocalendar()[1],
        'mois': pred_date.month,
        'annee': pred_date.year,
        'saison': saison,
        'vacances_scolaires': int(vacances),
        'temperature_moyenne': temperature,
        'meteo_principale': meteo,
        'evenement_special': evenement
    }
    
    # Convertir en format array si nécessaire
    # return np.array([...])
    
    return features
