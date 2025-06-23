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

def get_serie_a_teams(data_dir):
    """Ottiene tutte le squadre della Serie A."""
    teams = []
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith('.csv') and not '_transfermarkt' in file and not 'clasificacion' in file:
                team_name = file.replace('.csv', '')
                teams.append(team_name)
    return teams

# Dizionari per tenere traccia dei pattern
pattern_counts = defaultdict(int)
name_examples = defaultdict(list)
all_differences = []

# Analizza la Serie A
print("\nAnalizzando la Serie A...")
serie_a_path = os.path.join("pages", "data_serie_a_24-25")

if not os.path.exists(serie_a_path):
    print(f"Directory Serie A non trovata: {serie_a_path}")
else:
    teams = get_serie_a_teams(serie_a_path)
    print(f"Trovate {len(teams)} squadre nella Serie A")
    
    for team in teams:
        # Costruisci i percorsi dei file
        fbref_path = os.path.join(serie_a_path, f"{team}.csv")
        transfermarkt_path = os.path.join(serie_a_path, f"{team}_transfermarkt.csv")
        
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
                                'Team': team
                            }
                            name_examples[pattern].append(example)
                            all_differences.append(example)
                    else:
                        print("Nessun pattern trovato")
                        
        except Exception as e:
            print(f"Errore nell'analisi di {team}: {str(e)}")

# Crea il report
print("\nAnalisi dei pattern nei nomi dei giocatori della Serie A")
print("=" * 80)
print(f"\nTotale differenze trovate: {sum(pattern_counts.values())}")
print("\nPattern più comuni:")
for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"\n{pattern}: {count} occorrenze")
    print("Esempi:")
    for example in name_examples[pattern]:
        print(f"  - {example['Team']}")
        print(f"    FBRef: {example['FBRef']}")
        print(f"    Transfermarkt: {example['Transfermarkt']}")

# Salva i risultati in un file CSV
if all_differences:
    df = pd.DataFrame(all_differences)
    df.to_csv("serie_a_name_patterns_analysis.csv", index=False)
    print(f"\nAnalisi dettagliata salvata in serie_a_name_patterns_analysis.csv") 