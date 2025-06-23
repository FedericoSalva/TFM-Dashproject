import pandas as pd
import os
import numpy as np

def load_team_data(league_path, team_file):
    """Carica i dati di una squadra da un file CSV."""
    try:
        df = pd.read_csv(os.path.join(league_path, team_file))
        if 'Jugador' in df.columns:
            # Filtra i valori NaN e converte in stringa
            return [str(player) for player in df['Jugador'].dropna()]
        return []
    except:
        return []

def analyze_duplicates():
    base_path = "pages"
    leagues = ["Serie_A", "EPL", "La_Liga", "Bundesliga", "Ligue_1", "Primeira_Liga", "Eredivisie"]
    
    # Dizionario per tenere traccia di tutti i giocatori e le loro squadre
    player_teams = {}
    
    # Analizza Serie A separatamente
    serie_a_path = os.path.join(base_path, "data_serie_a_24-25")
    if os.path.exists(serie_a_path):
        for file in os.listdir(serie_a_path):
            if file.endswith('.csv') and not '_transfermarkt' in file:
                team_name = file.replace('.csv', '')
                players = load_team_data(serie_a_path, file)
                for player in players:
                    if player and player.lower() != 'nan' and player.lower() != 'jugador':
                        if player not in player_teams:
                            player_teams[player] = {'teams': set(), 'leagues': set()}
                        player_teams[player]['teams'].add(team_name)
                        player_teams[player]['leagues'].add('Serie A')
    
    # Analizza le altre leghe
    for league in leagues[1:]:  # Skip Serie A as it's already processed
        league_path = os.path.join(base_path, league, f"data_{league.lower()}_24-25")
        if os.path.exists(league_path):
            for file in os.listdir(league_path):
                if file.endswith('.csv') and not '_transfermarkt' in file:
                    team_name = file.replace('.csv', '')
                    players = load_team_data(league_path, file)
                    for player in players:
                        if player and player.lower() != 'nan' and player.lower() != 'jugador':
                            if player not in player_teams:
                                player_teams[player] = {'teams': set(), 'leagues': set()}
                            player_teams[player]['teams'].add(team_name)
                            player_teams[player]['leagues'].add(league.replace('_', ' '))
    
    # Trova i duplicati
    duplicates = {player: info for player, info in player_teams.items() 
                 if len(info['teams']) > 1}
    
    print(f"\nTotale giocatori duplicati: {len(duplicates)}")
    print("\nDettaglio dei giocatori duplicati:")
    print("=" * 100)
    
    # Ordina i duplicati per numero di squadre (decrescente) e poi per nome
    sorted_duplicates = sorted(duplicates.items(), 
                             key=lambda x: (-len(x[1]['teams']), x[0]))
    
    for player, info in sorted_duplicates:
        print(f"Giocatore: {player}")
        print(f"Numero di squadre: {len(info['teams'])}")
        print(f"Squadre: {', '.join(sorted(info['teams']))}")
        print(f"Leghe: {', '.join(sorted(info['leagues']))}")
        print("-" * 100)

if __name__ == "__main__":
    analyze_duplicates() 