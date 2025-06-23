import os
import pandas as pd
import numpy as np
from pathlib import Path

# Configurazione dei percorsi
BASE_PATH = "/Users/federico/dash_project/pages"
PROFILES_PATH = "/Users/federico/dash_project/pages/Scout Analysis/profili_scout_analysis_finale_corretti.csv"

# Pesi delle leghe
LEAGUE_WEIGHTS = {
    'Serie A': 2.0,
    'EPL': 2.0,
    'La Liga': 2.0,
    'Bundesliga': 2.0,
    'Ligue 1': 2.0,
    'Primeira Liga': 1.5,
    'Eredivisie': 1.5,
    'Süper Lig': 1.5,
    'MLS': 1.0,
    'Championship': 1.0
}

# Mapping dei ruoli transfermarkt ai ruoli dei profili
ROLE_MAPPING = {
    'Goalkeeper': 'GK',
    'Centre-Back': 'CB',
    'Centre-Forward': 'ST',
    'Central Midfield': 'CM',
    'Defensive Midfield': 'CM',
    'Left-Back': 'CB',
    'Right-Back': 'CB',
    'Left Winger': 'ST',
    'Right Winger': 'ST',
    'Second Striker': 'ST',
    'Attacking Midfield': 'CM',
    'Defensive Midfield': 'CM',
    'Left Midfield': 'CM',
    'Right Midfield': 'CM'
} 