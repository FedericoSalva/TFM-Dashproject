import pandas as pd
import re

# Leggiamo entrambi i file
ale_file = 'pages/Scout Analysis/profili_dei_giocatori_Ale .xlsx'
fede_file = 'pages/Scout Analysis/profili_dei_giocatori_Fede .xlsx'

df_ale = pd.read_excel(ale_file)
df_fede = pd.read_excel(fede_file)

print('=== ANALISI DETTAGLIATA PROFILI ===')

# Analizza profili ALE
print('\n--- PROFILI ALE ---')
ale_profili = {}
current_role = None
for idx, row in df_ale.iterrows():
    role = row['Profili_giocatori']
    subtype = row['Unnamed: 1']
    kpi_con_palla = str(row['Unnamed: 4']) if pd.notna(row['Unnamed: 4']) else ""
    kpi_senza_palla = str(row['Unnamed: 5']) if pd.notna(row['Unnamed: 5']) else ""
    
    if pd.notna(role) and role.isupper():
        current_role = role
        ale_profili[current_role] = []
        print(f"\n🎯 {current_role}")
    elif pd.notna(subtype) and current_role and subtype != 'RUOLI':
        # Estrai pesi dal testo
        pesi_con_palla = re.findall(r'peso[- ]*(\d+)', kpi_con_palla)
        pesi_senza_palla = re.findall(r'peso[- ]*(\d+)', kpi_senza_palla)
        
        total_con_palla = sum([int(p) for p in pesi_con_palla]) if pesi_con_palla else 0
        total_senza_palla = sum([int(p) for p in pesi_senza_palla]) if pesi_senza_palla else 0
        total_peso = total_con_palla + total_senza_palla
        
        perc_con_palla = (total_con_palla / total_peso * 100) if total_peso > 0 else 0
        perc_senza_palla = (total_senza_palla / total_peso * 100) if total_peso > 0 else 0
        
        ale_profili[current_role].append({
            'nome': subtype,
            'peso_con_palla': total_con_palla,
            'peso_senza_palla': total_senza_palla,
            'perc_con_palla': round(perc_con_palla, 1),
            'perc_senza_palla': round(perc_senza_palla, 1),
            'kpi_count_con': len(pesi_con_palla),
            'kpi_count_senza': len(pesi_senza_palla)
        })
        
        print(f"  • {subtype}: {round(perc_con_palla,1)}% con palla | {round(perc_senza_palla,1)}% senza palla | KPI: {len(pesi_con_palla)}+{len(pesi_senza_palla)}")

# Analizza profili FEDE
print('\n\n--- PROFILI FEDE ---')
fede_profili = {}
current_role = None
for idx, row in df_fede.iterrows():
    role = row['Profili_giocatori']
    subtype = row['Unnamed: 1']
    
    if pd.notna(role) and role.isupper():
        current_role = role
        fede_profili[current_role] = []
        print(f"\n🎯 {current_role}")
    elif pd.notna(subtype) and current_role and subtype != 'RUOLI':
        fede_profili[current_role].append(subtype)
        print(f"  • {subtype}")

# Confronto profili mancanti
print('\n\n=== CONFRONTO E PROFILI MANCANTI ===')
for role in set(list(ale_profili.keys()) + list(fede_profili.keys())):
    print(f"\n🏷️ {role}")
    
    ale_subtypes = [p['nome'] if isinstance(p, dict) else p for p in ale_profili.get(role, [])]
    fede_subtypes = fede_profili.get(role, [])
    
    print(f"  ALE ({len(ale_subtypes)}): {ale_subtypes}")
    print(f"  FEDE ({len(fede_subtypes)}): {fede_subtypes}")
    
    only_ale = set(ale_subtypes) - set(fede_subtypes)
    only_fede = set(fede_subtypes) - set(ale_subtypes)
    
    if only_ale:
        print(f"  ❌ Solo in ALE: {list(only_ale)}")
    if only_fede:
        print(f"  ➕ Solo in FEDE: {list(only_fede)}")

print('\n\n=== ANALISI PESI ALE (DETTAGLIATA) ===')
for role, profiles in ale_profili.items():
    print(f"\n🎯 {role}")
    for profile in profiles:
        if isinstance(profile, dict):
            print(f"  {profile['nome']}: {profile['peso_con_palla']+profile['peso_senza_palla']} tot | {profile['perc_con_palla']}% con | {profile['perc_senza_palla']}% senza | {profile['kpi_count_con']+profile['kpi_count_senza']} KPI") 