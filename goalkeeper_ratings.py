import pandas as pd
import numpy as np
from pathlib import Path
import os

# Pesi delle leghe aggiornati
LEAGUE_WEIGHTS = {
    'Serie_A': 1.4,      # Top 5 (aumentato da 1.3)
    'EPL': 1.4,          # Top 5 (aumentato da 1.3)
    'La_Liga': 1.4,      # Top 5 (aumentato da 1.3)
    'Bundesliga': 1.4,   # Top 5 (aumentato da 1.3)
    'Ligue_1': 1.4,      # Top 5 (aumentato da 1.3)
    'Primeira_Liga': 1.2,  # (aumentato da 1.1)
    'Eredivisie': 1.2,     # (aumentato da 1.1)
    'Süper_Lig': 1.2,     # (aumentato da 1.1)
    'MLS': 1.0,          # (aumentato da 0.9)
    'Championship': 1.0   # (aumentato da 0.9)
}

# Coefficienti per i minuti giocati
MINUTES_COEFFICIENTS = {
    (0, 500): 0.0,      # Sotto 500 minuti: rating 30
    (501, 1000): 0.7,   # 501-1000 minuti: coefficiente 0.7
    (1001, 1500): 0.85, # 1001-1500 minuti: coefficiente 0.85
    (1501, float('inf')): 1.0  # Oltre 1500 minuti: coefficiente 1.0
}

def safe_float_convert(value):
    """
    Converte in modo sicuro un valore in float, gestendo anche i numeri con virgola come separatore delle migliaia
    """
    if pd.isna(value) or value == '':
        return 0.0
    try:
        # Rimuove la virgola se presente e converte in float
        if isinstance(value, str):
            value = value.replace(',', '')
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def get_minutes_coefficient(minutes):
    """
    Restituisce il coefficiente in base ai minuti giocati
    """
    minutes = safe_float_convert(minutes)
    for (min_range, max_range), coefficient in MINUTES_COEFFICIENTS.items():
        if min_range <= minutes <= max_range:
            return coefficient
    return 0.0

def get_league_paths():
    """
    Restituisce i percorsi delle leghe da analizzare
    """
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
    """
    Ottiene i file delle squadre dalla directory della lega
    """
    team_files = []
    for file in league_path.glob('*.csv'):
        if file.name.endswith('_transfermarkt.csv') or file.name.endswith('_wyscout.csv'):
            continue
        if file.name in ['clasificacion.csv', 'marcatori_Serie_A_24-25.csv', 'Serie_A_24-25.csv']:
            continue
            
        # Gestione speciale per Juventus
        if file.name == 'Juventus.csv':
            transfermarkt_file = league_path / 'Juventus FC.csv'
        else:
            transfermarkt_file = league_path / f"{file.stem}_transfermarkt.csv"
            
        if transfermarkt_file.exists():
            team_files.append((file, transfermarkt_file))
    
    return team_files

def load_league_data(league_path):
    """
    Carica i dati della lega da FBRef e Transfermarkt
    """
    try:
        team_files = get_team_files(league_path)
        if not team_files:
            return None, None

        all_fbref_data = []
        all_transfermarkt_data = []

        for fbref_file, transfermarkt_file in team_files:
            # Carica dati FBRef
            fbref_df = pd.read_csv(fbref_file)
            fbref_df['Team'] = fbref_file.stem
            all_fbref_data.append(fbref_df)

            # Carica dati Transfermarkt
            transfermarkt_df = pd.read_csv(transfermarkt_file)
            transfermarkt_df['Team'] = fbref_file.stem
            all_transfermarkt_data.append(transfermarkt_df)

        return pd.concat(all_fbref_data, ignore_index=True), pd.concat(all_transfermarkt_data, ignore_index=True)
    except Exception as e:
        print(f"Errore nel caricamento dei dati: {str(e)}")
        return None, None

def normalize_kpi(value, min_val, max_val):
    """
    Normalizza un KPI nel range 0-1
    """
    if pd.isna(value) or pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)

def calculate_global_ranges(fbref_df):
    """
    Calcola i range globali per la normalizzazione dei KPI
    """
    kpi_ranges = {}
    
    # Dizionario per la conversione dei nomi delle colonne
    column_conversion = {
        'Att_GK': 'Att (GK)',
        'DistProm': 'DistProm.',
        'Mín': 'Mín'
    }
    
    # KPIs per Playmaker Keeper
    playmaker_kpis = {
        'Att (GK)': {'weight': 0.4, 'inverse': False},
        'DistProm.': {'weight': 0.3, 'inverse': False},
        'Mín': {'weight': 0.3, 'inverse': False}
    }
    
    # KPIs per Shot Stopper
    shot_stopper_kpis = {
        'PSxG': {'weight': 0.3, 'inverse': True},
        'PSxG/SoT': {'weight': 0.3, 'inverse': True},
        'PSxG+/-': {'weight': 0.4, 'inverse': True}
    }
    
    # Calcola i range per ogni KPI
    for kpi in list(playmaker_kpis.keys()) + list(shot_stopper_kpis.keys()):
        col_name = column_conversion.get(kpi, kpi)
        if col_name in fbref_df.columns:
            values = fbref_df[col_name].apply(safe_float_convert)
            kpi_ranges[kpi] = {
                'min': values.min(),
                'max': values.max()
            }
    
    return kpi_ranges

def calculate_goalkeeper_rating(player_data, kpi_ranges, league_weight=1.0):
    """
    Calcola i rating del portiere usando i pesi specifici per ogni KPI
    """
    minutes_coefficient = get_minutes_coefficient(player_data['Mín'])
    if minutes_coefficient == 0.0:
        return {
            'Playmaker_Keeper': 30.0,
            'Shot_Stopper': 30.0
        }
    normalized_stats = {}
    for kpi, ranges in kpi_ranges.items():
        value = safe_float_convert(player_data.get(kpi, 0))
        normalized_stats[kpi] = normalize_kpi(value, ranges['min'], ranges['max'])
    playmaker_weights = {
        'Att (GK)': 0.4,
        'DistProm.': 0.3,
        'Mín': 0.3
    }
    playmaker_rating = sum(normalized_stats[kpi] * weight
                          for kpi, weight in playmaker_weights.items()
                          if kpi in normalized_stats)
    shot_stopper_weights = {
        'PSxG': 0.3,
        'PSxG/SoT': 0.3,
        'PSxG+/-': 0.4
    }
    shot_stopper_rating = sum(normalized_stats[kpi] * weight
                             for kpi, weight in shot_stopper_weights.items()
                             if kpi in normalized_stats)
    playmaker_rating = playmaker_rating * minutes_coefficient * league_weight
    shot_stopper_rating = shot_stopper_rating * minutes_coefficient * league_weight
    # Scala più equilibrata (ridotto del 20% invece del 35%)
    playmaker_final = 30 + (playmaker_rating * 0.8 * 69)
    shot_stopper_final = 30 + (shot_stopper_rating * 0.8 * 69)
    playmaker_final = min(99.0, playmaker_final)
    shot_stopper_final = min(99.0, shot_stopper_final)
    return {
        'Playmaker_Keeper': round(playmaker_final, 1),
        'Shot_Stopper': round(shot_stopper_final, 1)
    }

def get_goalkeeper_ratings(fbref_df, transfermarkt_df, league_name):
    """Calcola i rating per tutti i portieri di una lega"""
    if fbref_df is None or fbref_df.empty or transfermarkt_df is None or transfermarkt_df.empty:
        return None
    
    # Ottieni i nomi dei portieri dal file transfermarkt
    goalkeepers_tm = transfermarkt_df[transfermarkt_df['Position'].str.lower() == 'goalkeeper']['Name'].tolist()
    
    # Filtra i dati FBRef per includere solo i portieri identificati in transfermarkt
    goalkeepers = fbref_df[fbref_df['Jugador'].isin(goalkeepers_tm)].copy()
    
    if goalkeepers.empty:
        print(f"Nessun portiere trovato in {league_name}")
        return None
    
    kpi_ranges = calculate_global_ranges(fbref_df)
    league_weight = LEAGUE_WEIGHTS.get(league_name, 1.0)
    ratings = []
    
    for _, player in goalkeepers.iterrows():
        # Trova il nome corrispondente in transfermarkt per assicurarsi che sia un portiere
        tm_player = transfermarkt_df[transfermarkt_df['Name'] == player['Jugador']]
        if not tm_player.empty and tm_player.iloc[0]['Position'].lower() == 'goalkeeper':
            rating = calculate_goalkeeper_rating(player, kpi_ranges, league_weight)
            ratings.append({
                'Player': player['Jugador'],
                'Team': player['Team'],
                'League': league_name,
                'Playmaker_Keeper': rating['Playmaker_Keeper'],
                'Shot_Stopper': rating['Shot_Stopper']
            })
    
    if not ratings:
        print(f"Nessun portiere valido trovato in {league_name}")
        return None
        
    return pd.DataFrame(ratings)

def main():
    """
    Funzione principale per analizzare tutte le leghe
    """
    league_paths = get_league_paths()
    all_ratings = []
    
    for league_name, league_path in league_paths.items():
        print(f"\nAnalizzando {league_name}...")
        
        # Carica i dati della lega
        fbref_df, transfermarkt_df = load_league_data(league_path)
        if fbref_df is None or transfermarkt_df is None:
            print(f"Impossibile caricare i dati per {league_name}")
            continue
        
        # Calcola i rating
        ratings = get_goalkeeper_ratings(fbref_df, transfermarkt_df, league_name)
        if ratings is not None:
            all_ratings.append(ratings)
            print(f"Analizzati {len(ratings)} portieri in {league_name}")
    
    if all_ratings:
        final_ratings = pd.concat(all_ratings, ignore_index=True)
        # Ordina per Playmaker_Keeper decrescente
        final_ratings = final_ratings.sort_values('Playmaker_Keeper', ascending=False)
        final_ratings.to_csv('goalkeeper_ratings.csv', index=False)
        print("\nAnalisi completata. I risultati sono stati salvati in 'goalkeeper_ratings.csv'")
        print(f"Analizzati {len(final_ratings)} portieri in totale")
        print("\nTop 20 portieri per rating Playmaker_Keeper:")
        print(final_ratings[['Player', 'Team', 'League', 'Playmaker_Keeper', 'Shot_Stopper']].head(20).to_string())
        print("\nTop 20 portieri per rating Shot_Stopper:")
        shot_stopper_ratings = final_ratings.sort_values('Shot_Stopper', ascending=False)
        print(shot_stopper_ratings[['Player', 'Team', 'League', 'Playmaker_Keeper', 'Shot_Stopper']].head(20).to_string())
    else:
        print("Nessun dato trovato per l'analisi")

if __name__ == "__main__":
    main() 