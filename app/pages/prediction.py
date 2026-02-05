"""
Page de prédiction avec modèle ML
"""

import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

from pages.ui_helpers import metric_with_info, render_title

try:
    from smartcare_model import (
        prepare_prediction_row,
        apply_overrides,
        predict_from_features,
        find_similar_days,
        compute_synthetic_lags,
        calculate_historical_trend,
        load_artifacts,
        build_prophet_future_frame,
        load_prophet_artifacts,
        forecast_prophet,
        evaluate_knn_quality,
    )
except Exception:
    prepare_prediction_row = None
    apply_overrides = None
    predict_from_features = None
    find_similar_days = None
    compute_synthetic_lags = None
    calculate_historical_trend = None
    load_artifacts = None
    build_prophet_future_frame = None
    load_prophet_artifacts = None
    forecast_prophet = None
    evaluate_knn_quality = None


def _load_metrics_json():
    """Charge les métriques du modèle depuis ML/artifacts/metrics.json."""
    try:
        base = Path(__file__).resolve().parent.parent.parent
        for folder in ("ml", "ML"):
            path = base / folder / "artifacts" / "metrics.json"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
    except Exception:
        pass
    return None


def show(df, model, model_available):
    """Affiche la page de prédiction"""

    pipeline_ready = (
        model_available
        and isinstance(model, dict)
        and "feature_cols" in model
        and "feature_df" in model
        and "model" in model
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

    model_options = ["Gradient Boosting", "Random Forest", "Prophet"]
    model_choice = st.selectbox(
        "Modèle de prédiction",
        model_options,
        index=0,
        key="prediction_model_choice",
        help="Choisissez le modèle utilisé pour la prédiction.",
    )
    model_key_map = {
        "Gradient Boosting": "gradient_boosting",
        "Random Forest": "random_forest",
        "Prophet": "prophet",
    }
    selected_model_key = model_key_map[model_choice]

    # Métriques du modèle et limites (MAE / MAPE + disclaimer)
    metrics_data = _load_metrics_json()
    metrics_key = "prophet" if selected_model_key == "prophet" else selected_model_key
    if metrics_data and metrics_key in metrics_data:
        with st.expander("📊 Performance du modèle et limites", expanded=False):
            m = metrics_data[metrics_key]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric_with_info(
                    "MAE (test)",
                    "Erreur absolue moyenne sur l'ensemble de test.",
                    f"{m.get('mae', 0):.1f}",
                )
            with col2:
                metric_with_info(
                    "RMSE (test)",
                    "Erreur quadratique moyenne (sensibilité aux grosses erreurs).",
                    f"{m.get('rmse', 0):.1f}",
                )
            with col3:
                metric_with_info(
                    "MAPE (test)",
                    "Erreur moyenne en pourcentage (sur l'ensemble de test).",
                    f"{m.get('mape', 0):.1f} %",
                )
            with col4:
                metric_with_info(
                    "SMAPE (test)",
                    "Erreur symétrique en pourcentage (pénalise moins les extrêmes).",
                    f"{m.get('smape', 0):.1f} %",
                )
            st.caption(
                "Modèle entraîné sur 2022–2026. Pour les dates hors période, la prédiction s'appuie sur la "
                "dernière période connue + contexte météo/événement."
            )
    
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
        render_title(
            "Prédiction pour une journée spécifique",
            "Prédiction d'une date donnée avec contexte météo/événement.",
            heading="###",
        )
        
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
                    [
                        'Aucun',
                        'Épidémie grippe',
                        'Épidémie gastro',
                        'Covid-19',
                        'Canicule',
                        'Grand froid',
                        'Pic pollution',
                        'Accident majeur',
                        'Grève du personnel',
                        'Tension hivernale',
                        'Plan blanc',
                        'Triple épidémie hivernale',
                        'Coupe du monde rugby 2023',
                        'JO Paris 2024',
                        'Tension été 2025'
                    ]
                )
        
        st.markdown("---")
        
        # Facteur de tendance temporelle (pour dates hors historique)
        if pipeline_ready and calculate_historical_trend is not None:
            st.markdown("### 🔮 Ajustement Tendance Temporelle")
            
            # Calculer la tendance historique (jusqu'à la dernière année disponible)
            max_year = int(model["feature_df"]["annee"].max())
            trend_data = calculate_historical_trend(
                model["feature_df"],
                end_year=max_year,
                target_year=max_year,
            )
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.info(f"📊 **Tendance historique détectée** : {trend_data['facteur_2026_pct']:+.1f}%")
                st.caption(
                    f"Basée sur l'évolution 2022 ({trend_data['adm_moyenne_start']:.0f} adm/j) → "
                    f"{trend_data.get('end_year', max_year)} ({trend_data['adm_moyenne_end']:.0f} adm/j)"
                )
            
            with col2:
                utiliser_auto = st.checkbox("Utiliser tendance auto", value=True, key="use_auto_trend")
            
            if not utiliser_auto:
                facteur_tendance = st.slider(
                    "Facteur personnalisé (%)",
                    min_value=-30.0,
                    max_value=50.0,
                    value=trend_data['facteur_2026_pct'],
                    step=1.0,
                    help="Ajustez selon vos anticipations : évolution démographique, capacité, etc.",
                    key="custom_trend"
                )
            else:
                facteur_tendance = trend_data['facteur_2026_pct']
            
            # Détail du calcul (expander optionnel)
            with st.expander("📖 Comment est calculée la tendance ?"):
                st.write(f"- **Admissions moyennes 2022** : {trend_data['adm_moyenne_start']:.0f} par jour")
                st.write(f"- **Admissions moyennes {trend_data.get('end_year', max_year)}** : {trend_data['adm_moyenne_end']:.0f} par jour")
                st.write(f"- **Croissance annuelle** : {trend_data['tendance_annuelle_pct']:.2f}%")
                st.write(
                    f"- **Extrapolation vers {trend_data.get('target_year', max_year)}** : "
                    f"{trend_data['facteur_2026_pct']:+.1f}%"
                )
                st.caption("La tendance est appliquée après la prédiction du modèle ML pour tenir compte de l'évolution temporelle.")
        else:
            facteur_tendance = 0.0
        
        st.markdown("---")
        
        if st.button("🚀 Calculer la Prédiction", type="primary", use_container_width=True):
            
            with st.spinner("Calcul en cours..."):
                if (
                    selected_model_key == "prophet"
                    and build_prophet_future_frame is not None
                    and load_prophet_artifacts is not None
                    and forecast_prophet is not None
                ):
                    st.info("🤖 Utilisation du modèle Prophet")
                    try:
                        prophet_model, prophet_regressors = load_prophet_artifacts()
                        future_df = build_prophet_future_frame([pred_date], df, prophet_regressors)
                        future_df = future_df.copy()

                        if "temperature_moyenne" in prophet_regressors:
                            future_df["temperature_moyenne"] = temperature
                        if "temperature_min" in prophet_regressors:
                            future_df["temperature_min"] = temperature
                        if "temperature_max" in prophet_regressors:
                            future_df["temperature_max"] = temperature
                        if "vacances_scolaires" in prophet_regressors:
                            future_df["vacances_scolaires"] = 1 if vacances else 0

                        meteo_cols = [c for c in prophet_regressors if c.startswith("meteo_")]
                        if meteo_cols:
                            for col in meteo_cols:
                                future_df[col] = 0
                            if meteo != "Aucun":
                                meteo_col = f"meteo_{meteo}"
                                if meteo_col in future_df.columns:
                                    future_df[meteo_col] = 1

                        event_cols = [c for c in prophet_regressors if c.startswith("event_")]
                        if event_cols:
                            for col in event_cols:
                                future_df[col] = 0
                            if evenement != "Aucun":
                                event_col = f"event_{evenement}"
                                if event_col in future_df.columns:
                                    future_df[event_col] = 1
                            else:
                                event_default = "event_Aucun"
                                if event_default in future_df.columns:
                                    future_df[event_default] = 1

                        forecast = forecast_prophet(prophet_model, future_df)
                        pred_admissions = max(0.0, float(forecast["yhat"].iloc[0]))
                        urg_ratio = df["nombre_passages_urgences"].mean() / df["nombre_admissions"].mean()
                        pred_urgences = pred_admissions * urg_ratio
                        pred_occupation = df["taux_occupation_lits"].mean()
                    except Exception as e:
                        st.error(f"Erreur avec Prophet : {e}")
                        st.warning("Passage au modèle ML/statistique")
                        pred_admissions, pred_urgences, pred_occupation = predict_with_stats(
                            df, day_of_week_fr.get(day_of_week, day_of_week),
                            saison, vacances, temperature, evenement
                        )

                elif pipeline_ready:
                    try:
                        selected_model = model["model"]
                        selected_feature_cols = model["feature_cols"]
                        if load_artifacts is not None and selected_model_key != "gradient_boosting":
                            try:
                                selected_model, selected_feature_cols = load_artifacts(
                                    model_name=selected_model_key
                                )
                            except Exception:
                                pass
                        meteo_override = None if meteo == "Aucun" else meteo
                        event_override = None if evenement == "Aucun" else evenement
                        
                        # Utiliser k-NN pour une journée spécifique (si disponible)
                        use_knn = find_similar_days is not None
                        
                        if use_knn:
                            st.info("🔍 Mode k-NN : Recherche de jours similaires dans l'historique")
                            
                            # Préparer les features contextuelles
                            target_features = {
                                "temperature": temperature,
                                "meteo": meteo_override if meteo_override else "Soleil",
                                "evenement": event_override if event_override else "Aucun",
                                "vacances": 1 if vacances else 0,
                            }
                            
                            # Trouver les jours similaires
                            similar_days = find_similar_days(
                                model["feature_df"],
                                pd.to_datetime(pred_date),
                                target_features,
                                k=10
                            )
                            
                            # Évaluer et afficher les métriques k-NN
                            if evaluate_knn_quality is not None:
                                knn_metrics = evaluate_knn_quality(similar_days)
                                
                                st.success(f"✓ {knn_metrics['n_jours']} jours similaires trouvés")
                                
                                # Afficher les métriques dans un expander
                                with st.expander("📊 Métriques de qualité k-NN", expanded=True):
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        metric_with_info(
                                            "Distance moyenne",
                                            "Distance moyenne entre le jour cible et les jours similaires.",
                                            f"{knn_metrics['distance_moyenne']:.2f}",
                                        )
                                        st.caption(f"Min: {knn_metrics['distance_min']:.2f} | Max: {knn_metrics['distance_max']:.2f}")
                                    
                                    with col2:
                                        if "adm_moyenne" in knn_metrics:
                                            metric_with_info(
                                                "Admissions moyennes",
                                                "Moyenne des admissions des jours similaires.",
                                                f"{knn_metrics['adm_moyenne']:.0f}",
                                            )
                                            st.caption(f"Écart-type: {knn_metrics['adm_std']:.1f}")
                                    
                                    with col3:
                                        if "adm_min" in knn_metrics and "adm_max" in knn_metrics:
                                            metric_with_info(
                                                "Fourchette admissions",
                                                "Min et max des admissions sur les jours similaires.",
                                                f"{knn_metrics['adm_min']:.0f} - {knn_metrics['adm_max']:.0f}",
                                            )
                                    
                                    # Top 3 jours les plus similaires
                                    if "top_3_dates" in knn_metrics:
                                        st.markdown("**🎯 Top 3 jours les plus similaires :**")
                                        for i, date in enumerate(knn_metrics["top_3_dates"][:3], 1):
                                            adm = ""
                                            if "top_3_admissions" in knn_metrics and i-1 < len(knn_metrics["top_3_admissions"]):
                                                adm = f" → {knn_metrics['top_3_admissions'][i-1]:.0f} admissions"
                                            st.caption(f"{i}. {date.strftime('%d/%m/%Y')}{adm}")
                            else:
                                st.success(f"✓ {len(similar_days)} jours similaires trouvés (distance moyenne : {similar_days['similarity_distance'].mean():.2f})")
                            
                            # Calculer les lags synthétiques
                            synthetic_lags = compute_synthetic_lags(similar_days)
                            
                            # Créer une ligne de prédiction avec lags synthétiques
                            row = prepare_prediction_row(
                                model["feature_df"],
                                model["feature_cols"],
                                target_date=None
                            )
                            
                            # Remplacer les lags par les valeurs synthétiques
                            for lag_col, lag_val in synthetic_lags.items():
                                if lag_col in row.columns:
                                    row[lag_col] = lag_val
                        else:
                            st.info("🤖 Mode ML classique : k-NN indisponible")
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
                                st.warning("⚠️ Date exacte non trouvée, utilisation de la dernière date disponible")
                        
                        # Appliquer les overrides météo/événement
                        row = apply_overrides(
                            row,
                            model["feature_cols"],
                            meteo=meteo_override,
                            event=event_override
                        )
                        
                        # Prédiction
                        result = predict_from_features(
                            row,
                            model["model"],
                            model["feature_cols"],
                            safety_margin=0.10
                        )

                        # Appliquer le facteur de tendance
                        pred_admissions_brut = result["prediction"]
                        pred_admissions = pred_admissions_brut * (1 + facteur_tendance / 100)
                        
                        urg_ratio = df["nombre_passages_urgences"].mean() / df["nombre_admissions"].mean()
                        pred_urgences = pred_admissions * urg_ratio
                        pred_occupation = df["taux_occupation_lits"].mean()
                        
                        # Afficher info sur le facteur appliqué
                        if abs(facteur_tendance) > 0.1:
                            st.info(f"📈 Facteur de tendance appliqué : {facteur_tendance:+.1f}% → Prédiction ajustée de {pred_admissions_brut:.0f} à {pred_admissions:.0f} admissions")

                    except Exception as e:
                        st.error(f"Erreur avec le modèle ML : {e}")
                        st.warning("Passage au modèle statistique de secours")
                        pred_admissions, pred_urgences, pred_occupation = predict_with_stats(
                            df, day_of_week_fr.get(day_of_week, day_of_week),
                            saison, vacances, temperature, evenement
                        )
                elif model_available and model is not None:
                    # Utiliser un modèle ML simple si fourni (cas où pipeline_ready=False)
                    st.info("🤖 Utilisation du modèle ML simple")
                    try:
                        # Vérifier si c'est un dict (format SmartCare) ou un modèle direct
                        actual_model = model["model"] if isinstance(model, dict) and "model" in model else model
                        
                        features = prepare_features_for_model(
                            pred_date, day_of_week, saison, vacances,
                            temperature, meteo, evenement
                        )
                        predictions = actual_model.predict([features])
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
                lits_total = int(df['lits_total'].iloc[-1]) if 'lits_total' in df.columns else 1650
                pred_lits_occupes = int(lits_total * pred_occupation)
                ratio_patient_staff = 3.5
                staff_needed = int(pred_lits_occupes / ratio_patient_staff)
                
                # Stocker les résultats pour la page Recommandations (session + fichier)
                pred_for_rec = {
                    'mode': 'single',
                    'pred_date': pred_date,
                    'day_of_week_fr': day_of_week_fr.get(day_of_week, day_of_week),
                    'pred_admissions': pred_admissions,
                    'pred_urgences': pred_urgences,
                    'pred_occupation': pred_occupation,
                    'pred_lits_occupes': pred_lits_occupes,
                    'staff_needed': staff_needed,
                    'lits_total': lits_total,
                }
                st.session_state.prediction_for_recommendations = pred_for_rec
                try:
                    from prediction_store import save_prediction_for_recommendations
                    ok = save_prediction_for_recommendations(pred_for_rec)
                    if ok:
                        st.toast("Prédiction sauvegardée pour la page Recommandations", icon="💾")
                except Exception:
                    pass
                
                # Affichage des résultats
                st.success("✅ Prédiction calculée")
                
                st.markdown("---")
                render_title(
                    "📊 Résultats de la prédiction",
                    "Résultat du modèle avec comparaison à la baseline historique.",
                    heading="###",
                )
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # Comparaison avec baseline
                    baseline_adm = df[df['jour_semaine'] == day_of_week_fr.get(day_of_week, day_of_week)]['nombre_admissions'].mean()
                    delta_adm = pred_admissions - baseline_adm
                    
                    metric_with_info(
                        "Admissions",
                        "Nombre d'admissions prédites pour la date choisie.",
                        f"{pred_admissions:.0f}",
                        delta=f"{delta_adm:+.0f}",
                        delta_color="inverse",
                    )
                
                with col2:
                    baseline_urg = df[df['jour_semaine'] == day_of_week_fr.get(day_of_week, day_of_week)]['nombre_passages_urgences'].mean()
                    delta_urg = pred_urgences - baseline_urg
                    
                    metric_with_info(
                        "Passages urgences",
                        "Estimation basée sur le ratio historique urgences/admissions.",
                        f"{pred_urgences:.0f}",
                        delta=f"{delta_urg:+.0f}",
                        delta_color="inverse",
                    )
                
                with col3:
                    metric_with_info(
                        "Hospitalisations",
                        "Estimation via un ratio admissions → hospitalisations.",
                        f"{pred_hospitalisations:.0f}",
                    )
                
                with col4:
                    color = "normal" if pred_occupation < 0.85 else "inverse"
                    metric_with_info(
                        "Taux occupation",
                        "Taux d'occupation prévu comparé au seuil critique (85%).",
                        f"{pred_occupation*100:.1f}%",
                        delta="Critique" if pred_occupation > 0.85 else "Normal",
                        delta_color=color,
                    )
                
                # Détails supplémentaires
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    render_title(
                        "🛏️ Besoins en lits",
                        "Projection basée sur le taux d'occupation estimé.",
                        heading="####",
                    )
                    metric_with_info(
                        "Lits occupés prévus",
                        "Lits occupés estimés = lits totaux × taux d'occupation.",
                        f"{pred_lits_occupes} / {lits_total}",
                    )
                    metric_with_info(
                        "Lits disponibles",
                        "Lits totaux - lits occupés prévus.",
                        f"{lits_total - pred_lits_occupes}",
                    )
                    
                    if pred_occupation > 0.85:
                        st.error(f"⚠️ Risque de saturation ({pred_occupation*100:.1f}%)")
                    elif pred_occupation > 0.75:
                        st.warning(f"⚠️ Surveillance nécessaire ({pred_occupation*100:.1f}%)")
                    else:
                        st.success(f"✅ Capacité suffisante ({pred_occupation*100:.1f}%)")
                
                with col2:
                    render_title(
                        "👥 Besoins en personnel",
                        "Estimation basée sur un ratio patients/personnel.",
                        heading="####",
                    )
                    
                    # Estimation besoins personnel
                    ratio_patient_staff = 3.5
                    staff_needed = int(pred_lits_occupes / ratio_patient_staff)
                    
                    baseline_staff = int((
                        df['nb_medecins_disponibles'].mean() +
                        df['nb_infirmiers_disponibles'].mean() +
                        df['nb_aides_soignants_disponibles'].mean()
                    ))
                    
                    metric_with_info(
                        "Personnel nécessaire",
                        "Lits occupés / ratio patients-personnel.",
                        f"{staff_needed}",
                    )
                    metric_with_info(
                        "Personnel disponible moyen",
                        "Moyenne historique des effectifs disponibles.",
                        f"{baseline_staff}",
                    )
                    
                    if staff_needed > baseline_staff * 1.1:
                        st.error("⚠️ Renfort nécessaire")
                    elif staff_needed > baseline_staff:
                        st.warning("⚠️ Mobilisation complète")
                    else:
                        st.success("✅ Effectifs suffisants")
                
                st.info("💡 Allez sur la page **Recommandations** pour comparer ces prédictions à vos ressources actuelles (médecins, lits) et obtenir des recommandations personnalisées.")
    
    # ========================================
    # TAB 2: Prédiction Multi-jours
    # ========================================
    with tab2:
        render_title(
            "Prédiction sur plusieurs jours",
            "Projection journalière sur une période choisie.",
            heading="###",
        )
        
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
        
        if st.button("🚀 Générer les Prédictions", type="primary", width="stretch"):
            with st.spinner(f"Calcul des prédictions pour {n_days} jours..."):
                
                predictions = []
                dates = pd.date_range(start=start_date, periods=n_days, freq='D')
                mean_admissions = max(df["nombre_admissions"].mean(), 1)
                urg_ratio = df["nombre_passages_urgences"].mean() / mean_admissions
                mean_occupation = df["taux_occupation_lits"].mean() * 100
                

                prophet_ready = (
                    build_prophet_future_frame is not None
                    and load_prophet_artifacts is not None
                    and forecast_prophet is not None
                )

                if selected_model_key == "prophet" and prophet_ready:
                    try:
                        prophet_model, prophet_regressors = load_prophet_artifacts()
                        future_df = build_prophet_future_frame(dates, df, prophet_regressors)
                        forecast = forecast_prophet(prophet_model, future_df)
                        for row in forecast.itertuples(index=False):
                            pred_adm = max(0.0, float(row.yhat))
                            pred_urg = pred_adm * urg_ratio
                            pred_occ = np.clip(mean_occupation * (pred_adm / mean_admissions), 50, 98)
                            predictions.append({
                                "date": row.ds,
                                "admissions": pred_adm,
                                "urgences": pred_urg,
                                "occupation": pred_occ,
                            })
                        st.info("✅ Prophet utilisé (multi-jours).")
                    except Exception:
                        pass
                
                if (
                    pipeline_ready
                    and not predictions
                    and selected_model_key in ("gradient_boosting", "random_forest")
                ):
                    # Utiliser le modèle ML : dernière ligne de features + overrides météo selon le mois (variation)
                    try:
                        selected_model = model["model"]
                        selected_feature_cols = model["feature_cols"]
                        if (
                            load_artifacts is not None
                            and selected_model_key != "gradient_boosting"
                        ):
                            try:
                                selected_model, selected_feature_cols = load_artifacts(
                                    model_name=selected_model_key
                                )
                            except Exception as e:
                                st.warning(f"Modèle {selected_model_key} indisponible, fallback gradient_boosting: {e}")

                        base_row = prepare_prediction_row(
                            model["feature_df"],
                            selected_feature_cols,
                            target_date=None,
                        )

                        last_date = model["feature_df"]["date"].max()
                        temp_mean_by_month = df.groupby(df["date"].dt.month)["temperature_moyenne"].mean().to_dict()
                        temp_min_by_month = df.groupby(df["date"].dt.month)["temperature_min"].mean().to_dict()
                        temp_max_by_month = df.groupby(df["date"].dt.month)["temperature_max"].mean().to_dict()
                        overall_temp = df["temperature_moyenne"].mean()

                        jour_map = {
                            "Lundi": 1.10,
                            "Mardi": 1.05,
                            "Mercredi": 1.00,
                            "Jeudi": 1.00,
                            "Vendredi": 0.95,
                            "Samedi": 0.85,
                            "Dimanche": 0.80,
                        }
                        saison_map = {
                            "Hiver": 1.15,
                            "Printemps": 1.00,
                            "Été": 0.90,
                            "Ete": 0.90,
                            "Automne": 1.05,
                        }

                        for i, date in enumerate(dates):
                            month = date.month
                            meteo_override = (
                                "Froid" if month in [12, 1, 2] else
                                "Canicule" if month in [6, 7, 8] else
                                None
                            )

                            target_date = pd.to_datetime(date)
                            if target_date <= last_date:
                                row = prepare_prediction_row(
                                    model["feature_df"],
                                    selected_feature_cols,
                                    target_date=target_date,
                                )
                            else:
                                vacances = 1 if month in [7, 8] else 0
                                target_features = {
                                    "temperature": temp_mean_by_month.get(month, overall_temp),
                                    "meteo": meteo_override if meteo_override else "Aucun",
                                    "evenement": "Aucun",
                                    "vacances": vacances,
                                }

                                if find_similar_days is not None:
                                    similar_days = find_similar_days(
                                        model["feature_df"],
                                        target_date,
                                        target_features,
                                        k=10,
                                    )
                                    row = base_row.copy()
                                    if compute_synthetic_lags is not None:
                                        synthetic_lags = compute_synthetic_lags(similar_days)
                                        for lag_col, lag_val in synthetic_lags.items():
                                            if lag_col in row.columns:
                                                row[lag_col] = lag_val
                                else:
                                    row = base_row.copy()

                                jour_fr = {
                                    0: "Lundi",
                                    1: "Mardi",
                                    2: "Mercredi",
                                    3: "Jeudi",
                                    4: "Vendredi",
                                    5: "Samedi",
                                    6: "Dimanche",
                                }[target_date.weekday()]
                                if month in [12, 1, 2]:
                                    saison = "Hiver"
                                elif month in [3, 4, 5]:
                                    saison = "Printemps"
                                elif month in [6, 7, 8]:
                                    saison = "Été"
                                else:
                                    saison = "Automne"

                                if "date" in row.columns:
                                    row["date"] = target_date
                                if "temperature_moyenne" in row.columns:
                                    row["temperature_moyenne"] = temp_mean_by_month.get(month, overall_temp)
                                if "temperature_min" in row.columns:
                                    row["temperature_min"] = temp_min_by_month.get(month, overall_temp - 5)
                                if "temperature_max" in row.columns:
                                    row["temperature_max"] = temp_max_by_month.get(month, overall_temp + 5)
                                if "is_weekend" in row.columns:
                                    row["is_weekend"] = 1 if target_date.weekday() >= 5 else 0
                                if "is_holiday" in row.columns:
                                    row["is_holiday"] = vacances
                                if "veille_holiday" in row.columns:
                                    row["veille_holiday"] = 0
                                if "lendemain_holiday" in row.columns:
                                    row["lendemain_holiday"] = 0
                                if "mult_jour_semaine" in row.columns:
                                    row["mult_jour_semaine"] = jour_map.get(jour_fr, 1.0)
                                if "mult_saison" in row.columns:
                                    row["mult_saison"] = saison_map.get(saison, 1.0)
                                if "mult_vacances" in row.columns:
                                    row["mult_vacances"] = 0.90 if vacances else 1.00

                            row = apply_overrides(
                                row,
                                selected_feature_cols,
                                meteo=meteo_override,
                                event=None,
                            )

                            result = predict_from_features(
                                row,
                                selected_model,
                                selected_feature_cols,
                                safety_margin=0.10,
                            )
                            pred_adm = result["prediction"]
                            pred_urg = pred_adm * urg_ratio
                            pred_occ = np.clip(mean_occupation * (pred_adm / mean_admissions), 50, 98)
                            predictions.append({
                                "date": date,
                                "admissions": pred_adm,
                                "urgences": pred_urg,
                                "occupation": pred_occ,
                            })
                        st.info("🤖 Prédictions ML : features datées quand disponibles, sinon k-NN pour synthétiser les lags.")
                    except Exception as e:
                        st.warning(f"Modèle ML indisponible pour cette plage : {e}. Passage au modèle statistique.")
                        predictions = []
                
                if not predictions:
                    # Fallback : modèle statistique
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
                        pred_adm, pred_urg, pred_occ = predict_with_stats(
                            df, day_fr, saison, False, 15.0, 'Aucun'
                        )
                        pred_occ = np.clip(mean_occupation * (pred_adm / mean_admissions), 50, 98)
                        predictions.append({
                            'date': date,
                            'admissions': pred_adm,
                            'urgences': pred_urg,
                            'occupation': pred_occ
                        })
                
                pred_df = pd.DataFrame(predictions)
                
                # Stocker les résultats pour la page Recommandations
                lits_total = int(df['lits_total'].iloc[-1]) if 'lits_total' in df.columns else 1650
                ratio_patient_staff = 3.5
                pred_df['lits_occupes'] = (pred_df['occupation'] / 100 * lits_total).astype(int)
                pred_df['staff_needed'] = (pred_df['lits_occupes'] / ratio_patient_staff).astype(int)
                peak_lits = pred_df['lits_occupes'].max()
                peak_staff = pred_df['staff_needed'].max()
                
                pred_for_rec = {
                    'mode': 'multi',
                    'start_date': start_date,
                    'n_days': n_days,
                    'pred_df': pred_df,
                    'lits_total': lits_total,
                    'peak_lits_occupes': int(peak_lits),
                    'peak_staff_needed': int(peak_staff),
                    'mean_lits_occupes': int(pred_df['lits_occupes'].mean()),
                    'mean_staff_needed': int(pred_df['staff_needed'].mean()),
                }
                st.session_state.prediction_for_recommendations = pred_for_rec
                try:
                    from prediction_store import save_prediction_for_recommendations
                    ok = save_prediction_for_recommendations(pred_for_rec)
                    if ok:
                        st.toast("Prédiction sauvegardée pour la page Recommandations", icon="💾")
                except Exception:
                    pass
                
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
                    
                    st.plotly_chart(fig, width="stretch")
                
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
                    
                    st.plotly_chart(fig, width="stretch")
                
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
                
                st.info("💡 Allez sur la page **Recommandations** pour comparer ces prédictions à vos ressources actuelles et obtenir des recommandations personnalisées.")
    
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
        elif 'Accident' in evenement or 'Afflux' in evenement:
            base_admissions *= 1.55
            base_urgences *= 1.90
            base_occupation *= 1.20
        elif 'Grève' in evenement or 'Greve' in evenement:
            base_admissions *= 0.90
            base_urgences *= 1.10
            base_occupation *= 1.05
        elif 'JO' in evenement or 'Coupe du monde' in evenement:
            base_admissions *= 1.15
            base_urgences *= 1.25
            base_occupation *= 1.10
        elif 'Tension' in evenement or 'Plan blanc' in evenement or 'Triple' in evenement:
            base_admissions *= 1.25
            base_urgences *= 1.35
            base_occupation *= 1.20
    
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
