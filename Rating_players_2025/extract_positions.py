import pandas as pd
import glob
import os

def get_all_positions():
    # Trova tutti i file transfermarkt
    transfermarkt_files = glob.glob('pages/data_serie_a_24-25/*_transfermarkt.csv')
    
    # Set per memorizzare i ruoli unici
    unique_positions = set()
    
    # Leggi ogni file e estrai i ruoli
    for file in transfermarkt_files:
        try:
            df = pd.read_csv(file)
            if 'Position' in df.columns:
                # Rimuovi i valori NaN e converti in stringhe
                positions = df['Position'].dropna().astype(str).unique()
                # Rimuovi eventuali spazi extra e converti in minuscolo per uniformità
                positions = [pos.strip().lower() for pos in positions]
                unique_positions.update(positions)
        except Exception as e:
            print(f"Errore nel leggere {file}: {str(e)}")
    
    # Converti il set in una lista ordinata, escludendo 'nan' come stringa
    positions_list = sorted([pos for pos in unique_positions if pos != 'nan'])
    
    # Crea un DataFrame con i ruoli e il conteggio
    positions_df = pd.DataFrame({
        'Position': positions_list,
        'Count': [sum(1 for _ in positions_list if _ == pos) for pos in positions_list]
    })
    
    # Salva in CSV
    positions_df.to_csv('unique_positions.csv', index=False)
    print(f"Trovati {len(positions_list)} ruoli unici. Salvati in 'unique_positions.csv'")
    
    # Stampa i ruoli trovati
    print("\nRuoli trovati:")
    for pos in positions_list:
        print(f"- {pos}")

if __name__ == "__main__":
    get_all_positions() 
