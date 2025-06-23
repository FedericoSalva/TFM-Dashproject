import dash
from dash import dcc, html, dash_table, callback, ALL
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime
from utils.name_standardization import standardize_player_name, get_source_name_column
from unidecode import unidecode
import csv
from urllib.parse import parse_qs
from dash import callback_context

# === CONFIGURAZIONE CAMPIONATI E PESI ===
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

# === PATH CONFIGURATION ===
BASE_PATH = "/Users/federico/dash_project"
PLAYERS_PHOTOS_PATH = "/assets/Players"

# Mappatura per gestire le differenze tra nomi squadre nei dati e nomi file loghi
TEAM_LOGO_MAPPING = {
    # Serie A
    'Internazionale': 'Inter',
    'Hellas_Verona': 'Hellas_Verona',
    'Como': 'Como',
    'Lazio': 'Lazio',
    'Udinese': 'Udinese',
    'Empoli': 'Empoli',
    'Juventus': 'Juventus',
    'Fiorentina': 'Fiorentina',
    'Roma': 'Roma',
    'Torino': 'Torino',
    'Napoli': 'Napoli',
    'Monza': 'Monza',
    'Bologna': 'Bologna',
    'Cagliari': 'Cagliari',
    'Genoa': 'Genoa',
    'Parma': 'Parma',
    'Lecce': 'Lecce',
    'Venezia': 'Venezia',
    'Atalanta': 'Atalanta',
    'Milan': 'Milan',
    
    # Bundesliga
    'Monchengladbach': 'Borussia_Mönchengladbach',
    'Dortmund': 'Borussia_Dortmund',
    
    # EPL
    'Bournemouth': 'Bornemouth',
    'Wolverhampton_Wanderers': 'Wolverhampton',
    'West_Ham_United': 'West_Ham',
    'Leicester_City': 'Leicester',
    'Brighton_and_Hove_Albion': 'Brighton',
    'Tottenham_Hotspur': 'Tottenham',
    
    # Primeira Liga
    'Vitoria_Guimaraes': 'Vitória_Guimarães',
    
    # La Liga
    'Alaves': 'Alavés',
    'Leganes': 'Leganés',
    
    # Ligue 1
    'Paris_Saint_Germain': 'Paris_Saint-Germain',
    'Saint_Etienne': 'Saint-Étienne',
    
    # Championship
    'Queens_Park_Rangers': 'QPR',
    'Sheffield_United': 'Sheffield_Utd',
    'Sheffield_Wednesday': 'Sheffield_Weds',
    'West_Bromwich_Albion': 'West_Brom',
    'Preston_North_End': 'Preston',
    'Blackburn_Rovers': 'Blackburn',
    
    # Eredivisie
    'Willem_II': 'Willem_II_Tilburg',
    
    # Süper Lig
    'BB_Bodrumspor': 'Bodrum_FK',
    'Başakşehir': 'Basaksehir',
    'Beşiktaş': 'Besiktas',
    'Eyüpspor': 'Eyupspor',
    'Göztepe': 'Goztepe',
    'Kasımpaşa': 'Kasimpasa',
    
    # MLS
    'Atlanta_Utd': 'Atlanta_United',
    'CF_Montréal': 'CF_Montreal',
    'D.C_United': 'DC_United',
    'Minnesota_Utd': 'Minnesota_United',
    'NE_Revolution': 'New_England_Revolution',
    'NY_Red_Bulls': 'New_York_Red_Bulls',
    'Portland_Timbers': 'Portland Timbers',
    'SJ_Earthquakes': 'San Jose Earthquakes',
    'Sporting_KC': 'Sporting Kansas City',
    'St_Louis': 'St. Louis City',
    'Toronto_FC': 'Toronto FC',
    'Charlotte': 'Charlotte_FC'
}

# Mappatura per i percorsi delle cartelle delle leghe
LEAGUE_FOLDER_MAPPING = {
    'Serie_A': 'Serie_A/2024-2025',
    'EPL': 'EPL',
    'La_Liga': 'La_Liga',
    'Bundesliga': 'Bundesliga',
    'Ligue_1': 'Ligue_1',
    'Primeira_Liga': 'Primeira_Liga',
    'Eredivisie': 'Eredivisie',
    'Championship': 'Championship',
    'Süper_Lig': 'Süper_Lig',
    'MLS': 'MLS',
    'Bundesliga_2': 'Bundesliga_2',
    'Ligue_2': 'Ligue_2',
    'Serie_B': 'Serie_B',
    'Liga_Argentina': 'Liga_Argentina',
    'Jupiler_Pro_League': 'Jupiler_Pro_League',
    'Brazilian_Série_A': 'Brazilian_Série_A'
}

# Mappatura posizione -> icona e colore (come nella home)
POSITION_ICONS = {
    'goalkeeper':  { 'icon': 'fas fa-hand-paper', 'color': '#e63946', 'label': 'Goalkeeper' },
    'centreback':  { 'icon': 'fas fa-shield-alt', 'color': '#457b9d', 'label': 'Centreback' },
    'fullback':    { 'icon': 'fas fa-running', 'color': '#1d3557', 'label': 'Fullback' },
    'midfielder':  { 'icon': 'fas fa-compass', 'color': '#2a9d8f', 'label': 'Midfielder' },
    'attacking_midfielder': { 'icon': 'fas fa-star', 'color': '#f4a261', 'label': 'Attacking Midfielder' },
    'winger':      { 'icon': 'fas fa-bolt', 'color': '#e76f51', 'label': 'Winger' },
    'striker':     { 'icon': 'fas fa-bullseye', 'color': '#264653', 'label': 'Striker' },
    'valverde':    { 'icon': 'fas fa-dna', 'color': '#6c757d', 'label': 'Valverde Profile' },
}

def load_player_data():
    """Load all player rating data"""
    data_files = {
        'goalkeeper': 'goalkeeper_ratings_complete_en.csv',
        'striker': 'striker_ratings_complete_en.csv',
        'winger': 'winger_ratings_complete_en.csv',
        'attacking_midfielder': 'attacking_midfielder_ratings_complete_en.csv',
        'midfielder': 'midfielder_ratings_complete_en.csv',
        'fullback': 'fullback_ratings_complete_en.csv',
        'centreback': 'centreback_ratings_complete_en.csv',
        'valverde': 'valverde_score_results.csv'
    }
    
    BASE_PATH = '/Users/federico/dash_project/'
    all_data = {}
    for position, filename in data_files.items():
        file_path = os.path.join(BASE_PATH, filename)
        if not os.path.exists(file_path):
            print(f"[ScoutAnalysis] File not found: {file_path}")
            continue
        try:
            # Detect separator
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = f.read(2048)
                if ';' in sample and sample.count(';') > sample.count(','):
                    sep = ';'
                else:
                    sep = ','
            df = pd.read_csv(file_path, sep=sep)
            print(f"[ScoutAnalysis] Loaded {position}: {df.shape[0]} rows, columns: {list(df.columns)}")
            if df.empty:
                print(f"[ScoutAnalysis] Loaded file is empty: {file_path}")
            # Add position column
            df['Position'] = position
            all_data[position] = df
        except Exception as e:
            print(f"[ScoutAnalysis] Error loading {file_path}: {e}")
    return all_data

def parse_market_value(value_str):
    """Parse market value string to numeric value in millions"""
    if pd.isna(value_str) or value_str == '' or value_str == '€0':
        return 0
    
    try:
        # Remove currency symbols
        value_str = str(value_str).replace('€', '').strip()
        
        # Handle European format with comma as decimal separator (e.g., "3.000.000,00")
        if ',' in value_str and '.' in value_str:
            # This is European format: dots as thousand separators, comma as decimal
            # Remove dots first, then replace comma with dot
            value_str = value_str.replace('.', '').replace(',', '.')
        elif ',' in value_str:
            # Only comma present, likely European format without thousand separators
            value_str = value_str.replace(',', '.')
        else:
            # Standard format with dots as thousand separators (e.g., "15.000.000")
            # Remove dots to get the full number
            value_str = value_str.replace('.', '')
        
        # Convert to float and then to millions
        value = float(value_str)
        result = value / 1_000_000  # Convert to millions
        return result
    except Exception as e:
        print(f"[DEBUG] Error parsing market value '{value_str}': {e}")
        return 0

def parse_salary(salary_str):
    """Parse salary string to numeric value in millions"""
    if pd.isna(salary_str) or salary_str == '' or salary_str == '€0':
        return 0
    
    try:
        # Remove currency symbols and convert to numeric
        salary_str = str(salary_str).replace('€', '').replace(',', '')
        
        # Handle values like "1.670.000.00" (points as thousand separators + decimal)
        if '.' in salary_str:
            parts = salary_str.split('.')
            if len(parts) > 1:
                # If last part has 2 digits, it's likely decimal part
                if len(parts[-1]) == 2:
                    whole_part = ''.join(parts[:-1])
                    decimal_part = parts[-1]
                    salary_str = whole_part + '.' + decimal_part
                else:
                    # All parts are thousands
                    salary_str = ''.join(parts)
        
        # Convert to float and then to millions
        value = float(salary_str)
        result = value / 1_000_000  # Convert to millions
        return result
    except Exception as e:
        return 0

def get_player_photo_path(player_name):
    """Get player photo path or return default"""
    if pd.isna(player_name) or player_name == '':
        return f"{PLAYERS_PHOTOS_PATH}/default.png"
    
    # Try different name variations
    name_variations = [
        player_name,
        player_name.replace(' ', '_'),
        player_name.replace('_', ' '),
        unidecode(player_name),
        unidecode(player_name).replace(' ', '_')
    ]
    
    for name_var in name_variations:
        photo_path = f"{PLAYERS_PHOTOS_PATH}/{name_var}.png"
        if os.path.exists(os.path.join(BASE_PATH, photo_path.lstrip('/'))):
            return photo_path
    
    return f"{PLAYERS_PHOTOS_PATH}/default.png"

def create_player_card(player_data, position, selected_profile=None):
    """Create a player card component with photo"""
    player_name = player_data.get('Player', 'Unknown')
    team = player_data.get('Team', 'Unknown')
    league = player_data.get('League', 'Unknown')
    age = player_data.get('Age', 'N/A')
    nationality = player_data.get('Nationality', 'N/A')
    height = player_data.get('Height', 'N/A')
    foot = player_data.get('Foot', 'N/A')
    market_value = player_data.get('Market Value', 'N/A')
    salary = player_data.get('Annual Salary', 'N/A')
    contract_until = player_data.get('Contract Until', 'N/A')
    release_clause = player_data.get('Release Clause', 'N/A')
    ranking = player_data.get('Ranking', None)
    
    # Get photo path
    photo_path = get_player_photo_path(player_name)
    
    # Get rating columns for this position
    rating_cols = [col for col in player_data.index if col not in 
                  ['Player', 'Team', 'League', 'Age', 'Nationality', 'Height', 'Foot', 
                   'Market Value', 'Contract Until', 'Position', 'Annual Salary', 'Release Clause', 'Ranking']]
    
    # Get ratings
    ratings = []
    for col in rating_cols:
        try:
            rating = float(player_data[col])
            if not pd.isna(rating):
                ratings.append((col, rating))
        except:
            continue
    
    ratings.sort(key=lambda x: x[1], reverse=True)
    
    # If a specific profile is selected, show only that
    if selected_profile and selected_profile != 'all':
        selected_rating = next((rating for profile, rating in ratings if profile == selected_profile), None)
        if selected_rating:
            ratings = [(selected_profile, selected_rating)]
    
    top_3_ratings = ratings[:3]
    
    # Determine card color based on best rating using new scale
    if ratings:
        best_rating = ratings[0][1]
        if best_rating >= 75:
            card_color = "#28a745"  # Green for high rating (≥75)
        elif best_rating >= 60:
            card_color = "#ffc107"  # Yellow for medium rating (60-74.9)
        else:
            card_color = "#dc3545"  # Red for low rating (<60)
    else:
        card_color = "#6c757d"  # Gray for no rating
    
    # Function to get rating color
    def get_rating_color(rating):
        if rating >= 75:
            return "#28a745"  # Green
        elif rating >= 60:
            return "#ffc107"  # Yellow
        else:
            return "#dc3545"  # Red
    
    # Create ranking badge
    ranking_badge = ""
    if ranking is not None:
        ranking_badge = html.Span(
            f"#{ranking}",
            style={
                "position": "absolute",
                "top": "8px",
                "right": "8px",
                "backgroundColor": card_color,
                "color": "white",
                "padding": "4px 8px",
                "borderRadius": "12px",
                "fontSize": "0.8rem",
                "fontWeight": "700",
                "fontFamily": "'Poppins', sans-serif",
                "zIndex": "10"
            }
        )
    
    return dbc.Card([
        dbc.CardHeader([
            ranking_badge,
            dbc.Row([
                dbc.Col([
                    html.Img(
                        src=photo_path,
                        className="player-photo",
                        style={
                            "width": "60px",
                            "height": "60px",
                            "border": f"3px solid {card_color}"
                        }
                    )
                ], width=3),
                dbc.Col([
                    html.H5(player_name, className="mb-0", style={
                        "fontFamily": "'Poppins', sans-serif",
                        "fontWeight": "600",
                        "color": "#1D3557"
                    }),
                    html.Small(f"{team} • {league}", className="text-muted", style={
                        "fontFamily": "'Poppins', sans-serif"
                    })
                ], width=9)
            ])
        ], style={
            "backgroundColor": "#f8f9fa",
            "borderBottom": f"2px solid {card_color}",
            "position": "relative"
        }),
        dbc.CardBody([
            html.Div([
                html.Span(f"Age: {age}", className="badge bg-secondary me-2", style={
                    "fontFamily": "'Poppins', sans-serif",
                    "fontWeight": "500"
                }),
                html.Span(f"Pos: {format_display_name(position)}", className="badge bg-primary", style={
                    "fontFamily": "'Poppins', sans-serif",
                    "fontWeight": "500"
                })
            ], className="mb-3"),
            html.Div([
                html.Small(f"Nationality: {nationality}", className="stats-item d-block"),
                html.Small(f"Height: {height}", className="stats-item d-block"),
                html.Small(f"Foot: {foot}", className="stats-item d-block")
            ], className="mb-3"),
            html.Div([
                html.Small(f"Value: {market_value}", className="stats-item d-block"),
                html.Small(f"Salary: {salary}", className="stats-item d-block"),
                html.Small(f"Contract: {contract_until}", className="stats-item d-block"),
                html.Small(f"Clause: {release_clause}", className="stats-item d-block")
            ], className="mb-3"),
            html.Div([
                html.H6("Profiles:", className="mb-2", style={
                    "fontFamily": "'Poppins', sans-serif",
                    "fontWeight": "600",
                    "color": "#1D3557"
                }),
                html.Div([
                    html.Span(
                        f"{format_display_name(profile)}: {rating:.1f}",
                        className="profile-badge",
                        style={
                            "display": "inline-block",
                            "margin": "2px 4px 2px 0",
                            "padding": "4px 8px",
                            "borderRadius": "12px",
                            "fontSize": "0.85rem",
                            "fontWeight": "600",
                            "color": "white",
                            "backgroundColor": get_rating_color(rating),
                            "fontFamily": "'Poppins', sans-serif"
                        }
                    )
                    for profile, rating in top_3_ratings
                ])
            ])
        ])
    ], className="h-100 player-card rating-card shadow-sm", style={
        "borderLeft": f"4px solid {card_color}",
        "transition": "all 0.3s ease"
    })

def create_advanced_filters():
    """Create advanced filters section"""
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.I(className="fas fa-bullseye me-2", style={
                        "color": "#fff",
                        "fontSize": "1.6rem",
                        "verticalAlign": "middle"
                    }),
                    html.Span("Advanced Filters", style={
                        "fontFamily": "'Poppins', sans-serif",
                        "fontWeight": "700",
                        "fontSize": "1.5rem",
                        "color": "#fff",
                        "verticalAlign": "middle"
                    })
                ], style={
                    "display": "flex",
                    "alignItems": "center"
                }),
                html.Small(
                    "Use the filters below to refine your search",
                    style={
                        "fontFamily": "'Poppins', sans-serif",
                        "color": "#fff",
                        "marginLeft": "48px"
                    }
                )
            ], style={
                "background": "#1D3557",
                "borderBottom": "2px solid #a8dadc",
                "paddingTop": "18px",
                "paddingBottom": "10px"
            }),
            dbc.CardBody([
                # Container per i filtri standard (nascosto per Valverde)
                html.Div(id='standard-filters', children=[
                    # Prima riga: League e Profile
                    dbc.Row([
                        dbc.Col([
                            html.Label("League", className="form-label", style={
                                "fontFamily": "'Poppins', sans-serif",
                                "fontWeight": "500",
                                "color": "#1D3557"
                            }),
                            dcc.Dropdown(
                                id='league-filter',
                                options=[{'label': 'All', 'value': 'all'}],
                                value='all',
                                className="mb-3"
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Profile", className="form-label", style={
                                "fontFamily": "'Poppins', sans-serif",
                                "fontWeight": "500",
                                "color": "#1D3557"
                            }),
                            dcc.Dropdown(
                                id='profile-filter',
                                options=[],
                                className="mb-3"
                            )
                        ], width=6)
                    ]),

                    # Seconda riga: Min Rating, Min Market Value, Min Annual Salary
                    dbc.Row([
                        dbc.Col([
                            html.Label("Min Rating", className="form-label", style={
                                "fontFamily": "'Poppins', sans-serif",
                                "fontWeight": "500",
                                "color": "#1D3557"
                            }),
                            dcc.Slider(
                                id='rating-filter',
                                min=60,
                                max=100,
                                step=1,
                                value=70,
                                marks={i: str(i) for i in range(60, 101, 10)},
                                className="mb-3"
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("Min Market Value (M€)", className="form-label", style={
                                "fontFamily": "'Poppins', sans-serif",
                                "fontWeight": "500",
                                "color": "#1D3557"
                            }),
                            dcc.Slider(
                                id='market-value-filter',
                                min=0,
                                max=100,
                                step=5,
                                value=0,
                                marks={i: str(i) for i in range(0, 101, 20)},
                                className="mb-3"
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("Min Annual Salary (M€)", className="form-label", style={
                                "fontFamily": "'Poppins', sans-serif",
                                "fontWeight": "500",
                                "color": "#1D3557"
                            }),
                            dcc.Slider(
                                id='salary-filter',
                                min=0,
                                max=20,
                                step=1,
                                value=0,
                                marks={i: str(i) for i in range(0, 21, 5)},
                                className="mb-3"
                            )
                        ], width=4)
                    ]),

                    # Terza riga: Max Age, Preferred Foot, Contract Status, Release Clause
                    dbc.Row([
                        dbc.Col([
                            html.Label("Max Age", className="form-label", style={
                                "fontFamily": "'Poppins', sans-serif",
                                "fontWeight": "500",
                                "color": "#1D3557"
                            }),
                            dcc.Slider(
                                id='age-filter',
                                min=16,
                                max=40,
                                step=1,
                                value=40,
                                marks={i: str(i) for i in [16, 24, 32, 40]},
                                className="mb-3"
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Preferred Foot", className="form-label", style={
                                "fontFamily": "'Poppins', sans-serif",
                                "fontWeight": "500",
                                "color": "#1D3557"
                            }),
                            dcc.Dropdown(
                                id='foot-filter',
                                options=[
                                    {'label': 'All', 'value': 'all'},
                                    {'label': 'Left', 'value': 'left'},
                                    {'label': 'Right', 'value': 'right'}
                                ],
                                value='all',
                                className="mb-3"
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Contract Status", className="form-label", style={
                                "fontFamily": "'Poppins', sans-serif",
                                "fontWeight": "500",
                                "color": "#1D3557"
                            }),
                            dcc.Dropdown(
                                id='contract-filter',
                                options=[
                                    {'label': 'All', 'value': 'all'},
                                    {'label': 'Expiring', 'value': 'expiring'},
                                    {'label': 'Long Term', 'value': 'long_term'}
                                ],
                                value='all',
                                className="mb-3"
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Release Clause", className="form-label", style={
                                "fontFamily": "'Poppins', sans-serif",
                                "fontWeight": "500",
                                "color": "#1D3557"
                            }),
                            dcc.Dropdown(
                                id='release-clause-filter',
                                options=[
                                    {'label': 'All', 'value': 'all'},
                                    {'label': 'With Clause', 'value': 'with_clause'},
                                    {'label': 'No Clause', 'value': 'no_clause'}
                                ],
                                value='all',
                                className="mb-3"
                            )
                        ], width=3)
                    ])
                ]),

                # Quarta riga: Player Search (sempre visibile)
                dbc.Row([
                    dbc.Col([
                        html.Label("Player Search", className="form-label", style={
                            "fontFamily": "'Poppins', sans-serif",
                            "fontWeight": "500",
                            "color": "#1D3557"
                        }),
                        dcc.Input(
                            id='player-search',
                            type='text',
                            placeholder='Search by player name...',
                            className="form-control",
                            style={
                                "fontFamily": "'Poppins', sans-serif",
                                "borderRadius": "25px",
                                "border": "2px solid #e1e5e9",
                                "padding": "10px 15px",
                                "transition": "all 0.3s ease"
                            }
                        )
                    ], width=12)
                ])
            ])
        ], className="shadow-sm", style={
            "border": "none",
            "borderRadius": "15px",
            "overflow": "hidden"
        })
    ])

def create_scout_analysis_layout():
    """Create the comprehensive scout analysis layout"""
    return html.Div([
        # Store for pagination state
        dcc.Store(id='current-page-store', data={'page': 1}),
        
        # Advanced Filters Section
        dbc.Row([
            dbc.Col([
                create_advanced_filters()
            ], width=12)
        ], className="mb-4"),
        
        # Position Section (always visible)
        dbc.Row([
            dbc.Col([
                # Barra blu scuro con icona e nome ruolo
                html.Div(id='position-bar', style={
                    "background": "#1D3557",
                    "borderRadius": "12px 12px 0 0",
                    "padding": "18px 24px 10px 24px",
                    "marginBottom": "0px",
                    "display": "flex",
                    "alignItems": "center"
                })
            ], width=12)
        ]),
        # Position Content (always visible)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='position-content')
                    ])
                ], className="shadow-sm", style={
                    "border": "none",
                    "borderRadius": "0 0 15px 15px",
                    "overflow": "hidden",
                    "background": "linear-gradient(135deg, #f8f9fa 60%, #e9ecef 100%)"
                })
            ], width=12)
        ]),
        
        # Pagination Controls (always present but hidden when not needed)
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Small(id="pagination-info", style={"color": "#6c757d", "marginRight": "20px"}),
                        dbc.Button(
                            html.I(className="fas fa-chevron-left"),
                            id="prev-page-btn",
                            color="primary",
                            outline=True,
                            disabled=True,
                            size="sm",
                            style={"marginRight": "10px"}
                        ),
                        dbc.Button(
                            html.I(className="fas fa-chevron-right"),
                            id="next-page-btn",
                            color="primary",
                            outline=True,
                            disabled=True,
                            size="sm"
                        )
                    ], style={
                        "textAlign": "center",
                        "padding": "15px",
                        "backgroundColor": "#f8f9fa",
                        "borderRadius": "10px"
                    })
                ], id='pagination-controls', style={'display': 'none'})
            ], width=12)
        ], className="mt-3"),
    ])

# Layout principale
layout = create_scout_analysis_layout()

# CSS aggiuntivo per mantenere la coerenza con la home page
additional_css = """
<style>
/* Stili generali */
body {
    font-family: 'Poppins', sans-serif;
}

/* Stili per i filtri */
.form-control:focus, .Select-control:focus {
    border-color: #457b9d;
    box-shadow: 0 0 0 0.2rem rgba(69, 123, 157, 0.25);
}

/* Stili per le card */
.card {
    transition: all 0.3s ease;
    border: none;
    border-radius: 15px;
    overflow: hidden;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}

/* Stili per le card dei giocatori */
.player-card {
    transition: all 0.3s ease;
    border: none;
    border-radius: 15px;
    overflow: hidden;
}

.player-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.2) !important;
}

/* Stili per i dropdown */
.Select-control {
    border-radius: 25px;
    border: 2px solid #e1e5e9;
    transition: all 0.3s ease;
}

.Select-control:hover {
    border-color: #457b9d;
}

/* Stili per gli slider */
.rc-slider-track {
    background-color: #457b9d;
}

.rc-slider-handle {
    border-color: #457b9d;
    background-color: #457b9d;
}

.rc-slider-handle:hover {
    border-color: #1D3557;
    background-color: #1D3557;
}

/* Stili per i badge */
.badge {
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
    border-radius: 15px;
}

/* Stili per i titoli */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
}

/* Stili per i link */
a {
    color: #457b9d;
    transition: all 0.3s ease;
}

a:hover {
    color: #1D3557;
    text-decoration: none;
}

/* Stili per i bottoni */
.btn {
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
    border-radius: 25px;
    transition: all 0.3s ease;
}

.btn-primary {
    background-color: #457b9d;
    border-color: #457b9d;
}

.btn-primary:hover {
    background-color: #1D3557;
    border-color: #1D3557;
    transform: translateY(-2px);
}

/* Stili per le card header */
.card-header {
    background-color: #f8f9fa;
    border-bottom: 2px solid #457b9d;
    font-family: 'Poppins', sans-serif;
}

/* Stili per i placeholder */
::placeholder {
    font-family: 'Poppins', sans-serif;
    color: #6c757d;
}

/* Stili per i focus */
.form-control:focus {
    border-color: #457b9d;
    box-shadow: 0 0 0 0.2rem rgba(69, 123, 157, 0.25);
}

/* Animazioni */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.5s ease-out;
}

/* Stili per le card dei giocatori con rating */
.rating-card {
    position: relative;
    overflow: hidden;
}

.rating-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #e63946, #f4a261, #2a9d8f, #457b9d);
}

/* Stili per le immagini dei giocatori */
.player-photo {
    border-radius: 50%;
    object-fit: cover;
    transition: all 0.3s ease;
}

.player-photo:hover {
    transform: scale(1.05);
}

/* Stili per i profili */
.profile-badge {
    background: linear-gradient(45deg, #457b9d, #1D3557);
    color: white;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 2px;
    display: inline-block;
}

/* Stili per le statistiche */
.stats-item {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 8px 12px;
    margin: 2px;
    font-size: 0.85rem;
    color: #6c757d;
    border-left: 3px solid #457b9d;
}

/* Stili per i filtri avanzati */
.advanced-filters {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

/* Stili per i risultati */
.results-section {
    background-color: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

/* Responsive design */
@media (max-width: 768px) {
    .card {
        margin-bottom: 15px;
    }
    
    .player-card {
        margin-bottom: 10px;
    }
    
    .advanced-filters {
        padding: 15px;
    }
}
</style>
"""

def register_callbacks(app):
    @app.callback(
        [Output('league-filter', 'options'),
         Output('league-filter', 'value'),
         Output('profile-filter', 'options'),
         Output('profile-filter', 'value')],
        [Input('url', 'search')]
    )
    def update_league_and_profile_options_from_url(search):
        # Estrai la posizione dalla query string
        position = None
        if search:
            qs = parse_qs(search.lstrip('?'))
            position = qs.get('position', [None])[0]
        if not position or position == 'all':
            return [{'label': 'All', 'value': 'all'}], 'all', [], None
        
        df, leagues, profiles = load_position_data(position)
        if df is None:
            return [{'label': 'All', 'value': 'all'}], 'all', [], None
        
        league_options = [{'label': 'All', 'value': 'all'}] + [
            {'label': format_display_name(l), 'value': l} for l in leagues
        ]
        
        # Profile options without "All" - user must select a specific profile
        profile_options = [
            {'label': format_display_name(p), 'value': p} for p in profiles
        ]
        
        # Set the first profile as default value
        default_profile = profiles[0] if profiles else None
        
        return league_options, 'all', profile_options, default_profile

    @app.callback(
        Output('position-content', 'children'),
        [Input('url', 'search'),
         Input('league-filter', 'value'),
         Input('rating-filter', 'value'),
         Input('market-value-filter', 'value'),
         Input('salary-filter', 'value'),
         Input('player-search', 'value'),
         Input('age-filter', 'value'),
         Input('foot-filter', 'value'),
         Input('contract-filter', 'value'),
         Input('release-clause-filter', 'value'),
         Input('profile-filter', 'value'),
         Input('current-page-store', 'data')]
    )
    def update_content(search, league, min_rating, min_market_value, min_salary, search_term, max_age,
                      foot, contract, release_clause, profile, page_data):
        # Estrai la posizione dalla query string
        position = None
        if search:
            qs = parse_qs(search.lstrip('?'))
            position = qs.get('position', [None])[0]
        if not position or position == 'all':
            return html.Div("Select a position to view players", className="text-center text-muted")
        
        # Get current page from store
        current_page = page_data.get('page', 1) if page_data else 1
        
        player_data = load_player_data()
        position_content = create_position_section(
            player_data, position, league, min_rating, min_market_value, 
            min_salary, search_term, max_age, foot, contract, release_clause, position, profile, current_page
        )
        return position_content

    @app.callback(
        Output('position-bar', 'children'),
        [Input('url', 'search')]
    )
    def update_position_bar(search):
        position = None
        if search:
            qs = parse_qs(search.lstrip('?'))
            position = qs.get('position', [None])[0]
        icon_info = POSITION_ICONS.get(position, POSITION_ICONS['centreback'])
        return html.Div([
            html.I(className=icon_info['icon'], style={
                "color": "#fff",  # Icona bianca solo qui
                "fontSize": "1.3rem",
                "verticalAlign": "middle",
                "marginRight": "12px"
            }),
            html.Span(icon_info['label'], style={
                "fontFamily": "'Poppins', sans-serif",
                "fontWeight": "700",
                "fontSize": "1.3rem",
                "color": "#fff",
                "verticalAlign": "middle"
            }),
            html.Small(" Select a profile to filter results", style={
                "fontFamily": "'Poppins', sans-serif",
                "color": "#fff",
                "marginLeft": "18px"
            })
        ], style={
            "display": "flex",
            "alignItems": "center"
        })

    # Callback to update pagination controls visibility and content
    @app.callback(
        Output('pagination-controls', 'style'),
        Output('pagination-info', 'children'),
        Output('prev-page-btn', 'disabled'),
        Output('next-page-btn', 'disabled'),
        [Input('url', 'search'),
         Input('league-filter', 'value'),
         Input('rating-filter', 'value'),
         Input('market-value-filter', 'value'),
         Input('salary-filter', 'value'),
         Input('player-search', 'value'),
         Input('age-filter', 'value'),
         Input('foot-filter', 'value'),
         Input('contract-filter', 'value'),
         Input('release-clause-filter', 'value'),
         Input('profile-filter', 'value')],
        [State('current-page-store', 'data')]
    )
    def update_pagination_controls(search, league, rating, market_value, salary, search_term, age, foot, contract, release_clause, profile, page_data):
        # Get current page from page_data
        current_page = 1
        if page_data and isinstance(page_data, dict):
            current_page = page_data.get('current_page', 1)
        
        # Get position from URL
        position = None
        if search:
            qs = parse_qs(search.lstrip('?'))
            position = qs.get('position', [None])[0]
        
        if not position or position == 'all':
            return {'display': 'none'}, "", True, True
        
        # Special handling for Valverde Score - skip all advanced filters
        if position == 'valverde':
            # Load Valverde Score data
            valverde_file = os.path.join(BASE_PATH, 'valverde_score_results.csv')
            
            if not os.path.exists(valverde_file):
                return {'display': 'none'}, "", True, True
            
            try:
                df = pd.read_csv(valverde_file)
            except:
                return {'display': 'none'}, "", True, True
            
            if df.empty:
                return {'display': 'none'}, "", True, True
            
            # Only apply search filter for Valverde Score
            if search_term:
                df = df[df['Player'].str.contains(search_term, case=False, na=False)]
            
            # Pagination settings
            players_per_page = 25
            total_players = len(df)
            total_pages = (total_players + players_per_page - 1) // players_per_page
            
            # Ensure current_page is within valid range
            current_page = max(1, min(current_page, total_pages))
            
            # Create pagination controls
            pagination_info = f"Page {current_page} of {total_pages} ({total_players} players total)"
            prev_disabled = current_page <= 1
            next_disabled = current_page >= total_pages
            
            return {'display': 'block'}, pagination_info, prev_disabled, next_disabled
        
        # Load and filter data to get total pages for other positions
        player_data = load_player_data()
        if position not in player_data:
            return {'display': 'none'}, "", True, True
        
        df = player_data[position].copy()
        
        # Apply same filters as in create_position_section
        if league != 'all':
            df = df[df['League'] == league]
        if search_term:
            df = df[df['Player'].str.contains(search_term, case=False, na=False)]
        if foot != 'all':
            # Handle case-insensitive foot matching with null values
            mask = df['Foot'].notna() & (df['Foot'].str.lower() == foot.lower())
            df = df[mask]
        if release_clause != 'all':
            if release_clause == 'with_clause':
                # Check for non-zero release clauses
                df['Release_Clause_Numeric'] = df['Release Clause'].apply(parse_market_value)
                df = df[df['Release_Clause_Numeric'] > 0]
            else:
                # Check for zero or no release clauses
                df['Release_Clause_Numeric'] = df['Release Clause'].apply(parse_market_value)
                df = df[df['Release_Clause_Numeric'] == 0]
        
        # Only apply age filter if Age column exists
        if 'Age' in df.columns:
            df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
            df = df[df['Age'] <= age]
        
        if rating > 0:
            rating_cols = [col for col in df.columns if any(profile in col for profile in ['Playmaker_Keeper', 'Shot_Stopper', 'Guardian', 'Deep_Distributor', 'Enforcer', 'Sentinel_Fullback', 'Advanced_Wingback', 'Overlapping_Runner', 'Pivot_Master', 'Maestro', 'Box_to_Box', 'Diez', 'Space_Invader', 'Key_Passer', 'Creative_Winger', 'Falso_Nueve', 'Aerial_Dominator', 'Lethal_Striker'])]
            if profile and profile in df.columns:
                df = df[df[profile] >= rating]
            else:
                df = df[df[rating_cols].max(axis=1) >= rating]
        
        if market_value > 0:
            df['Market_Value_Numeric'] = df['Market Value'].apply(parse_market_value)
            df = df[df['Market_Value_Numeric'] >= market_value]
        
        if salary > 0:
            df['Salary_Numeric'] = df['Annual Salary'].apply(parse_salary)
            df = df[df['Salary_Numeric'] >= salary]
        
        # Pagination settings
        players_per_page = 25
        total_players = len(df)
        total_pages = (total_players + players_per_page - 1) // players_per_page
        
        # Ensure current_page is within valid range
        current_page = max(1, min(current_page, total_pages))
        
        # Create pagination controls
        pagination_info = f"Page {current_page} of {total_pages} ({total_players} players total)"
        prev_disabled = current_page <= 1
        next_disabled = current_page >= total_pages
        
        return {'display': 'block'}, pagination_info, prev_disabled, next_disabled

    @app.callback(
        Output('current-page-store', 'data'),
        [Input('url', 'search'),
         Input('prev-page-btn', 'n_clicks'),
         Input('next-page-btn', 'n_clicks'),
         Input('league-filter', 'value'),
         Input('rating-filter', 'value'),
         Input('market-value-filter', 'value'),
         Input('salary-filter', 'value'),
         Input('player-search', 'value'),
         Input('age-filter', 'value'),
         Input('foot-filter', 'value'),
         Input('contract-filter', 'value'),
         Input('release-clause-filter', 'value'),
         Input('profile-filter', 'value')],
        [State('current-page-store', 'data')]
    )
    def handle_pagination(search, prev_clicks, next_clicks, league, rating, market_value, salary, 
                         search_term, age, foot, contract, release_clause, profile, current_data):
        # Get current page data
        current_data = current_data or {'page': 1}
        current_page = current_data.get('page', 1)
        
        # Check what triggered the callback
        ctx = callback_context
        if not ctx.triggered:
            return {'page': 1}
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # If URL changed or filters changed, reset to page 1
        if trigger_id in ['url', 'league-filter', 'rating-filter', 'market-value-filter', 'salary-filter', 
                         'player-search', 'age-filter', 'foot-filter', 'contract-filter', 'release-clause-filter', 'profile-filter']:
            return {'page': 1}
        
        # Handle previous button
        elif trigger_id == 'prev-page-btn':
            new_page = max(1, current_page - 1)
            return {'page': new_page}
        
        # Handle next button
        elif trigger_id == 'next-page-btn':
            new_page = current_page + 1
            return {'page': new_page}
        
        return current_data

    @app.callback(
        Output('standard-filters', 'style'),
        [Input('url', 'search')]
    )
    def toggle_standard_filters(search):
        if search:
            qs = parse_qs(search.lstrip('?'))
            position = qs.get('position', [None])[0]
            if position == 'valverde':
                return {'display': 'none'}
        return {'display': 'block'}

def create_position_section(player_data, position, league, min_rating, min_market_value, min_salary, 
                          search_term, max_age, foot, contract, release_clause, 
                          position_filter, selected_profile, current_page=1):
    """Create a section for a specific position with pagination"""
    
    # Special handling for Valverde Score
    if position == 'valverde':
        return create_valverde_score_view()
    
    if position not in player_data:
        return html.Div("No data available for this position")
    
    df = player_data[position].copy()
    
    # Apply filters
    if league != 'all':
        df = df[df['League'] == league]
    print(f"[ScoutAnalysis] After league filter: {len(df)} rows")
    
    if search_term:
        df = df[df['Player'].str.contains(search_term, case=False, na=False)]
    print(f"[ScoutAnalysis] After search_term filter: {len(df)} rows")
    
    if foot != 'all':
        # Handle case-insensitive foot matching with null values
        mask = df['Foot'].notna() & (df['Foot'].str.lower() == foot.lower())
        df = df[mask]
    print(f"[ScoutAnalysis] After foot filter: {len(df)} rows")
    
    if contract != 'all':
        # Parse contract dates and filter
        # For now, skip contract filtering as it requires date parsing
        pass  # TODO: Implement contract filtering with date parsing
    print(f"[ScoutAnalysis] After contract filter: {len(df)} rows")
    
    if release_clause != 'all':
        if release_clause == 'with_clause':
            # Check for non-zero release clauses
            df['Release_Clause_Numeric'] = df['Release Clause'].apply(parse_market_value)
            df = df[df['Release_Clause_Numeric'] > 0]
        else:
            # Check for zero or no release clauses
            df['Release_Clause_Numeric'] = df['Release Clause'].apply(parse_market_value)
            df = df[df['Release_Clause_Numeric'] == 0]
    print(f"[ScoutAnalysis] After release_clause filter: {len(df)} rows")
    
    # Only filter by Position if the column exists
    if position_filter != 'all' and 'Position' in df.columns:
        df = df[df['Position'] == position_filter]
    print(f"[ScoutAnalysis] After position_filter: {len(df)} rows")
    
    # Filter by age
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    df = df[df['Age'] <= max_age]
    print(f"[ScoutAnalysis] After max_age filter: {len(df)} rows")
    
    # Filter by minimum rating
    if min_rating > 0:
        # Get rating columns
        rating_cols = [col for col in df.columns if any(profile in col for profile in ['Playmaker_Keeper', 'Shot_Stopper', 'Guardian', 'Deep_Distributor', 'Enforcer', 'Sentinel_Fullback', 'Advanced_Wingback', 'Overlapping_Runner', 'Pivot_Master', 'Maestro', 'Box_to_Box', 'Diez', 'Space_Invader', 'Key_Passer', 'Creative_Winger', 'Falso_Nueve', 'Aerial_Dominator', 'Lethal_Striker'])]
        
        # Filter by selected profile if specified
        if selected_profile and selected_profile != 'all':
            if selected_profile in df.columns:
                df = df[df[selected_profile] >= min_rating]
            else:
                df = df[df[rating_cols].max(axis=1) >= min_rating]
        else:
            # Filter by any profile rating
            df = df[df[rating_cols].max(axis=1) >= min_rating]
    print(f"[ScoutAnalysis] After min_rating filter: {len(df)} rows")
    
    # Filter by market value
    if min_market_value > 0:
        print(f"[DEBUG] Filtering by market value >= {min_market_value}M€")
        df['Market_Value_Numeric'] = df['Market Value'].apply(parse_market_value)
        print(f"[DEBUG] Market values range: {df['Market_Value_Numeric'].min():.2f} - {df['Market_Value_Numeric'].max():.2f}M€")
        before_filter = len(df)
        df = df[df['Market_Value_Numeric'] >= min_market_value]
        after_filter = len(df)
        print(f"[DEBUG] Market value filter: {before_filter} -> {after_filter} players")
    print(f"[ScoutAnalysis] After market_value filter: {len(df)} rows")
    
    # Filter by salary
    if min_salary > 0:
        print(f"[DEBUG] Filtering by salary >= {min_salary}M€")
        df['Salary_Numeric'] = df['Annual Salary'].apply(parse_salary)
        print(f"[DEBUG] Salaries range: {df['Salary_Numeric'].min():.2f} - {df['Salary_Numeric'].max():.2f}M€")
        before_filter = len(df)
        df = df[df['Salary_Numeric'] >= min_salary]
        after_filter = len(df)
        print(f"[DEBUG] Salary filter: {before_filter} -> {after_filter} players")
    print(f"[ScoutAnalysis] After salary filter: {len(df)} rows")
    
    # Sort by selected profile rating instead of max rating
    if selected_profile and selected_profile in df.columns:
        # Sort by the selected profile rating
        df = df.sort_values(selected_profile, ascending=False)
        # Add the selected profile rating as a column for display
        df['Selected_Rating'] = df[selected_profile]
    else:
        # Fallback to max rating if profile not found
        def get_max_rating(row):
            rating_cols = [col for col in df.columns if any(profile in col for profile in ['Playmaker_Keeper', 'Shot_Stopper', 'Guardian', 'Deep_Distributor', 'Enforcer', 'Sentinel_Fullback', 'Advanced_Wingback', 'Overlapping_Runner', 'Pivot_Master', 'Maestro', 'Box_to_Box', 'Diez', 'Space_Invader', 'Key_Passer', 'Creative_Winger', 'Falso_Nueve', 'Aerial_Dominator', 'Lethal_Striker'])]
            max_rating = 0
            for col in rating_cols:
                try:
                    rating = float(row[col])
                    if not pd.isna(rating) and rating > max_rating:
                        max_rating = rating
                except:
                    continue
            return max_rating
        
        df['Selected_Rating'] = df.apply(get_max_rating, axis=1)
        df = df.sort_values('Selected_Rating', ascending=False)
    
    # Pagination settings
    players_per_page = 25
    total_players = len(df)
    total_pages = (total_players + players_per_page - 1) // players_per_page
    
    # Ensure current_page is within valid range
    current_page = max(1, min(current_page, total_pages))
    
    # Get players for current page
    start_idx = (current_page - 1) * players_per_page
    end_idx = start_idx + players_per_page
    df_page = df.iloc[start_idx:end_idx]
    
    # Create results header with selected profile
    profile_display_name = format_display_name(selected_profile) if selected_profile else "All Profiles"
    results_header = html.Div([
        html.H4(f"{profile_display_name} Rankings - {format_display_name(position)}", style={
            "fontFamily": "'Poppins', sans-serif",
            "fontWeight": "700",
            "color": "#1D3557",
            "marginBottom": "20px",
            "textAlign": "center"
        }),
        html.Div([
            html.Span(f"Showing {len(df_page)} of {total_players} players", className="badge bg-info me-2"),
            html.Span(f"Top rating: {df['Selected_Rating'].max():.1f}", className="badge bg-success me-2"),
            html.Span(f"Average rating: {df['Selected_Rating'].mean():.1f}", className="badge bg-warning")
        ], style={
            "textAlign": "center",
            "marginBottom": "15px"
        }),
        # Color legend
        html.Div([
            html.Small("Rating Scale: ", style={
                "fontFamily": "'Poppins', sans-serif",
                "fontWeight": "600",
                "color": "#1D3557",
                "marginRight": "10px"
            }),
            html.Span("≥75", style={
                "backgroundColor": "#28a745",
                "color": "white",
                "padding": "2px 6px",
                "borderRadius": "8px",
                "fontSize": "0.75rem",
                "fontWeight": "600",
                "marginRight": "5px"
            }),
            html.Small("High", style={
                "fontFamily": "'Poppins', sans-serif",
                "color": "#28a745",
                "fontWeight": "600",
                "marginRight": "15px"
            }),
            html.Span("60-74.9", style={
                "backgroundColor": "#ffc107",
                "color": "white",
                "padding": "2px 6px",
                "borderRadius": "8px",
                "fontSize": "0.75rem",
                "fontWeight": "600",
                "marginRight": "5px"
            }),
            html.Small("Medium", style={
                "fontFamily": "'Poppins', sans-serif",
                "color": "#ffc107",
                "fontWeight": "600",
                "marginRight": "15px"
            }),
            html.Span("<60", style={
                "backgroundColor": "#dc3545",
                "color": "white",
                "padding": "2px 6px",
                "borderRadius": "8px",
                "fontSize": "0.75rem",
                "fontWeight": "600",
                "marginRight": "5px"
            }),
            html.Small("Low", style={
                "fontFamily": "'Poppins', sans-serif",
                "color": "#dc3545",
                "fontWeight": "600"
            })
        ], style={
            "textAlign": "center",
            "marginBottom": "20px"
        })
    ])
    
    # Function to get rating color
    def get_rating_color(rating):
        if rating >= 75:
            return "#28a745"  # Green
        elif rating >= 60:
            return "#ffc107"  # Yellow
        else:
            return "#dc3545"  # Red
    
    # Create simple ranking list
    ranking_items = []
    for idx, (_, player) in enumerate(df_page.iterrows(), start_idx + 1):
        player_name = player['Player']
        team = player['Team']
        league = player['League']
        age = player['Age']
        nationality = player['Nationality']
        market_value = player['Market Value']
        
        # Get rating for selected profile
        if selected_profile and selected_profile in player.index:
            profile_rating = player['Selected_Rating']
        else:
            profile_rating = 0
        
        rating_color = get_rating_color(profile_rating)
        
        # Get player photo
        photo_path = get_player_photo_path(player_name)
        
        # Get team logo path (assuming it follows the same pattern as player photos)
        team_clean = team.replace(' ', '_')
        league_clean = league.replace(' ', '_')
        
        # Use mapping if available, otherwise use original name
        logo_filename = TEAM_LOGO_MAPPING.get(team_clean, team_clean)
        
        # Use league folder mapping if available, otherwise use original league name
        league_folder = LEAGUE_FOLDER_MAPPING.get(league_clean, league_clean)
        team_logo_path = f"/assets/{league_folder}/{logo_filename}.png"
        
        ranking_item = html.Div([
            html.Div([
                # Prima riga con tutte le informazioni principali
                html.Div([
                    # Colonna sinistra: numero, foto, nome e squadra
                    html.Div([
                        # Numero di ranking
                        html.Span(f"{idx}.", style={
                            "fontWeight": "700",
                            "color": "#1D3557",
                            "marginRight": "15px",
                            "display": "inline-block",
                            "verticalAlign": "middle",
                            "width": "30px"
                        }),
                        # Foto giocatore
                        html.Img(
                            src=photo_path,
                            style={
                                "width": "45px",
                                "height": "45px",
                                "borderRadius": "50%",
                                "marginRight": "15px",
                                "verticalAlign": "middle",
                                "objectFit": "cover"
                            }
                        ),
                        # Nome giocatore
                        html.Span(player_name, style={
                            "fontWeight": "600",
                            "color": "#1D3557",
                            "marginRight": "15px",
                            "verticalAlign": "middle",
                            "fontSize": "1.1rem"
                        }),
                        # Logo e nome squadra
                        html.Div([
                            html.Img(
                                src=team_logo_path,
                                style={
                                    "width": "25px",
                                    "height": "25px",
                                    "marginRight": "8px",
                                    "verticalAlign": "middle"
                                }
                            ),
                            html.Span(
                                f"{team.replace('_', ' ')} ({league.replace('_', ' ')})",
                                style={
                                    "color": "#6c757d",
                                    "verticalAlign": "middle"
                                }
                            )
                        ], style={
                            "display": "inline-block",
                            "verticalAlign": "middle"
                        })
                    ], style={
                        "display": "inline-block",
                        "verticalAlign": "middle",
                        "width": "60%"
                    }),
                    
                    # Colonna destra: rating
                    html.Div([
                        html.Span(
                            f"{profile_rating:.1f}",
                            style={
                                "backgroundColor": rating_color,
                                "color": "white",
                                "padding": "6px 12px",
                                "borderRadius": "12px",
                                "fontWeight": "600",
                                "fontSize": "1.1rem",
                                "float": "right"
                            }
                        )
                    ], style={
                        "display": "inline-block",
                        "verticalAlign": "middle",
                        "width": "40%",
                        "textAlign": "right"
                    })
                ], style={
                    "marginBottom": "8px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between"
                }),
                
                # Seconda riga: Info personali e contrattuali
                html.Div([
                    # Info personali
                    html.Div([
                        html.Span(f"Age: {age} | ", className="text-muted"),
                        html.Span(f"Nationality: {nationality} | ", className="text-muted"),
                        html.Span(f"Height: {player.get('Height', 'N/A')} | ", className="text-muted"),
                        html.Span(f"Foot: {player.get('Foot', 'N/A')}", className="text-muted"),
                    ], style={
                        "flex": "1",
                        "fontSize": "0.9rem"
                    }),
                    
                    # Info contrattuali
                    html.Div([
                        html.Span(f"Value: {player.get('Market Value', 'N/A')} | ", className="text-muted"),
                        html.Span(f"Salary: {player.get('Annual Salary', 'N/A')} | ", className="text-muted"),
                        html.Span(f"Contract: {player.get('Contract Until', 'N/A')} | ", className="text-muted"),
                        html.Span(f"Release Clause: {player.get('Release Clause', 'N/A')}", className="text-muted"),
                    ], style={
                        "flex": "1",
                        "fontSize": "0.9rem",
                        "textAlign": "right"
                    })
                ], style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "marginBottom": "10px"
                })
            ], style={
                "padding": "15px",
                "border": "1px solid #e9ecef",
                "borderRadius": "8px",
                "marginBottom": "10px",
                "backgroundColor": "white",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                "transition": "all 0.2s ease-in-out",
                ":hover": {
                    "boxShadow": "0 4px 8px rgba(0,0,0,0.1)",
                    "transform": "translateY(-2px)"
                }
            })
        ])
        ranking_items.append(ranking_item)
    
    if not ranking_items:
        return html.Div([
            html.Div("No players found with selected filters", style={
                "textAlign": "center",
                "padding": "40px",
                "color": "#6c757d",
                "fontFamily": "'Poppins', sans-serif"
            })
        ])
    
    return html.Div([
        results_header,
        html.Div(ranking_items, style={
            "maxWidth": "1200px",
            "margin": "0 auto"
        })
    ])

def create_valverde_score_view():
    """Create Valverde Score view using the dedicated CSV file"""
    # Load Valverde Score data
    valverde_file = os.path.join(BASE_PATH, 'valverde_score_results.csv')
    
    if not os.path.exists(valverde_file):
        return html.Div("Valverde Score data not available")
    
    try:
        df = pd.read_csv(valverde_file)
    except:
        return html.Div("Error loading Valverde Score data")
    
    if df.empty:
        return html.Div("No Valverde Score data available")
    
    # Sort by Valverde Score
    df = df.sort_values('Valverde_Score', ascending=False)
    
    # Function to get Valverde Score color (different scale: ≥90 green, ≥80 yellow, <80 red)
    def get_valverde_color(score):
        if score >= 90:
            return "#28a745"  # Green for elite (≥90)
        elif score >= 80:
            return "#ffc107"  # Yellow for good (≥80)
        else:
            return "#dc3545"  # Red for below average (<80)
    
    # Create results header
    results_header = html.Div([
        html.H4("Valverde Score Rankings", style={
            "fontFamily": "'Poppins', sans-serif",
            "fontWeight": "700",
            "color": "#1D3557",
            "marginBottom": "20px",
            "textAlign": "center"
        }),
        html.Div([
            html.Span(f"Showing {len(df)} players", className="badge bg-info me-2"),
            html.Span(f"Top score: {df['Valverde_Score'].max():.1f}", className="badge bg-success me-2"),
            html.Span(f"Average score: {df['Valverde_Score'].mean():.1f}", className="badge bg-warning")
        ], style={
            "textAlign": "center",
            "marginBottom": "15px"
        }),
        # Valverde Score color legend
        html.Div([
            html.Small("Valverde Score Scale: ", style={
                "fontFamily": "'Poppins', sans-serif",
                "fontWeight": "600",
                "color": "#1D3557",
                "marginRight": "10px"
            }),
            html.Span("≥90", style={
                "backgroundColor": "#28a745",
                "color": "white",
                "padding": "2px 6px",
                "borderRadius": "8px",
                "fontSize": "0.75rem",
                "fontWeight": "600",
                "marginRight": "5px"
            }),
            html.Small("Elite", style={
                "fontFamily": "'Poppins', sans-serif",
                "color": "#28a745",
                "fontWeight": "600",
                "marginRight": "15px"
            }),
            html.Span("80-89.9", style={
                "backgroundColor": "#ffc107",
                "color": "white",
                "padding": "2px 6px",
                "borderRadius": "8px",
                "fontSize": "0.75rem",
                "fontWeight": "600",
                "marginRight": "5px"
            }),
            html.Small("Good", style={
                "fontFamily": "'Poppins', sans-serif",
                "color": "#ffc107",
                "fontWeight": "600",
                "marginRight": "15px"
            }),
            html.Span("<80", style={
                "backgroundColor": "#dc3545",
                "color": "white",
                "padding": "2px 6px",
                "borderRadius": "8px",
                "fontSize": "0.75rem",
                "fontWeight": "600",
                "marginRight": "5px"
            }),
            html.Small("Below Average", style={
                "fontFamily": "'Poppins', sans-serif",
                "color": "#dc3545",
                "fontWeight": "600"
            })
        ], style={
            "textAlign": "center",
            "marginBottom": "25px",
            "padding": "10px",
            "backgroundColor": "#f8f9fa",
            "borderRadius": "8px"
        })
    ])
    
    # Create player cards
    cards = []
    for idx, (_, player) in enumerate(df.iterrows(), 1):
        valverde_score = player['Valverde_Score']
        card_color = get_valverde_color(valverde_score)
        
        # Parse top 3 profiles and ratings
        top_profiles = player['Top_3_Profiles'].split(', ')
        top_ratings = [float(r) for r in player['Top_3_Ratings'].split(', ')]
        profiles_with_ratings = list(zip(top_profiles, top_ratings))
        
        # Get player photo
        photo_path = get_player_photo_path(player['Player'])
        
        # Create card
        card = dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([
                        html.Img(
                            src=photo_path,
                            className="player-photo",
                            style={
                                "width": "60px",
                                "height": "60px",
                                "border": f"3px solid {card_color}",
                                "borderRadius": "50%",
                                "objectFit": "cover"
                            }
                        )
                    ], width=3),
                    dbc.Col([
                        html.H5(player['Player'], className="mb-0", style={
                            "fontFamily": "'Poppins', sans-serif",
                            "fontWeight": "600",
                            "color": "#1D3557"
                        }),
                        html.Small(f"Valverde Score: {valverde_score:.1f}", className="text-muted", style={
                            "fontFamily": "'Poppins', sans-serif",
                            "fontWeight": "600",
                            "color": card_color + "!important"
                        })
                    ], width=9)
                ])
            ], style={
                "backgroundColor": "#f8f9fa",
                "borderBottom": f"2px solid {card_color}"
            }),
            dbc.CardBody([
                html.Div([
                    html.Span(f"High Profiles: {player['Number_of_High_Ratings']}", className="badge bg-primary me-2", style={
                        "fontFamily": "'Poppins', sans-serif",
                        "fontWeight": "500"
                    })
                ], className="mb-3"),
                html.Div([
                    html.H6("Top 3 Profiles:", className="mb-2", style={
                        "fontFamily": "'Poppins', sans-serif",
                        "fontWeight": "600",
                        "color": "#1D3557"
                    }),
                    html.Div([
                        html.Span(
                            f"{format_display_name(profile)}: {rating:.1f}",
                            style={
                                "display": "inline-block",
                                "margin": "2px 4px 2px 0",
                                "padding": "4px 8px",
                                "borderRadius": "12px",
                                "fontSize": "0.85rem",
                                "fontWeight": "600",
                                "color": "white",
                                "backgroundColor": "#457b9d",
                                "fontFamily": "'Poppins', sans-serif"
                            }
                        )
                        for profile, rating in profiles_with_ratings
                    ])
                ])
            ])
        ], className="h-100 player-card rating-card shadow-sm", style={
            "borderLeft": f"4px solid {card_color}",
            "transition": "all 0.3s ease"
        })
        
        cards.append(dbc.Col(card, width=3, className="mb-3"))
    
    if not cards:
        return html.Div([
            html.Div("No Valverde Score players found", style={
                "textAlign": "center",
                "padding": "40px",
                "color": "#6c757d",
                "fontFamily": "'Poppins', sans-serif"
            })
        ])
    
    return html.Div([
        results_header,
        dbc.Row(cards, className="justify-content-start")
    ])

def load_position_data(position):
    """Carica il file CSV della posizione e restituisce il DataFrame, le opzioni League e Profile."""
    # Mappa posizione -> file
    file_map = {
        'goalkeeper': 'goalkeeper_ratings_complete_en.csv',
        'centreback': 'centreback_ratings_complete_en.csv',
        'fullback': 'fullback_ratings_complete_en.csv',
        'midfielder': 'midfielder_ratings_complete_en.csv',
        'attacking_midfielder': 'attacking_midfielder_ratings_complete_en.csv',
        'striker': 'striker_ratings_complete_en.csv',
        'winger': 'winger_ratings_complete_en.csv',
        'valverde': 'valverde_score_results.csv'
    }
    filename = file_map.get(position)
    if not filename or not os.path.exists(filename):
        return None, [], []
    
    # Rileva il separatore
    with open(filename, 'r', encoding='utf-8') as f:
        sample = f.read(1024)
        if ';' in sample:
            separator = ';'
        else:
            separator = ','
    
    # Carica il DataFrame
    df = pd.read_csv(filename, sep=separator)
    
    # Per il Valverde Score, gestisci diversamente
    if position == 'valverde':
        # Per il Valverde Score, non abbiamo League e Profile nel senso tradizionale
        # Restituisci liste vuote per League e Profile
        return df, [], []
    
    # Estrai le leghe uniche
    leagues = sorted(df['League'].dropna().unique().tolist())
    
    # Estrai i profili (tutte le colonne che non sono anagrafiche)
    exclude_cols = {
        'Player', 'Team', 'League', 'Age', 'Nationality', 'Height', 'Foot', 
        'Market Value', 'Contract Until', 'Position', 'Annual Salary', 'Release Clause'
    }
    profile_cols = [col for col in df.columns if col not in exclude_cols]
    
    return df, leagues, profile_cols

def format_display_name(name):
    """Formatta il nome per la visualizzazione: rimuove underscore e capitalizza."""
    return name.replace('_', ' ').title() 