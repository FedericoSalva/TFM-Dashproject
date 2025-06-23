import pandas as pd

print("🔍 ANALISI SOVRAPPOSIZIONI PROFILI")
print("=" * 50)

# Analisi per ruolo
profiles_analysis = {
    'PORTIERE': [
        {'nome': 'Playmaker Keeper', 'peso': '30/70', 'focus': 'Costruzione + Parate'},
        {'nome': 'Shot-Stopper', 'peso': '10/90', 'focus': 'Solo Parate'}
    ],
    'CENTRALE': [
        {'nome': 'Guardian', 'peso': '20/80', 'focus': 'Difesa posizionale'},
        {'nome': 'Deep Distributor', 'peso': '70/30', 'focus': 'Regista arretrato'},
        {'nome': 'Enforcer', 'peso': '15/85', 'focus': 'Aggressività/Tackle'}
    ],
    'TERZINO': [
        {'nome': 'Sentinel Fullback', 'peso': '20/80', 'focus': 'Copertura laterale'},
        {'nome': 'Advanced Wingback', 'peso': '60/40', 'focus': 'Bilanciato'},
        {'nome': 'Overlapping Runner', 'peso': '70/30', 'focus': 'Sovrapposizioni'}
    ],
    'CENTROCAMPISTA': [
        {'nome': 'Pivot Master', 'peso': '25/75', 'focus': 'Schermo/Recupero'},
        {'nome': 'Playmaking Engine', 'peso': '75/25', 'focus': 'Smistamento/Creatività'},
        {'nome': 'Box-to-Box', 'peso': '55/45', 'focus': 'Dinamismo/Campo'}
    ],
    'CENTROCAMPISTAAVANZATO': [
        {'nome': 'Maestro', 'peso': '85/15', 'focus': 'Tecnica/Corto'},
        {'nome': 'Visionary', 'peso': '90/10', 'focus': 'Creatività/Filtranti'},
        {'nome': 'Late-Runner', 'peso': '75/25', 'focus': 'Inserimenti/Gol'}
    ],
    'ALA': [
        {'nome': 'Safe Haven', 'peso': '60/40', 'focus': 'Conservativo/Possesso'},
        {'nome': 'Key Passer', 'peso': '85/15', 'focus': 'Assist/Creatività'},
        {'nome': 'Direct Winger', 'peso': '80/20', 'focus': 'Dribbling/Tiro'}
    ],
    'ATTACCANTE': [
        {'nome': 'Hybrid Forward', 'peso': '70/30', 'focus': 'Mobile/Costruzione'},
        {'nome': 'Aerial Dominator', 'peso': '40/60', 'focus': 'Fisico/Aereo'},
        {'nome': 'Lethal Striker', 'peso': '85/15', 'focus': 'Finalizzazione pura'}
    ]
}

print("\n🎯 ANALISI PER RUOLO:")
total_profiles = 0
for role, profiles in profiles_analysis.items():
    total_profiles += len(profiles)
    print(f"\n{role} ({len(profiles)} profili):")
    for profile in profiles:
        print(f"  • {profile['nome']}: {profile['peso']} - {profile['focus']}")

print(f"\n📊 TOTALE PROFILI: {total_profiles} + 1 Chameleon = {total_profiles + 1}")

print("\n🚨 POSSIBILI SOVRAPPOSIZIONI:")

# Controllo sovrapposizioni
overlaps = []

# CENTROCAMPISTAAVANZATO - possibile sovrapposizione
print("\n🔴 CENTROCAMPISTAAVANZATO:")
print("  • Maestro (85/15) e Visionary (90/10) sono molto simili")
print("    - Entrambi molto orientati al gioco con palla")
print("    - Focus su creatività e tecnica")
print("    - Differenza solo 5% nei pesi")

# ALA - leggera sovrapposizione
print("\n🟡 ALA:")
print("  • Key Passer (85/15) e Direct Winger (80/20) abbastanza simili")
print("    - Entrambi molto offensivi")
print("    - Differenza solo 5-10% nei pesi")

print("\n✅ RUOLI BEN DIFFERENZIATI:")
print("  • PORTIERE: Molto distinti (30/70 vs 10/90)")
print("  • CENTRALE: Tre profili chiari (difensivo, regista, aggressivo)")
print("  • TERZINO: Gradazione chiara (difensivo → bilanciato → offensivo)")
print("  • CENTROCAMPISTA: Tre ruoli distinti (schermo, regista, dinamico)")
print("  • ATTACCANTE: Molto diversi (mobile, fisico, finalizzatore)")

print("\n💡 RACCOMANDAZIONI:")
print("\n📋 OPZIONE 1 - MANTIENI TUTTO (21 profili):")
print("  ✅ Copertura completa di tutti gli stili")
print("  ✅ Massima granularità per scouting")
print("  ❌ Complessità maggiore per implementazione")
print("  ❌ Possibili confusioni tra profili simili")

print("\n📋 OPZIONE 2 - OTTIMIZZA (16-18 profili):")
print("  🔄 CENTROCAMPISTAAVANZATO: Unire Maestro+Visionary in 'Creative Playmaker'")
print("  🔄 ALA: Differenziare meglio Key Passer vs Direct Winger")
print("  🔄 TERZINO: Mantenere 3 profili (buona gradazione)")
print("  🔄 Altri ruoli: Mantenere così")

print("\n📋 OPZIONE 3 - SEMPLIFICA (14 profili):")
print("  📉 2 profili per ruolo (tranne Attaccante che resta 3)")
print("  📉 Portiere: Playmaker vs Shot-Stopper")
print("  📉 Centrale: Guardian vs Deep Distributor")
print("  📉 Terzino: Defensive vs Offensive")
print("  📉 Centrocampista: Defensive vs Creative")
print("  📉 CentrocampistaAvanzato: Creative vs Finisher")
print("  📉 Ala: Conservative vs Attacking")

print("\n🎯 MIA RACCOMANDAZIONE:")
print("OPZIONE 2 - Mantieni 18 profili con piccoli aggiustamenti:")
print("1. Unire Maestro+Visionary in 'Creative Playmaker' (90/10)")
print("2. Rinominare Late-Runner in 'Box-to-Box Avanzato' per distinguerlo")
print("3. Differenziare Key Passer (assistman puro) da Direct Winger (1vs1)")
print("4. Risultato: 18 profili ben distinti + 1 Chameleon")

print("\n❓ COSA PREFERISCI?")
print("A) Mantieni tutto (21 profili) - Massima copertura")
print("B) Ottimizza (18 profili) - Bilanciato") 
print("C) Semplifica (14 profili) - Implementazione più facile") 
