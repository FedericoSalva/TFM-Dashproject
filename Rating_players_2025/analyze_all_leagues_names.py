import pandas as pd
import os
from collections import defaultdict
from utils.name_analysis import analyze_name_differences

def analyze_name_patterns(fbref_name, transfermarkt_name):
    """Analizza i pattern di differenze tra i nomi."""
    if fbref_name == "NON TROVATO" or transfermarkt_name == "NON TROVATO":
        return None
        
    # Converti entrambi i nomi in lowercase per il confronto
    fbref_lower = fbref_name.lower()
    transfermarkt_lower = transfermarkt_name.lower()
    
    patterns = []
    
    # Controlla inversione nome/cognome
    fbref_parts = fbref_lower.split()
    transfermarkt_parts = transfermarkt_lower.split()
    
    if set(fbref_parts) == set(transfermarkt_parts) and fbref_parts != transfermarkt_parts:
        patterns.append("Inversione nome/cognome")
    
    # Controlla accenti
    if any(c != d for c, d in zip(fbref_lower, transfermarkt_lower) if c.isalpha() and d.isalpha()):
        patterns.append("Differenze negli accenti")
    
    # Controlla iniziali vs nome completo
    if any(len(part) == 1 for part in fbref_parts) != any(len(part) == 1 for part in transfermarkt_parts):
        patterns.append("Iniziali vs nome completo")
    
    # Controlla presenza di trattini
    if ("-" in fbref_name) != ("-" in transfermarkt_name):
        patterns.append("Differenze nei trattini")
    
    # Controlla numero di parti del nome
    if len(fbref_parts) != len(transfermarkt_parts):
        patterns.append("Numero diverso di parti del nome")
    
    # Se non troviamo pattern specifici ma i nomi sono diversi
    if not patterns and fbref_lower != transfermarkt_lower:
        patterns.append("Altre differenze")
    
    return ", ".join(patterns) if patterns else None

def get_teams(league_path):
    """Ottiene tutte le squadre in una lega."""
    teams = []
    if os.path.exists(league_path):
        for file in os.listdir(league_path):
            if file.endswith('.csv') and not '_transfermarkt' in file and not 'clasificacion' in file:
                team_name = file.replace('.csv', '')
                teams.append(team_name)
    return teams

# Definisci le leghe da analizzare con i loro percorsi
LEAGUES = {
    "Bundesliga": "data_bundesliga_24-25",
    "Championship": "data_championship_24-25",
    "EPL": "data_epl_24-25",
    "Eredivisie": "data_eredivisie_24-25",
    "La_Liga": "data_la_liga_24-25",
    "Ligue_1": "data_ligue_1_24-25",
    "MLS": "data_mls_24-25",
    "Primeira_Liga": "data_primeira_liga_24-25",
    "Serie_A": "data_serie_a_24-25",
    "Super_Lig": "data_super_lig_24-25"
}

# Dizionari per tenere traccia dei pattern
pattern_counts = defaultdict(int)
name_examples = defaultdict(list)
all_differences = []

# Analizza ogni lega
for league, data_dir in LEAGUES.items():
    print(f"\nAnalizzando {league}...")
    
    # Gestisci il percorso speciale per la Serie A
    if league == "Serie_A":
        league_path = os.path.join("pages", data_dir)
    else:
        league_path = os.path.join("pages", league, data_dir)
    
    if not os.path.exists(league_path):
        print(f"Directory non trovata: {league_path}")
        continue
        
    teams = get_teams(league_path)
    print(f"Trovate {len(teams)} squadre in {league}")
    
    for team in teams:
        # Costruisci i percorsi dei file
        fbref_path = os.path.join(league_path, f"{team}.csv")
        transfermarkt_path = os.path.join(league_path, f"{team}_transfermarkt.csv")
        
        if not os.path.exists(fbref_path):
            print(f"File FBRef mancante per {team}")
            continue
        if not os.path.exists(transfermarkt_path):
            print(f"File Transfermarkt mancante per {team}")
            continue
            
        try:
            # Carica i dati
            fbref_df = pd.read_csv(fbref_path)
            transfermarkt_df = pd.read_csv(transfermarkt_path)
            
            print(f"\nAnalizzando {team}...")
            print(f"Giocatori in FBRef: {len(fbref_df)}")
            print(f"Giocatori in Transfermarkt: {len(transfermarkt_df)}")
            
            # Analizza le differenze
            diff_df = analyze_name_differences(fbref_df, transfermarkt_df)
            unmatched = diff_df[~diff_df['Match']]
            
            print(f"Giocatori non matchati: {len(unmatched)}")
            
            for _, row in unmatched.iterrows():
                if row['Nome_FBRef'] != "NON TROVATO" and row['Nome_Transfermarkt'] != "NON TROVATO":
                    print(f"\nConfrontando:")
                    print(f"FBRef: {row['Nome_FBRef']}")
                    print(f"Transfermarkt: {row['Nome_Transfermarkt']}")
                    
                    pattern = analyze_name_patterns(row['Nome_FBRef'], row['Nome_Transfermarkt'])
                    if pattern:
                        print(f"Pattern trovato: {pattern}")
                        pattern_counts[pattern] += 1
                        
                        # Salva un esempio per ogni pattern (massimo 3 esempi per pattern)
                        if len(name_examples[pattern]) < 3:
                            example = {
                                'Pattern': pattern,
                                'FBRef': row['Nome_FBRef'],
                                'Transfermarkt': row['Nome_Transfermarkt'],
                                'League': league,
                                'Team': team
                            }
                            name_examples[pattern].append(example)
                            all_differences.append(example)
                    else:
                        print("Nessun pattern trovato")
                        
        except Exception as e:
            print(f"Errore nell'analisi di {team}: {str(e)}")

# Crea il report
print("\nAnalisi dei pattern nei nomi dei giocatori")
print("=" * 80)
print(f"\nTotale differenze trovate: {sum(pattern_counts.values())}")
print("\nPattern più comuni:")
for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"\n{pattern}: {count} occorrenze")
    print("Esempi:")
    for example in name_examples[pattern]:
        print(f"  - {example['League']}, {example['Team']}")
        print(f"    FBRef: {example['FBRef']}")
        print(f"    Transfermarkt: {example['Transfermarkt']}")

# Salva i risultati in un file CSV
if all_differences:
    df = pd.DataFrame(all_differences)
    df.to_csv("all_leagues_name_patterns_analysis.csv", index=False)
    print(f"\nAnalisi dettagliata salvata in all_leagues_name_patterns_analysis.csv") 
