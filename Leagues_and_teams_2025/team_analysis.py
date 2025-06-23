from dash import html
import pandas as pd
import os

# Mapping between league names and their folder names
LEAGUE_FOLDER_MAPPING = {
    "Premier League": "EPL",
    "EPL": "EPL",
    "Bundesliga": "Bundesliga",
    "Bundesliga 2": "Bundesliga_2", 
    "La Liga": "La_Liga",
    "Ligue 1": "Ligue_1",
    "Ligue 2": "Ligue_2",
    "Serie B": "Serie_B",
    "Eredivisie": "Eredivisie",
    "Primeira Liga": "Primeira_Liga",
    "Championship": "Championship",
    "Jupiler Pro League": "Jupiler_Pro_League",
    "Liga Argentina": "Liga_Argentina",
    "MLS": "MLS",
    "Süper Lig": "Süper_Lig",
    "Brazilian Série A": "Brazilian_Série_A"
}

def create_team_page(team_name, league_name):
    """Create a basic team page for leagues other than Serie A"""
    try:
        return html.Div([
            html.H1(f"{team_name} - {league_name}"),
            html.P("Team analysis for other leagues is not fully implemented yet."),
            html.P("This is a placeholder page.")
        ])
    except Exception as e:
        print(f"Error creating page for {team_name}: {str(e)}")
        return html.Div([
            html.H1(f"{team_name} - {league_name}"),
            html.P("Error loading team data. Please try again later.")
        ]) 
