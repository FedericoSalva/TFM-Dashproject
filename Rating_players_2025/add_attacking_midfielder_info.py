import pandas as pd
import numpy as np
from pathlib import Path
import re

def safe_float_convert(value):
    """Converte in modo sicuro un valore in float, gestendo anche i numeri con virgola come separatore delle migliaia"""
    if pd.isna(value) or value == '':
        return 0.0
    try:
        if isinstance(value, str):
            # Rimuove il simbolo dell'euro e le virgole
            value = value.replace('€', '').replace(',', '').strip()
            # Gestisce i valori in milioni (es. "12.00m" -> 12000000)
            if 'm' in value.lower():
                value = float(value.lower().replace('m', '')) * 1000000
            else:
                value = float(value)
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def extract_age(date_of_birth):
    """Estrae l'età dalla stringa 'Date of Birth/Age'"""
    if pd.isna(date_of_birth):
        return np.nan
    try:
        # Cerca il pattern (XX) nella stringa
        match = re.search(r'\((\d+)\)', date_of_birth)
        if match:
            return int(match.group(1))
        return np.nan
    except:
        return np.nan

def get_transfermarkt_data(league_path):
    """Carica e processa i dati Transfermarkt per una lega"""
    all_tm_data = []
    
    for file in league_path.glob('*_transfermarkt.csv'):
        try:
            df = pd.read_csv(file)
            # Filtra solo gli attacking midfielder e central midfielder
            df = df[df['Position'].isin(['Attacking Midfield', 'Central Midfield'])].copy()
            
            # Estrae l'età
            df['Age'] = df['Date of Birth/Age'].apply(extract_age)
            
            # Processa il valore di mercato
            df['Market Value'] = df['Market Value'].apply(safe_float_convert)
            
            # Aggiunge il nome della squadra
            df['Team'] = file.stem.replace('_transfermarkt', '')
            
            all_tm_data.append(df)
        except Exception as e:
            print(f"Errore nel processare {file}: {str(e)}")
    
    if not all_tm_data:
        return None
    
    return pd.concat(all_tm_data, ignore_index=True)

def get_capology_data(league_name):
    """Carica e processa i dati Capology per una lega"""
    base_path = Path('/Users/federico/dash_project/pages/Salari_Capology')
    league_path = base_path / league_name
    
    if not league_path.exists():
        return None
    
    all_capology_data = []
    
    for team_dir in league_path.iterdir():
        if team_dir.is_dir():
            capology_file = team_dir / f"Tabla_Limpia_{team_dir.name}.csv"
            if capology_file.exists():
                try:
                    df = pd.read_csv(capology_file)
                    # Seleziona solo le colonne necessarie
                    df = df[['Jugador', 'Bruto Anual', 'Cláusula De Rescisión']].copy()
                    
                    # Processa i valori numerici
                    df['Bruto Anual'] = df['Bruto Anual'].apply(safe_float_convert)
                    df['Cláusula De Rescisión'] = df['Cláusula De Rescisión'].apply(safe_float_convert)
                    
                    # Applica il salario base dove manca
                    df['Bruto Anual'] = df['Bruto Anual'].fillna(500000)
                    
                    # Aggiunge il nome della squadra
                    df['Team'] = team_dir.name
                    
                    all_capology_data.append(df)
                except Exception as e:
                    print(f"Errore nel processare {capology_file}: {str(e)}")
    
    if not all_capology_data:
        return None
    
    return pd.concat(all_capology_data, ignore_index=True)

def get_league_paths():
    """Restituisce i percorsi delle leghe da analizzare"""
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

def main():
    """Funzione principale per aggiungere i dati al CSV esistente"""
    # Carica il CSV esistente
    try:
        final_ratings = pd.read_csv('attacking_midfielder_ratings.csv')
        print(f"Caricato il file esistente con {len(final_ratings)} attacking midfielder/central midfielder")
    except Exception as e:
        print(f"Errore nel caricare il file esistente: {str(e)}")
        return

    league_paths = get_league_paths()
    all_tm_data = []  # Lista per tutti i dati Transfermarkt
    all_capology_data = []  # Lista per tutti i dati Capology
    
    # Raccogliamo tutti i dati Transfermarkt
    for league_name, league_path in league_paths.items():
        print(f"\nAnalizzando dati Transfermarkt per {league_name}...")
        tm_data = get_transfermarkt_data(league_path)
        if tm_data is not None:
            all_tm_data.append(tm_data)
    
    # Raccogliamo tutti i dati Capology
    for league_name in league_paths.keys():
        print(f"\nAnalizzando dati Capology per {league_name}...")
        capology_data = get_capology_data(league_name)
        if capology_data is not None:
            all_capology_data.append(capology_data)
    
    # Facciamo un unico merge con tutti i dati Transfermarkt
    if all_tm_data:
        tm_combined = pd.concat(all_tm_data, ignore_index=True)
        final_ratings = pd.merge(
            final_ratings,
            tm_combined[['Name', 'Team', 'Age', 'Nationality', 'Height', 'Foot', 'Market Value', 'Contract Until', 'Position']],
            left_on=['Player', 'Team'],
            right_on=['Name', 'Team'],
            how='left'
        )
        final_ratings.drop('Name', axis=1, inplace=True)
    
    # Facciamo un unico merge con tutti i dati Capology
    if all_capology_data:
        capology_combined = pd.concat(all_capology_data, ignore_index=True)
        final_ratings = pd.merge(
            final_ratings,
            capology_combined[['Jugador', 'Team', 'Bruto Anual', 'Cláusula De Rescisión']],
            left_on=['Player', 'Team'],
            right_on=['Jugador', 'Team'],
            how='left'
        )
        final_ratings.drop('Jugador', axis=1, inplace=True)
    
    # Rinomina le colonne in inglese
    final_ratings = final_ratings.rename(columns={
        'Bruto Anual': 'Annual Salary',
        'Cláusula De Rescisión': 'Release Clause'
    })
    
    # Formatta i valori monetari
    def format_currency(value, decimals=0):
        if pd.isna(value):
            return ''
        try:
            # Formatta con separatore delle migliaia e decimali specificati
            return f"€{value:,.{decimals}f}".replace(',', '.')
        except:
            return ''

    # Applica la formattazione alle colonne monetarie
    final_ratings['Annual Salary'] = final_ratings['Annual Salary'].apply(lambda x: format_currency(x, decimals=2))  # 2 decimali per i salari
    final_ratings['Release Clause'] = final_ratings['Release Clause'].apply(format_currency)  # 0 decimali per le clausole
    final_ratings['Market Value'] = final_ratings['Market Value'].apply(format_currency)  # 0 decimali per i valori di mercato
    
    # Ordina per rating Diez (il rating principale per gli attacking midfielder)
    final_ratings = final_ratings.sort_values('Diez', ascending=False)
    
    # Salva il risultato in un nuovo file
    final_ratings.to_csv('attacking_midfielder_ratings_complete_en.csv', index=False)
    print("\nAnalisi completata. I risultati sono stati salvati in 'attacking_midfielder_ratings_complete_en.csv'")
    print(f"Analizzati {len(final_ratings)} attacking midfielder/central midfielder in totale")
    
    # Mostra i top 20 per ogni profilo
    print("\nTop 20 per rating Diez:")
    print(final_ratings[['Player', 'Team', 'League', 'Diez', 'Space_Invader',
                        'Age', 'Position', 'Market Value', 'Annual Salary']].head(20).to_string())
    
    print("\nTop 20 per rating Space Invader:")
    space_invader_sorted = final_ratings.sort_values('Space_Invader', ascending=False)
    print(space_invader_sorted[['Player', 'Team', 'League', 'Diez', 'Space_Invader',
                               'Age', 'Position', 'Market Value', 'Annual Salary']].head(20).to_string())

if __name__ == "__main__":
    main() 
