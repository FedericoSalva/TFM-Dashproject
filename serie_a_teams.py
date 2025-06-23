from dash import dcc, html, callback_context, ALL, no_update, State
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import os
import dash
import re
from fuzzywuzzy import fuzz  # invece di thefuzz

# Comprehensive team mapping - all variants point to the same canonical name
TEAM_VARIANTS = {
    # Inter variants - canonical name: "Inter"
    "inter": "Inter",
    "internazionale": "Inter", 
    "inter milan": "Inter",
    
    # Hellas Verona variants - canonical name: "Hellas Verona"
    "hellas verona": "Hellas Verona",
    "hellas_verona": "Hellas Verona",
    "verona": "Hellas Verona",
    "hellas": "Hellas Verona",
    
    # Other teams (add as needed)
    "napoli": "Napoli",
    "atalanta": "Atalanta", 
    "roma": "Roma",
    "fiorentina": "Fiorentina",
    "lazio": "Lazio",
    "milan": "Milan",
    "ac milan": "Milan",
    "bologna": "Bologna",
    "como": "Como",
    "torino": "Torino",
    "udinese": "Udinese",
    "genoa": "Genoa",
    "cagliari": "Cagliari",
    "parma": "Parma",
    "lecce": "Lecce",
    "empoli": "Empoli",
    "monza": "Monza"
}

# Lista delle squadre di Serie A (excluding Juventus which has its own implementation)
teams = [
    "Napoli", "Inter", "Atalanta", "Roma", "Fiorentina", "Lazio",
    "Milan", "Bologna", "Como", "Torino", "Udinese", "Genoa", "Hellas Verona",
    "Cagliari", "Parma", "Lecce", "Empoli", "Monza"
]

# Configurazione dei pesi dei campionati
LEAGUE_WEIGHTS = {
    # Top 5 leghe - peso 2.0
    "Serie_A": 2.0,
    "EPL": 2.0, 
    "La_Liga": 2.0,
    "Bundesliga": 2.0,
    "Ligue_1": 2.0,
    
    # Altre leghe europee - peso 1.5
    "Primeira_Liga": 1.5,
    "Eredivisie": 1.5,
    "Süper_Lig": 1.5,
    
    # Altre leghe - peso 1.0
    "MLS": 1.0,
    "Championship": 1.0
}

# Base path
BASE_PATH = "/Users/federico/dash_project/pages"

# Dizionario di mappatura dei nomi delle squadre
TEAM_NAME_MAPPING = {
    # Serie A
    "Inter": "Internazionale",
    "Inter Milan": "Internazionale",
    "Hellas": "Hellas Verona",
    "Verona": "Hellas Verona",
    
    # Premier League
    "Man United": "Manchester United",
    "Man City": "Manchester City",
    "Newcastle": "Newcastle United",
    "Wolves": "Wolverhampton",
    "Brighton": "Brighton & Hove Albion",
    
    # La Liga
    "Atletico": "Atletico Madrid",
    "Atlético": "Atletico Madrid",
    "Athletic": "Athletic Club",
    "Real": "Real Madrid",
    
    # Aggiungere altre mappature necessarie...
}

def normalize_team_variants(team_name):
    """Normalize team name variants - ONLY for Inter and Hellas Verona"""
    if not team_name:
        return team_name
    
    team_lower = team_name.lower().strip()
    
    # Inter variants - all map to "Inter"
    inter_variants = ["inter", "internazionale", "inter milan"]
    if team_lower in inter_variants:
        return "Inter"
    
    # Hellas Verona variants - all map to "Hellas Verona" 
    hellas_variants = ["hellas verona", "hellas_verona", "hellas", "verona"]
    if team_lower in hellas_variants:
        return "Hellas Verona"
    
    # For all other teams, return capitalized version
    return team_name.strip().title()

def find_team_in_data(team_name, data_df, team_column="Equipo"):
    """Find a team in dataframe considering variants"""
    # First try exact match
    if team_name in data_df[team_column].values:
        return team_name
    
    # For Inter, try all variants
    if team_name == "Inter":
        for variant in ["Inter", "Internazionale", "Inter Milan"]:
            if variant in data_df[team_column].values:
                return variant
    
    # For Hellas Verona, try all variants  
    if team_name == "Hellas Verona":
        for variant in ["Hellas Verona", "Hellas_Verona", "Hellas", "Verona"]:
            if variant in data_df[team_column].values:
                return variant
    
    return team_name

def normalize_team_name(name):
    """Normalizza il nome della squadra rimuovendo caratteri speciali e uniformando il formato"""
    if pd.isna(name):
        return name
    
    name = str(name).strip()
    # Rimuovi caratteri speciali e uniforma gli spazi
    name = name.replace("_", " ").replace("-", " ")
    # Rimuovi spazi multipli
    name = " ".join(name.split())
    return name

def find_matching_team_name(name, possible_names, threshold=85):
    """
    Trova il nome della squadra più simile tra quelli possibili usando fuzzy matching.
    
    Args:
        name (str): Nome della squadra da cercare
        possible_names (list): Lista di nomi possibili
        threshold (int): Soglia minima di similarità (0-100)
    
    Returns:
        str: Nome corrispondente se trovato, altrimenti il nome originale
    """
    if pd.isna(name):
        return name
    
    name = normalize_team_name(name)
    
    # Prima controlla nel dizionario di mappatura
    if name in TEAM_NAME_MAPPING:
        return TEAM_NAME_MAPPING[name]
    
    # Poi cerca la corrispondenza più simile
    best_match = None
    best_ratio = 0
    
    for possible_name in possible_names:
        possible_name = normalize_team_name(possible_name)
        
        # Prova diverse varianti di matching fuzzy
        ratios = [
            fuzz.ratio(name.lower(), possible_name.lower()),
            fuzz.partial_ratio(name.lower(), possible_name.lower()),
            fuzz.token_sort_ratio(name.lower(), possible_name.lower())
        ]
        
        max_ratio = max(ratios)
        if max_ratio > best_ratio and max_ratio >= threshold:
            best_ratio = max_ratio
            best_match = possible_name
    
    return best_match if best_match else name

def get_file_name_for_team(team_name, file_type):
    """Get the correct file name for a team based on file type"""
    # First normalize the team name
    canonical_name = normalize_team_variants(team_name)
    
    # File name mappings for each type
    file_mappings = {
        "wyscout": {
            "Inter": "Internazionale",
            "Hellas Verona": "Hellas_Verona"
        },
        "players": {
            "Inter": "Internazionale", 
            "Hellas Verona": "Hellas_Verona"
        },
        "transfermarkt": {
            "Inter": "Inter Milan",
            "Hellas Verona": "Hellas Verona",
            "Napoli": "SSC Napoli",
            "Atalanta": "Atalanta BC",
            "Roma": "AS Roma",
            "Fiorentina": "ACF Fiorentina", 
            "Lazio": "SS Lazio",
            "Milan": "AC Milan",
            "Bologna": "Bologna FC 1909",
            "Como": "Como 1907",
            "Torino": "Torino FC",
            "Udinese": "Udinese Calcio",
            "Genoa": "Genoa CFC",
            "Cagliari": "Cagliari Calcio",
            "Parma": "Parma Calcio 1913",
            "Lecce": "US Lecce",
            "Empoli": "FC Empoli",
            "Monza": "AC Monza"
        },
        "salary": {
            "Hellas Verona": "Hellas_Verona"
        }
    }
    
    # Get the mapping for this file type
    mapping = file_mappings.get(file_type, {})
    return mapping.get(canonical_name, canonical_name)

def get_team_info(team_name, display_name):
    """Get basic team information from various data sources for any Serie A team"""
    season = "24-25"  # Hardcoded season
    
    # Read classification data
    clasificacion_df = pd.read_csv(f"pages/data_serie_a_{season}/clasificacion.csv")
    
    # Find team position
    team_position = None
    for idx, row in clasificacion_df.iterrows():
        if row["Equipo"] == display_name:
            team_position = idx + 1  # +1 because position starts from 1
            break
    
    if team_position is None:
        team_position = 0  # Default if not found
    
    # Get the correct file name for this team
    file_team_name = display_name
    if display_name == "Inter":
        file_team_name = "Internazionale"
    elif display_name == "Hellas Verona":
        file_team_name = "Hellas_Verona"
    
    # Read market value and age data from Serie A_transfermarkt.csv
    transfermarkt_df = pd.read_csv(f"pages/data_serie_a_{season}/Serie A_transfermarkt.csv")
    
    # Find the team in transfermarkt data
    market_value = 0.0
    avg_age = 0.0
    
    for _, row in transfermarkt_df.iterrows():
        if (display_name.lower() in row['nombre'].lower() or 
            row['nombre'].lower() in display_name.lower() or
            (display_name == "Inter" and "inter" in row['nombre'].lower()) or
            (display_name == "Hellas Verona" and "hellas" in row['nombre'].lower()) or
            (display_name == "Atalanta" and "atalanta" in row['nombre'].lower()) or
            (display_name == "Milan" and "milan" in row['nombre'].lower() and "inter" not in row['nombre'].lower())):
            
            # Extract market value (remove '€' and 'm' and convert to float)
            market_value_str = row['valor_total'].replace('€', '').replace('m', '')
            market_value = float(market_value_str)
            
            # Get average age from extranjeros column  
            avg_age = float(row['extranjeros'])
            break
    
    # Calculate total salary
    total_salary = 0
    
    # Read salary data from Capology file
    salary_file = f"pages/Salari_Capology/Serie_A/{file_team_name}/Tabla_Limpia_{file_team_name}.csv"
    if os.path.exists(salary_file):
        try:
            salary_df = pd.read_csv(salary_file)
            if "Bruto Anual" in salary_df.columns:
                # Clean and sum salary data
                for salary_str in salary_df["Bruto Anual"].dropna():
                    if isinstance(salary_str, str) and "€" in salary_str:
                        # Remove €, spaces, and commas, then convert to float
                        clean_salary = salary_str.replace("€", "").replace(" ", "").replace(",", "")
                        try:
                            total_salary += float(clean_salary)
                        except:
                            continue
        except Exception as e:
            print(f"Error reading salary file for {display_name}: {e}")
            total_salary = 0

    # Read formation data
    most_used_formation = "4-3-3"  # Default
    wyscout_file = f"pages/data_serie_a_{season}/{file_team_name}_wyscout.csv"
    if os.path.exists(wyscout_file):
        try:
            wyscout_df = pd.read_csv(wyscout_file, sep=";")
            if not wyscout_df.empty and "Seleccionar esquema" in wyscout_df.columns:
                formations = wyscout_df["Seleccionar esquema"].dropna()
                if not formations.empty:
                    most_used_formation = formations.mode()[0] if len(formations.mode()) > 0 else formations.iloc[0]
        except Exception as e:
            print(f"Error reading wyscout file for {display_name}: {e}")
    
    return {
        "position": team_position,
        "market_value": market_value,
        "total_salary": round(total_salary / 1_000_000, 2),  # Convert to millions
        "avg_age": avg_age,
        "formation": most_used_formation.split()[0] if ' ' in most_used_formation else most_used_formation
    }

def get_team_stats(display_name):
    """Get team statistics from the classification data for any Serie A team"""
    season = "24-25"
    clasificacion_df = pd.read_csv(f"pages/data_serie_a_{season}/clasificacion.csv")
    team_stats = clasificacion_df[clasificacion_df["Equipo"] == display_name].iloc[0]
    
    return {
        "wins": int(team_stats["PG"]),  # Partite Vinte
        "draws": int(team_stats["PE"]),  # Pareggi
        "losses": int(team_stats["PP"]), # Sconfitte
        "goals_for": int(team_stats["GF"]),  # Gol Fatti
        "goals_against": int(team_stats["GC"])  # Gol Subiti
    }

def create_wdl_chart(wins, draws, losses):
    """Create a donut chart for Wins/Draws/Losses"""
    total_matches = wins + draws + losses
    
    fig = go.Figure(data=[go.Pie(
        labels=['Wins', 'Draws', 'Losses'],
        values=[wins, draws, losses],
        hole=.7,
        marker_colors=['#28a745', '#ffc107', '#dc3545'],
        textinfo='value',
        showlegend=False
    )])
    
    fig.add_annotation(
        text=f"{total_matches}",
        x=0.5, y=0.5,
        font=dict(size=20, color='black'),
        showarrow=False
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=200,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def create_goals_chart(goals_for, goals_against):
    """Create a pie chart for Goals For (green) and Against (red)"""
    goal_diff = goals_for - goals_against
    
    # Create the base figure
    fig = go.Figure(data=[go.Pie(
        values=[goals_for, goals_against],
        labels=['Goals For', 'Goals Against'],
        hole=0.7,
        showlegend=False,
        hovertemplate="%{label}: %{value}<extra></extra>",
        textinfo='none',
        marker_colors=['#28a745', '#dc3545'],  # Green, Red
        sort=False
    )])
    
    # Add the goal difference annotation in the center
    fig.add_annotation(
        text=f"+{goal_diff}" if goal_diff > 0 else str(goal_diff),
        x=0.5,
        y=0.5,
        font=dict(size=24, color='black'),
        showarrow=False
    )
    
    # Update layout
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=200,
        width=None,  # Let it be responsive
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        autosize=True,  # Make it responsive
    )

    return fig

def create_player_button(player_name):
    """Create a player button with image and name"""
    try:
        with open(f"assets/Players/{player_name}.png", "rb"):
            img_src = f"/assets/Players/{player_name}.png"
    except:
        img_src = "/assets/Players/default.png"
    
    return dbc.Button(
        [
            # Image container
            html.Div(
                html.Img(
                    src=img_src,
                    style={
                        'width': '80px',
                        'height': '80px',
                        'border-radius': '50%',
                        'object-fit': 'cover',
                    }
                ),
                style={
                    'display': 'flex',
                    'align-items': 'center',
                    'justify-content': 'center',
                    'margin-bottom': '8px',
                }
            ),
            # Player name
            html.Div(
                player_name,
                style={
                    'font-size': '0.85rem',
                    'text-align': 'center',
                    'white-space': 'normal',
                    'word-wrap': 'break-word',
                    'max-width': '90px',
                    'color': '#2c3e50',
                    'font-weight': '500',
                    'line-height': '1.2'
                }
            )
        ],
        style={
            'width': '100px',
            'height': 'auto',
            'background-color': 'white',
            'border': '2px solid #e9ecef',
            'border-radius': '50%',
            'padding': '5px',
            'margin': '10px',
            'display': 'flex',
            'flex-direction': 'column',
            'align-items': 'center',
            'justify-content': 'center',
            'transition': 'all 0.2s ease',
        },
        color="light",
        className="player-btn shadow-sm",
        id={'type': 'player-button', 'index': player_name}
    )

def create_team_layout(team_name):
    """Create the team layout with all sections"""
    
    # Normalize team name for display and consistency
    display_name = normalize_team_variants(team_name)
    
    # Team logo path
    logo_path = f"/assets/{display_name}.png"  # Default
    
    # For specific teams with different paths
    if display_name == "Como":
        logo_path = "/assets/Serie_A/2024-2025/Como.png"
    elif display_name == "Hellas Verona":
        logo_path = "/assets/Serie_A/2024-2025/Hellas_Verona.png"
    
    return html.Div([
        # Add this at the top of the layout
        dcc.Store(id=f'player-styles-{display_name}', data={
            'player-marker:hover': {
                'transform': 'scale(1.1)',
                'z-index': '1000'
            },
            'player-marker:hover .player-minutes': {
                'display': 'block'
            }
        }),
        
        # Hidden div for triggering callbacks
        html.Div(id=f"trigger-update-{display_name}", children="initial", style={"display": "none"}),
        
        # Header bar
        html.Div(
            dbc.Container(
                html.H1(f"{display_name} - Team Overview", className="text-white mb-0", 
                       style={"fontSize": "1.75rem"}),
                fluid=True,
                className="py-2"
            ),
            className="bg-primary mb-4"
        ),
        
        # Main content
        dbc.Container([
            # Team info section
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        # Logo column
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    html.Img(
                                        src=logo_path,
                                        style={
                                            "width": "100px",
                                            "height": "auto",
                                            "objectFit": "contain"
                                        }
                                    ),
                                    className="d-flex justify-content-center align-items-center"
                                ),
                                className="border-0 bg-transparent"
                            ),
                            width=12,
                            lg=3,
                            className="text-center mb-3 mb-lg-0"
                        ),
                        # Stats column
                        dbc.Col([
                            dbc.Row([
                                # Position
                                dbc.Col(
                                    dbc.Card([
                                        html.H6("Position", className="text-muted mb-1", 
                                               style={"fontSize": "0.8rem"}),
                                        html.H3(id=f"team-position-{display_name}", className="mb-0",
                                               style={"fontSize": "1.2rem"})
                                    ], body=True, className="text-center h-100 shadow-sm py-2"),
                                    width=12,
                                    lg=4,
                                    className="mb-2 mb-lg-0"
                                ),
                                # Market Value
                                dbc.Col(
                                    dbc.Card([
                                        html.H6("Market Value", className="text-muted mb-1",
                                               style={"fontSize": "0.8rem"}),
                                        html.H3(id=f"market-value-{display_name}", className="mb-0",
                                               style={"fontSize": "1.2rem"})
                                    ], body=True, className="text-center h-100 shadow-sm py-2"),
                                    width=12,
                                    lg=4,
                                    className="mb-2 mb-lg-0"
                                ),
                                # Average Age
                                dbc.Col(
                                    dbc.Card([
                                        html.H6("Avg Age", className="text-muted mb-1",
                                               style={"fontSize": "0.8rem"}),
                                        html.H3(id=f"avg-age-{display_name}", className="mb-0",
                                               style={"fontSize": "1.2rem"})
                                    ], body=True, className="text-center h-100 shadow-sm py-2"),
                                    width=12,
                                    lg=4,
                                    className="mb-2 mb-lg-0"
                                ),
                            ], className="mb-2"),
                            dbc.Row([
                                # Formation
                                dbc.Col(
                                    dbc.Card([
                                        html.H6("Formation", className="text-muted mb-1",
                                               style={"fontSize": "0.8rem"}),
                                        html.H3(id=f"formation-{display_name}", className="mb-0",
                                               style={"fontSize": "1.2rem"})
                                    ], body=True, className="text-center h-100 shadow-sm py-2"),
                                    width=12,
                                    lg=6,
                                    className="mb-2 mb-lg-0"
                                ),
                                # Total Salary
                                dbc.Col(
                                    dbc.Card([
                                        html.H6("Total Salary", className="text-muted mb-1",
                                               style={"fontSize": "0.8rem"}),
                                        html.H3(id=f"total-salary-{display_name}", className="mb-0",
                                               style={"fontSize": "1.2rem"})
                                    ], body=True, className="text-center h-100 shadow-sm py-2"),
                                    width=12,
                                    lg=6,
                                    className="mb-2 mb-lg-0"
                                ),
                            ]),
                        ], width=12, lg=9)
                    ])
                ])
            ], className="shadow-sm mb-4"),
            
            # Stats charts
            dbc.Row([
                # Wins/Draws/Losses chart
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Wins / Draws / Losses", className="text-center"),
                        dbc.CardBody(
                            dcc.Graph(
                                id=f'wdl-chart-{display_name}',
                                config={'displayModeBar': False}
                            )
                        )
                    ], className="shadow-sm"),
                    width=12,
                    lg=6,
                    className="mb-4"
                ),
                # Goals chart
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Goal Difference", className="text-center"),
                        dbc.CardBody(
                            dcc.Graph(
                                id=f'goals-chart-{display_name}',
                                config={'displayModeBar': False}
                            )
                        )
                    ], className="shadow-sm"),
                    width=12,
                    lg=6,
                    className="mb-4"
                )
            ]),
            
            # Players section
            dbc.Card([
                dbc.CardHeader(
                    html.H3("Squad", className="text-center m-0")
                ),
                dbc.CardBody([
                    # Goalkeepers
                    html.Div([
                        html.H4("Goalkeepers", className="mb-3"),
                        html.Div(id=f"goalkeeper-buttons-{display_name}", className="d-flex flex-wrap gap-2")
                    ], className="mb-4"),
                    
                    # Defenders
                    html.Div([
                        html.H4("Defenders", className="mb-3"),
                        html.Div(id=f"defender-buttons-{display_name}", className="d-flex flex-wrap gap-2")
                    ], className="mb-4"),
                    
                    # Midfielders
                    html.Div([
                        html.H4("Midfielders", className="mb-3"),
                        html.Div(id=f"midfielder-buttons-{display_name}", className="d-flex flex-wrap gap-2")
                    ], className="mb-4"),
                    
                    # Attackers
                    html.Div([
                        html.H4("Attackers", className="mb-3"),
                        html.Div(id=f"attacker-buttons-{display_name}", className="d-flex flex-wrap gap-2")
                    ])
                ])
            ], className="shadow-sm mb-4"),

            # Team Analysis Sections
            dbc.Card([
                dbc.CardHeader(
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                tab_id="tab-offensive",
                                label="Offensive Analysis ⚔️",
                                active_label_style={'color': '#1D3557'}
                            ),
                            dbc.Tab(
                                tab_id="tab-defensive",
                                label="Defensive Analysis 🛡️",
                                active_label_style={'color': '#1D3557'}
                            ),
                            dbc.Tab(
                                tab_id="tab-set-pieces",
                                label="Set Pieces Analysis 🎯",
                                active_label_style={'color': '#1D3557'}
                            ),
                        ],
                        id=f"analysis-tabs-{display_name}",
                        active_tab="tab-offensive",
                    )
                ),
                dbc.CardBody(
                    html.Div(id=f"analysis-content-{display_name}")
                )
            ], className="shadow-sm mb-4")
        ], fluid=True)
    ], className="bg-light min-vh-100")

def register_team_callbacks(app, team_name):
    """Register callbacks for a specific team"""
    
    # Use normalized team name for consistency between layout and callbacks
    display_name = normalize_team_variants(team_name)
    
    @app.callback(
        [
            Output(f"team-position-{display_name}", "children"),
            Output(f"market-value-{display_name}", "children"),
            Output(f"avg-age-{display_name}", "children"),
            Output(f"formation-{display_name}", "children"),
            Output(f"total-salary-{display_name}", "children")
        ],
        Input(f"trigger-update-{display_name}", "children")
    )
    def update_team_info(_):
        info = get_team_info(team_name, display_name)
        return [
            f"#{info['position']}",
            f"€{info['market_value']:.1f}M",
            f"{info['avg_age']:.1f} years",
            info['formation'].split()[0] if ' ' in info['formation'] else info['formation'],
            f"€{info['total_salary']:.2f}M"
        ]

    @app.callback(
        [Output(f"wdl-chart-{display_name}", "figure"),
         Output(f"goals-chart-{display_name}", "figure")],
        Input(f"trigger-update-{display_name}", "children")
    )
    def update_charts(_):
        stats = get_team_stats(display_name)
        wdl_fig = create_wdl_chart(stats["wins"], stats["draws"], stats["losses"])
        goals_fig = create_goals_chart(stats["goals_for"], stats["goals_against"])
        return wdl_fig, goals_fig

    @app.callback(
        [
            Output(f"goalkeeper-buttons-{display_name}", "children"),
            Output(f"defender-buttons-{display_name}", "children"),
            Output(f"midfielder-buttons-{display_name}", "children"),
            Output(f"attacker-buttons-{display_name}", "children")
        ],
        Input(f"trigger-update-{display_name}", "children")
    )
    def update_player_buttons(_):
        # Get the correct file name
        file_name = display_name
        if display_name == "Inter":
            file_name = "Internazionale"
        elif display_name == "Hellas Verona":
            file_name = "Hellas_Verona"
        
        # Read player data
        df = pd.read_csv(f"pages/data_serie_a_24-25/{file_name}.csv")
        
        # Extract primary position for each player
        df['primary_pos'] = df['Posc'].str.split(',').str[0]
        
        # Create buttons for each position group
        goalkeepers = [create_player_button(player) for player in df[df['primary_pos'] == 'PO']['Jugador']]
        defenders = [create_player_button(player) for player in df[df['primary_pos'] == 'DF']['Jugador']]
        midfielders = [create_player_button(player) for player in df[df['primary_pos'] == 'CC']['Jugador']]
        attackers = [create_player_button(player) for player in df[df['primary_pos'] == 'DL']['Jugador']]
        
        return goalkeepers, defenders, midfielders, attackers

    @app.callback(
        Output(f"analysis-content-{display_name}", "children"),
        Input(f"analysis-tabs-{display_name}", "active_tab")
    )
    def update_analysis_content(active_tab):
        if active_tab == "tab-offensive":
            return create_offensive_analysis(display_name)
        elif active_tab == "tab-defensive":
            return create_defensive_analysis(display_name)
        elif active_tab == "tab-set-pieces":
            return create_set_pieces_analysis(display_name)
        else:
            return html.Div("No analysis selected")

def get_team_layout(team_name):
    """Get the layout for a specific team"""
    return create_team_layout(team_name)

def draw_formation(team_name, formation="4-2-3-1", players=None):
    """Draw the team formation on a soccer field"""
    # Create empty figure with transparent background
    field = go.Figure()
    
    # Get top players for this team based on minutes played
    season = "24-25"
    file_name = get_file_name_for_team(team_name, "players")
    team_file = f"pages/data_serie_a_{season}/{file_name}.csv"
    
    default_players = {
        'GK': {'name': 'Goalkeeper', 'number': '1', 'minutes': 2000},
        'LB': {'name': 'Left Back', 'number': '3', 'minutes': 1800},
        'CB1': {'name': 'Centre Back', 'number': '4', 'minutes': 2000},
        'CB2': {'name': 'Centre Back', 'number': '5', 'minutes': 2000},
        'RB': {'name': 'Right Back', 'number': '2', 'minutes': 1800},
        'CDM1': {'name': 'Def Mid', 'number': '6', 'minutes': 1900},
        'CDM2': {'name': 'Def Mid', 'number': '8', 'minutes': 1900},
        'LW': {'name': 'Left Wing', 'number': '11', 'minutes': 1700},
        'CAM': {'name': 'Att Mid', 'number': '10', 'minutes': 1800},
        'RW': {'name': 'Right Wing', 'number': '7', 'minutes': 1700},
        'ST': {'name': 'Striker', 'number': '9', 'minutes': 1600}
    }
    
    # Try to get actual player data
    if os.path.exists(team_file):
        try:
            df = pd.read_csv(team_file)
            # Convert minutes to numeric
            if 'Mín' in df.columns:
                df['minutes'] = pd.to_numeric(df['Mín'].str.replace(',', ''), errors='coerce')
                
                # Get top players by position
                position_mapping = {
                    'PO': ['GK'],
                    'DF': ['LB', 'CB1', 'CB2', 'RB'],
                    'CC': ['CDM1', 'CDM2', 'CAM'],
                    'DL': ['LW', 'RW', 'ST']
                }
                
                # Extract primary position
                df['primary_pos'] = df['Posc'].str.split(',').str[0]
                
                for pos in position_mapping:
                    pos_players = df[df['primary_pos'] == pos].nlargest(len(position_mapping[pos]), 'minutes')
                    for i, (_, player) in enumerate(pos_players.iterrows()):
                        if i < len(position_mapping[pos]):
                            role = position_mapping[pos][i]
                            default_players[role] = {
                                'name': player['Jugador'],
                                'number': str(player.get('Número', i+1)),
                                'minutes': int(player['minutes']) if not pd.isna(player['minutes']) else 1500
                            }
        except Exception as e:
            print(f"Error loading player data for {team_name}: {e}")
    
    # Formation positions (x, y coordinates)
    positions = {
        'GK': (3, 50),     # Goalkeeper
        'LB': (20, 80),    # Left back
        'CB1': (20, 60),   # Left center back
        'CB2': (20, 40),   # Right center back
        'RB': (20, 20),    # Right back
        'CDM1': (45, 60),  # Left defensive mid
        'CDM2': (45, 40),  # Right defensive mid
        'LW': (75, 80),    # Left wing
        'CAM': (75, 50),   # Attacking mid
        'RW': (75, 20),    # Right wing
        'ST': (95, 50)     # Striker
    }
    
    # Find player with max minutes
    max_minutes = max(player['minutes'] for player in default_players.values())
    
    # Draw each player
    for position, coords in positions.items():
        player = default_players[position]
        
        # Add player marker
        field.add_trace(go.Scatter(
            x=[coords[0]],
            y=[coords[1]],
            mode='markers+text',
            text=player['number'],
            textposition='middle center',
            textfont=dict(
                color='white',
                size=14,
                family='Arial'
            ),
            marker=dict(
                size=30,
                color='#1D3557',
                line=dict(
                    color='#007bff' if player['minutes'] == max_minutes else '#dee2e6',
                    width=3
                )
            ),
            name=player['name'],
            hovertemplate=f"{player['name']}<br>{player['minutes']} minutes<extra></extra>",
            showlegend=False
        ))
        
        # Add player name
        field.add_trace(go.Scatter(
            x=[coords[0]],
            y=[coords[1] - 8],
            mode='text',
            text=player['name'],
            textposition='top center',
            textfont=dict(
                color='white',
                size=11,
                family='Arial',
                weight='bold'
            ),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Update layout
    field.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            range=[0, 100],
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=False,
            fixedrange=True
        ),
        yaxis=dict(
            range=[0, 100],
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=False,
            scaleanchor='x',
            scaleratio=1,
            fixedrange=True
        )
    )
    
    return dcc.Graph(
        figure=field,
        config={
            'displayModeBar': False,
            'staticPlot': True
        },
        style={
            'height': '100%',
            'width': '100%',
            'backgroundColor': 'transparent'
        }
    )

def create_offensive_analysis(display_name):
    """Create offensive analysis for any Serie A team using the exact Juventus structure"""
    try:
        # Determine comparison group
        top_performing_teams = ['Atalanta', 'Napoli', 'Inter']
        
        if display_name in top_performing_teams:
            # Compare with top 4
            comparison_teams = ['Napoli', 'Inter', 'Atalanta', 'Juventus']
            comparison_label = "Top 4"
        else:
            # Compare with Serie A average
            comparison_teams = None  # Will use all teams
            comparison_label = "Serie A Avg"

        # Get team file name mapping
        file_team_name = display_name
        if display_name == "Inter":
            file_team_name = "Internazionale"
        elif display_name == "Hellas Verona":
            file_team_name = "Hellas_Verona"
        
        # Load Serie A data for build-up analysis
        df_serie_a = pd.read_csv("pages/data_serie_a_24-25/Serie_A_24-25.csv")
        
        # Build-up metrics and their max reference values
        metrics = {
            'PrgP': {'name': 'Progressive Passes', 'max': 1600},
            'PrgC': {'name': 'Progressive Carries', 'max': 900},
            'Pos': {'name': 'Possession %', 'max': 65},
            '% Cmp': {'name': 'Pass Accuracy %', 'max': 90},
            '3º_cent': {'name': 'Central Third Touches', 'max': 12000},
            'Dist. prg.': {'name': 'Progressive Distance', 'max': 100000}
        }
        
        # Create first radar chart for build-up analysis
        fig1 = go.Figure()
        
        # Add team trace
        team_data = df_serie_a[df_serie_a['Equipo'] == display_name].iloc[0]
        team_values = [(team_data[metric] / metrics[metric]['max']) for metric in metrics.keys()]
        team_values.append(team_values[0])  # Close the polygon
        
        fig1.add_trace(go.Scatterpolar(
            r=team_values,
            theta=[metrics[m]['name'] for m in metrics.keys()] + [metrics[list(metrics.keys())[0]]['name']],
            fill='toself',
            name=display_name,
            line=dict(color='#000000'),
            fillcolor='rgba(0,0,0,0.2)'
        ))

        # Add comparison trace
        if comparison_teams:
            # Top teams comparison
            comparison_df = df_serie_a[df_serie_a['Equipo'].isin(comparison_teams)]
            comparison_avg = comparison_df[list(metrics.keys())].mean()
        else:
            # Serie A average
            comparison_avg = df_serie_a[list(metrics.keys())].mean()
            
        comparison_values = [(comparison_avg[metric] / metrics[metric]['max']) for metric in metrics.keys()]
        comparison_values.append(comparison_values[0])  # Close the polygon
        
        fig1.add_trace(go.Scatterpolar(
            r=comparison_values,
            theta=[metrics[m]['name'] for m in metrics.keys()] + [metrics[list(metrics.keys())[0]]['name']],
            fill='toself',
            name=f'{comparison_label} Average',
            line=dict(color='#4A90E2'),
            fillcolor='rgba(74,144,226,0.2)'
        ))
        
        fig1.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title=f"Build-up Analysis vs {comparison_label}",
            title_x=0.5
        )

        # Load Wyscout data for detailed attacking analysis
        wyscout_file = f"pages/data_serie_a_24-25/{file_team_name}_wyscout.csv"
        if not os.path.exists(wyscout_file):
            return html.Div(f"Wyscout data not available for {display_name}")
            
        df_wyscout = pd.read_csv(wyscout_file, sep=';')
        
        # Filter only team data
        df_wyscout = df_wyscout[df_wyscout['Equipo'] == display_name]
        
        # Calculate per game metrics
        attack_types = {
            'Positional Attacks': df_wyscout['Ataques posicionales / con remate'].mean(),
            'Counter Attacks': df_wyscout['Contraataques / con remate'].mean()
        }
        
        # Calculate percentages
        total_attacks = sum(attack_types.values())
        attack_percentages = {k: (v/total_attacks)*100 for k, v in attack_types.items()}
        
        # Attack distribution chart
        attack_fig = go.Figure(data=[
            go.Bar(
                y=list(attack_types.keys()),
                x=list(attack_types.values()),
                orientation='h',
                marker_color=['#1D3557', '#457B9D'],
                text=[f'{v:.1f} ({attack_percentages[k]:.1f}%)' for k, v in attack_types.items()],
                textposition='auto',
                name='Total Attacks'
            )
        ])
        
        attack_fig.update_layout(
            title="Attack Type Distribution per Game",
            xaxis_title="Average per Game",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=200,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=False
            ),
            yaxis=dict(
                showgrid=False
            ),
            bargap=0.3
        )
        
        # Build-up style metrics
        team_wyscout = df_wyscout[df_wyscout['Equipo'] == display_name]
        pass_types = {
            'Lateral Passes': team_wyscout['Pases laterales / logrados'].mean(),
            'Long Passes': team_wyscout['Pases largos / logrados'].mean(),
            'Final Third Passes': team_wyscout['Pases en el último tercio / logrados'].mean(),
            'Deep Passes': team_wyscout['Pases en profundidad completados'].mean(),
            'Progressive Passes': team_wyscout['Pases progresivos / precisos'].mean(),
            'Crosses': team_wyscout['Centros / precisos'].mean()
        }
        
        # Create horizontal bar chart for pass types
        build_up_fig = go.Figure()
        
        colors = {
            'Lateral Passes': '#A8DADC',
            'Long Passes': '#457B9D',
            'Final Third Passes': '#1D3557',
            'Deep Passes': '#2A6F97',
            'Progressive Passes': '#073B4C',
            'Crosses': '#E63946'
        }

        # Add bars
        build_up_fig.add_trace(go.Bar(
            x=list(pass_types.values()),
            y=list(pass_types.keys()),
            orientation='h',
            marker_color=[colors[type_] for type_ in pass_types.keys()],
            text=[f'{value:.1f}' for value in pass_types.values()],
            textposition='outside',
            textfont=dict(size=12),
            hovertemplate='%{y}: %{x:.1f}<extra></extra>'
        ))

        # Update layout
        build_up_fig.update_layout(
            title="Pass Type Distribution per Game",
            title_x=0.5,
            xaxis_title="Average per Game",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            margin=dict(l=20, r=100, t=40, b=20),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=False
            ),
            yaxis=dict(
                showgrid=False,
                autorange="reversed"
            ),
            bargap=0.3,
            showlegend=False
        )
        
        # Key stats
        key_stats = html.Div([
            html.H5("Key Stats per Game", className="text-center mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Box Touches", className="card-title"),
                            html.H3(f"{df_wyscout['Toques en el área de penalti'].mean():.1f}")
                        ])
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Box Entries", className="card-title"),
                            html.H3(f"{df_wyscout['Entradas al área de penalti (carreras / pases cruzados)'].mean():.1f}")
                        ])
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Pass Intensity", className="card-title"),
                            html.H3(f"{df_wyscout['Intensidad de paso'].mean():.1f}")
                        ])
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("PPDA", className="card-title"),
                            html.H3(f"{df_wyscout['PPDA'].mean():.1f}")
                        ])
                    ], className="text-center")
                ], width=3)
            ], className="mb-4")
        ])
        
        # Text analysis - dynamic based on comparison
        if comparison_teams:
            comp_pass_acc = comparison_df['% Cmp'].mean()
            comp_possession = comparison_df['Pos'].mean()
            comp_prog_carries = comparison_df['PrgC'].mean()
            comp_central_touches = comparison_df['3º_cent'].mean()
        else:
            comp_pass_acc = df_serie_a['% Cmp'].mean()
            comp_possession = df_serie_a['Pos'].mean()
            comp_prog_carries = df_serie_a['PrgC'].mean()
            comp_central_touches = df_serie_a['3º_cent'].mean()

        build_up_analysis = html.Div([
            html.H5("Build-up Analysis", className="text-center mb-4"),
            html.P([
                f"{display_name} shows the following build-up characteristics:",
                html.Ul([
                    html.Li(f"Pass accuracy: {team_data['% Cmp']:.1f}% (vs {comp_pass_acc:.1f}% {comparison_label} avg)"),
                    html.Li(f"Possession: {team_data['Pos']:.1f}% (vs {comp_possession:.1f}% {comparison_label} avg)"),
                    html.Li(f"Progressive carries: {team_data['PrgC']:.0f} (vs {comp_prog_carries:.0f} {comparison_label} avg)"),
                    html.Li(f"Central third touches: {team_data['3º_cent']:,.0f} (vs {comp_central_touches:,.0f} {comparison_label} avg)")
                ])
            ])
        ], className="mt-4")

        attacking_analysis = html.Div([
            html.H5("Attacking Style Analysis", className="text-center mb-4"),
            html.P([
                f"{display_name} attacking patterns show:",
                html.Ul([
                    html.Li(f"Preference for positional attacks ({attack_types['Positional Attacks']:.1f} per game) over counter-attacks ({attack_types['Counter Attacks']:.1f} per game)"),
                    html.Li(f"Box presence with {df_wyscout['Toques en el área de penalti'].mean():.1f} touches in the box per game"),
                    html.Li(f"Build-up primarily through progressive passes ({pass_types['Progressive Passes']:.1f} per game) and deep passes ({pass_types['Deep Passes']:.1f} per game)"),
                    html.Li(f"Pass intensity of {df_wyscout['Intensidad de paso'].mean():.1f}, indicating a controlled approach to build-up")
                ])
            ])
        ], className="mt-4")
        
        # Finishing quality analysis
        finishing_metrics = {
            'npxG/Sh': {'name': 'Shot Quality (npxG/Shot)', 'max': 0.15},
            'G/T': {'name': 'Conversion Rate', 'max': 0.20},
            'TalArc/90': {'name': 'Shots on Target per 90', 'max': 6.0},
            'Gls./90': {'name': 'Goals per 90', 'max': 2.5}
        }

        # Create finishing quality radar chart
        finishing_fig = go.Figure()

        # Calculate team values
        team_values = {
            'npxG/Sh': team_data['npxG/90'] / team_data['T/90'] if team_data['T/90'] > 0 else 0,
            'G/T': team_data['G/T'],
            'TalArc/90': team_data['TalArc/90'],
            'Gls./90': team_data['Gls./90']
        }

        # Normalize values between 0 and 1
        team_normalized = []
        for metric in finishing_metrics.keys():
            value = team_values[metric]
            max_val = finishing_metrics[metric]['max']
            value = value / max_val
            value = min(max(value, 0), 1)
            team_normalized.append(value)
        
        team_normalized.append(team_normalized[0])

        # Add team trace
        finishing_fig.add_trace(go.Scatterpolar(
            r=team_normalized,
            theta=[metrics['name'] for metrics in finishing_metrics.values()] + [finishing_metrics[list(finishing_metrics.keys())[0]]['name']],
            fill='toself',
            name=display_name,
            line=dict(color='#000000'),
            fillcolor='rgba(0,0,0,0.2)'
        ))

        # Calculate comparison average
        if comparison_teams:
            comparison_data = df_serie_a[df_serie_a['Equipo'].isin(comparison_teams)]
        else:
            comparison_data = df_serie_a
            
        comparison_avg = {
            'npxG/Sh': (comparison_data['npxG/90'] / comparison_data['T/90']).mean(),
            'G/T': comparison_data['G/T'].mean(),
            'TalArc/90': comparison_data['TalArc/90'].mean(),
            'Gls./90': comparison_data['Gls./90'].mean()
        }

        # Normalize comparison values
        comparison_normalized = []
        for metric in finishing_metrics.keys():
            value = comparison_avg[metric]
            max_val = finishing_metrics[metric]['max']
            value = value / max_val
            value = min(max(value, 0), 1)
            comparison_normalized.append(value)
        
        comparison_normalized.append(comparison_normalized[0])

        # Add comparison trace
        finishing_fig.add_trace(go.Scatterpolar(
            r=comparison_normalized,
            theta=[metrics['name'] for metrics in finishing_metrics.values()] + [finishing_metrics[list(finishing_metrics.keys())[0]]['name']],
            fill='toself',
            name=f'{comparison_label} Average',
            line=dict(color='#4A90E2'),
            fillcolor='rgba(74,144,226,0.2)'
        ))

        finishing_fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title=f"Finishing Quality Analysis vs {comparison_label}",
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400
        )

        finishing_analysis = html.Div([
            html.H5("Finishing Quality Analysis", className="text-center mb-4"),
            html.P([
                f"Analysis of {display_name} finishing quality compared to {comparison_label}:",
                html.Ul([
                    html.Li(f"Shot Quality: {team_values['npxG/Sh']:.3f} npxG per shot ({comparison_label} avg: {comparison_avg['npxG/Sh']:.3f})"),
                    html.Li(f"Conversion Rate: {team_values['G/T']*100:.1f}% of shots scored ({comparison_label} avg: {comparison_avg['G/T']*100:.1f}%)"),
                    html.Li(f"Shots on Target per 90: {team_values['TalArc/90']:.2f} ({comparison_label} avg: {comparison_avg['TalArc/90']:.2f})"),
                    html.Li(f"Goals per 90: {team_values['Gls./90']:.2f} ({comparison_label} avg: {comparison_avg['Gls./90']:.2f})")
                ])
            ])
        ], className="mt-4")

        return html.Div([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=fig1)
                ], width=12, className="mb-4"),
                dbc.Col([
                    build_up_analysis
                ], width=12, className="mb-4"),
                dbc.Col([
                    dcc.Graph(figure=attack_fig)
                ], width=12, className="mb-4"),
                dbc.Col([
                    dcc.Graph(figure=build_up_fig)
                ], width=12, className="mb-4"),
                dbc.Col([
                    key_stats
                ], width=12, className="mb-4"),
                dbc.Col([
                    attacking_analysis
                ], width=12, className="mb-4"),
                dbc.Col([
                    dcc.Graph(figure=finishing_fig)
                ], width=12, className="mb-4"),
                dbc.Col([
                    finishing_analysis
                ], width=12, className="mb-4")
            ])
        ])
        
    except Exception as e:
        return html.Div(f"Error loading offensive analysis: {str(e)}")

def create_defensive_analysis(display_name):
    """Create defensive analysis for any Serie A team using the exact Juventus structure"""
    try:
        # Get team file name mapping
        file_team_name = display_name
        if display_name == "Inter":
            file_team_name = "Internazionale"
        elif display_name == "Hellas Verona":
            file_team_name = "Hellas_Verona"
        
        # Load Wyscout data
        wyscout_file = f"pages/data_serie_a_24-25/{file_team_name}_wyscout.csv"
        if not os.path.exists(wyscout_file):
            return html.Div(f"Wyscout data not available for {display_name}")
            
        df_wyscout = pd.read_csv(wyscout_file, sep=';')
        
        # Load Serie A data for defensive quality analysis
        df_serie_a = pd.read_csv("pages/data_serie_a_24-25/Serie_A_24-25.csv")
        
        defensive_style_analysis = create_defensive_style_analysis_dynamic(df_wyscout, display_name)
        defensive_quality_analysis = create_defensive_quality_analysis_dynamic(df_serie_a, display_name)
        
        return html.Div([
            html.H4("Defensive Analysis", className="text-center mb-4"),
            defensive_style_analysis,
            html.Hr(className="my-4"),
            defensive_quality_analysis
        ])
        
    except Exception as e:
        return html.Div(f"Error loading defensive analysis: {str(e)}")

def create_set_pieces_analysis(display_name):
    """Create set pieces analysis for any Serie A team using the exact Juventus structure"""
    try:
        # Determine comparison group
        top_performing_teams = ['Atalanta', 'Napoli', 'Inter']
        
        if display_name in top_performing_teams:
            # Compare with top 4
            comparison_teams = ['Napoli', 'Inter', 'Atalanta', 'Juventus']
            comparison_label = "Top 4"
        else:
            # Compare with Serie A average
            comparison_teams = None
            comparison_label = "Serie A"

        # Get team file name mapping
        file_team_name = display_name
        if display_name == "Inter":
            file_team_name = "Internazionale"
        elif display_name == "Hellas Verona":
            file_team_name = "Hellas_Verona"
        
        # Load data
        df_serie_a = pd.read_csv("pages/data_serie_a_24-25/Serie_A_24-25.csv")
        
        wyscout_file = f"pages/data_serie_a_24-25/{file_team_name}_wyscout.csv"
        if not os.path.exists(wyscout_file):
            return html.Div(f"Wyscout data not available for {display_name}")
            
        df_wyscout = pd.read_csv(wyscout_file, sep=";")
        
        # Calculate set piece metrics for Serie A data
        def calculate_set_piece_metrics(df):
            df_metrics = df.copy()
            # Convert columns to numeric, replacing any non-numeric values with NaN
            numeric_cols = ['PassDead', 'PassDead_GCA', 'FK', '90 s']
            for col in numeric_cols:
                df_metrics[col] = pd.to_numeric(df_metrics[col], errors='coerce')
            
            # Calculate derived metrics
            df_metrics['PassDead_GCA90'] = df_metrics['PassDead_GCA'] / df_metrics['90 s']
            df_metrics['FK_per90'] = df_metrics['FK'] / df_metrics['90 s']
            df_metrics['FK_Efficiency'] = (df_metrics['PassDead_GCA'] / df_metrics['FK'] * 100).fillna(0)
            
            return df_metrics[['Equipo', 'PassDead_GCA90', 'FK_per90', 'FK_Efficiency']]
        
        # Process Serie A data
        df_processed = calculate_set_piece_metrics(df_serie_a)
        
        if comparison_teams:
            target_df = df_processed[df_processed['Equipo'].isin(comparison_teams)]
        else:
            target_df = df_processed
        
        # Calculate averages for insights (only numeric columns)
        numeric_columns = ['PassDead_GCA90', 'FK_per90', 'FK_Efficiency']
        target_avg = target_df[numeric_columns].mean()
        team_data = df_processed[df_processed['Equipo'] == display_name].iloc[0]
        
        # Create radar chart
        metric_labels = {
            'PassDead_GCA90': 'Set Goals',
            'FK_per90': 'Free Kicks',
            'FK_Efficiency': 'Set Efficiency'
        }
        
        # Define fixed maximum values for each metric
        max_values = {
            'PassDead_GCA90': 0.3,
            'FK_per90': 15.5,
            'FK_Efficiency': 3.0
        }
        
        fig_radar = go.Figure()
        
        # Add team trace
        team_normalized_values = [team_data[col] * (2.5 / max_values[col]) for col in numeric_columns]
        fig_radar.add_trace(go.Scatterpolar(
            r=team_normalized_values,
            theta=[metric_labels[col] for col in numeric_columns],
            name=display_name,
            fill='toself',
            line=dict(color='#000000'),
            fillcolor='rgba(0,0,0,0.2)'
        ))
        
        # Add comparison average trace
        avg_normalized_values = [target_avg[col] * (2.5 / max_values[col]) for col in numeric_columns]
        fig_radar.add_trace(go.Scatterpolar(
            r=avg_normalized_values,
            theta=[metric_labels[col] for col in numeric_columns],
            name=f'{comparison_label} Average',
            fill='toself',
            line=dict(color='#4A90E2'),
            fillcolor='rgba(74,144,226,0.2)'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 2.5]
                )),
            showlegend=True,
            title=f"Set Pieces Effectiveness - {display_name} vs {comparison_label}"
        )
        
        # Process Wyscout data for detailed team analysis
        team_wyscout = df_wyscout.copy()
        corners_total = team_wyscout['Córneres / con remate'].mean()
        corners_shots = team_wyscout['Unnamed: 39'].mean()
        freekicks_total = team_wyscout['Tiros libres / con remate'].mean()
        freekicks_shots = team_wyscout['Unnamed: 42'].mean()
        
        # Create bar chart for team detailed analysis
        fig_detail = go.Figure(data=[
            go.Bar(name='Total', x=['Corner Kicks', 'Free Kicks'], 
                  y=[corners_total, freekicks_total]),
            go.Bar(name='With Shot', x=['Corner Kicks', 'Free Kicks'], 
                  y=[corners_shots, freekicks_shots])
        ])
        
        fig_detail.update_layout(
            barmode='group',
            title=f"{display_name} Set Pieces Analysis - Average per Match",
            yaxis_title="Count"
        )
        
        # Generate insights
        def generate_insights(team_data, target_avg):
            insights = []
            metrics_info = {
                'PassDead_GCA90': ('Goal-Creating Actions from Set Pieces per 90', 'higher'),
                'FK_per90': ('Free Kicks per 90', 'neutral'),
                'FK_Efficiency': ('Free Kick Efficiency (%)', 'higher')
            }
            
            for metric, (metric_name, preference) in metrics_info.items():
                team_value = team_data[metric]
                avg_value = target_avg[metric]
                diff_pct = ((team_value - avg_value) / avg_value) * 100
                
                if abs(diff_pct) > 10:  # Only show significant differences
                    if diff_pct > 0:
                        color = "success" if preference == "higher" else "warning"
                        text = f"{display_name} excels in {metric_name}, performing {abs(diff_pct):.1f}% better than the {comparison_label} average"
                    else:
                        color = "warning" if preference == "higher" else "success"
                        text = f"{display_name} shows room for improvement in {metric_name}, performing {abs(diff_pct):.1f}% below the {comparison_label} average"
                    
                    insights.append(dbc.Alert(text, color=color, className="mb-2"))
            
            return insights
        
        insights = generate_insights(team_data, target_avg)
        
        # Return the complete layout
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Set Pieces Effectiveness", className="mb-0")),
                        dbc.CardBody([
                            dcc.Graph(figure=fig_radar)
                        ])
                    ], className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader(html.H5("Key Insights", className="mb-0")),
                        dbc.CardBody(insights)
                    ])
                ], width=12, lg=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Detailed Analysis", className="mb-0")),
                        dbc.CardBody([
                            dcc.Graph(figure=fig_detail)
                        ])
                    ])
                ], width=12, lg=6)
            ])
        ])
        
    except Exception as e:
        return html.Div(f"Error loading set pieces analysis: {str(e)}")

def create_defensive_style_analysis_dynamic(df_wyscout, team_name):
    """Create defensive style analysis for any team"""
    # Filter opponents only (not the team itself)
    df_opponents = df_wyscout[
        (df_wyscout['Competición'] == 'Italy. Serie A') & 
        (df_wyscout['Equipo'] != team_name)
    ].copy()

    # Calculate percentages for different types of ball recoveries
    df_opponents['% Recuperi Bassi'] = df_opponents['Unnamed: 20'].astype(float) / df_opponents['Balones recuperados /bajos / medios / altos'].astype(float) * 100
    df_opponents['% Recuperi Medi'] = df_opponents['Unnamed: 21'].astype(float) / df_opponents['Balones recuperados /bajos / medios / altos'].astype(float) * 100
    df_opponents['% Recuperi Alti'] = df_opponents['Unnamed: 22'].astype(float) / df_opponents['Balones recuperados /bajos / medios / altos'].astype(float) * 100
    
    # Calculate percentage of defensive duels won
    df_opponents['% Duelli Difensivi Vinti'] = df_opponents['Unnamed: 65'].astype(float) / df_opponents['Duelos defensivos / ganados'].astype(float) * 100
    
    # Calculate percentage of long passes successful
    df_opponents['% Passaggi Lunghi Riusciti'] = df_opponents['Unnamed: 88'].astype(float) / df_opponents['Pases largos / logrados'].astype(float) * 100

    # Define playing styles based on PPDA and pass intensity
    def get_playing_style(row):
        if row['PPDA'] < df_opponents['PPDA'].median():
            if row['Intensidad de paso'] < df_opponents['Intensidad de paso'].median():
                return 'Passive Build-up'
            else:
                return 'Fast Transitions'
        else:
            if row['Intensidad de paso'] < df_opponents['Intensidad de paso'].median():
                return 'Deep Press'
            else:
                return 'Pressure & Possession'
    
    df_opponents['Style'] = df_opponents.apply(get_playing_style, axis=1)

    # Metrics for radar chart
    metrics = {
        'PPDA': {'name': 'PPDA', 'max': 25},
        '% Duelli Difensivi Vinti': {'name': 'Defensive Duels Won %', 'max': 80},
        'Faltas': {'name': 'Fouls', 'max': 15},
        'Interceptaciones': {'name': 'Interceptions', 'max': 45},
        '% Recuperi Alti': {'name': 'High Recovery %', 'max': 30},
        '% Passaggi Lunghi Riusciti': {'name': 'Long Passes Success %', 'max': 80}
    }

    # Create radar chart
    radar_fig = go.Figure()
    
    colors = {
        'Passive Build-up': '#1D3557',
        'Fast Transitions': '#457B9D',
        'Deep Press': '#E63946',
        'Pressure & Possession': '#A8DADC'
    }
    
    for style in df_opponents['Style'].unique():
        style_data = df_opponents[df_opponents['Style'] == style]
        values = []
        for metric in metrics.keys():
            value = style_data[metric].astype(float).mean() / metrics[metric]['max']
            values.append(value)
        values.append(values[0])  # Close polygon
        
        radar_fig.add_trace(go.Scatterpolar(
            r=values,
            theta=[metrics[m]['name'] for m in metrics.keys()] + [metrics[list(metrics.keys())[0]]['name']],
            fill='toself',
            name=style,
            line=dict(color=colors[style]),
            fillcolor=colors[style].replace(')', ', 0.2)').replace('rgb', 'rgba'),
        ))

    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                showline=True,
                linewidth=1,
                gridcolor='rgba(0,0,0,0.1)',
                gridwidth=1
            ),
            angularaxis=dict(
                gridcolor='rgba(0,0,0,0.1)',
                gridwidth=1,
                linewidth=1,
                showline=True,
                linecolor='rgba(0,0,0,0.3)'
            ),
            bgcolor='rgba(255,255,255,0.95)'
        ),
        showlegend=True,
        title=f'{team_name} Defensive Performance vs Different Playing Styles',
        height=600,
        margin=dict(t=100, b=50, l=50, r=50)
    )

    # Create ball recovery distribution chart
    recovery_fig = go.Figure()
    for style in df_opponents['Style'].unique():
        style_data = df_opponents[df_opponents['Style'] == style]
        recovery_fig.add_trace(go.Bar(
            name=style,
            x=['Low', 'Medium', 'High'],
            y=[
                style_data['% Recuperi Bassi'].mean(),
                style_data['% Recuperi Medi'].mean(),
                style_data['% Recuperi Alti'].mean()
            ],
            text=[f"{val:.1f}%" for val in [
                style_data['% Recuperi Bassi'].mean(),
                style_data['% Recuperi Medi'].mean(),
                style_data['% Recuperi Alti'].mean()
            ]],
            textposition='auto',
        ))

    recovery_fig.update_layout(
        title='Ball Recovery Distribution by Opposition Style',
        yaxis_title='Percentage of Recoveries',
        barmode='group',
        height=400
    )

    # Generate automatic insights
    insights = []
    for style in df_opponents['Style'].unique():
        style_data = df_opponents[df_opponents['Style'] == style]
        
        # PPDA analysis
        ppda_avg = style_data['PPDA'].astype(float).mean()
        if ppda_avg < df_opponents['PPDA'].astype(float).mean():
            insights.append(f"✅ Strong pressing performance against {style} teams (PPDA: {ppda_avg:.2f})")
        
        # Defensive duels analysis
        duels_won = style_data['% Duelli Difensivi Vinti'].mean()
        if duels_won > 50:
            insights.append(f"💪 Good defensive duel success rate against {style} teams ({duels_won:.1f}%)")
        
        # High ball recoveries analysis
        high_recoveries = style_data['% Recuperi Alti'].mean()
        if high_recoveries > df_opponents['% Recuperi Alti'].mean():
            insights.append(f"🔄 Above average high ball recoveries against {style} teams ({high_recoveries:.1f}%)")

    return html.Div([
        dcc.Graph(figure=radar_fig),
        html.H4("Ball Recovery Analysis", className="mt-4"),
        dcc.Graph(figure=recovery_fig),
        html.Div([
            html.H5("Key Defensive Insights", className="mt-4"),
            html.Ul([html.Li(insight) for insight in insights], className="mt-3")
        ], className="mt-4")
    ])

def create_defensive_quality_analysis_dynamic(df_serie_a, team_name):
    """Create defensive quality analysis for any team"""
    # Determine comparison group
    top_performing_teams = ['Atalanta', 'Napoli', 'Inter']
    
    if team_name in top_performing_teams:
        # Compare with top 4
        comparison_teams = ['Napoli', 'Inter', 'Atalanta', 'Juventus']
        comparison_label = "Top 4"
    else:
        # Compare with Serie A average
        comparison_teams = None
        comparison_label = "Serie A"
    
    # Load classification data
    clasificacion = pd.read_csv("pages/data_serie_a_24-25/clasificacion.csv")
    
    if comparison_teams:
        target_df = clasificacion[clasificacion['Equipo'].isin(comparison_teams)].copy()
    else:
        target_df = clasificacion.copy()
    
    # Calculate GC90 and xGA90
    target_df['GC90'] = target_df['GC'] / target_df['PJ']
    target_df['xGA90'] = target_df['xGA'] / target_df['PJ']
    
    # Merge with Serie A data for other statistics
    target_df = target_df.merge(
        df_serie_a[['Equipo', 'Tkl_%', 'Exitosa%', 'Bloqueos_totales', 'Intercepciones', 'Errores', 'Tkl+Int']], 
        on='Equipo',
        how='left'
    )
    
    # Define metrics and their maximum values
    metrics = {
        'GC90': {'name': 'Goals Conceded/90', 'max': 2.0},
        'xGA90': {'name': 'xG Against/90', 'max': 2.0},
        'Tkl_%': {'name': 'Tackle Success %', 'max': 65},
        'Exitosa%': {'name': 'Duels Won %', 'max': 60},
        'Bloqueos_totales': {'name': 'Blocks', 'max': 400},
        'Intercepciones': {'name': 'Interceptions', 'max': 300},
        'Errores': {'name': 'Errors (Inverse)', 'max': 30},
        'Tkl+Int': {'name': 'Defensive Actions', 'max': 900}
    }

    # Invert errors (higher is better)
    max_errores = target_df['Errores'].max()
    target_df['Errores'] = max_errores - target_df['Errores']

    # Create radar chart
    radar_fig = go.Figure()

    # Add team trace
    team_data = target_df[target_df['Equipo'] == team_name]
    if not team_data.empty:
        team_values = []
        for metric in metrics.keys():
            value = team_data[metric].iloc[0] / metrics[metric]['max']
            value = min(max(value, 0), 1)  # Clamp between 0 and 1
            team_values.append(value)
        team_values.append(team_values[0])  # Close polygon

        radar_fig.add_trace(go.Scatterpolar(
            r=team_values,
            theta=[metrics[m]['name'] for m in metrics.keys()] + [metrics[list(metrics.keys())[0]]['name']],
            fill='toself',
            name=team_name,
            line=dict(color='#000000'),
            fillcolor='rgba(0,0,0,0.2)'
        ))

    # Add comparison average trace
    comparison_values = []
    for metric in metrics.keys():
        value = target_df[metric].mean() / metrics[metric]['max']
        value = min(max(value, 0), 1)  # Clamp between 0 and 1
        comparison_values.append(value)
    comparison_values.append(comparison_values[0])  # Close polygon

    radar_fig.add_trace(go.Scatterpolar(
        r=comparison_values,
        theta=[metrics[m]['name'] for m in metrics.keys()] + [metrics[list(metrics.keys())[0]]['name']],
        fill='toself',
        name=f'{comparison_label} Average',
        line=dict(color='#4A90E2'),
        fillcolor='rgba(74,144,226,0.2)'
    ))

    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title=f"Defensive Quality Analysis - {team_name} vs {comparison_label}",
        title_x=0.5,
        height=500
    )

    return html.Div([
        dcc.Graph(figure=radar_fig)
    ]) 