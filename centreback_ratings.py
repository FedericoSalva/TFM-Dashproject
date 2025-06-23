import pandas as pd
import numpy as np
from pathlib import Path
import os

# Pesi delle leghe
LEAGUE_WEIGHTS = {
    'Serie_A': 1.7,      # Top 5
    'EPL': 1.7,          # Top 5
    'La_Liga': 1.7,      # Top 5
    'Bundesliga': 1.7,   # Top 5
    'Ligue_1': 1.7,      # Top 5
    'Primeira_Liga': 1.2,
    'Eredivisie': 1.2,
    'Süper_Lig': 1.2,
    'MLS': 1.0,
    'Championship': 1.0
}

# Coefficienti per i minuti giocati
MINUTES_COEFFICIENTS = {
    (0, 500): 0.0,      # Sotto 500 minuti: rating 30
    (501, 1000): 0.7,   # 501-1000 minuti: coefficiente 0.7
    (1001, 1500): 0.85, # 1001-1500 minuti: coefficiente 0.85
    (1501, float('inf')): 1.0  # Oltre 1500 minuti: coefficiente 1.0
}

def safe_float_convert(value):
    """Converte in modo sicuro un valore in float, gestendo anche i numeri con virgola come separatore delle migliaia"""
    if pd.isna(value) or value == '':
        return 0.0
    try:
        if isinstance(value, str):
            value = value.replace(',', '')
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def get_minutes_coefficient(minutes):
    """Restituisce il coefficiente in base ai minuti giocati"""
    minutes = safe_float_convert(minutes)
    for (min_range, max_range), coefficient in MINUTES_COEFFICIENTS.items():
        if min_range <= minutes <= max_range:
            return coefficient
    return 0.0

def normalize_kpi(value, min_val, max_val):
    """Normalizza un KPI tra 0 e 1"""
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)

def get_league_paths():
    """Restituisce i percorsi delle leghe da analizzare"""
    base_path = Path('/Users/federico/dash_project/pages')
    league_paths = {
        'Serie_A': base_path / 'data_serie_a_24-25',
        'EPL': base_path / 'EPL/data_EPL_24-25',
        'La_Liga': base_path / 'La_Liga/data_La_Liga_24-25',
        'Bundesliga': base_path / 'Bundesliga/data_Bundesliga_24-25',
        'Ligue_1': base_path / 'Ligue_1/data_Ligue_1_24-25',
        'Primeira_Liga': base_path / 'Primeira_Liga/data_Primeira_Liga_24-25',
        'Eredivisie': base_path / 'Eredivisie/data_Eredivisie_24-25',
        'Süper_Lig': base_path / 'Süper_Lig/data_Süper_Lig_24-25',
        'MLS': base_path / 'MLS/data_MLS_24',
        'Championship': base_path / 'Championship/data_Championship_24-25'
    }
    return league_paths

def get_team_files(league_path):
    """Restituisce le coppie di file FBRef e Transfermarkt per ogni squadra"""
    team_files = []
    for fbref_file in league_path.glob('*.csv'):
        if fbref_file.name.endswith('_fbref.csv'):
            team_name = fbref_file.stem.replace('_fbref', '')
            transfermarkt_file = league_path / f'{team_name}_transfermarkt.csv'
        if transfermarkt_file.exists():
                team_files.append((fbref_file, transfermarkt_file))
    return team_files

def load_league_data(league_path):
    """Carica i dati della lega da FBRef e Transfermarkt"""
    try:
        team_files = get_team_files(league_path)
        if not team_files:
            print(f"Nessun file trovato in {league_path}")
            return None, None

        all_fbref_data = []
        all_transfermarkt_data = []

        for fbref_file, transfermarkt_file in team_files:
            try:
            fbref_df = pd.read_csv(fbref_file)
            fbref_df['Team'] = fbref_file.stem
            all_fbref_data.append(fbref_df)
                
            transfermarkt_df = pd.read_csv(transfermarkt_file)
            transfermarkt_df['Team'] = fbref_file.stem
            all_transfermarkt_data.append(transfermarkt_df)
            except Exception as e:
                print(f"Errore nel caricamento dei file {fbref_file} o {transfermarkt_file}: {str(e)}")
                continue

        if not all_fbref_data or not all_transfermarkt_data:
            print(f"Nessun dato valido trovato in {league_path}")
            return None, None

        return pd.concat(all_fbref_data, ignore_index=True), pd.concat(all_transfermarkt_data, ignore_index=True)
    except Exception as e:
        print(f"Errore nel caricamento dei dati per {league_path}: {str(e)}")
        return None, None

def calculate_global_ranges(fbref_df):
    """Calcola i range globali per la normalizzazione dei KPI"""
    kpi_ranges = {}
    
    # KPI per Guardian (20/80 con/senza palla)
    guardian_kpis = {
        'Con palla': {
            '% Cmp': {'weight': 0.4, 'inverse': False},
            'PA': {'weight': 0.35, 'inverse': False},
            'Long. Prom.': {'weight': 0.15, 'inverse': False},
            'Cmp': {'weight': 0.1, 'inverse': False}
        },
        'Senza palla': {
            'Tkl(Desafios)': {'weight': 0.3, 'inverse': False},
            '3.º cent.': {'weight': 0.25, 'inverse': False},
            '% de ganados': {'weight': 0.25, 'inverse': False},
            'Recup.': {'weight': 0.2, 'inverse': False}
        }
    }
    
    # KPI per Deep Distributor (70/30 con/senza palla)
    distributor_kpis = {
        'Con palla': {
            'PrgP': {'weight': 0.35, 'inverse': False},
            '1/3': {'weight': 0.3, 'inverse': False},
            'Camb.': {'weight': 0.25, 'inverse': False},
            '% Cmp (largos)': {'weight': 0.1, 'inverse': False}
        },
        'Senza palla': {
            'Int': {'weight': 0.4, 'inverse': False},
            '3.º cent.': {'weight': 0.35, 'inverse': False},
            'TklG': {'weight': 0.15, 'inverse': False},
            'Recup.': {'weight': 0.1, 'inverse': False}
        }
    }
    
    # KPI per Enforcer (15/85 con/senza palla)
    enforcer_kpis = {
        'Con palla': {
            'PrgP': {'weight': 0.4, 'inverse': False},
            '% Cmp': {'weight': 0.35, 'inverse': False},
            'Dist. prg.': {'weight': 0.15, 'inverse': False},
            'Toques': {'weight': 0.1, 'inverse': False}
        },
        'Senza palla': {
            'Int': {'weight': 0.35, 'inverse': False},
            'Recup.': {'weight': 0.3, 'inverse': False},
            '% de ganados': {'weight': 0.2, 'inverse': False},
            'Tkl(Desafios)': {'weight': 0.15, 'inverse': False}
        }
    }
    
    # Calcola i range per tutti i KPI
    all_kpis = set()
    for profile in [guardian_kpis, distributor_kpis, enforcer_kpis]:
        for phase in profile.values():
            all_kpis.update(phase.keys())
    
    for kpi in all_kpis:
        if kpi in fbref_df.columns:
            values = fbref_df[kpi].apply(safe_float_convert)
            if not values.empty and values.notna().any():
            kpi_ranges[kpi] = {
                'min': values.min(),
                'max': values.max()
            }
    
    return kpi_ranges, guardian_kpis, distributor_kpis, enforcer_kpis

def calculate_centreback_rating(player_data, kpi_ranges, guardian_kpis, distributor_kpis, enforcer_kpis, league_weight=1.0):
    """Calcola i rating del difensore centrale per i tre profili"""
    minutes_coefficient = get_minutes_coefficient(player_data['Mín'])
    if minutes_coefficient == 0.0:
        return {
            'Guardian': 30.0,
            'Deep_Distributor': 30.0,
            'Enforcer': 30.0
        }
    
    normalized_stats = {}
    for kpi, ranges in kpi_ranges.items():
        value = safe_float_convert(player_data.get(kpi, 0))
        normalized_stats[kpi] = normalize_kpi(value, ranges['min'], ranges['max'])
    
    def calculate_profile_rating(profile_kpis):
        rating = 0.0
        total_weight = 0.0
        
        # Calcola rating con palla (20% per Guardian, 70% per Distributor, 15% per Enforcer)
        with_ball_weight = 0.2 if profile_kpis == guardian_kpis else (0.7 if profile_kpis == distributor_kpis else 0.15)
        for kpi, info in profile_kpis['Con palla'].items():
            if kpi in normalized_stats:
                rating += normalized_stats[kpi] * info['weight'] * with_ball_weight
                total_weight += info['weight'] * with_ball_weight
        
        # Calcola rating senza palla (80% per Guardian, 30% per Distributor, 85% per Enforcer)
        without_ball_weight = 0.8 if profile_kpis == guardian_kpis else (0.3 if profile_kpis == distributor_kpis else 0.85)
        for kpi, info in profile_kpis['Senza palla'].items():
            if kpi in normalized_stats:
                rating += normalized_stats[kpi] * info['weight'] * without_ball_weight
                total_weight += info['weight'] * without_ball_weight
        
        if total_weight > 0:
            rating = rating / total_weight
        
        return rating
    
    # Calcola i rating per ogni profilo
    guardian_rating = calculate_profile_rating(guardian_kpis)
    distributor_rating = calculate_profile_rating(distributor_kpis)
    enforcer_rating = calculate_profile_rating(enforcer_kpis)
    
    # Applica i coefficienti
    guardian_final = 30 + (guardian_rating * 1.0 * 69) * minutes_coefficient * league_weight
    distributor_final = 30 + (distributor_rating * 1.0 * 69) * minutes_coefficient * league_weight
    enforcer_final = 30 + (enforcer_rating * 0.85 * 69) * minutes_coefficient * league_weight
    
    # Limita i rating a 99.0
    return {
        'Guardian': round(min(99.0, guardian_final), 1),
        'Deep_Distributor': round(min(99.0, distributor_final), 1),
        'Enforcer': round(min(99.0, enforcer_final), 1)
    }

def get_centreback_ratings(fbref_df, transfermarkt_df, league_name):
    """Calcola i rating per tutti i difensori centrali di una lega"""
    if fbref_df is None or fbref_df.empty or transfermarkt_df is None or transfermarkt_df.empty:
        return None
    
    # Ottieni i nomi dei difensori centrali dal file transfermarkt
    centrebacks_tm = transfermarkt_df[
        transfermarkt_df['Position'].str.lower().isin(['centre-back', 'center-back'])
    ]['Name'].tolist()
    
    # Filtra i dati FBRef per includere solo i difensori centrali identificati in transfermarkt
    centrebacks = fbref_df[fbref_df['Jugador'].isin(centrebacks_tm)].copy()
    
    if centrebacks.empty:
        print(f"Nessun difensore centrale trovato in {league_name}")
        return None
    
    kpi_ranges, guardian_kpis, distributor_kpis, enforcer_kpis = calculate_global_ranges(fbref_df)
    league_weight = LEAGUE_WEIGHTS.get(league_name, 1.0)
    ratings = []
    
    for _, player in centrebacks.iterrows():
        # Trova il nome corrispondente in transfermarkt per assicurarsi che sia un difensore centrale
        tm_player = transfermarkt_df[transfermarkt_df['Name'] == player['Jugador']]
        if not tm_player.empty and tm_player.iloc[0]['Position'].lower() in ['centre-back', 'center-back']:
            rating = calculate_centreback_rating(
                player, kpi_ranges, guardian_kpis, distributor_kpis, enforcer_kpis, league_weight
            )
            ratings.append({
                'Player': player['Jugador'],
                'Team': player['Team'],
                'League': league_name,
                'Guardian': rating['Guardian'],
                'Deep_Distributor': rating['Deep_Distributor'],
                'Enforcer': rating['Enforcer']
            })
    
    if not ratings:
        print(f"Nessun difensore centrale valido trovato in {league_name}")
        return None
        
    return pd.DataFrame(ratings)

def main():
    """Funzione principale per analizzare tutte le leghe e generare il CSV"""
    league_paths = get_league_paths()
    all_ratings = []
    
    for league_name, league_path in league_paths.items():
        print(f"\nAnalizzando {league_name}...")
        if not league_path.exists():
            print(f"Directory {league_path} non trovata")
            continue
            
        fbref_df, transfermarkt_df = load_league_data(league_path)
        if fbref_df is None or transfermarkt_df is None:
            continue
            
        ratings = get_centreback_ratings(fbref_df, transfermarkt_df, league_name)
        if ratings is not None:
            all_ratings.append(ratings)
            print(f"Analizzati {len(ratings)} difensori centrali in {league_name}")
    
    if all_ratings:
        final_ratings = pd.concat(all_ratings, ignore_index=True)
        
        # Salva i risultati
        final_ratings.to_csv('centreback_ratings.csv', index=False)
        print("\nAnalisi completata. I risultati sono stati salvati in 'centreback_ratings.csv'")
    else:
        print("Nessun dato trovato per l'analisi")

if __name__ == "__main__":
    main() 