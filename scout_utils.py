import pandas as pd
import os
from pages.Scout_Analysis.scout_analysis import TEAM_LOGO_MAPPING, LEAGUE_FOLDER_MAPPING

# Percorso base del progetto
BASE_PATH = "/Users/federico/dash_project"

PROFILES_TO_COMPARE = [
    # Strikers
    "Falso_Nueve", "Aerial_Dominator", "Lethal_Striker",
    # Wingers
    "Key_Passer", "Creative_Winger",
    # Attacking Midfielders
    "Diez", "Space_Invader",
    # Midfielders
    "Pivot_Master", "Maestro", "Box_to_Box",
    # Fullbacks
    "Sentinel_Fullback", "Advanced_Wingback", "Overlapping_Runner",
    # Centrebacks
    "Guardian", "Deep_Distributor", "Enforcer",
    # Goalkeepers
    "Playmaker_Keeper", "Shot_Stopper"
]

def get_team_logo_path(team, league):
    """Get team logo path using the mappings from scout_analysis"""
    if pd.isna(team) or pd.isna(league):
        return "/assets/default_team.png"
    
    team_clean = team.replace(' ', '_')
    league_clean = league.replace(' ', '_')
    
    logo_filename = TEAM_LOGO_MAPPING.get(team_clean, team_clean)
    league_folder = LEAGUE_FOLDER_MAPPING.get(league_clean, league_clean)
    team_logo_path = f"/assets/{league_folder}/{logo_filename}.png"
    
    return team_logo_path

def load_all_player_data_for_dropdown():
    """Carica tutti i nomi dei giocatori dai file di rating per i menu a tendina."""
    data_files = [
        'goalkeeper_ratings_complete_en.csv', 'striker_ratings_complete_en.csv',
        'winger_ratings_complete_en.csv', 'attacking_midfielder_ratings_complete_en.csv',
        'midfielder_ratings_complete_en.csv', 'fullback_ratings_complete_en.csv',
        'centreback_ratings_complete_en.csv'
    ]
    
    all_players = []
    for file in data_files:
        file_path = os.path.join(BASE_PATH, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = f.read(2048)
                sep = ';' if ';' in sample and sample.count(';') > sample.count(',') else ','
            
            df = pd.read_csv(file_path, sep=sep, usecols=['Player'])
            all_players.extend(df['Player'].dropna().unique())
        except Exception as e:
            print(f"Error loading {file}: {e}")
            
    return [{'label': name, 'value': name} for name in sorted(list(set(all_players)))]

def load_profiles_by_position():
    """Carica e raggruppa i profili per ruolo dal CSV."""
    profiles_path = os.path.join(BASE_PATH, 'pages/Scout_Analysis/profili_scout_analysis_finale_corretti.csv')
    try:
        df = pd.read_csv(profiles_path, sep=';')
        df.columns = [col.strip() for col in df.columns]
        df['RUOLO'] = df['RUOLO'].ffill()
        
        profiles = {}
        for role, group in df.groupby('RUOLO'):
            profiles[role.strip()] = group['PROFILO'].dropna().unique().tolist()
        
        return {k: v for k, v in profiles.items() if v and k != 'BONUS'}
    except Exception as e:
        print(f"Error loading profiles: {e}")
        return {}

def get_player_data(player_name, role_file_name=None):
    """Carica i dati completi di un giocatore, cercando in un file specifico se fornito."""
    data_files = [
        'goalkeeper_ratings_complete_en.csv', 'striker_ratings_complete_en.csv',
        'winger_ratings_complete_en.csv', 'attacking_midfielder_ratings_complete_en.csv',
        'midfielder_ratings_complete_en.csv', 'fullback_ratings_complete_en.csv',
        'centreback_ratings_complete_en.csv'
    ]
    
    files_to_search = [os.path.join(BASE_PATH, role_file_name)] if role_file_name else [os.path.join(BASE_PATH, f) for f in data_files]
    
    for file_path in files_to_search:
        try:
            if not os.path.exists(file_path): continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = f.read(2048)
                sep = ';' if ';' in sample and sample.count(';') > sample.count(',') else ','
            
            df = pd.read_csv(file_path, sep=sep)
            player_data = df[df['Player'] == player_name]
            
            if not player_data.empty:
                return player_data.iloc[0]
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    return None

def get_player_info(player_name):
    """Trova un giocatore e restituisce i suoi dati e il nome del suo ruolo."""
    position_map = {
        'goalkeeper': 'GOALKEEPER', 'centreback': 'CENTRE BACK', 'fullback': 'FULLBACK',
        'midfielder': 'MIDFIELDER', 'attacking_midfielder': 'ATTACKING MIDFIELDER',
        'winger': 'WINGER', 'striker': 'STRIKER'
    }
    
    for position_key, role_name in position_map.items():
        file_name = f'{position_key}_ratings_complete_en.csv'
        player_data = get_player_data(player_name, file_name)
        if player_data is not None:
            return role_name, player_data
            
    return None, None 