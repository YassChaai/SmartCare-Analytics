#!/usr/bin/env python3
"""
Script de génération de données Smart Care pour 2022-2026
Respecte la documentation et les règles du projet Smart Care
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

class SmartCareDataGenerator:
    def __init__(self, base_path):
        """Initialise le générateur avec les fichiers de référence"""
        self.base_path = base_path
        self.parameters = None
        self.hospital_baseline = None
        self.event_rules = None
        self.school_holidays = None
        self.special_events = None
        self.staff_variation = None
        self.weather_ref = None
        self.luxembourg_weather = None

        # États pour la variabilité temporelle
        self._prev_admissions = None
        self._prev_urgences = None
        self._daily_shock_adm = 1.0
        self._daily_shock_urg = 1.0
        
        self.load_reference_data()

    def _get_param_float(self, name, default):
        """Récupère un paramètre numérique avec valeur par défaut."""
        value = self.get_parameter(name)
        if value is None:
            return default
        try:
            return self.normalize_number(value)
        except Exception:
            return default

    def _year_trend_factor(self, date, base_year=2022):
        """Applique une tendance annuelle douce (par défaut +2%/an)."""
        annual_trend = self._get_param_float('tendance_annuelle_admissions', 0.02)
        years_diff = date.year - base_year
        return (1 + annual_trend) ** max(0, years_diff)

    def _seasonality_factor(self, date):
        """Saisonnalité infra-annuelle (sinusoïde) + légère variation mensuelle."""
        amplitude = self._get_param_float('amplitude_saisonnalite', 0.08)
        day_of_year = date.timetuple().tm_yday
        seasonal = 1 + amplitude * np.sin(2 * np.pi * (day_of_year / 365.0))

        month_factors = {
            1: 1.05, 2: 1.06, 3: 1.02, 4: 0.98, 5: 0.97, 6: 0.98,
            7: 0.95, 8: 0.94, 9: 1.00, 10: 1.02, 11: 1.03, 12: 1.06
        }
        monthly = month_factors.get(date.month, 1.0)
        return seasonal * monthly

    def _temperature_factor(self, temperature_moyenne):
        """Impact météo sur admissions/urgences (extrêmes = hausse)."""
        if temperature_moyenne <= -2:
            return 1.12
        if temperature_moyenne <= 2:
            return 1.06
        if temperature_moyenne >= 32:
            return 1.15
        if temperature_moyenne >= 27:
            return 1.08
        return 1.0
        
    def load_reference_data(self):
        """Charge tous les fichiers de référence"""
        print("Chargement des données de référence...")
        
        # Charger les paramètres de génération
        self.parameters = pd.read_csv(
            os.path.join(self.base_path, 'Jeu de données - Smart Care - generation_parameters.csv')
        )
        
        # Charger la baseline de l'hôpital
        self.hospital_baseline = pd.read_csv(
            os.path.join(self.base_path, 'Jeu de données - Smart Care - hospital_baseline.csv'),
            decimal=','
        )
        
        # Charger les règles d'événements
        self.event_rules = pd.read_csv(
            os.path.join(self.base_path, 'Jeu de données - Smart Care - event_detection_rules.csv')
        )
        
        # Charger les vacances scolaires
        self.school_holidays = pd.read_csv(
            os.path.join(self.base_path, 'Jeu de données - Smart Care - school_holidays_reference.csv')
        )
        
        # Charger les événements spéciaux
        self.special_events = pd.read_csv(
            os.path.join(self.base_path, 'Jeu de données - Smart Care - special_event_reference.csv')
        )

        # Compléter avec des événements manquants (impacts par défaut)
        default_special_events = [
            {
                'evenement_type': 'Canicule',
                'date_debut': '2022-01-01',
                'date_fin': '2026-12-31',
                'condition_declenchement': 'temp_max > 30 sur plusieurs jours',
                'impact_admissions_min': 0.08,
                'impact_admissions_max': 0.20
            },
            {
                'evenement_type': 'Tension_hiver_2022',
                'date_debut': '2022-01-10',
                'date_fin': '2022-03-15',
                'condition_declenchement': 'tension hivernale + sortie progressive Covid',
                'impact_admissions_min': 0.05,
                'impact_admissions_max': 0.12
            },
            {
                'evenement_type': 'Plan_blanc_covid_leve_2022',
                'date_debut': '2022-03-15',
                'date_fin': '2022-03-31',
                'condition_declenchement': 'levée plan blanc Covid AP-HP',
                'impact_admissions_min': -0.03,
                'impact_admissions_max': 0.0
            },
            {
                'evenement_type': 'Canicule_IDF_2022',
                'date_debut': '2022-07-18',
                'date_fin': '2022-07-19',
                'condition_declenchement': 'vigilance orange canicule IDF',
                'impact_admissions_min': 0.12,
                'impact_admissions_max': 0.25
            },
            {
                'evenement_type': 'Triple_epidemie_hiver_2022',
                'date_debut': '2022-11-15',
                'date_fin': '2023-01-31',
                'condition_declenchement': 'grippe + bronchiolite + Covid',
                'impact_admissions_min': 0.15,
                'impact_admissions_max': 0.35
            },
            {
                'evenement_type': 'Coupe_monde_rugby_2023',
                'date_debut': '2023-09-08',
                'date_fin': '2023-10-28',
                'condition_declenchement': 'mass gathering (Stade de France/Paris)',
                'impact_admissions_min': 0.03,
                'impact_admissions_max': 0.08
            },
            {
                'evenement_type': 'JO_Paris_2024',
                'date_debut': '2024-07-26',
                'date_fin': '2024-08-11',
                'condition_declenchement': 'jeux olympiques Paris',
                'impact_admissions_min': 0.04,
                'impact_admissions_max': 0.10
            },
            {
                'evenement_type': 'Plan_blanc_hiver_2024_2025',
                'date_debut': '2024-12-15',
                'date_fin': '2025-02-15',
                'condition_declenchement': 'tension hivernale grippe',
                'impact_admissions_min': 0.10,
                'impact_admissions_max': 0.25
            },
            {
                'evenement_type': 'Tension_ete_2025',
                'date_debut': '2025-07-01',
                'date_fin': '2025-08-31',
                'condition_declenchement': 'organisation accès aux soins été',
                'impact_admissions_min': 0.02,
                'impact_admissions_max': 0.06
            },
            {
                'evenement_type': 'Accident_majeur',
                'date_debut': '2022-01-01',
                'date_fin': '2026-12-31',
                'condition_declenchement': 'incident majeur imprévisible',
                'impact_admissions_min': 0.10,
                'impact_admissions_max': 0.30
            },
            {
                'evenement_type': 'Greve_personnel',
                'date_debut': '2022-01-01',
                'date_fin': '2026-12-31',
                'condition_declenchement': 'mouvement social',
                'impact_admissions_min': -0.08,
                'impact_admissions_max': 0.05
            },
            {
                'evenement_type': 'Pic_pollution',
                'date_debut': '2022-01-01',
                'date_fin': '2026-12-31',
                'condition_declenchement': 'pollution atmosphérique',
                'impact_admissions_min': 0.03,
                'impact_admissions_max': 0.10
            },
        ]
        existing = set(self.special_events['evenement_type'].astype(str).tolist())
        missing_rows = [row for row in default_special_events if row['evenement_type'] not in existing]
        if missing_rows:
            self.special_events = pd.concat(
                [self.special_events, pd.DataFrame(missing_rows)],
                ignore_index=True
            )
        
        # Charger les variations de personnel
        self.staff_variation = pd.read_csv(
            os.path.join(self.base_path, 'Jeu de données - Smart Care - staff_varation_rules.csv')
        )
        
        # Charger la météo de référence
        self.weather_ref = pd.read_csv(
            os.path.join(self.base_path, 'Jeu de données - Smart Care - weather_daily_reference.csv'),
            decimal=','
        )
        
        # Charger la météo Luxembourg
        self.luxembourg_weather = pd.read_csv(
            os.path.join(self.base_path, 'Luxembourg_2019-2024_meteo(in).csv'),
            sep=';'
        )
        
        print("✓ Données de référence chargées")
        
    def get_parameter(self, name):
        """Récupère une valeur de paramètre"""
        value = self.parameters[self.parameters['parametre'] == name]['valeur'].values
        return value[0] if len(value) > 0 else None
    
    def get_hospital_info(self, hospital_id):
        """Récupère les informations d'un hôpital"""
        return self.hospital_baseline[self.hospital_baseline['hospital_id'] == hospital_id].iloc[0]
    
    def normalize_number(self, value):
        """Normalise les nombres avec virgule en point"""
        if isinstance(value, str):
            return float(value.replace(',', '.'))
        return float(value)
    
    def get_season(self, date):
        """Détermine la saison à partir d'une date"""
        month = date.month
        if month in [12, 1, 2]:
            return 'Hiver'
        elif month in [3, 4, 5]:
            return 'Printemps'
        elif month in [6, 7, 8]:
            return 'Été'
        else:
            return 'Automne'
    
    def get_day_name(self, date):
        """Retourne le jour de la semaine en français"""
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        return days[date.weekday()]
    
    def get_weather_from_luxembourg(self, date):
        """Extrait les données météo du fichier Luxembourg pour une date donnée"""
        date_str = date.strftime('%Y%m%d')
        
        # Chercher dans les données Luxembourg
        matching = self.luxembourg_weather[
            self.luxembourg_weather['Date (AAAAMMJJ)'] == int(date_str)
        ]
        
        if len(matching) > 0:
            row = matching.iloc[0]
            return {
                'temperature_moyenne': self.normalize_number(row['Temperature moyenne (C)']),
                'temperature_min': self.normalize_number(row['Temperature min (C)']),
                'temperature_max': self.normalize_number(row['Temperature max (C)']),
                'meteo_principale': row['Meteo'],
                'humidite': row.get('Moyenne Temp min-max (C)', 0),
                'vent': row.get('Amplitude thermique (C)', 0),
                'pression': 1013  # valeur par défaut
            }
        return None
    
    def get_weather_data(self, date):
        """Récupère ou génère les données météo pour une date"""
        # Essayer de trouver dans les données Luxembourg d'abord
        weather = self.get_weather_from_luxembourg(date)
        if weather:
            return weather
        
        # Sinon, générer basé sur les données de référence
        return self.generate_weather(date)
    
    def generate_weather(self, date):
        """Génère les données météo basées sur les saisons"""
        season = self.get_season(date)
        
        # Plages de température par saison
        temp_ranges = {
            'Hiver': (0, 10),
            'Printemps': (8, 18),
            'Été': (18, 28),
            'Automne': (10, 18)
        }
        
        weather_options = {
            'Hiver': ['Gris', 'Froid', 'Neige', 'Pluie'],
            'Printemps': ['Frais', 'Pluie', 'Soleil'],
            'Été': ['Soleil', 'Chaud', 'Orageux'],
            'Automne': ['Nuageux', 'Pluie', 'Frais']
        }
        
        min_temp, max_temp = temp_ranges.get(season, (10, 15))
        
        return {
            'temperature_moyenne': round(np.random.uniform(min_temp, max_temp), 1),
            'temperature_min': round(np.random.uniform(min_temp - 3, min_temp), 1),
            'temperature_max': round(np.random.uniform(max_temp, max_temp + 3), 1),
            'meteo_principale': random.choice(weather_options.get(season, ['Frais'])),
            'humidite': round(np.random.uniform(40, 95), 1),
            'vent': round(np.random.uniform(5, 30), 1),
            'pression': round(np.random.uniform(1000, 1025), 1)
        }
    
    def is_school_holiday(self, date):
        """Vérifie si la date est durant les vacances scolaires"""
        # Zone C (Paris) pour Luxembourg proche de France
        zone = 'Zone C'
        
        holidays_zone = self.school_holidays[self.school_holidays['zone'] == zone]
        
        for _, row in holidays_zone.iterrows():
            try:
                holiday_date = pd.to_datetime(row['date']).date()
                if date == holiday_date:
                    return 1
            except:
                pass
        
        # Marques les périodes de vacances scolaires connues
        month = date.month
        day = date.day
        
        # Vacances Noël (fin décembre - début janvier)
        if (month == 12 and day >= 20) or (month == 1 and day <= 5):
            return 1
        # Vacances d'hiver (février)
        if month == 2 and 13 <= day <= 24:
            return 1
        # Vacances de printemps (avril)
        if month == 4 and 10 <= day <= 24:
            return 1
        # Vacances d'été (juillet-août)
        if month in [7, 8]:
            return 1
        # Vacances de Toussaint (octobre-novembre)
        if month == 10 and 25 <= day <= 31:
            return 1
        if month == 11 and day <= 3:
            return 1
        
        return 0
    
    def get_staff_availability(self, hospital_info, date, personnel_type):
        """Calcule la disponibilité du personnel selon les variations"""
        reference = {
            'medecin': hospital_info['nb_medecins_reference'],
            'infirmier': hospital_info['nb_infirmiers_reference'],
            'aide_soignant': hospital_info['nb_aides_soignants_reference']
        }
        
        ref_value = self.normalize_number(reference.get(personnel_type, 0))

        # Tendance annuelle (baisse légère possible) + saisonnalité
        staff_trend = self._get_param_float('tendance_annuelle_staff', -0.05)
        years_diff = date.year - 2022
        ref_value *= (1 + staff_trend) ** max(0, years_diff)

        staff_season_amp = self._get_param_float('amplitude_saisonnalite_staff', 0.03)
        day_of_year = date.timetuple().tm_yday
        ref_value *= (1 + staff_season_amp * np.sin(2 * np.pi * (day_of_year / 365.0)))

        # Vacances scolaires (baisse plus marquée sur certains métiers)
        if self.is_school_holiday(date):
            vacation_factor = self._get_param_float('facteur_vacances_staff', 0.92)
            ref_value *= vacation_factor
        
        # Appliquer les variations mensuelles
        month = date.month
        staff_rules = self.staff_variation[
            (self.staff_variation['type_personnel'] == personnel_type) &
            (self.staff_variation['periode'] == f'mois={month:02d}')
        ]
        
        if len(staff_rules) > 0:
            # Convertir les probabilités en nombres
            staff_rules_copy = staff_rules.copy()
            staff_rules_copy['probabilite_num'] = staff_rules_copy['probabilite'].apply(self.normalize_number)
            total_prob = staff_rules_copy['probabilite_num'].sum()
            
            if total_prob > 0:
                weighted_value = 0
                for _, rule in staff_rules_copy.iterrows():
                    min_val = self.normalize_number(rule['borne_min'])
                    max_val = self.normalize_number(rule['borne_max'])
                    prob = rule['probabilite_num']
                    weighted_value += np.random.uniform(min_val, max_val) * (prob / total_prob)
                base_staff = weighted_value
                # Ajouter du bruit journalier contrôlé
                noise_rate = self._get_param_float('taux_bruit_staff', 0.06)
                noise = np.random.normal(0, base_staff * noise_rate)
                return max(0, int(base_staff + noise))

        # Si pas de règle trouvée, utiliser la valeur de référence ajustée + bruit
        noise_rate = self._get_param_float('taux_bruit_staff', 0.06)
        noise = np.random.normal(0, ref_value * noise_rate)
        return max(0, int(ref_value + noise))
    
    def calculate_admissions(self, date, hospital_info, events, weather):
        """Calcule le nombre d'admissions"""
        # Baseline
        base_admissions = self.normalize_number(hospital_info['admissions_moyennes_jour'])

        # Tendance annuelle + saisonnalité
        base_admissions *= self._year_trend_factor(date) * self._seasonality_factor(date)
        
        # Variance journalière
        noise_rate = self.normalize_number(self.get_parameter('taux_bruit_admissions'))
        noise = np.random.normal(0, base_admissions * noise_rate)
        
        # Jour de semaine (profil plus réaliste)
        weekday_factors = {
            0: 1.05,  # Lundi
            1: 1.02,
            2: 1.00,
            3: 1.00,
            4: 0.98,
            5: 0.88,  # Samedi
            6: 0.85,  # Dimanche
        }
        weekend_factor = weekday_factors.get(date.weekday(), 1.0)
        
        # Impact des événements
        event_impact = 0
        for event in events:
            if event != 'Aucun':
                event_row = self.special_events[self.special_events['evenement_type'] == event]
                if len(event_row) > 0:
                    impact_min = self.normalize_number(event_row.iloc[0]['impact_admissions_min'])
                    impact_max = self.normalize_number(event_row.iloc[0]['impact_admissions_max'])
                    event_impact += np.random.uniform(impact_min, impact_max)
        
        # Vacances scolaires - baisse des admissions
        vacation_factor = 0.92 if self.is_school_holiday(date) else 1.0

        # Température (impact extrêmes)
        temp_factor = self._temperature_factor(weather['temperature_moyenne'])

        # Choc rare (afflux massif / incident)
        shock_factor = self._daily_shock_adm

        expected = base_admissions * weekend_factor * vacation_factor * temp_factor * (1 + event_impact) * shock_factor

        # Autocorrélation (inertie jour à jour)
        ar_weight = self._get_param_float('poids_autocorrelation_admissions', 0.25)
        if self._prev_admissions is not None:
            expected = (1 - ar_weight) * expected + ar_weight * self._prev_admissions

        admissions = int(expected + noise)
        self._prev_admissions = admissions
        return max(admissions, 100)
    
    def calculate_urgences_passages(self, date, hospital_info, weather):
        """Calcule le nombre de passages aux urgences"""
        base_urgences = self.normalize_number(hospital_info['passages_urgences_moyens_jour'])

        # Tendance annuelle + saisonnalité
        base_urgences *= self._year_trend_factor(date) * self._seasonality_factor(date)
        
        # Variation météo
        weather_factor = self._temperature_factor(weather['temperature_moyenne'])
        
        # Jour de semaine2026
        day_of_week = date.weekday()
        if day_of_week == 4:  # Vendredi
            daily_factor = 1.10
        elif day_of_week == 5:  # Samedi
            daily_factor = 1.15
        elif day_of_week == 6:  # Dimanche
            daily_factor = 1.08
        else:
            daily_factor = 1.0
        
        # Vacances scolaires - impact sur urgences
        vacation_factor = 1.05 if self.is_school_holiday(date) else 1.0
        
        # Choc rare (afflux massif / incident)
        shock_factor = self._daily_shock_urg

        expected = base_urgences * weather_factor * daily_factor * vacation_factor * shock_factor

        # Autocorrélation (inertie jour à jour)
        ar_weight = self._get_param_float('poids_autocorrelation_urgences', 0.20)
        if self._prev_urgences is not None:
            expected = (1 - ar_weight) * expected + ar_weight * self._prev_urgences

        urgences = int(expected)
        self._prev_urgences = urgences
        return max(urgences, 300)
    
    def detect_events(self, date, weather):
        """Détecte les événements basés sur les conditions"""
        events = []
        season = self.get_season(date)
        
        for _, rule in self.event_rules.iterrows():
            evenement = rule['evenement_type']
            
            # Vérifier les conditions
            if evenement == 'Epidemie_grippe':
                if season == 'Hiver':
                    events.append(evenement)
            elif evenement == 'Vague_froid':
                if weather['temperature_min'] <= 0:
                    events.append(evenement)
            elif evenement == 'Canicule':
                if weather['temperature_max'] >= 25:
                    events.append(evenement)

        # Événements aléatoires (accidents, grèves, pollution)
        random_events = {
            'Accident_majeur': self._get_param_float('prob_event_accident_majeur', 0.002),
            'Greve_personnel': self._get_param_float('prob_event_greve_personnel', 0.003),
            'Pic_pollution': self._get_param_float('prob_event_pic_pollution', 0.005),
        }
        for evt, prob in random_events.items():
            if random.random() < prob:
                events.append(evt)

        # Événements datés (Paris/IDF) ajoutés aux règles
        fixed_events = [
            ('Tension_hiver_2022', '2022-01-10', '2022-03-15'),
            ('Plan_blanc_covid_leve_2022', '2022-03-15', '2022-03-31'),
            ('Canicule_IDF_2022', '2022-07-18', '2022-07-19'),
            ('Triple_epidemie_hiver_2022', '2022-11-15', '2023-01-31'),
            ('Coupe_monde_rugby_2023', '2023-09-08', '2023-10-28'),
            ('JO_Paris_2024', '2024-07-26', '2024-08-11'),
            ('Plan_blanc_hiver_2024_2025', '2024-12-15', '2025-02-15'),
            ('Tension_ete_2025', '2025-07-01', '2025-08-31'),
        ]
        for evt, start_str, end_str in fixed_events:
            start = pd.Timestamp(start_str)
            end = pd.Timestamp(end_str)
            if start <= date <= end:
                events.append(evt)
        
        # Éviter les doublons
        events = list(dict.fromkeys(events))
        return events if events else ['Aucun']
    
    def generate_daily_data(self, start_date, end_date, hospital_id):
        """Génère les données journalières"""
        hospital_info = self.get_hospital_info(hospital_id)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        daily_data = []
        weather_data = []

        # Réinitialiser l'inertie entre séries
        self._prev_admissions = None
        self._prev_urgences = None
        
        print(f"Génération des données du {start_date.date()} au {end_date.date()}...")
        
        for i, date in enumerate(dates):
            if (i + 1) % 100 == 0:
                print(f"  {i + 1} jours générés...")

            # Chocs rares (afflux massif / incident local)
            shock_prob = self._get_param_float('prob_choc_afflux', 0.006)
            if random.random() < shock_prob:
                self._daily_shock_adm = np.random.uniform(1.15, 1.40)
                self._daily_shock_urg = np.random.uniform(1.20, 1.55)
            else:
                self._daily_shock_adm = 1.0
                self._daily_shock_urg = 1.0
            
            # Récupérer les données météo
            weather = self.get_weather_data(date)
            
            # Ajouter aux données météo
            weather_row = {
                'date': date.date(),
                'temperature_moyenne': weather['temperature_moyenne'],
                'temperature_min': weather['temperature_min'],
                'temperature_max': weather['temperature_max'],
                'meteo_principale': weather['meteo_principale'],
                'vent': weather['vent'],
                'humidite': weather['humidite'],
                'pression': weather['pression']
            }
            weather_data.append(weather_row)
            
            # Détecter les événements
            events = self.detect_events(date, weather)
            event_principal = events[0] if events else 'Aucun'
            
            # Calculer l'impact des événements
            impact = 0.0
            for event in events:
                if event != 'Aucun':
                    event_row = self.special_events[self.special_events['evenement_type'] == event]
                    if len(event_row) > 0:
                        impact_min = self.normalize_number(event_row.iloc[0]['impact_admissions_min'])
                        impact_max = self.normalize_number(event_row.iloc[0]['impact_admissions_max'])
                        impact += np.random.uniform(impact_min, impact_max)
            
            # Calculer les effectifs
            admissions = self.calculate_admissions(date, hospital_info, events, weather)
            urgences = self.calculate_urgences_passages(date, hospital_info, weather)
            
            # Calculer l'occupation des lits
            total_lits = self.normalize_number(hospital_info['lits_total_mco'])
            duree_moyenne = self.normalize_number(hospital_info['duree_sejour_moyenne'])
            
            # Estimation de l'occupation
            lits_occupes = int(min(
                total_lits * 0.7 + np.random.normal(0, total_lits * 0.1),
                total_lits * 0.95
            ))
            taux_occupation = lits_occupes / total_lits
            
            # Personnel disponible
            medecins = self.get_staff_availability(hospital_info, date, 'medecin')
            infirmiers = self.get_staff_availability(hospital_info, date, 'infirmier')
            aides = self.get_staff_availability(hospital_info, date, 'aide_soignant')
            
            total_personnel_ref = (
                self.normalize_number(hospital_info['nb_medecins_reference']) +
                self.normalize_number(hospital_info['nb_infirmiers_reference']) +
                self.normalize_number(hospital_info['nb_aides_soignants_reference'])
            )
            
            taux_couverture = (medecins + infirmiers + aides) / total_personnel_ref if total_personnel_ref > 0 else 0.85
            
            # Hospitalisations et sorties
            hospitalisations = int(admissions * 0.65)
            sorties = max(1, int(lits_occupes / duree_moyenne))
            
            row = {
                'date': date.date(),
                'jour_semaine': self.get_day_name(date),
                'jour_mois': date.day,
                'semaine_annee': date.isocalendar()[1],
                'mois': date.month,
                'annee': date.year,
                'saison': self.get_season(date),
                'vacances_scolaires': self.is_school_holiday(date),
                'temperature_moyenne': weather['temperature_moyenne'],
                'temperature_min': weather['temperature_min'],
                'temperature_max': weather['temperature_max'],
                'meteo_principale': weather['meteo_principale'],
                'indice_chaleur': max(0, weather['temperature_max'] - 25) if weather['temperature_max'] > 25 else 0,
                'indice_froid': max(0, -weather['temperature_min']) if weather['temperature_min'] < 0 else 0,
                'lits_total': int(total_lits),
                'lits_occupes': lits_occupes,
                'taux_occupation_lits': round(taux_occupation, 2),
                'nb_medecins_disponibles': medecins,
                'nb_infirmiers_disponibles': infirmiers,
                'nb_aides_soignants_disponibles': aides,
                'taux_couverture_personnel': round(taux_couverture, 2),
                'nombre_admissions': admissions,
                'nombre_passages_urgences': urgences,
                'nombre_hospitalisations': hospitalisations,
                'nombre_sorties': sorties,
                'evenement_special': event_principal,
                'impact_evenement_estime': round(impact, 2)
            }
            
            daily_data.append(row)
        
        return pd.DataFrame(daily_data), pd.DataFrame(weather_data)
    
    def generate_school_holidays(self):
        """Génère les dates de vacances scolaires pour 2022-2026"""
        holidays = []
        zone = 'Zone C'
        
        vacation_periods = {
            2022: [
                ('2022-01-01', '2022-01-05', 'Noel'),
                ('2022-02-13', '2022-02-24', 'Hiver'),
                ('2022-04-10', '2022-04-24', 'Printemps'),
                ('2022-07-01', '2022-08-31', 'Ete'),
                ('2022-10-25', '2022-11-03', 'Toussaint'),
                ('2022-12-20', '2022-12-31', 'Noel'),
            ],
            2023: [
                ('2023-01-01', '2023-01-05', 'Noel'),
                ('2023-02-12', '2023-02-23', 'Hiver'),
                ('2023-04-09', '2023-04-23', 'Printemps'),
                ('2023-07-01', '2023-08-31', 'Ete'),
                ('2023-10-24', '2023-11-02', 'Toussaint'),
                ('2023-12-20', '2023-12-31', 'Noel'),
            ],
            2024: [
                ('2024-01-01', '2024-01-05', 'Noel'),
                ('2024-02-11', '2024-02-22', 'Hiver'),
                ('2024-04-07', '2024-04-21', 'Printemps'),
                ('2024-07-01', '2024-08-31', 'Ete'),
                ('2024-10-22', '2024-11-01', 'Toussaint'),
                ('2024-12-20', '2024-12-31', 'Noel'),
            ],
            2025: [
                ('2025-01-01', '2025-01-05', 'Noel'),
                ('2025-02-09', '2025-02-21', 'Hiver'),
                ('2025-04-06', '2025-04-20', 'Printemps'),
                ('2025-07-01', '2025-08-31', 'Ete'),
                ('2025-10-19', '2025-11-02', 'Toussaint'),
                ('2025-12-20', '2025-12-31', 'Noel'),
            ],
            2026: [
                ('2026-01-01', '2026-01-05', 'Noel'),
                ('2026-02-08', '2026-02-20', 'Hiver'),
                ('2026-04-05', '2026-04-19', 'Printemps'),
                ('2026-07-01', '2026-08-31', 'Ete'),
                ('2026-10-18', '2026-11-01', 'Toussaint'),
                ('2026-12-20', '2026-12-31', 'Noel'),
            ]
        }
        
        for year, periods in vacation_periods.items():
            for start_str, end_str, vacation_type in periods:
                start = pd.to_datetime(start_str).date()
                end = pd.to_datetime(end_str).date()
                
                current = start
                while current <= end:
                    holidays.append({
                        'date': current,
                        'zone': zone,
                        'vacances_scolaires': 1,
                        'type_vacances': vacation_type
                    })
                    current += pd.Timedelta(days=1)
        
        return pd.DataFrame(holidays)
    
    def generate_event_detection_rules_extended(self):
        """Génère les règles d'événements étendues pour 2022-2026"""
        rules = []
        
        base_rules = [
            {
                'evenement_type': 'Epidemie_grippe',
                'condition_temperature': 'saison=Hiver',
                'condition_duree': '>=14 jours',
                'condition_meteo': 'any',
                'priorite_evenement': 9,
                'evenement_declenche': 'TRUE'
            },
            {
                'evenement_type': 'Vague_froid',
                'condition_temperature': 'temp_min <= 0',
                'condition_duree': '>=2 jours',
                'condition_meteo': 'Gris',
                'priorite_evenement': 6,
                'evenement_declenche': 'TRUE'
            },
            {
                'evenement_type': 'Canicule',
                'condition_temperature': 'temp_max >= 25',
                'condition_duree': '>=1 jour',
                'condition_meteo': 'Soleil',
                'priorite_evenement': 10,
                'evenement_declenche': 'FALSE'
            },
            {
                'evenement_type': 'Tension_hiver_2022',
                'condition_temperature': 'date_range=2022-01-10..2022-03-15',
                'condition_duree': 'fixed',
                'condition_meteo': 'any',
                'priorite_evenement': 8,
                'evenement_declenche': 'TRUE'
            },
            {
                'evenement_type': 'Plan_blanc_covid_leve_2022',
                'condition_temperature': 'date_range=2022-03-15..2022-03-31',
                'condition_duree': 'fixed',
                'condition_meteo': 'any',
                'priorite_evenement': 4,
                'evenement_declenche': 'TRUE'
            },
            {
                'evenement_type': 'Canicule_IDF_2022',
                'condition_temperature': 'date_range=2022-07-18..2022-07-19',
                'condition_duree': 'fixed',
                'condition_meteo': 'Soleil',
                'priorite_evenement': 10,
                'evenement_declenche': 'TRUE'
            },
            {
                'evenement_type': 'Triple_epidemie_hiver_2022',
                'condition_temperature': 'date_range=2022-11-15..2023-01-31',
                'condition_duree': 'fixed',
                'condition_meteo': 'any',
                'priorite_evenement': 9,
                'evenement_declenche': 'TRUE'
            },
            {
                'evenement_type': 'Coupe_monde_rugby_2023',
                'condition_temperature': 'date_range=2023-09-08..2023-10-28',
                'condition_duree': 'fixed',
                'condition_meteo': 'any',
                'priorite_evenement': 6,
                'evenement_declenche': 'TRUE'
            },
            {
                'evenement_type': 'JO_Paris_2024',
                'condition_temperature': 'date_range=2024-07-26..2024-08-11',
                'condition_duree': 'fixed',
                'condition_meteo': 'any',
                'priorite_evenement': 7,
                'evenement_declenche': 'TRUE'
            },
            {
                'evenement_type': 'Plan_blanc_hiver_2024_2025',
                'condition_temperature': 'date_range=2024-12-15..2025-02-15',
                'condition_duree': 'fixed',
                'condition_meteo': 'any',
                'priorite_evenement': 9,
                'evenement_declenche': 'TRUE'
            },
            {
                'evenement_type': 'Tension_ete_2025',
                'condition_temperature': 'date_range=2025-07-01..2025-08-31',
                'condition_duree': 'fixed',
                'condition_meteo': 'any',
                'priorite_evenement': 5,
                'evenement_declenche': 'TRUE'
            }
        ]
        
        for year in [2022, 2023, 2024, 2025, 2026]:
            for rule in base_rules:
                rules.append(rule)
        
        return pd.DataFrame(rules)
    
    def generate_special_events_extended(self):
        """Génère les événements spéciaux étendus pour 2022-2026"""
        events = []
        
        for year in [2022, 2023, 2024, 2025, 2026]:
            events.extend([
                {
                    'evenement_type': 'Epidemie_grippe',
                    'date_debut': f'{year}-12-15',
                    'date_fin': f'{year}-02-10' if year < 2026 else '2027-02-10',
                    'condition_declenchement': 'pic hivernal + surveillance',
                    'impact_admissions_min': 0.1,
                    'impact_admissions_max': 0.25
                },
                {
                    'evenement_type': 'Vague_froid',
                    'date_debut': f'{year}-12-28',
                    'date_fin': f'{year}-01-05' if year > 2022 else '2023-01-05',
                    'condition_declenchement': 'temp_min < 0 sur plusieurs jours',
                    'impact_admissions_min': 0.05,
                    'impact_admissions_max': 0.12
                },
                {
                    'evenement_type': 'Canicule',
                    'date_debut': f'{year}-07-15',
                    'date_fin': f'{year}-08-15',
                    'condition_declenchement': 'temp_max > 30 sur plusieurs jours',
                    'impact_admissions_min': 0.08,
                    'impact_admissions_max': 0.20
                },
                {
                    'evenement_type': 'Accident_majeur',
                    'date_debut': f'{year}-01-01',
                    'date_fin': f'{year}-12-31',
                    'condition_declenchement': 'incident majeur imprévisible',
                    'impact_admissions_min': 0.10,
                    'impact_admissions_max': 0.30
                },
                {
                    'evenement_type': 'Greve_personnel',
                    'date_debut': f'{year}-01-01',
                    'date_fin': f'{year}-12-31',
                    'condition_declenchement': 'mouvement social',
                    'impact_admissions_min': -0.08,
                    'impact_admissions_max': 0.05
                },
                {
                    'evenement_type': 'Pic_pollution',
                    'date_debut': f'{year}-01-01',
                    'date_fin': f'{year}-12-31',
                    'condition_declenchement': 'pollution atmosphérique',
                    'impact_admissions_min': 0.03,
                    'impact_admissions_max': 0.10
                }
            ])

        # Événements spécifiques Paris/IDF (2022-2025)
        events.extend([
            {
                'evenement_type': 'Tension_hiver_2022',
                'date_debut': '2022-01-10',
                'date_fin': '2022-03-15',
                'condition_declenchement': 'tension hivernale + sortie progressive Covid',
                'impact_admissions_min': 0.05,
                'impact_admissions_max': 0.12
            },
            {
                'evenement_type': 'Plan_blanc_covid_leve_2022',
                'date_debut': '2022-03-15',
                'date_fin': '2022-03-31',
                'condition_declenchement': 'levée plan blanc Covid AP-HP',
                'impact_admissions_min': -0.03,
                'impact_admissions_max': 0.0
            },
            {
                'evenement_type': 'Canicule_IDF_2022',
                'date_debut': '2022-07-18',
                'date_fin': '2022-07-19',
                'condition_declenchement': 'vigilance orange canicule IDF',
                'impact_admissions_min': 0.12,
                'impact_admissions_max': 0.25
            },
            {
                'evenement_type': 'Triple_epidemie_hiver_2022',
                'date_debut': '2022-11-15',
                'date_fin': '2023-01-31',
                'condition_declenchement': 'grippe + bronchiolite + Covid',
                'impact_admissions_min': 0.15,
                'impact_admissions_max': 0.35
            },
            {
                'evenement_type': 'Coupe_monde_rugby_2023',
                'date_debut': '2023-09-08',
                'date_fin': '2023-10-28',
                'condition_declenchement': 'mass gathering (Stade de France/Paris)',
                'impact_admissions_min': 0.03,
                'impact_admissions_max': 0.08
            },
            {
                'evenement_type': 'JO_Paris_2024',
                'date_debut': '2024-07-26',
                'date_fin': '2024-08-11',
                'condition_declenchement': 'jeux olympiques Paris',
                'impact_admissions_min': 0.04,
                'impact_admissions_max': 0.10
            },
            {
                'evenement_type': 'Plan_blanc_hiver_2024_2025',
                'date_debut': '2024-12-15',
                'date_fin': '2025-02-15',
                'condition_declenchement': 'tension hivernale grippe',
                'impact_admissions_min': 0.10,
                'impact_admissions_max': 0.25
            },
            {
                'evenement_type': 'Tension_ete_2025',
                'date_debut': '2025-07-01',
                'date_fin': '2025-08-31',
                'condition_declenchement': 'organisation accès aux soins été',
                'impact_admissions_min': 0.02,
                'impact_admissions_max': 0.06
            },
        ])
        
        return pd.DataFrame(events)
    
    def generate_staff_variation_extended(self):
        """Génère les variations de personnel complètes pour tous les mois"""
        variations = []
        
        personnel_types = ['medecin', 'infirmier', 'aide_soignant']
        
        # Ranges par type de personnel et mois
        ranges = {
            'medecin': {
                'default': (55, 70),
                'vacances': (50, 60),
                'weekend': (45, 55)
            },
            'infirmier': {
                'default': (215, 270),
                'vacances': (190, 240),
                'weekend': (180, 220)
            },
            'aide_soignant': {
                'default': (170, 215),
                'vacances': (150, 190),
                'weekend': (140, 180)
            }
        }
        
        for month in range(1, 13):
            for personnel in personnel_types:
                range_info = ranges[personnel]
                
                # Variation normale
                variations.append({
                    'type_personnel': personnel,
                    'periode': f'mois={month:02d}',
                    'borne_min': range_info['default'][0],
                    'borne_max': range_info['default'][1],
                    'probabilite': 0.8
                })
                
                # Variation basse
                variations.append({
                    'type_personnel': personnel,
                    'periode': f'mois={month:02d}',
                    'borne_min': range_info['vacances'][0],
                    'borne_max': range_info['vacances'][1],
                    'probabilite': 0.1
                })
                
                # Variation haute
                variations.append({
                    'type_personnel': personnel,
                    'periode': f'mois={month:02d}',
                    'borne_min': range_info['weekend'][0],
                    'borne_max': range_info['weekend'][1],
                    'probabilite': 0.1
                })
        
        return pd.DataFrame(variations)
    
    def generate_all_years(self):
        """Génère les données pour 2022, 2023, 2024, 2025 et 2026"""
        hospital_id = self.get_parameter('hospital_reference')
        
        all_daily_data = []
        all_weather_data = []
        
        # Générer pour chaque année
        for year in [2022, 2023, 2024, 2025, 2026]:
            print(f"\n{'='*50}")
            print(f"Génération de l'année {year}")
            print(f"{'='*50}")
            
            start_date = pd.Timestamp(year=year, month=1, day=1)
            if year == 2026:
                end_date = pd.Timestamp(year=year, month=1, day=31)
            else:
                end_date = pd.Timestamp(year=year, month=12, day=31)
            
            # Générer les données journalières et météo
            year_data, year_weather = self.generate_daily_data(start_date, end_date, hospital_id)
            all_daily_data.append(year_data)
            all_weather_data.append(year_weather)
        
        # Combiner les données
        df_combined_daily = pd.concat(all_daily_data, ignore_index=True)
        df_combined_weather = pd.concat(all_weather_data, ignore_index=True)
        
        return df_combined_daily, df_combined_weather
    
    def save_data(self, df, output_path):
        """Sauvegarde les données générées"""
        print(f"\nSauvegarde des données dans {output_path}...")
        
        # Convertir les dates en string si la colonne existe
        df_save = df.copy()
        if 'date' in df_save.columns:
            df_save['date'] = df_save['date'].astype(str)
        
        # Remplacer les décimales (. en ,) pour les nombres décimaux
        float_cols = [col for col in df_save.columns if col in [
            'temperature_moyenne', 'temperature_min', 'temperature_max', 
            'indice_chaleur', 'indice_froid', 'taux_occupation_lits', 
            'taux_couverture_personnel', 'impact_evenement_estime',
            'impact_admissions_min', 'impact_admissions_max',
            'borne_min', 'borne_max', 'probabilite'
        ]]
        
        for col in float_cols:
            if col in df_save.columns:
                df_save[col] = df_save[col].apply(lambda x: str(x).replace('.', ','))
        
        # Sauvegarder sans index et avec séparateur virgule
        df_save.to_csv(output_path, index=False, sep=',', encoding='utf-8')
        print(f"✓ Données sauvegardées: {output_path}")


def main():
    """Fonction principale"""
    # Chemin de base (dossier data/raw du projet)
    base_path = Path(__file__).resolve().parents[1] / "data" / "raw"
    
    # Initialiser le générateur
    generator = SmartCareDataGenerator(base_path)
    
    # Définir la seed pour la reproductibilité
    seed = int(generator.get_parameter('seed_random'))
    np.random.seed(seed)
    random.seed(seed)
    
    print(f"\n{'='*50}")
    print("GÉNÉRATEUR DE DONNÉES SMART CARE")
    print(f"{'='*50}")
    print(f"Période: 2022-2026")
    print(f"Hôpital: {generator.get_parameter('hospital_reference')}")
    print(f"Mode: {generator.get_parameter('mode_generation')}")
    print(f"Seed: {seed}")
    print(f"{'='*50}\n")
    
    # Générer les données
    df_daily, df_weather = generator.generate_all_years()
    
    # Générer les vacances scolaires
    df_holidays = generator.generate_school_holidays()
    
    # Générer les fichiers de référence étendus
    df_events_rules = generator.generate_event_detection_rules_extended()
    df_special_events = generator.generate_special_events_extended()
    df_staff_variation = generator.generate_staff_variation_extended()
    
    # Afficher les statistiques
    print(f"\n{'='*50}")
    print("STATISTIQUES GÉNÉRALES")
    print(f"{'='*50}")
    print(f"Nombre total de jours: {len(df_daily)}")
    print(f"Période: {df_daily['date'].min()} à {df_daily['date'].max()}")
    print(f"\nRésumé par année:")
    for year in [2022, 2023, 2024]:
        year_data = df_daily[df_daily['annee'] == year]
        print(f"\n  {year}:")
        print(f"    Jours: {len(year_data)}")
        print(f"    Admissions totales: {year_data['nombre_admissions'].sum()}")
        print(f"    Passages urgences: {year_data['nombre_passages_urgences'].sum()}")
        print(f"    Taux occupation moyen: {year_data['taux_occupation_lits'].mean():.2f}")
        print(f"    Événements spéciaux: {len(year_data[year_data['evenement_special'] != 'Aucun'])}")
    
    # Sauvegarder les données
    output_daily = os.path.join(
        base_path,
        f'Jeu de données - Smart Care - daily_hospital_context_2022-2026_generated.csv'
    )
    output_weather = os.path.join(
        base_path,
        f'Jeu de données - Smart Care - weather_daily_reference_2022-2026_generated.csv'
    )
    output_holidays = os.path.join(
        base_path,
        f'Jeu de données - Smart Care - school_holidays_reference_2022-2026_generated.csv'
    )
    output_events_rules = os.path.join(
        base_path,
        f'Jeu de données - Smart Care - event_detection_rules_2022-2026_generated.csv'
    )
    output_special_events = os.path.join(
        base_path,
        f'Jeu de données - Smart Care - special_event_reference_2022-2026_generated.csv'
    )
    output_staff_variation = os.path.join(
        base_path,
        f'Jeu de données - Smart Care - staff_varation_rules_2022-2026_generated.csv'
    )
    
    generator.save_data(df_daily, output_daily)
    generator.save_data(df_weather, output_weather)
    generator.save_data(df_holidays, output_holidays)
    generator.save_data(df_events_rules, output_events_rules)
    generator.save_data(df_special_events, output_special_events)
    generator.save_data(df_staff_variation, output_staff_variation)
    
    print(f"\n{'='*50}")
    print("FICHIERS GÉNÉRÉS (2022-2026)")
    print(f"{'='*50}")
    print(f"✓ daily_hospital_context_2022-2026_generated.csv")
    print(f"✓ weather_daily_reference_2022-2026_generated.csv")
    print(f"✓ school_holidays_reference_2022-2026_generated.csv")
    print(f"✓ event_detection_rules_2022-2026_generated.csv")
    print(f"✓ special_event_reference_2022-2026_generated.csv")
    print(f"✓ staff_varation_rules_2022-2026_generated.csv")
    print(f"\nFichiers de référence statiques (originaux):")
    print(f"  - generation_parameters.csv")
    print(f"  - hospital_baseline.csv")
    print(f"  - Luxembourg_2019-2024_meteo.csv")
    print(f"{'='*50}\n")


if __name__ == '__main__':
    main()
