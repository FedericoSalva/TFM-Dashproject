from pathlib import Path

# Base paths
BASE_PATH = Path("/Users/federico/dash_project/pages")

# League weights
LEAGUE_WEIGHTS = {
    "Serie_A": 2.0,
    "EPL": 2.0,
    "La_Liga": 2.0,
    "Bundesliga": 2.0,
    "Ligue_1": 2.0,
    "Eredivisie": 1.5,
    "Primeira_Liga": 1.5,
    "Süper_Lig": 1.5,
    "MLS": 1.0,
    "Championship": 1.0
}

# Exact file names for transfermarkt data
TRANSFERMARKT_FILE_NAMES = {
    "Serie_A": {
        "Juventus FC": "Juventus FC.csv",
    },
    "La_Liga": {
        "Osasuna": "Osasuna_transfemarkt.csv",
        "Villarreal": "Villareal_transfermarkt.csv"
    },
    "Ligue_1": {
        "Lille": "Lille_trasnfermarkt.csv"
    },
    "Eredivisie": {
        "PSV Eindhoven": "PSV_Eindhoven_transfermarkt.csv"
    }
}

# Path templates for different leagues
LEAGUE_PATHS = {
    "Serie_A": {
        "fbref": str(BASE_PATH / "data_serie_a_24-25" / "{team}.csv"),
        "transfermarkt": str(BASE_PATH / "data_serie_a_24-25" / "{team_transfermarkt}"),
        "capology": str(BASE_PATH / "Salari_Capology/Serie_A/{team}/Tabla_Limpia_{team}.csv")
    }
}

# Template for other leagues
STANDARD_LEAGUE_TEMPLATE = {
    "fbref": str(BASE_PATH / "{league}/data_{league_lower}_24-25" / "{team}.csv"),
    "transfermarkt": str(BASE_PATH / "{league}/data_{league_lower}_24-25" / "{team_transfermarkt}"),
    "capology": str(BASE_PATH / "Salari_Capology/{league}/{team}/Tabla_Limpia_{team}.csv")
}

# Generate paths for other leagues
for league in LEAGUE_WEIGHTS.keys():
    if league != "Serie_A":
        league_lower = league.lower().replace("_", "_")
        LEAGUE_PATHS[league] = {
            "fbref": STANDARD_LEAGUE_TEMPLATE["fbref"].format(
                league=league, league_lower=league_lower, team="{team}"
            ),
            "transfermarkt": STANDARD_LEAGUE_TEMPLATE["transfermarkt"].format(
                league=league, league_lower=league_lower, team="{team}"
            ),
            "capology": STANDARD_LEAGUE_TEMPLATE["capology"].format(
                league=league, team="{team}"
            )
        }

def get_league_weight(league_name: str) -> float:
    """Get the weight for a specific league."""
    return LEAGUE_WEIGHTS.get(league_name, 1.0)

def get_transfermarkt_filename(league: str, team: str) -> str:
    """Get the exact transfermarkt filename for a team."""
    league_files = TRANSFERMARKT_FILE_NAMES.get(league, {})
    if team in league_files:
        return league_files[team]
    return f"{team}_transfermarkt.csv"

def get_paths_for_team(league: str, team: str) -> dict:
    """Get all paths (fbref, transfermarkt, capology) for a specific team."""
    if league not in LEAGUE_PATHS:
        raise ValueError(f"League {league} not found in configuration")
    
    paths = {}
    for source, path_template in LEAGUE_PATHS[league].items():
        if source == "transfermarkt":
            team_transfermarkt = get_transfermarkt_filename(league, team)
            paths[source] = path_template.format(team=team, team_transfermarkt=team_transfermarkt)
        else:
            paths[source] = path_template.format(team=team)
    
    return paths 