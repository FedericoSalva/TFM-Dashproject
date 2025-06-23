from dash import html
from pages.team_analysis import create_team_page, LEAGUE_FOLDER_MAPPING
import os

def get_teams_for_league(league_name):
    """Get list of teams for a specific league"""
    league_folder = LEAGUE_FOLDER_MAPPING.get(league_name)
    if not league_folder:
        return []
    
    # Get the data folder path
    season = "24-25"
    data_path = f"pages/{league_folder}/data_{league_name.lower().replace(' ', '_')}_{season}"
    
    # Get all CSV files that don't end with _wyscout.csv or _transfermarkt.csv
    teams = []
    if os.path.exists(data_path):
        for file in os.listdir(data_path):
            if file.endswith(".csv") and not file.endswith(("_wyscout.csv", "_transfermarkt.csv")):
                team_name = file.replace(".csv", "")
                teams.append(team_name)
    
    return teams

def create_league_team_page(team_name, league_name):
    """Create a page for a team from a specific league"""
    try:
        return create_team_page(team_name, league_name)
    except Exception as e:
        print(f"Error creating page for {team_name} in {league_name}: {str(e)}")
        return html.Div([
            html.H1(f"{team_name} - {league_name}"),
            html.P("Error loading team data. Please try again later.")
        ])

def get_league_team_layout(team_name, league_name):
    """Get the layout for a specific team in a league"""
    if league_name not in LEAGUE_FOLDER_MAPPING:
        return html.Div("League not found")
    
    teams = get_teams_for_league(league_name)
    if team_name not in teams:
        return html.Div("Team not found in this league")
    
    return create_league_team_page(team_name, league_name) 
