import dash
from dash import dcc, html, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs
import pandas as pd
import os
import plotly.graph_objects as go
from pages.Scout_Analysis.scout_analysis import (
    create_player_card, POSITION_ICONS,
    TEAM_LOGO_MAPPING, 
    LEAGUE_FOLDER_MAPPING,
    get_player_photo_path
)
from fpdf import FPDF
from dash.exceptions import PreventUpdate
import random
import numpy as np
from scipy.stats import percentileofscore
import plotly.io as pio

# Importazioni dal nuovo file di utilità
from pages.Scout_Analysis.scout_utils import (
    BASE_PATH,
    PROFILES_TO_COMPARE,
    get_team_logo_path,
    load_all_player_data_for_dropdown,
    load_profiles_by_position,
    get_player_info,
    get_player_data
)

# Caricamento dati condivisi
PLAYER_OPTIONS = load_all_player_data_for_dropdown()
PROFILES_BY_POSITION = load_profiles_by_position()

def format_display_name(name):
    """Formatta il nome per la visualizzazione: rimuove underscore e capitalizza."""
    if not isinstance(name, str):
        return ""
    return name.replace('_', ' ').title()

def create_direct_comparison_layout():
    """Layout per il confronto diretto dei giocatori, con nuovo design e logica."""
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className="fas fa-balance-scale me-2", style={"fontSize": "1.6rem"}),
                html.Span("Direct Player Comparison", style={"fontWeight": "700", "fontSize": "1.5rem"})
            ], className="d-flex align-items-center")
        ], style={"background": "#1D3557", "color": "white", "padding": "1rem"}),
        
        dbc.CardBody([
            # 1. Selezione Profilo
            dbc.Row([
                dbc.Col([
                    html.Label("Profile", className="form-label fw-bold"),
                    dcc.Dropdown(
                        id='profile-dropdown',
                        placeholder="Select a profile...",
                        options=[{'label': format_display_name(p), 'value': p} for p in PROFILES_TO_COMPARE]
                    )
                ], width={"size": 6, "offset": 3})
            ], className="mb-4 justify-content-center"),

            # 2. Selezione Giocatori (inizialmente disabilitata)
            dbc.Row([
                dbc.Col([
                    html.Label("Player 1", className="form-label fw-bold"),
                    dcc.Dropdown(id='player1-dropdown', placeholder="Select Player 1", disabled=True)
                ], md=6),
                dbc.Col([
                    html.Label("Player 2", className="form-label fw-bold"),
                    dcc.Dropdown(id='player2-dropdown', placeholder="Select Player 2", disabled=True)
                ], md=6),
            ], className="mb-4"),
            
            html.Hr(),

            # Risultati del confronto
            dbc.Row([
                dbc.Col(id='player1-card', md=6),
                dbc.Col(id='player2-card', md=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col(dcc.Graph(id='radar-chart-comparison')),
            ]),
            
            # NUOVO: Placeholder per la tabella delle statistiche
            html.Div(id='fbref-stats-comparison', className="mt-4"),
            
            dbc.Button("Export to PDF", id="export-pdf-btn", color="primary", className="mt-3"),
            dcc.Download(id="download-pdf"),
        ], style={"padding": "2rem"})
    ])

def create_layout():
    """Creates the main layout for the player comparison page."""
    return html.Div(id='comparison-content')

def create_detailed_player_card(player_data, selected_profile):
    """Crea una card dettagliata per il giocatore, simile al nuovo design."""
    if player_data is None:
        return dbc.Card(dbc.CardBody("Player data not available."), className="h-100 shadow-sm")

    # --- Estrazione Dati ---
    name = player_data.get('Player', 'N/A')
    team = player_data.get('Team', 'N/A')
    league = player_data.get('League', 'N/A')
    age = player_data.get('Age')
    nationality = player_data.get('Nationality', 'N/A')
    height = player_data.get('Height', 'N/A')
    foot = player_data.get('Foot', 'N/A')
    market_value = player_data.get('Market Value', 'N/A')
    salary = player_data.get('Annual Salary', 'N/A')
    contract = player_data.get('Contract Until', 'N/A')
    release_clause = player_data.get('Release Clause', 'N/A')
    
    # Gestione rating
    rating_val = player_data.get(selected_profile)
    rating_display = f"{rating_val:.1f}" if pd.notna(rating_val) and isinstance(rating_val, (int, float)) else "N/A"

    # Gestione valori mancanti
    def format_na(value, prefix="", suffix=""):
        if pd.isna(value) or value in ['N/A', '', None, 'nan']:
            return "N/A"
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return f"{prefix}{value}{suffix}"

    # --- URL Immagini ---
    player_photo_url = get_player_photo_path(name)
    team_logo_url = get_team_logo_path(team, league)

    # --- Costruzione Card ---
    return dbc.Card(
        dbc.CardBody([
            # Linea 1: Foto, Nome, Team, Rating
            dbc.Row([
                dbc.Col(
                    html.Img(src=player_photo_url, className="img-fluid rounded-circle", style={'height': '60px', 'width': '60px', 'objectFit': 'cover'}),
                    width="auto", className="pe-2"
                ),
                dbc.Col([
                    html.H5(name, className="mb-0 fw-bold"),
                    html.Div([
                        html.Img(src=team_logo_url, style={'height': '20px', 'marginRight': '5px'}),
                        html.Span(f"{team.replace('_', ' ')} ({league.replace('_', ' ')})", className="text-muted")
                    ])
                ], className="d-flex flex-column justify-content-center"),
                dbc.Col(
                    html.Span(rating_display, className="badge rounded-pill", style={'backgroundColor': '#2a9d8f', 'color': 'white', 'fontSize': '1.1rem', 'padding': '0.6rem 0.8rem'}),
                    width="auto", className="d-flex align-items-center"
                )
            ], align="center", justify="between", className="mb-3"),
            
            # Linea 2: Dati anagrafici
            html.P([
                html.Span(f"Age: {format_na(age)}"),
                html.Span(f" | Nationality: {format_na(nationality)}", className="mx-1"),
                html.Span(f" | Height: {format_na(height)}", className="mx-1"),
                html.Span(f" | Foot: {format_na(foot)}", className="mx-1")
            ], className="text-muted", style={'fontSize': '0.85rem'}),
            
            # Linea 3: Dati finanziari
            html.P([
                html.Span(f"Value: {format_na(market_value)}"),
                html.Span(f" | Salary: {format_na(salary)}", className="mx-1"),
                html.Span(f" | Contract: {format_na(contract)}", className="mx-1"),
                html.Span(f" | Clause: {format_na(release_clause)}", className="mx-1")
            ], className="text-muted", style={'fontSize': '0.85rem'})
        ]),
        className="h-100 shadow-sm border-0 p-2"
    )

def create_comparison_radar(player1_data, player2_data):
    """Crea un grafico radar per confrontare due giocatori."""
    if player1_data is None or player2_data is None:
        return go.Figure()

    # Estrai i rating dei profili per entrambi i giocatori
    p1_ratings = player1_data.get(PROFILES_TO_COMPARE, pd.Series(0, index=PROFILES_TO_COMPARE)).fillna(0)
    p2_ratings = player2_data.get(PROFILES_TO_COMPARE, pd.Series(0, index=PROFILES_TO_COMPARE)).fillna(0)

    # Filtra solo i profili dove almeno un giocatore ha un rating > 0
    common_profiles = [
        p for p in PROFILES_TO_COMPARE
        if p1_ratings.get(p, 0) > 0 or p2_ratings.get(p, 0) > 0
    ]

    if not common_profiles:
        return go.Figure()

    # Crea il grafico
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[p1_ratings.get(p) for p in common_profiles],
        theta=common_profiles,
        fill='toself',
        name=player1_data['Player']
    ))
    fig.add_trace(go.Scatterpolar(
        r=[p2_ratings.get(p) for p in common_profiles],
        theta=common_profiles,
        fill='toself',
        name=player2_data['Player']
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        title="Player Profile Comparison"
    )

    return fig

def generate_pdf_report(player1_data, player2_data, radar_fig):
    """Genera un report PDF per il confronto dei giocatori."""
    pdf = FPDF()
    pdf.add_page()
    
    # FIX: Aggiunge sia il font Arial regular che quello bold per un supporto completo
    try:
        # Percorsi standard per i font su macOS
        arial_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
        arial_bold_path = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
        
        pdf.add_font('Arial', '', arial_path, uni=True)
        pdf.add_font('Arial', 'B', arial_bold_path, uni=True)
        
        # Ora possiamo usare Arial 'B' senza problemi
        pdf.set_font('Arial', 'B', 16)
    except Exception as e:
        print(f"ATTENZIONE: Impossibile caricare i font Arial di sistema. Errore: {e}")
        # Fallback di emergenza
        pdf.set_font('Helvetica', 'B', 16)
    
    # Titolo
    pdf.cell(0, 10, txt="Player Comparison Report", ln=True, align='C')
    pdf.ln(10)

    # Dati dei giocatori
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(90, 10, txt=player1_data.get('Player', 'N/A'), border=1)
    pdf.cell(10, 10, txt="")
    pdf.cell(0, 10, txt=player2_data.get('Player', 'N/A'), border=1, ln=True)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(90, 8, txt=f"Team: {player1_data.get('Team', 'N/A').replace('_', ' ')}", border=1)
    pdf.cell(10, 8, txt="")
    pdf.cell(0, 8, txt=f"Team: {player2_data.get('Team', 'N/A').replace('_', ' ')}", border=1, ln=True)
    
    pdf.cell(90, 8, txt=f"Age: {player1_data.get('Age', 'N/A')}", border=1)
    pdf.cell(10, 8, txt="")
    pdf.cell(0, 8, txt=f"Age: {player2_data.get('Age', 'N/A')}", border=1, ln=True)

    pdf.cell(90, 8, txt=f"Market Value: {player1_data.get('Market Value', 'N/A')}", border=1)
    pdf.cell(10, 8, txt="")
    pdf.cell(0, 8, txt=f"Market Value: {player2_data.get('Market Value', 'N/A')}", border=1, ln=True)

    pdf.ln(10)

    # NUOVO: Aggiunta della tabella statistiche FBRef
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, txt="FBRef Key Stats (Season 24/25)", ln=True, align='C')
    pdf.ln(2)

    p1_stats = get_fbref_stats(player1_data)
    p2_stats = get_fbref_stats(player2_data)
    stat_names_map = {
        'PJ': 'Appearances',
        'Mín': 'Minutes Played',
        'Gls.': 'Goals',
        'Ass': 'Assists'
    }

    # Header della tabella
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(70, 8, 'Statistic', border=1, align='C')
    pdf.cell(60, 8, player1_data.get('Player', 'Player 1'), border=1, align='C')
    pdf.cell(60, 8, player2_data.get('Player', 'Player 2'), border=1, align='C', ln=True)

    # Righe della tabella
    pdf.set_font('Arial', '', 11)
    for key, name in stat_names_map.items():
        pdf.cell(70, 8, name, border=1)
        pdf.cell(60, 8, str(p1_stats.get(key, 'N/A')), border=1, align='C')
        pdf.cell(60, 8, str(p2_stats.get(key, 'N/A')), border=1, align='C', ln=True)

    pdf.ln(10)
    
    image_path = "comparison_radar.png"
    try:
        radar_fig.write_image(image_path, engine="kaleido", scale=2)
    except Exception as e:
        print(f"ERRORE CRITICO: Impossibile creare l'immagine del grafico con Kaleido. Errore: {e}")
        return None

    pdf.image(image_path, x=10, w=190)
    os.remove(image_path)

    return bytes(pdf.output(dest='S'))

def register_callbacks(app):
    @callback(
        Output("download-pdf", "data"),
        [Input("export-pdf-btn", "n_clicks")],
        [State("player1-dropdown", "value"),
         State("player2-dropdown", "value"),
         State("profile-dropdown", "value")] # Aggiungiamo il profilo allo stato
    )
    def export_pdf(n_clicks, player1_name, player2_name, selected_profile):
        if not all([n_clicks, player1_name, player2_name, selected_profile]):
            raise dash.exceptions.PreventUpdate

        player1_data = get_player_data(player1_name)
        player2_data = get_player_data(player2_name)
        radar_fig = create_kpi_radar_chart(player1_name, player2_name, selected_profile)

        pdf_data = generate_pdf_report(player1_data, player2_data, radar_fig)
        
        if pdf_data is None:
            # Se la generazione del PDF è fallita, non fare nulla.
            # L'errore sarà visibile nel terminale.
            raise dash.exceptions.PreventUpdate

        return dcc.send_bytes(pdf_data, "player_comparison.pdf")

    @callback(
        Output('comparison-content', 'children'),
        [Input('url', 'search')]
    )
    def display_page(search):
        query_params = parse_qs(search.lstrip('?')) if search else {}
        mode = query_params.get('mode', [None])[0]

        # Se il mode è 'similar', reindirizza alla nuova pagina
        if mode == 'similar':
            return dcc.Location(pathname="/similar-players", id="redirect-to-similar")
        
        # Altrimenti, mostra il layout di confronto diretto (default)
        return create_direct_comparison_layout()

    @callback(
        [Output('player1-dropdown', 'options'),
         Output('player2-dropdown', 'options'),
         Output('player1-dropdown', 'disabled'),
         Output('player2-dropdown', 'disabled'),
         Output('player1-dropdown', 'value'),
         Output('player2-dropdown', 'value')],
        [Input('profile-dropdown', 'value')],
        prevent_initial_call=True
    )
    def update_player_options(selected_profile):
        if not selected_profile:
            return [], [], True, True, None, None

        # Normalizza il nome del profilo selezionato per il confronto
        profile_to_find = selected_profile.replace('_', ' ')

        role_found = None
        for role, profiles in PROFILES_BY_POSITION.items():
            # Confronta i profili normalizzati
            normalized_profiles = [p.replace('_', ' ') for p in profiles]
            if profile_to_find in normalized_profiles:
                role_found = role
                break
        
        if not role_found:
             return [], [], True, True, None, None
        
        position_map_inverse = {
            'GOALKEEPER': 'goalkeeper',
            'CENTRE BACK': 'centreback',
            'FULLBACK': 'fullback',
            'MIDFIELDER': 'midfielder',
            'ATTACKING MIDFIELDER': 'attacking_midfielder',
            'WINGER': 'winger',
            'STRIKER': 'striker'
        }
        
        position_file_key = position_map_inverse.get(role_found)

        if not position_file_key:
             return [], [], True, True, None, None

        # Carica il file dei giocatori per quel ruolo
        file_path = os.path.join(BASE_PATH, f'{position_file_key}_ratings_complete_en.csv')
        
        try:
            if not os.path.exists(file_path):
                return [], [], True, True, None, None

            df = pd.read_csv(file_path, sep=';' if ';' in open(file_path).read(1024) else ',')
            
            # Filtra i giocatori che hanno un rating valido per quel profilo
            if selected_profile in df.columns:
                df_filtered = df[pd.to_numeric(df[selected_profile], errors='coerce').notna()]
            else:
                df_filtered = df

            players = sorted(df_filtered['Player'].unique().tolist())
            player_options = [{'label': name, 'value': name} for name in players]
            
            return player_options, player_options, False, False, None, None
        except Exception as e:
            print(f"Error loading players for profile {selected_profile}: {e}")
            return [], [], True, True, None, None

    @callback(
        [Output('player1-card', 'children'),
         Output('player2-card', 'children'),
         Output('radar-chart-comparison', 'figure'),
         Output('fbref-stats-comparison', 'children')],
        [Input('player1-dropdown', 'value'),
         Input('player2-dropdown', 'value')],
        [State('profile-dropdown', 'value')],
        prevent_initial_call=True
    )
    def update_comparison_view(player1_name, player2_name, selected_profile):
        if not all([selected_profile, player1_name, player2_name]):
            raise PreventUpdate

        _, player1_data = get_player_info(player1_name)
        _, player2_data = get_player_info(player2_name)

        card1 = create_detailed_player_card(player1_data, selected_profile)
        card2 = create_detailed_player_card(player2_data, selected_profile)

        radar_fig = create_kpi_radar_chart(player1_name, player2_name, selected_profile)
        
        stats_table = create_stats_comparison_table(player1_data, player2_data)

        return card1, card2, radar_fig, stats_table

def get_kpis_for_profile(profile_name):
    """Gets the list of KPIs for a specific profile from the CSV."""
    profiles_path = os.path.join(BASE_PATH, 'pages/Scout_Analysis/profili_scout_analysis_finale_corretti.csv')
    try:
        df = pd.read_csv(profiles_path, sep=';', encoding='utf-8')
        df.columns = [col.strip() for col in df.columns]
        
        df['PROFILO'] = df['PROFILO'].ffill()
        
        # FIX: Normalize the incoming profile name to match CSV format (with spaces)
        profile_name_with_spaces = profile_name.replace('_', ' ')
        
        profile_group = df[df['PROFILO'] == profile_name_with_spaces]
        
        if profile_group.empty:
            return []

        kpi_con = profile_group['KPI CON PALLA'].dropna().tolist()
        kpi_senza = profile_group['KPI SENZA PALLA'].dropna().tolist()
        
        all_kpis = [kpi.strip() for kpi in kpi_con + kpi_senza if isinstance(kpi, str) and kpi.strip()]
        
        return list(dict.fromkeys(all_kpis)) # Remove duplicates while preserving order
    except Exception as e:
        print(f"Error loading KPIs for profile {profile_name}: {e}")
        return []

def get_team_filepath(player_info):
    """Constructs the filepath to the team's FBRef CSV."""
    if player_info is None or 'Team' not in player_info or 'League' not in player_info:
        return None
    
    team = player_info['Team'].replace(' ', '_')
    league = player_info['League'].replace(' ', '_')

    # Handle special league paths
    if league == 'Serie_A':
        return os.path.join(BASE_PATH, 'pages', 'data_serie_a_24-25', f"{team}.csv")
    elif league == 'MLS':
        return os.path.join(BASE_PATH, 'pages', 'MLS', 'data_MLS_24', f"{team}.csv")
    elif league == 'Primeira_Liga':
         return os.path.join(BASE_PATH, 'pages', 'Primeira_Liga', 'data_primeira_liga_24-25', f"{team}.csv")

    # Generic path for other leagues
    league_lower = league.lower()
    return os.path.join(BASE_PATH, 'pages', league, f"data_{league_lower}_24-25", f"{team}.csv")


def get_raw_kpi_data(player_name, player_info, kpis):
    """Gets raw KPI values for a player from their team file, ensuring they are numeric."""
    filepath = get_team_filepath(player_info)
    if not filepath or not os.path.exists(filepath):
        return {kpi: 0.0 for kpi in kpis}

    try:
        df_team = pd.read_csv(filepath)
        player_col = 'Jugador' if 'Jugador' in df_team.columns else 'Player'
        
        player_row = df_team[df_team[player_col] == player_name]
        if player_row.empty:
            return {kpi: 0.0 for kpi in kpis}
        
        player_series = player_row.iloc[0]
        kpi_values = {}
        for kpi in kpis:
            raw_value = player_series.get(kpi, 0)
            
            # Handle potential commas as decimal separators and ensure value is string before replacing
            if isinstance(raw_value, str):
                raw_value = raw_value.replace(',', '.')

            # Force conversion to numeric, coerce errors to NaN
            numeric_value = pd.to_numeric(raw_value, errors='coerce')
            
            # Replace NaN with 0.0
            kpi_values[kpi] = 0.0 if pd.isna(numeric_value) else float(numeric_value)
            
        return kpi_values
    except Exception as e:
        print(f"Error in get_raw_kpi_data for {player_name}: {e}")
        return {kpi: 0.0 for kpi in kpis}


def calculate_percentiles(player1_name, player2_name, role, kpis):
    """Calculates on-the-fly percentiles for two players against their peers."""
    role_file = os.path.join(BASE_PATH, f"{role.lower().replace(' ', '')}_ratings_complete_en.csv")
    df_role = pd.read_csv(role_file, sep=';' if ';' in open(role_file).read(1024) else ',')

    all_kpi_values = {kpi: [] for kpi in kpis}

    # Gather data for all players in that role
    for _, peer_row in df_role.iterrows():
        peer_name = peer_row['Player']
        peer_kpi_values = get_raw_kpi_data(peer_name, peer_row, kpis)
        for kpi in kpis:
            all_kpi_values[kpi].append(peer_kpi_values[kpi])
            
    p1_raw = get_raw_kpi_data(player1_name, df_role[df_role['Player'] == player1_name].iloc[0], kpis)
    p2_raw = get_raw_kpi_data(player2_name, df_role[df_role['Player'] == player2_name].iloc[0], kpis)
    
    p1_percentiles = [percentileofscore(all_kpi_values[kpi], p1_raw[kpi]) for kpi in kpis]
    p2_percentiles = [percentileofscore(all_kpi_values[kpi], p2_raw[kpi]) for kpi in kpis]
    
    return p1_percentiles, p2_percentiles


def create_kpi_radar_chart(player1_name, player2_name, selected_profile):
    role, _ = get_player_info(player1_name)
    kpis_to_compare = get_kpis_for_profile(selected_profile)
    
    if not kpis_to_compare:
        return go.Figure().update_layout(title="No KPIs found for this profile", paper_bgcolor='rgba(0,0,0,0)')
        
    p1_percentiles, p2_percentiles = calculate_percentiles(player1_name, player2_name, role, kpis_to_compare)
    
    fig = go.Figure()
    
    # Colori coerenti con l'app
    color_p1 = 'rgba(29, 53, 87, 0.6)'  # Blu scuro semi-trasparente
    color_p2 = 'rgba(230, 57, 70, 0.6)'  # Rosso semi-trasparente

    fig.add_trace(go.Scatterpolar(
        r=p1_percentiles,
        theta=[kpi.replace('_', ' ') for kpi in kpis_to_compare], # Pulisco le etichette
        fill='toself',
        name=player1_name,
        line=dict(color=color_p1.replace('0.6', '1')), # Bordo opaco
        marker=dict(color=color_p1)
    ))
    fig.add_trace(go.Scatterpolar(
        r=p2_percentiles,
        theta=[kpi.replace('_', ' ') for kpi in kpis_to_compare],
        fill='toself',
        name=player2_name,
        line=dict(color=color_p2.replace('0.6', '1')), # Bordo opaco
        marker=dict(color=color_p2)
    ))

    fig.update_layout(
        title={
            'text': f"<b>{selected_profile.replace('_', ' ')}</b> Profile Comparison",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': '#1D3557', 'family': "'Poppins', sans-serif"}
        },
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showline=False, showticklabels=False, gridcolor='rgba(0,0,0,0.1)'),
            angularaxis=dict(
                tickfont=dict(size=11, color='#4A4A4A'),
                gridcolor='rgba(0,0,0,0.1)'
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        paper_bgcolor='rgba(255,255,255,0.9)',
        plot_bgcolor='rgba(255,255,255,0.9)',
        margin=dict(t=80, b=80)
    )
    return fig

def get_fbref_stats(player_info):
    """Gets key FBRef stats for a player from their team's CSV file."""
    stats_to_get = ['PJ', 'Mín', 'Gls.', 'Ass']
    default_stats = {stat: 'N/A' for stat in stats_to_get}

    if player_info is None:
        return default_stats

    filepath = get_team_filepath(player_info)
    if not filepath or not os.path.exists(filepath):
        print(f"Stats file not found for player: {player_info.get('Player')} at path {filepath}")
        return default_stats

    try:
        df_team = pd.read_csv(filepath)
        player_col = 'Jugador' if 'Jugador' in df_team.columns else 'Player'
        
        player_row = df_team[df_team[player_col] == player_info['Player']]
        if player_row.empty:
            print(f"Player {player_info.get('Player')} not found in {filepath}")
            return default_stats
        
        player_series = player_row.iloc[0]
        
        extracted_stats = {}
        for stat in stats_to_get:
            value = player_series.get(stat)
            if pd.notna(value):
                cleaned_value = str(value).replace(',', '')
                extracted_stats[stat] = cleaned_value
            else:
                extracted_stats[stat] = 'N/A'
                
        return extracted_stats
    except Exception as e:
        print(f"Error getting FBRef stats for {player_info.get('Player')}: {e}")
        return default_stats

def create_stats_comparison_table(player1_info, player2_info):
    """Creates a table comparing key FBRef stats for two players."""
    if player1_info is None or player2_info is None:
        return None

    p1_stats = get_fbref_stats(player1_info)
    p2_stats = get_fbref_stats(player2_info)

    stat_names = {
        'PJ': 'Appearances',
        'Mín': 'Minutes Played',
        'Gls.': 'Goals',
        'Ass': 'Assists'
    }

    table_header = [
        html.Thead(html.Tr([
            html.Th("Statistic", style={'width': '34%'}),
            html.Th(player1_info['Player'], style={'width': '33%', 'textAlign': 'center'}),
            html.Th(player2_info['Player'], style={'width': '33%', 'textAlign': 'center'})
        ], className="text-center"))
    ]
    
    rows = []
    for key, display_name in stat_names.items():
        rows.append(html.Tr([
            html.Td(display_name),
            html.Td(p1_stats.get(key, 'N/A'), className="text-center"),
            html.Td(p2_stats.get(key, 'N/A'), className="text-center")
        ]))
    
    table_body = [html.Tbody(rows)]

    return dbc.Card([
        dbc.CardHeader("FBRef Key Stats (Season 24/25)"),
        dbc.CardBody(
            dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True, responsive=True)
        )
    ], className="shadow-sm") 