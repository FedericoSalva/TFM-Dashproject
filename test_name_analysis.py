import pandas as pd
from utils.name_analysis import analyze_name_differences, print_unmatched_analysis

# Crea dati di esempio
fbref_data = {
    'Jugador': [
        "Lukáš Hrádecký",
        "Ermedin Demirovic",
        "Kevin de bruyne",
        "Virgil VAN DER SAR",
        "Jean-clair todibo",
        "Konan N'dri",
        "João felix",
        "Matthijs de Ligt",
        "Giocatore Solo FBRef"
    ]
}

transfermarkt_data = {
    'Name': [
        "Lukas Hradecky",
        "Ermedin Demirović",
        "Kevin De Bruyne",
        "Virgil Van Der Sar",
        "Jean-Clair Todibo",
        "Konan N'Dri",
        "Joao Félix",
        "Matthijs De Ligt",
        "Giocatore Solo Transfermarkt"
    ]
}

# Crea DataFrame
fbref_df = pd.DataFrame(fbref_data)
transfermarkt_df = pd.DataFrame(transfermarkt_data)

# Analizza le differenze
print("Analizzando le differenze nei nomi...")
diff_df = analyze_name_differences(fbref_df, transfermarkt_df)

# Stampa l'analisi
print_unmatched_analysis(diff_df) 