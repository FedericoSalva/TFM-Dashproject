import os

# Base path per i dati
BASE_PATH = "/Users/federico/dash_project/pages"

# Configurazione dei percorsi delle leghe
LEAGUE_PATHS = {
    "Serie_A": "data_serie_a_24-25",
    "EPL": "EPL/data_EPL_24-25",
    "La_Liga": "La_Liga/data_La_Liga_24-25",
    "Bundesliga": "Bundesliga/data_Bundesliga_24-25",
    "Ligue_1": "Ligue_1/data_Ligue_1_24-25",
    "Primeira_Liga": "Primeira_Liga/data_Primeira_Liga_24-25",
    "Eredivisie": "Eredivisie/data_Eredivisie_24-25",
    "Championship": "Championship/data_Championship_24-25",
    "Süper_Lig": "Süper_Lig/data_Süper_Lig_24-25",
    "MLS": "MLS/data_MLS_24"
}

# Mapping dei nomi delle squadre per gestire casi speciali
TEAM_NAME_MAPPING = {
    # Serie A
    "Juventus": "Juventus FC",
    "Inter": "Internazionale",
    
    # EPL
    "Manchester United": "Manchester_United",
    "Manchester City": "Manchester_City",
    "Brighton & Hove Albion": "Brighton_and_Hove_Albion",
    
    # La Liga
    "Real Madrid": "Real_Madrid",
    "Barcelona": "Barcelona",
    "Villarreal": "Villareal"  # Gestisce un typo nei file
}

# Casi speciali per i file
SPECIAL_FILE_CASES = {
    "Osasuna": "Osasuna_transfemarkt.csv",  # Gestisce un typo
    "Juventus": "Juventus FC.csv",  # Caso speciale per FBRef
}

def get_league_data_path(league: str) -> str:
    """Restituisce il percorso corretto della directory dei dati per una lega."""
    if league not in LEAGUE_PATHS:
        print(f"Warning: Lega sconosciuta {league}")
        return os.path.join(BASE_PATH, f"{league}/data_{league.upper()}_24-25")
    return os.path.join(BASE_PATH, LEAGUE_PATHS[league])

def get_team_name(team: str) -> str:
    """Restituisce il nome standardizzato della squadra."""
    return TEAM_NAME_MAPPING.get(team, team.replace(" ", "_"))

def get_fbref_path(league: str, team: str) -> str:
    """Restituisce il percorso corretto per il file FBRef di una squadra."""
    base_dir = get_league_data_path(league)
    team_name = get_team_name(team)
    
    # Controlla prima i casi speciali
    if team in SPECIAL_FILE_CASES:
        file_path = os.path.join(base_dir, SPECIAL_FILE_CASES[team])
        if os.path.exists(file_path):
            return file_path
    
    # Prova il pattern standard
    file_path = os.path.join(base_dir, f"{team_name}.csv")
    return file_path

def get_transfermarkt_path(league: str, team: str) -> str:
    """Restituisce il percorso corretto per il file Transfermarkt di una squadra."""
    base_dir = get_league_data_path(league)
    team_name = get_team_name(team)
    
    # Lista di possibili pattern di file da provare
    patterns = [
        "{team}_transfermarkt.csv",
        "{team}_transfemarkt.csv",  # Gestisce un typo
        "{team}_trasnfermarkt.csv"  # Gestisce un altro typo
    ]
    
    # Prova ogni pattern
    for pattern in patterns:
        file_path = os.path.join(base_dir, pattern.format(team=team_name))
        if os.path.exists(file_path):
            return file_path
    
    # Se non viene trovato alcun file, restituisci il percorso standard
    return os.path.join(base_dir, f"{team_name}_transfermarkt.csv")

def test_paths():
    """Funzione di test per verificare la generazione dei percorsi."""
    # Casi di test
    test_cases = [
        # Casi Serie A
        ("Serie_A", "Juventus"),
        ("Serie_A", "Inter"),
        ("Serie_A", "Milan"),
        
        # Casi EPL
        ("EPL", "Manchester United"),
        ("EPL", "Manchester City"),
        ("EPL", "Brighton & Hove Albion"),
        
        # Casi La Liga
        ("La_Liga", "Real Madrid"),
        ("La_Liga", "Barcelona"),
        ("La_Liga", "Osasuna"),
        ("La_Liga", "Villarreal")
    ]
    
    print("=== Test Generazione Percorsi ===")
    for league, team in test_cases:
        print(f"\nTest {team} in {league}:")
        
        # Test percorso lega
        league_path = get_league_data_path(league)
        print(f"Percorso lega: {league_path}")
        print(f"Esiste: {os.path.exists(league_path)}")
        
        # Test file FBRef
        fbref_path = get_fbref_path(league, team)
        print(f"Percorso FBRef: {fbref_path}")
        print(f"Esiste: {os.path.exists(fbref_path)}")
        
        # Test file Transfermarkt
        transfermarkt_path = get_transfermarkt_path(league, team)
        print(f"Percorso Transfermarkt: {transfermarkt_path}")
        print(f"Esiste: {os.path.exists(transfermarkt_path)}")

if __name__ == "__main__":
    test_paths() 