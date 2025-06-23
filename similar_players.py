import dash
from dash import dcc, html, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from pages.Scout_Analysis.scout_utils import (
    BASE_PATH,
    PROFILES_TO_COMPARE,
    load_profiles_by_position,
    get_player_info,
    get_team_logo_path
)
from pages.Scout_Analysis.scout_analysis import get_player_photo_path

# Caricamento dati condivisi
PROFILES_BY_POSITION = load_profiles_by_position()

def format_display_name(name):
    """Formatta il nome per la visualizzazione: rimuove underscore e capitalizza."""
    if not isinstance(name, str):
        return ""
    return name.replace('_', ' ').title()

def create_layout():
    """Crea il layout per la pagina 'Similar Players' con il nuovo flusso."""
    return dbc.Container([
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.I(className="fas fa-users me-2", style={"fontSize": "1.6rem"}),
                    html.Span("Find Similar Players", style={"fontWeight": "700", "fontSize": "1.5rem"})
                ], className="d-flex align-items-center")
            ], style={"background": "#1D3557", "color": "white", "padding": "1rem"}),
            
            dbc.CardBody([
                # Card per i Criteri di Ricerca
                dbc.Card([
                    dbc.CardHeader("Search Criteria"),
                    dbc.CardBody([
                        dbc.Row([
                            # 1. Selezione Profilo
                            dbc.Col([
                                html.Label("1. Select Profile", className="form-label fw-bold"),
                                dcc.Dropdown(
                                    id='similar-profile-dropdown',
                                    placeholder="Select a profile...",
                                    options=[{'label': format_display_name(p), 'value': p} for p in PROFILES_TO_COMPARE]
                                )
                            ], md=6),

                            # 2. Selezione Giocatore
                            dbc.Col([
                                html.Label("2. Select Player", className="form-label fw-bold"),
                                dcc.Dropdown(id='similar-player-dropdown', placeholder="Select a player", disabled=True)
                            ], md=6),
                        ], className="mb-4"),

                        # 3. Selezione Numero Risultati
                        dbc.Row([
                            dbc.Col([
                                html.Label("3. Number of Results", className="form-label fw-bold"),
                                dcc.Slider(
                                    id='num-results-slider',
                                    min=1,
                                    max=20,
                                    step=1,
                                    value=10,
                                    marks={i: str(i) for i in range(1, 21) if i % 2 != 0 or i == 10 or i == 20 or i == 1},
                                    tooltip={"placement": "bottom", "always_visible": True}
                                )
                            ], width=12)
                        ])
                    ])
                ], className="mb-4 shadow-sm"),
                
                html.Hr(),
                
                # Area per visualizzare i risultati
                dcc.Loading(
                    id="loading-similar-players",
                    type="default",
                    children=dbc.Row(
                        dbc.Col(
                            html.Div(id='similar-players-output-area'),
                            width=12,
                            className="mt-4"
                        )
                    )
                )
            ], style={"padding": "2rem"})
        ])
    ], fluid=True, className="mt-4")

def create_similar_player_card(player_data, similarity_score):
    """Crea una card per mostrare un giocatore simile."""
    if player_data is None:
        return None

    name = player_data.get('Player', 'N/A')
    team = player_data.get('Team', 'N/A')
    league = player_data.get('League', 'N/A')
    player_photo_url = get_player_photo_path(name)
    team_logo_url = get_team_logo_path(team, league)

    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col(html.Img(src=player_photo_url, className="img-fluid rounded-circle", style={'height': '50px', 'width': '50px', 'objectFit': 'cover'}), width="auto"),
                dbc.Col([
                    html.H6(name, className="mb-0 fw-bold"),
                    html.Div([
                        html.Img(src=team_logo_url, style={'height': '18px', 'marginRight': '5px'}),
                        html.Span(f"{team.replace('_', ' ')} ({league.replace('_', ' ')})", className="text-muted small")
                    ])
                ]),
                dbc.Col(
                    html.Div([
                        html.Span("Similarity", className="small text-muted d-block", style={'lineHeight': '1'}),
                        html.Span(f"{similarity_score:.1%}", className="fw-bold", style={'fontSize': '1.1rem', 'color': '#2a9d8f'})
                    ], className="text-center"),
                    width="auto", className="d-flex flex-column justify-content-center align-items-center"
                )
            ], align="center")
        ]),
        className="mb-2 shadow-sm"
    )

def register_callbacks(app):
    """Registra i callback per la pagina 'Similar Players'."""

    @callback(
        [Output('similar-player-dropdown', 'options'),
         Output('similar-player-dropdown', 'disabled'),
         Output('similar-player-dropdown', 'value')],
        [Input('similar-profile-dropdown', 'value')],
        prevent_initial_call=True
    )
    def update_player_options_for_profile(selected_profile):
        if not selected_profile:
            return [], True, None

        # Mappatura diretta per i profili problematici
        profile_mapping = {
            'Box_to_Box': 'Box-to-Box',
            'Shot_Stopper': 'Shot-Stopper',
            'Playmaker_Keeper': 'Playmaker Keeper',
            'Falso_Nueve': 'Falso Nueve',
            'Aerial_Dominator': 'Aerial Dominator',
            'Lethal_Striker': 'Lethal Striker',
            'Key_Passer': 'Key Passer',
            'Creative_Winger': 'Creative Winger',
            'Sentinel_Fullback': 'Sentinel Fullback',
            'Advanced_Wingback': 'Advanced Wingback',
            'Overlapping_Runner': 'Overlapping Runner',
            'Deep_Distributor': 'Deep Distributor'
        }
        
        # Converti il nome del profilo per la ricerca nel dizionario
        profile_to_find = profile_mapping.get(selected_profile, selected_profile.replace('_', ' '))
        
        role_found = None
        for role, profiles in PROFILES_BY_POSITION.items():
            if profile_to_find in profiles:
                role_found = role
                break
        
        if not role_found:
            return [], True, None

        position_map_inverse = {
            'GOALKEEPER': 'goalkeeper', 'CENTRE BACK': 'centreback', 'FULLBACK': 'fullback',
            'MIDFIELDER': 'midfielder', 'ATTACKING MIDFIELDER': 'attacking_midfielder',
            'WINGER': 'winger', 'STRIKER': 'striker'
        }
        pos_key = position_map_inverse.get(role_found)
        if not pos_key:
            return [], True, None

        file_path = os.path.join(BASE_PATH, f'{pos_key}_ratings_complete_en.csv')
        try:
            df = pd.read_csv(file_path, sep=';' if ';' in open(file_path).read(1024) else ',')
            if selected_profile in df.columns:
                # Filtra per giocatori con un rating > 75 in quel profilo e ordina
                df_filtered = df[pd.to_numeric(df[selected_profile], errors='coerce') > 75].copy()
                df_filtered = df_filtered.sort_values(by=selected_profile, ascending=False)
                players = df_filtered['Player'].unique().tolist()
                player_options = [{'label': name, 'value': name} for name in players]
                return player_options, False, None
            else:
                return [], True, None
        except Exception as e:
            print(f"Error updating player options for similar search: {e}")
            return [], True, None

    @callback(
        Output('similar-players-output-area', 'children'),
        [Input('similar-player-dropdown', 'value')],
        [State('num-results-slider', 'value')],
        prevent_initial_call=True
    )
    def find_and_display_similar_players(selected_player_name, num_results):
        if not selected_player_name:
            return ""

        role, selected_player_data = get_player_info(selected_player_name)
        if not role or selected_player_data is None:
            return dbc.Alert(f"Could not find data for {selected_player_name}.", color="danger", className="mt-4")

        position_map_inverse = {
            'GOALKEEPER': 'goalkeeper', 'CENTRE BACK': 'centreback', 'FULLBACK': 'fullback',
            'MIDFIELDER': 'midfielder', 'ATTACKING MIDFIELDER': 'attacking_midfielder',
            'WINGER': 'winger', 'STRIKER': 'striker'
        }
        pos_key = position_map_inverse.get(role)
        if not pos_key:
            return dbc.Alert(f"Invalid role found for {selected_player_name}.", color="danger", className="mt-4")
        
        file_path = os.path.join(BASE_PATH, f'{pos_key}_ratings_complete_en.csv')
        try:
            df_role = pd.read_csv(file_path, sep=';' if ';' in open(file_path).read(1024) else ',')
        except FileNotFoundError:
            return dbc.Alert(f"Data file for role {role} not found.", color="danger", className="mt-4")

        # 1. Trova i profili che esistono effettivamente in questo DataFrame
        existing_profiles = [p for p in PROFILES_TO_COMPARE if p in df_role.columns]
        if not existing_profiles:
            return dbc.Alert(f"No profile data found in the file for role {role}.", color="warning")

        # 2. Riempi i valori NaN con 0 solo per le colonne dei profili esistenti
        df_role[existing_profiles] = df_role[existing_profiles].fillna(0)
        
        # Aggiorna anche i dati del giocatore selezionato per coerenza
        # È importante ricaricarlo dal DF appena pulito per avere i dati allineati
        selected_player_data = df_role[df_role['Player'] == selected_player_name].iloc[0]

        # 3. Usa la lista dei profili esistenti per il calcolo
        df_role_filtered = df_role[df_role['Player'] != selected_player_name]

        # FIX: Escludi giocatori con un vettore di profili nullo (tutti zeri)
        # per evitare punteggi di similarità fuorvianti del 100%.
        df_role_filtered = df_role_filtered[df_role_filtered[existing_profiles].sum(axis=1) > 0]

        player_vector = selected_player_data[existing_profiles].values.reshape(1, -1)
        peer_vectors = df_role_filtered[existing_profiles].values

        if peer_vectors.shape[0] == 0:
            return dbc.Alert(f"Not enough players in the {role} role to perform a comparison.", color="warning", className="mt-4")
        
        # --- LOGICA DI SIMILARITÀ BASATA SUL RADAR ---
        
        # 1. Calcolare la similarità del coseno (per lo stile)
        cosine_sim = cosine_similarity(player_vector, peer_vectors)[0]
        
        # 2. Calcolare la distanza euclidea (per il livello)
        euclidean_dist = euclidean_distances(player_vector, peer_vectors)[0]
        
        # 3. Normalizzare la distanza euclidea in similarità
        if np.max(euclidean_dist) > 0:
            euclidean_sim = 1 - (euclidean_dist / np.max(euclidean_dist))
        else:
            euclidean_sim = np.ones_like(euclidean_dist)
        
        # 4. Calcolare la sovrapposizione del radar per ogni giocatore
        radar_similarities = []
        for i in range(len(peer_vectors)):
            # Calcola l'area di sovrapposizione tra i due radar
            player_radar = player_vector[0]  # Vettore del giocatore selezionato
            peer_radar = peer_vectors[i]     # Vettore del giocatore di confronto
            
            # Normalizza i vettori per il confronto del radar (0-100)
            player_normalized = player_radar / np.max(player_radar) * 100
            peer_normalized = peer_radar / np.max(peer_radar) * 100
            
            # Calcola la sovrapposizione come media delle differenze minime
            # Più simili sono i valori, più alta è la sovrapposizione
            overlap_scores = []
            for j in range(len(player_normalized)):
                # Calcola quanto si sovrappongono i due valori
                min_val = min(player_normalized[j], peer_normalized[j])
                max_val = max(player_normalized[j], peer_normalized[j])
                
                if max_val > 0:
                    # La sovrapposizione è la percentuale del valore minimo rispetto al massimo
                    overlap = min_val / max_val
                else:
                    overlap = 1.0  # Se entrambi sono 0, sono identici
                
                overlap_scores.append(overlap)
            
            # La similarità del radar è la media delle sovrapposizioni
            radar_sim = np.mean(overlap_scores)
            radar_similarities.append(radar_sim)
        
        radar_similarities = np.array(radar_similarities)
        
        # 5. Calcolare il punteggio finale combinando tutti i metodi
        weight_cosine = 0.65      # Peso per lo stile (coseno)
        weight_euclidean = 0.20   # Peso per il livello (euclidea)
        weight_radar = 0.15       # Peso per la sovrapposizione del radar
        
        final_scores = (weight_cosine * cosine_sim) + (weight_euclidean * euclidean_sim) + (weight_radar * radar_similarities)
        
        # 6. Normalizzazione finale per assicurarsi che i punteggi siano tra 0 e 1
        if np.max(final_scores) > 0:
            final_scores = final_scores / np.max(final_scores)
        
        # 7. Creare una lista di giocatori simili con il nuovo punteggio
        similar_players = []
        for i, score in enumerate(final_scores):
            player_info = df_role_filtered.iloc[i]
            similar_players.append((player_info, score))
            
        # 8. Ordinare e prendere i primi N
        similar_players.sort(key=lambda x: x[1], reverse=True)
        top_n_similar = similar_players[:num_results]

        if not top_n_similar:
            return dbc.Alert(f"No similar players found for {selected_player_name}.", color="info", className="mt-4")
        
        output_title = html.H4(f"Top {num_results} Most Similar Players to {selected_player_name}", className="mb-4 text-center")
        output_cards = [create_similar_player_card(player, score) for player, score in top_n_similar]
        
        return html.Div([output_title] + output_cards) 