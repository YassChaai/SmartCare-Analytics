"""
Page de recommandations automatiques - basée uniquement sur les résultats du modèle de prédiction.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta

from pages.ui_helpers import metric_with_info, render_title


def _get_reference_single_day(df, pred_date, day_of_week_fr):
    """Récupère la donnée du même jour de la semaine précédente (ex: Lundi 12 → Lundi 5)."""
    pred_date = pd.to_datetime(pred_date)
    ref_date_target = pred_date - timedelta(days=7)
    ref_candidates = df[
        (df['jour_semaine'] == day_of_week_fr) &
        (df['date'] <= ref_date_target + timedelta(days=3)) &
        (df['date'] >= ref_date_target - timedelta(days=3))
    ]
    if ref_candidates.empty:
        ref_candidates = df[df['jour_semaine'] == day_of_week_fr].copy()
        ref_candidates = ref_candidates[ref_candidates['date'] < pred_date].tail(1)
    if ref_candidates.empty:
        ref_candidates = df[df['date'] < pred_date].tail(7)
    return ref_candidates.iloc[-1:] if not ref_candidates.empty else pd.DataFrame()


def _get_reference_multi_day(df, start_date, n_days):
    """Récupère les X jours qui précèdent la date de début de prédiction."""
    start_date = pd.to_datetime(start_date)
    ref_end = start_date - timedelta(days=1)
    ref_start = ref_end - timedelta(days=n_days - 1)
    ref_df = df[(df['date'] >= ref_start) & (df['date'] <= ref_end)]
    return ref_df


def _compute_staff_proportions(ref_row_or_df):
    """Calcule les proportions médecins/infirmiers/aides à partir des données de référence."""
    if isinstance(ref_row_or_df, pd.Series):
        total = (ref_row_or_df['nb_medecins_disponibles'] +
                 ref_row_or_df['nb_infirmiers_disponibles'] +
                 ref_row_or_df['nb_aides_soignants_disponibles'])
        if total <= 0:
            return 0.15, 0.50, 0.35
        return (
            ref_row_or_df['nb_medecins_disponibles'] / total,
            ref_row_or_df['nb_infirmiers_disponibles'] / total,
            ref_row_or_df['nb_aides_soignants_disponibles'] / total,
        )
    ref_df = ref_row_or_df
    total_med = ref_df['nb_medecins_disponibles'].sum()
    total_inf = ref_df['nb_infirmiers_disponibles'].sum()
    total_aides = ref_df['nb_aides_soignants_disponibles'].sum()
    total = total_med + total_inf + total_aides
    if total <= 0:
        return 0.15, 0.50, 0.35
    return total_med / total, total_inf / total, total_aides / total


def _render_kpi_with_ref(label, tooltip, valeur_atteindre, valeur_reference, delta_ok_if_positive=False):
    """Affiche un KPI avec valeur à atteindre et valeur de référence."""
    delta = valeur_atteindre - valeur_reference
    delta_str = f"{delta:+d}" if delta != 0 else "="
    metric_with_info(
        label,
        tooltip,
        f"{valeur_atteindre}",
        delta=f"Réf. {valeur_reference} ({delta_str})",
    )


def _render_single_day(df, pred_data):
    """Affiche les KPIs pour une prédiction mono-jour."""
    pred_date = pred_data['pred_date']
    day_fr = pred_data['day_of_week_fr']
    pred_lits = pred_data['pred_lits_occupes']
    pred_staff = pred_data['staff_needed']

    ref_df = _get_reference_single_day(df, pred_date, day_fr)
    if ref_df.empty:
        st.warning("Données de référence indisponibles pour la comparaison.")
        return

    ref = ref_df.iloc[0]
    ref_medecins = int(ref['nb_medecins_disponibles'])
    ref_infirmiers = int(ref['nb_infirmiers_disponibles'])
    ref_aides = int(ref['nb_aides_soignants_disponibles'])
    ref_lits_occupes = int(ref['lits_occupes'])
    ref_date_str = ref['date'].strftime('%d/%m/%Y')

    p_med, p_inf, p_aides = _compute_staff_proportions(ref)
    pred_medecins = max(0, int(pred_staff * p_med))
    pred_infirmiers = max(0, int(pred_staff * p_inf))
    pred_aides = max(0, int(pred_staff * p_aides))

    render_title(
        f"Prédiction mono-jour : {pd.to_datetime(pred_date).strftime('%d/%m/%Y')} ({day_fr})",
        "Comparaison prédiction vs référence du même jour de semaine.",
        heading="####",
    )
    st.caption(f"Données de référence : {day_fr} {ref_date_str}")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        _render_kpi_with_ref(
            "🛏️ Lits occupés",
            "Lits occupés prévus vs référence (même jour semaine précédente).",
            pred_lits,
            ref_lits_occupes,
        )
    with col2:
        _render_kpi_with_ref(
            "👨‍⚕️ Médecins",
            "Besoin estimé en médecins vs référence.",
            pred_medecins,
            ref_medecins,
        )
    with col3:
        _render_kpi_with_ref(
            "👩‍⚕️ Infirmiers",
            "Besoin estimé en infirmiers vs référence.",
            pred_infirmiers,
            ref_infirmiers,
        )
    with col4:
        _render_kpi_with_ref(
            "🩺 Aides-soignants",
            "Besoin estimé en aides-soignants vs référence.",
            pred_aides,
            ref_aides,
        )


def _render_multi_day(df, pred_data):
    """Affiche les KPIs et graphiques pour une prédiction multi-jours."""
    start_date = pred_data['start_date']
    n_days = pred_data['n_days']
    pred_df = pred_data['pred_df']

    ref_df = _get_reference_multi_day(df, start_date, n_days)
    if ref_df.empty:
        st.warning("Données de référence indisponibles pour la période précédente.")
        return

    ref_df = ref_df.sort_values('date').reset_index(drop=True)
    pred_df = pred_df.head(n_days).copy()
    pred_df = pred_df.reset_index(drop=True)

    # Réaligner si les tailles diffèrent (prendre le min)
    min_len = min(len(ref_df), len(pred_df))
    ref_df = ref_df.iloc[:min_len]
    pred_df = pred_df.iloc[:min_len]

    ref_date_str = f"{ref_df['date'].iloc[0].strftime('%d/%m/%Y')} → {ref_df['date'].iloc[-1].strftime('%d/%m/%Y')}"

    render_title(
        f"Prédiction multi-jours : {n_days} jours à partir du {pd.to_datetime(start_date).strftime('%d/%m/%Y')}",
        "Comparaison entre la période prédite et la période de référence précédente.",
        heading="####",
    )
    st.caption(f"Données de référence : {n_days} jours précédents ({ref_date_str})")
    st.markdown("---")

    # Calcul personnel référence par jour (proportions moyennes)
    p_med, p_inf, p_aides = _compute_staff_proportions(ref_df)
    ref_df = ref_df.copy()
    ref_df['staff_total'] = (
        ref_df['nb_medecins_disponibles'] +
        ref_df['nb_infirmiers_disponibles'] +
        ref_df['nb_aides_soignants_disponibles']
    )

    # KPIs agrégés (moyennes)
    pred_lits_mean = int(pred_df['lits_occupes'].mean())
    pred_staff_mean = int(pred_df['staff_needed'].mean())
    ref_lits_mean = int(ref_df['lits_occupes'].mean())
    ref_staff_mean = int(ref_df['staff_total'].mean())

    pred_med_mean = max(0, int(pred_staff_mean * p_med))
    pred_inf_mean = max(0, int(pred_staff_mean * p_inf))
    pred_aides_mean = max(0, int(pred_staff_mean * p_aides))
    ref_med_mean = int(ref_df['nb_medecins_disponibles'].mean())
    ref_inf_mean = int(ref_df['nb_infirmiers_disponibles'].mean())
    ref_aides_mean = int(ref_df['nb_aides_soignants_disponibles'].mean())

    render_title(
        "KPIs (moyennes sur la période)",
        "Moyennes sur la période prédite vs période de référence.",
        heading="#####",
    )
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        _render_kpi_with_ref(
            "🛏️ Lits occupés",
            "Moyenne des lits occupés sur la période.",
            pred_lits_mean,
            ref_lits_mean,
        )
    with col2:
        _render_kpi_with_ref(
            "👨‍⚕️ Médecins",
            "Moyenne des besoins en médecins sur la période.",
            pred_med_mean,
            ref_med_mean,
        )
    with col3:
        _render_kpi_with_ref(
            "👩‍⚕️ Infirmiers",
            "Moyenne des besoins en infirmiers sur la période.",
            pred_inf_mean,
            ref_inf_mean,
        )
    with col4:
        _render_kpi_with_ref(
            "🩺 Aides-soignants",
            "Moyenne des besoins en aides-soignants sur la période.",
            pred_aides_mean,
            ref_aides_mean,
        )

    st.markdown("---")
    render_title(
        "Évolution dans le temps : Prédiction vs Référence",
        "Comparaison jour par jour entre la prédiction et la référence.",
        heading="#####",
    )

    dates_pred = pred_df['date'].dt.strftime('%d/%m')
    dates_ref = ref_df['date'].dt.strftime('%d/%m')
    jours = [f"J{i+1}" for i in range(min_len)]

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=jours,
            y=pred_df['lits_occupes'],
            name='Prédiction',
            line=dict(color='#2E3FE8', width=2),
            mode='lines+markers'
        ))
        fig.add_trace(go.Scatter(
            x=jours,
            y=ref_df['lits_occupes'],
            name='Référence',
            line=dict(color='#7E7E7E', width=2, dash='dash'),
            mode='lines+markers'
        ))
        fig.update_layout(
            title="Lits occupés",
            xaxis_title="Jour",
            yaxis_title="Nombre",
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=jours,
            y=pred_df['staff_needed'],
            name='Prédiction',
            line=dict(color='#FF5700', width=2),
            mode='lines+markers'
        ))
        fig.add_trace(go.Scatter(
            x=jours,
            y=ref_df['staff_total'],
            name='Référence',
            line=dict(color='#7E7E7E', width=2, dash='dash'),
            mode='lines+markers'
        ))
        fig.update_layout(
            title="Personnel total",
            xaxis_title="Jour",
            yaxis_title="Nombre",
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    if 'admissions' in pred_df.columns:
        ref_has_adm = 'nombre_admissions' in ref_df.columns
        if ref_has_adm:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=jours,
                y=pred_df['admissions'],
                name='Prédiction',
                line=dict(color='#388E3C', width=2),
                mode='lines+markers'
            ))
            fig.add_trace(go.Scatter(
                x=jours,
                y=ref_df['nombre_admissions'],
                name='Référence',
                line=dict(color='#7E7E7E', width=2, dash='dash'),
                mode='lines+markers'
            ))
            fig.update_layout(
                title="Admissions",
                xaxis_title="Jour",
                yaxis_title="Nombre",
                height=300,
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            st.plotly_chart(fig, use_container_width=True)


def _load_prediction_data():
    """Charge les données de prédiction depuis session_state ou fichier JSON."""
    if 'prediction_for_recommendations' in st.session_state and st.session_state.prediction_for_recommendations:
        return st.session_state.prediction_for_recommendations
    try:
        from prediction_store import load_prediction_for_recommendations
        return load_prediction_for_recommendations()
    except Exception:
        return None


def show(df):
    """Affiche la page de recommandations (uniquement basée sur le modèle de prédiction)."""

    st.markdown('<p class="main-header">Recommandations Automatiques</p>', unsafe_allow_html=True)
    render_title(
        "💡 Comparaison Prédiction vs Données de référence",
        "Compare la prédiction aux données historiques de référence.",
        heading="###",
    )
    st.markdown("---")

    pred_data = _load_prediction_data()
    if not pred_data:
        st.info("""
        **💡 Effectuez une prédiction sur la page Prédiction** (prédiction simple ou multi-jours), 
        puis revenez sur cette page pour afficher les KPIs et graphiques comparant les valeurs prédites 
        aux données de référence.
        """)
        return
    mode = pred_data['mode']

    if mode == 'single':
        _render_single_day(df, pred_data)
    else:
        _render_multi_day(df, pred_data)
