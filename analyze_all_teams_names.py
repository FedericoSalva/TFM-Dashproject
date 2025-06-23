import pandas as pd
import os
from utils.name_analysis import analyze_name_differences, print_unmatched_analysis, suggest_name_fixes

def get_league_teams(league_path):
    """Ottiene tutte le squadre in una lega."""
    teams = []
    if os.path.exists(league_path):
        for file in os.listdir(league_path):
            if file.endswith('.csv') and not '_transfermarkt' in file and not 'clasificacion' in file:
                team_name = file.replace('.csv', '')
                teams.append(team_name)
    return teams

# Definisci le leghe da analizzare
LEAGUES = {
    "Serie_A": "data_serie_a_24-25",
    "EPL": "data_epl_24-25",
    "La_Liga": "data_la_liga_24-25",
    "Bundesliga": "data_bundesliga_24-25",
    "Ligue_1": "data_ligue_1_24-25",
    "Primeira_Liga": "data_primeira_liga_24-25",
    "Eredivisie": "data_eredivisie_24-25"
}

all_differences = []

# Analizza ogni lega
for league, data_dir in LEAGUES.items():
    print(f"\nAnalizzando {league}...")
    print("=" * 80)
    
    # Gestisci il percorso speciale per la Serie A
    if league == "Serie_A":
        league_path = os.path.join("pages", data_dir)
    else:
        league_path = os.path.join("pages", league, data_dir)
    
    teams = get_league_teams(league_path)
    
    for team in teams:
        print(f"\nAnalizzando {team}...")
        print("-" * 40)
        
        # Costruisci i percorsi dei file
        fbref_path = os.path.join(league_path, f"{team}.csv")
        transfermarkt_path = os.path.join(league_path, f"{team}_transfermarkt.csv")
        
        # Verifica che entrambi i file esistano
        if not os.path.exists(fbref_path) or not os.path.exists(transfermarkt_path):
            print(f"File mancanti per {team}")
            continue
            
        try:
            # Carica i dati
            fbref_df = pd.read_csv(fbref_path)
            transfermarkt_df = pd.read_csv(transfermarkt_path)
            
            # Analizza le differenze
            diff_df = analyze_name_differences(fbref_df, transfermarkt_df)
            unmatched = diff_df[~diff_df['Match']]
            
            if not unmatched.empty:
                print(f"Trovati {len(unmatched)} giocatori non matchati in {team}")
                
                # Aggiungi informazioni sulla lega e squadra
                unmatched['League'] = league
                unmatched['Team'] = team
                all_differences.append(unmatched)
                
                # Stampa i dettagli
                for _, row in unmatched.iterrows():
                    print(f"\nNome Standardizzato: {row['Nome_Standardizzato']}")
                    print(f"FBRef: {row['Nome_FBRef']}")
                    print(f"Transfermarkt: {row['Nome_Transfermarkt']}")
                    
        except Exception as e:
            print(f"Errore nell'analisi di {team}: {str(e)}")

# Combina tutti i risultati
if all_differences:
    final_df = pd.concat(all_differences, ignore_index=True)
    
    # Salva i risultati in un file CSV
    output_file = "name_differences_analysis.csv"
    final_df.to_csv(output_file, index=False)
    print(f"\nAnalisi completa salvata in {output_file}")
    
    # Stampa statistiche finali
    print("\nStatistiche finali:")
    print("-" * 40)
    print(f"Totale giocatori non matchati: {len(final_df)}")
    print("\nGiocatori non matchati per lega:")
    print(final_df['League'].value_counts())
    
    # Trova i pattern più comuni di mismatch
    print("\nSquadre con più problemi di matching:")
    print(final_df.groupby(['League', 'Team']).size().sort_values(ascending=False).head(10))
else:
    print("Nessuna differenza trovata nell'analisi") 