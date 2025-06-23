import pandas as pd
import os

def load_player_data(player_name):
    """Carica tutti i dati disponibili per un giocatore specifico."""
    base_path = "pages"
    leagues = ["Serie_A", "EPL", "La_Liga", "Bundesliga", "Ligue_1", "Primeira_Liga", "Eredivisie"]
    
    player_data = []
    
    def process_league_data(league_path, league_name):
        if not os.path.exists(league_path):
            return
            
        for file in os.listdir(league_path):
            team_name = file.replace('.csv', '')
            
            # FBRef data
            if file.endswith('.csv') and not '_transfermarkt' in file:
                try:
                    df = pd.read_csv(os.path.join(league_path, file))
                    if 'Jugador' in df.columns:
                        player_rows = df[df['Jugador'].str.contains(player_name, case=False, na=False)]
                        if not player_rows.empty:
                            for _, row in player_rows.iterrows():
                                player_data.append({
                                    'Source': 'FBRef',
                                    'Team': team_name,
                                    'League': league_name,
                                    'Data': row.to_dict()
                                })
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    
            # Transfermarkt data
            tm_file = f"{team_name}_transfermarkt.csv"
            if tm_file in os.listdir(league_path):
                try:
                    df = pd.read_csv(os.path.join(league_path, tm_file))
                    if 'Name' in df.columns:
                        player_rows = df[df['Name'].str.contains(player_name, case=False, na=False)]
                        if not player_rows.empty:
                            for _, row in player_rows.iterrows():
                                player_data.append({
                                    'Source': 'Transfermarkt',
                                    'Team': team_name,
                                    'League': league_name,
                                    'Data': row.to_dict()
                                })
                except Exception as e:
                    print(f"Error reading {tm_file}: {e}")
                    
            # Capology data
            capology_path = os.path.join(base_path, "Salari_Capology", league_name.replace('_', ' '), team_name)
            if os.path.exists(capology_path):
                cap_file = f"Tabla_Limpia_{team_name}.csv"
                if cap_file in os.listdir(capology_path):
                    try:
                        df = pd.read_csv(os.path.join(capology_path, cap_file))
                        if 'Jugador' in df.columns:
                            player_rows = df[df['Jugador'].str.contains(player_name, case=False, na=False)]
                            if not player_rows.empty:
                                for _, row in player_rows.iterrows():
                                    player_data.append({
                                        'Source': 'Capology',
                                        'Team': team_name,
                                        'League': league_name,
                                        'Data': row.to_dict()
                                    })
                    except Exception as e:
                        print(f"Error reading {cap_file}: {e}")
    
    # Process Serie A separately
    serie_a_path = os.path.join(base_path, "data_serie_a_24-25")
    process_league_data(serie_a_path, "Serie A")
    
    # Process other leagues
    for league in leagues[1:]:
        league_path = os.path.join(base_path, league, f"data_{league.lower()}_24-25")
        process_league_data(league_path, league.replace('_', ' '))
    
    return player_data

def print_player_analysis(player_name):
    """Stampa l'analisi dettagliata dei dati di un giocatore."""
    print(f"\nAnalisi dati per {player_name}")
    print("=" * 100)
    
    data = load_player_data(player_name)
    
    if not data:
        print(f"Nessun dato trovato per {player_name}")
        return
        
    for entry in data:
        print(f"\nFonte: {entry['Source']}")
        print(f"Squadra: {entry['Team']}")
        print(f"Lega: {entry['League']}")
        print("\nDati disponibili:")
        for key, value in entry['Data'].items():
            if pd.notna(value):  # Mostra solo i valori non-NaN
                print(f"  {key}: {value}")
        print("-" * 100)

if __name__ == "__main__":
    # Analizza i dati di Kvaratskhelia
    print_player_analysis("Kvaratskhelia") 
