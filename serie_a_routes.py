from dash import html
from pages.serie_a_teams import get_team_layout, normalize_team_name, teams
from fuzzywuzzy import fuzz
import os

# Mapping dei nomi delle squadre e loro varianti
TEAM_NAME_MAPPING = {
    "napoli": "Napoli",
    "inter": "Internazionale",
    "internazionale": "Internazionale",
    "atalanta": "Atalanta",
    "roma": "Roma",
    "fiorentina": "Fiorentina",
    "lazio": "Lazio",
    "milan": "Milan",
    "acmilan": "Milan",
    "bologna": "Bologna",
    "como": "Como",
    "torino": "Torino",
    "toro": "Torino",
    "udinese": "Udinese",
    "genoa": "Genoa",
    "hellas": "Hellas_Verona",
    "hellasverona": "Hellas_Verona",
    "hellas_verona": "Hellas_Verona",
    "verona": "Hellas_Verona",
    "hell verona": "Hellas_Verona",
    "cagliari": "Cagliari",
    "parma": "Parma",
    "lecce": "Lecce",
    "empoli": "Empoli",
    "monza": "Monza",
    "juventus": "Juventus",
    "juve": "Juventus"
}

# Use teams from serie_a_teams.py
SERIE_A_TEAMS = teams + ["Juventus"]  # Add Juventus to the list

# Casi speciali che devono matchare esattamente
SPECIAL_CASES = {
    "inter": "Internazionale",
    "internazionale": "Internazionale",
    "hellas verona": "Hellas_Verona",
    "hellas_verona": "Hellas_Verona"
}

def find_best_match(team_name):
    """Find the best matching team name using fuzzy matching"""
    if not team_name:
        return None
        
    # Check special cases first
    team_lower = team_name.lower()
    if team_lower in SPECIAL_CASES:
        return SPECIAL_CASES[team_lower]
        
    # Try fuzzy matching
    best_ratio = 0
    best_match = None
    
    for official_name in SERIE_A_TEAMS:
        ratio = fuzz.ratio(team_lower, official_name.lower())
        if ratio > best_ratio and ratio > 80:  # 80% threshold for matching
            best_ratio = ratio
            best_match = official_name
            
    return best_match

# Remove the old functions since we're using serie_a_teams.py now

# Function to get layout for a specific team (updated to use serie_a_teams.py)
def get_team_layout_route(team_name):
    """Get the layout for a specific team via routing"""
    
    # Special handling for Juventus - ALWAYS use team_page.py
    if team_name and team_name.lower() == 'juventus':
        from pages.team_page import layout
        return layout
    
    # Find best matching team name for other teams
    matched_name = find_best_match(team_name)
    
    if not matched_name:
        return html.Div([
            html.H1("Team not found"),
            html.P(f"The team '{team_name}' was not found in Serie A.")
        ])
    
    # For all other teams, use the function from serie_a_teams.py
    return get_team_layout(matched_name) 