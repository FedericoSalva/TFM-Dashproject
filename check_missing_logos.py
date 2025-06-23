import pandas as pd
import os
from collections import defaultdict

# Percorso base
BASE_PATH = "/Users/federico/dash_project"

# File di dati da analizzare
data_files = [
    'goalkeeper_ratings_complete_en.csv',
    'striker_ratings_complete_en.csv',
    'winger_ratings_complete_en.csv',
    'attacking_midfielder_ratings_complete_en.csv',
    'midfielder_ratings_complete_en.csv',
    'fullback_ratings_complete_en.csv',
    'centreback_ratings_complete_en.csv'
]

# Mappatura leghe -> cartelle
league_mapping = {
    'Serie_A': 'Serie_A/2024-2025',
    'EPL': 'EPL',
    'La_Liga': 'La_Liga',
    'Bundesliga': 'Bundesliga',
    'Ligue_1': 'Ligue_1',
    'Primeira_Liga': 'Primeira_Liga',
    'Eredivisie': 'Eredivisie',
    'Championship': 'Championship',
    'Süper_Lig': 'Süper_Lig',
    'MLS': 'MLS',
    'Bundesliga_2': 'Bundesliga_2',
    'Ligue_2': 'Ligue_2',
    'Serie_B': 'Serie_B',
    'Liga_Argentina': 'Liga_Argentina',
    'Jupiler_Pro_League': 'Jupiler_Pro_League',
    'Brazilian_Série_A': 'Brazilian_Série_A'
}

def get_existing_logos():
    """Ottiene la lista dei loghi esistenti"""
    existing_logos = defaultdict(set)
    
    for league, folder in league_mapping.items():
        logo_path = os.path.join(BASE_PATH, 'assets', folder)
        if os.path.exists(logo_path):
            for file in os.listdir(logo_path):
                if file.endswith('.png'):
                    team_name = file.replace('.png', '')
                    existing_logos[league].add(team_name)
    
    return existing_logos

def get_teams_from_data():
    """Ottiene le squadre dai file di dati"""
    teams_by_league = defaultdict(set)
    
    for file in data_files:
        file_path = os.path.join(BASE_PATH, file)
        if not os.path.exists(file_path):
            print(f"File non trovato: {file}")
            continue
            
        try:
            # Rileva il separatore
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = f.read(2048)
                if ';' in sample and sample.count(';') > sample.count(','):
                    sep = ';'
                else:
                    sep = ','
            
            df = pd.read_csv(file_path, sep=sep)
            
            # Estrai squadre e leghe
            for _, row in df.iterrows():
                team = row.get('Team', '')
                league = row.get('League', '')
                
                if team and league:
                    teams_by_league[league].add(team)
                    
        except Exception as e:
            print(f"Errore nel leggere {file}: {e}")
    
    return teams_by_league

def find_missing_logos():
    """Trova i loghi mancanti"""
    existing_logos = get_existing_logos()
    teams_from_data = get_teams_from_data()
    
    missing_logos = defaultdict(set)
    
    for league, teams in teams_from_data.items():
        if league in existing_logos:
            existing = existing_logos[league]
            for team in teams:
                # Normalizza il nome della squadra per il confronto
                team_normalized = team.replace(' ', '_').replace('-', '_')
                
                # Controlla se esiste il logo
                if team_normalized not in existing:
                    # Controlla anche variazioni comuni
                    found = False
                    for existing_team in existing:
                        if (team_normalized.lower() in existing_team.lower() or 
                            existing_team.lower() in team_normalized.lower()):
                            found = True
                            break
                    
                    if not found:
                        missing_logos[league].add(team)
        else:
            # Lega non trovata nelle cartelle
            missing_logos[league].update(teams)
    
    return missing_logos

def main():
    print("Analisi dei loghi mancanti...")
    print("=" * 50)
    
    missing_logos = find_missing_logos()
    
    if not missing_logos:
        print("Tutti i loghi sono presenti! 🎉")
        return
    
    print("Loghi mancanti per lega:")
    print()
    
    total_missing = 0
    for league, teams in missing_logos.items():
        if teams:
            print(f"📁 {league}:")
            for team in sorted(teams):
                print(f"   ❌ {team}")
            print(f"   Totale mancanti: {len(teams)}")
            print()
            total_missing += len(teams)
    
    print(f"📊 Totale generale: {total_missing} loghi mancanti")
    
    # Suggerimenti per i percorsi
    print("\n" + "=" * 50)
    print("SUGGERIMENTI PER I PERCORSI:")
    print()
    
    for league, teams in missing_logos.items():
        if teams:
            print(f"Per {league}, aggiungi i seguenti file in assets/{league_mapping.get(league, league)}/:")
            for team in sorted(teams):
                team_filename = team.replace(' ', '_').replace('-', '_') + '.png'
                print(f"   {team_filename}")
            print()

if __name__ == "__main__":
    main() 