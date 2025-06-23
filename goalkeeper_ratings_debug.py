import pandas as pd
import numpy as np
from pathlib import Path

# Costanti
LEAGUE_WEIGHT = 2.0  # Serie A
MINUTES_THRESHOLD = 500
MINUTES_COEFFICIENTS = {
    (0, 500): 0,  # rating = 40
    (500, 1000): 0.7,
    (1000, 1600): 0.85,
    (1600, float('inf')): 1.0
}

def get_minutes_coefficient(minutes):
    """Restituisce il coefficiente in base ai minuti giocati"""
    if minutes < MINUTES_THRESHOLD:
        return 0  # rating = 40
    for (min_start, min_end), coeff in MINUTES_COEFFICIENTS.items():
        if min_start <= minutes < min_end:
            return coeff
    return 0

def normalize_rating(rating, min_rating=40, max_rating=99):
    """Normalizza il rating tra min_rating e max_rating"""
    return min_rating + (max_rating - min_rating) * (rating / 100)

def get_all_serie_a_goalkeepers():
    """Trova tutti i portieri della Serie A dai file Transfermarkt"""
    goalkeepers = {}
    data_dir = Path("pages/data_serie_a_24-25")
    
    for file in data_dir.glob("*_transfermarkt.csv"):
        team = file.stem.replace("_transfermarkt", "")
        print(f"\nProcessando {team}...")
        df = pd.read_csv(file)
        print("Colonne disponibili:", df.columns.tolist())
        print("Prime righe del file:")
        print(df.head())
        
        # Ora ripristiniamo il codice per i portieri
        gk_df = df[df['Position'] == 'Goalkeeper']
        print(f"Portieri trovati in {team}:", len(gk_df))
        for _, gk in gk_df.iterrows():
            goalkeepers[gk['Name']] = team
            print(f"Aggiunto portiere: {gk['Name']} ({team})")
            
    print("\nTotale portieri trovati:", len(goalkeepers))
    return goalkeepers

def calculate_goalkeeper_ratings():
    """Calcola i rating per tutti i portieri della Serie A"""
    goalkeepers = get_all_serie_a_goalkeepers()
    ratings = []
    
    for gk_name, team in goalkeepers.items():
        # Carica i dati FBref del portiere
        fbref_file = f"pages/data_serie_a_24-25/{team}.csv"
        if not Path(fbref_file).exists():
            continue
            
        df = pd.read_csv(fbref_file, decimal=',')
        gk_data = df[df['Jugador'] == gk_name]
        
        if gk_data.empty:
            continue
            
        gk_data = gk_data.iloc[0]
        minutes = float(str(gk_data['Min']).replace(',', ''))
        coeff = get_minutes_coefficient(minutes)
        
        if coeff == 0:
            ratings.append({
                'Player': gk_name,
                'Team': team,
                'Minutes': minutes,
                'Playmaker Rating': 40,
                'Shot-Stopper Rating': 40
            })
            continue
            
        # Calcola rating Playmaker Keeper
        with_ball = {
            'PA': gk_data.get('PA', 0) * 0.09,
            'Att (GK)': gk_data.get('Att (GK)', 0) * 0.08,
            'Long. Prom.': gk_data.get('Long. Prom.', 0) * 0.07,
            '% Cmp': gk_data.get('% Cmp', 0) * 0.06
        }
        
        without_ball = {
            'PSxG+/-': gk_data.get('PSxG+/-', 0) * 0.25,
            'Salvadas': gk_data.get('Salvadas', 0) * 0.18,
            '%Salvadas': gk_data.get('%Salvadas', 0) * 0.17,
            'DistProm': gk_data.get('DistProm', 0) * 0.10
        }
        
        playmaker_base = (sum(with_ball.values()) * 0.3 + sum(without_ball.values()) * 0.7)
        playmaker_rating = normalize_rating(playmaker_base * coeff * LEAGUE_WEIGHT)
        
        # Calcola rating Shot-Stopper
        with_ball = {
            '% Cmp': gk_data.get('% Cmp', 0) * 0.10
        }
        
        without_ball = {
            'PaC%': gk_data.get('PaC%', 0) * 0.36,
            '%Salvadas': gk_data.get('%Salvadas', 0) * 0.27,
            'PSxG+/-': gk_data.get('PSxG+/-', 0) * 0.18,
            'Salvadas': gk_data.get('Salvadas', 0) * 0.09
        }
        
        shotstopper_base = (sum(with_ball.values()) * 0.1 + sum(without_ball.values()) * 0.9)
        shotstopper_rating = normalize_rating(shotstopper_base * coeff * LEAGUE_WEIGHT)
        
        ratings.append({
            'Player': gk_name,
            'Team': team,
            'Minutes': minutes,
            'Playmaker Rating': round(playmaker_rating),
            'Shot-Stopper Rating': round(shotstopper_rating)
        })
    
    # Crea DataFrame e ordina per rating più alto
    ratings_df = pd.DataFrame(ratings)
    playmaker_sorted = ratings_df.sort_values('Playmaker Rating', ascending=False)
    shotstopper_sorted = ratings_df.sort_values('Shot-Stopper Rating', ascending=False)
    
    print("\nPlaymaker Keeper Ratings:")
    print(playmaker_sorted[['Player', 'Team', 'Minutes', 'Playmaker Rating']].head(10))
    print("\nShot-Stopper Ratings:")
    print(shotstopper_sorted[['Player', 'Team', 'Minutes', 'Shot-Stopper Rating']].head(10))

if __name__ == "__main__":
    calculate_goalkeeper_ratings() 