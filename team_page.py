from dash import dcc, html, callback_context, ALL, no_update, State
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import os
import dash
import re

def get_team_info():
    """Get basic team information from various data sources"""
    season = "24-25"  # Hardcoded season
    # Read classification data
    clasificacion_df = pd.read_csv(f"pages/data_serie_a_{season}/clasificacion.csv")
    juve_position = clasificacion_df[clasificacion_df["Equipo"] == "Juventus"].index[0] + 1
    
    # Read market value and age data
    juve_df = pd.read_csv(f"pages/data_serie_a_{season}/Juventus FC.csv")
    
    # Calculate average age from Date of Birth/Age column
    ages = juve_df["Date of Birth/Age"].str.extract(r"\((\d+)\)").astype(float)
    avg_age = float(round(ages.mean(), 1)) if not ages.empty else 0
    
    # Extract market value (removing '€' and 'm' and converting to float)
    market_values = juve_df["Market Value"].str.extract(r"€(\d+\.\d+)m").astype(float)
    market_value = float(round(market_values.sum(), 2)) if not market_values.empty else 0
    
    # Calculate total salary
    total_salary = 0
    
    # Read salary data from Capology file
    salary_file = "pages/Salari_Capology/Serie_A/Juventus/Tabla_Limpia_Juventus.csv"
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
            print(f"Error reading salary file: {e}")
            total_salary = 0
    
    # Manual salaries for specific players
    salari_manuali = {
        "Vasilije Adžić": 740_000,
        "Kenan Yıldız": 2_960_000,
        "Jonas Rouhi": 370_000,
        "Nicolò Savona": 370_000,
        "Samuel Mbangula": 560_000,
        "Alberto costa": 930_000,
        "Renato Veiga": 1_480_000
    }
    
    # First add manual salaries
    # total_salary = sum(salari_manuali.values())  # COMMENTED OUT - now using Capology file only
    
    # Then process player folders
    # if os.path.exists(base_path):  # COMMENTED OUT - base_path not needed with Capology file
    base_path = ""  # Dummy definition to avoid NameError
    # for nome in os.listdir(base_path):  # COMMENTED OUT
    
    # Old player folder processing removed - now using Capology file only

    # Read formation data
    wyscout_df = pd.read_csv(f"pages/data_serie_a_{season}/Juventus_wyscout.csv", sep=";")
    most_used_formation = wyscout_df["Seleccionar esquema"].mode()[0]
    
    return {
        "position": juve_position,
        "market_value": market_value,
        "total_salary": round(total_salary / 1_000_000, 2),  # Convert to millions
        "avg_age": avg_age,
        "formation": most_used_formation
    }

# Basic layout
layout = html.Div([
    # Add this at the top of the layout
    dcc.Store(id='player-styles', data={
        'player-marker:hover': {
            'transform': 'scale(1.1)',
            'z-index': '1000'
        },
        'player-marker:hover .player-minutes': {
            'display': 'block'
        }
    }),
    
    # Hidden div for triggering callbacks
    html.Div(id="trigger-update", children="initial", style={"display": "none"}),
    
    # Header bar
    html.Div(
        dbc.Container(
            html.H1("Juventus FC - Team Overview", className="text-white mb-0", 
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
                                    src="/assets/Juventus.png",
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
                                    html.H3(id="team-position", className="mb-0",
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
                                    html.H3(id="market-value", className="mb-0",
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
                                    html.H3(id="avg-age", className="mb-0",
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
                                    html.H3(id="formation", className="mb-0",
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
                                    html.H3(id="total-salary", className="mb-0",
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
                            id='wdl-chart',
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
                            id='goals-chart',
                            config={'displayModeBar': False}
                        )
                    )
                ], className="shadow-sm"),
                width=12,
                lg=6,
                className="mb-4"
            )
        ]),
        
        # Top Scorer and Formation combined section
        dbc.Card([
            dbc.CardHeader(
                html.H3("Top Scorer & Starting XI", className="text-center m-0")
            ),
            dbc.CardBody([
                dbc.Row([
                    # Top Scorer section
                    dbc.Col(
                        html.Div([
                            html.Img(
                                src="/assets/Players/Dušan Vlahović.png", 
                                style={
                                    'width': '120px', 
                                    'height': '120px', 
                                    'border-radius': '50%',
                                    'margin-bottom': '10px'
                                }
                            ),
                            html.H4("Dušan Vlahović", className="mb-2"),
                            # Stats container
                            html.Div([
                                # Goals
                                html.Div([
                                    html.Span("Goals: ", className="text-muted"),
                                    html.Span("9", style={'font-weight': 'bold'})
                                ], className="mb-1"),
                                # Assists
                                html.Div([
                                    html.Span("Assists: ", className="text-muted"),
                                    html.Span("4", style={'font-weight': 'bold'})
                                ], className="mb-1"),
                                # xG
                                html.Div([
                                    html.Span("xG: ", className="text-muted"),
                                    html.Span("12.0", style={'font-weight': 'bold'})
                                ], className="mb-1"),
                                # Goals per 90'
                                html.Div([
                                    html.Span("Goals/90': ", className="text-muted"),
                                    html.Span("0.46", style={'font-weight': 'bold'})
                                ], className="mb-1")
                            ], style={
                                'display': 'flex',
                                'flex-direction': 'column',
                                'align-items': 'center',
                                'text-align': 'center',
                                'margin-top': '10px'
                            })
                        ], style={
                            'display': 'flex', 
                            'flex-direction': 'column', 
                            'align-items': 'center', 
                            'text-align': 'center',
                            'height': '100%',
                            'justify-content': 'center'
                        }),
                        width={"xs": 12, "md": 4},
                        className="mb-4 mb-lg-0"
                    ),
                    
                    # Formation section
                    dbc.Col([
                        html.Div([
                            # Center line
                            html.Div(
                                style={
                                    'position': 'absolute',
                                    'left': '50%',
                                    'top': '0',
                                    'bottom': '0',
                                    'width': '2px',
                                    'backgroundColor': 'white',
                                    'zIndex': '1'
                                }
                            ),
                            # Center circle
                            html.Div(
                                style={
                                    'position': 'absolute',
                                    'left': '50%',
                                    'top': '50%',
                                    'width': '70px',
                                    'height': '70px',
                                    'borderRadius': '50%',
                                    'border': '2px solid white',
                                    'transform': 'translate(-50%, -50%)',
                                    'zIndex': '1'
                                }
                            ),
                            # Left penalty area
                            html.Div(
                                style={
                                    'position': 'absolute',
                                    'left': '0',
                                    'top': '50%',
                                    'width': '80px',
                                    'height': '160px',
                                    'border': '2px solid white',
                                    'transform': 'translateY(-50%)',
                                    'zIndex': '1'
                                }
                            ),
                            # Left small box
                            html.Div(
                                style={
                                    'position': 'absolute',
                                    'left': '0',
                                    'top': '50%',
                                    'width': '30px',
                                    'height': '80px',
                                    'border': '2px solid white',
                                    'transform': 'translateY(-50%)',
                                    'zIndex': '1'
                                }
                            ),
                            # Left penalty arc
                            html.Div(
                                style={
                                    'position': 'absolute',
                                    'left': '80px',
                                    'top': '50%',
                                    'width': '20px',
                                    'height': '60px',
                                    'borderRadius': '0 30px 30px 0',
                                    'border': '2px solid white',
                                    'borderLeft': 'none',
                                    'transform': 'translateY(-50%)',
                                    'zIndex': '1'
                                }
                            ),
                            # Right penalty area
                            html.Div(
                                style={
                                    'position': 'absolute',
                                    'right': '0',
                                    'top': '50%',
                                    'width': '80px',
                                    'height': '160px',
                                    'border': '2px solid white',
                                    'transform': 'translateY(-50%)',
                                    'zIndex': '1'
                                }
                            ),
                            # Right small box
                            html.Div(
                                style={
                                    'position': 'absolute',
                                    'right': '0',
                                    'top': '50%',
                                    'width': '30px',
                                    'height': '80px',
                                    'border': '2px solid white',
                                    'transform': 'translateY(-50%)',
                                    'zIndex': '1'
                                }
                            ),
                            # Right penalty arc
                            html.Div(
                                style={
                                    'position': 'absolute',
                                    'right': '80px',
                                    'top': '50%',
                                    'width': '20px',
                                    'height': '60px',
                                    'borderRadius': '30px 0 0 30px',
                                    'border': '2px solid white',
                                    'borderRight': 'none',
                                    'transform': 'translateY(-50%)',
                                    'zIndex': '1'
                                }
                            ),
                            # Formation display container
                            html.Div(
                                id='formation-display',
                                style={
                                    'width': '500px',
                                    'height': '300px',
                                    'position': 'relative',
                                    'backgroundColor': '#3a8750',
                                    'borderRadius': '8px',
                                    'overflow': 'hidden',
                                    'display': 'flex',
                                    'justifyContent': 'center',
                                    'alignItems': 'center',
                                    'marginTop': '20px',
                                    'border': '2px solid white',
                                    'margin': '0 auto'
                                }
                            )
                        ], style={
                            'position': 'relative',
                            'width': '100%',
                            'height': '300px',
                            'display': 'flex',
                            'justifyContent': 'center'
                        })
                    ], md=8, xs=12, className="mb-4")
                ])
            ])
        ], className="shadow-sm mb-4"),
        
        # Players section
        dbc.Card([
            dbc.CardHeader(
                html.H3("Squad", className="text-center m-0")
            ),
            dbc.CardBody([
                # Goalkeepers
                html.Div([
                    html.H4("Goalkeepers", className="mb-3"),
                    html.Div(id="goalkeeper-buttons", className="d-flex flex-wrap gap-2")
                ], className="mb-4"),
                
                # Defenders
                html.Div([
                    html.H4("Defenders", className="mb-3"),
                    html.Div(id="defender-buttons", className="d-flex flex-wrap gap-2")
                ], className="mb-4"),
                
                # Midfielders
                html.Div([
                    html.H4("Midfielders", className="mb-3"),
                    html.Div(id="midfielder-buttons", className="d-flex flex-wrap gap-2")
                ], className="mb-4"),
                
                # Attackers
                html.Div([
                    html.H4("Attackers", className="mb-3"),
                    html.Div(id="attacker-buttons", className="d-flex flex-wrap gap-2")
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
                    id="analysis-tabs",
                    active_tab="tab-offensive",
                )
            ),
            dbc.CardBody(
                html.Div(id="analysis-content")
            )
        ], className="shadow-sm mb-4")
    ], fluid=True)
], className="bg-light min-vh-100")

def draw_formation(formation="4-2-3-1", players=None):
    """Draw the team formation on a soccer field"""
    # Create empty figure with transparent background
    field = go.Figure()
    
    # Default player data with minutes played
    default_players = {
        'GK': {'name': 'Di Gregorio', 'number': '29', 'minutes': 2610},
        'LB': {'name': 'Cambiaso', 'number': '27', 'minutes': 2008},
        'CB1': {'name': 'Gatti', 'number': '4', 'minutes': 2185},
        'CB2': {'name': 'Kalulu', 'number': '15', 'minutes': 2188},
        'RB': {'name': 'McKennie', 'number': '16', 'minutes': 2035},
        'CDM1': {'name': 'Locatelli', 'number': '5', 'minutes': 2476},
        'CDM2': {'name': 'Thuram', 'number': '19', 'minutes': 2056},
        'LW': {'name': 'Yıldız', 'number': '10', 'minutes': 2223},
        'CAM': {'name': 'Koopmeiners', 'number': '8', 'minutes': 1994},
        'RW': {'name': 'González', 'number': '11', 'minutes': 1459},
        'ST': {'name': 'Vlahović', 'number': '9', 'minutes': 1746}
    }
    
    # Formation positions (x, y coordinates) - adjusted for better spacing
    positions = {
        'GK': (3, 50),     # Goalkeeper - molto vicino alla porta
        'LB': (20, 80),    # Left back
        'CB1': (20, 60),   # Left center back
        'CB2': (20, 40),   # Right center back
        'RB': (20, 20),    # Right back
        'CDM1': (45, 60),  # Left defensive mid - ampio spazio dai difensori
        'CDM2': (45, 40),  # Right defensive mid
        'LW': (75, 80),    # Left wing - molto distante dai centrocampisti
        'CAM': (75, 50),   # Attacking mid
        'RW': (75, 20),    # Right wing
        'ST': (95, 50)     # Striker - molto avanzato
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
        
        # Add player name - adjusted position and style
        field.add_trace(go.Scatter(
            x=[coords[0]],
            y=[coords[1] - 8],  # Increased distance from circle
            mode='text',
            text=player['name'],
            textposition='top center',
            textfont=dict(
                color='white',
                size=11,  # Slightly larger font
                family='Arial',
                weight='bold'  # Make text bold
            ),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Update layout - make background transparent
    field.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            range=[0, 100],  # Adjusted range for better proportions
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=False,
            fixedrange=True
        ),
        yaxis=dict(
            range=[0, 100],  # Adjusted range for better proportions
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

def get_team_stats():
    """Get team statistics from the classification data"""
    season = "24-25"
    clasificacion_df = pd.read_csv(f"pages/data_serie_a_{season}/clasificacion.csv")
    juve_stats = clasificacion_df[clasificacion_df["Equipo"] == "Juventus"].iloc[0]
    
    return {
        "wins": int(juve_stats["PG"]),  # Partite Vinte
        "draws": int(juve_stats["PE"]),  # Pareggi
        "losses": int(juve_stats["PP"]), # Sconfitte
        "goals_for": int(juve_stats["GF"]),  # Gol Fatti
        "goals_against": int(juve_stats["GC"])  # Gol Subiti
    }

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

def register_team_callbacks(app):
    @app.callback(
        [
            Output("team-position", "children"),
            Output("market-value", "children"),
            Output("avg-age", "children"),
            Output("formation", "children"),
            Output("total-salary", "children")
        ],
        Input("trigger-update", "children")
    )
    def update_team_info(_):
        info = get_team_info()
        return [
            f"#{info['position']}",
            f"€{info['market_value']:.1f}M",
            f"{info['avg_age']:.1f} years",
            info['formation'].split()[0] if ' ' in info['formation'] else info['formation'],
            f"€{info['total_salary']:.2f}M"
        ]

    @app.callback(
        Output("formation-display", "children"),
        Input("trigger-update", "children")
    )
    def update_formation_display(_):
        """Update the formation display"""
        try:
            print("Updating formation display...")  # Debug print
            formation = draw_formation()
            print("Formation drawn successfully")  # Debug print
            return formation
        except Exception as e:
            print(f"Error updating formation display: {str(e)}")
            return html.Div("Error loading formation", className="text-danger")

    @app.callback(
        [Output("wdl-chart", "figure"),
         Output("goals-chart", "figure")],
        Input("trigger-update", "children")
    )
    def update_charts(_):
        stats = get_team_stats()
        wdl_fig = create_wdl_chart(stats["wins"], stats["draws"], stats["losses"])
        goals_fig = create_goals_chart(stats["goals_for"], stats["goals_against"])
        return wdl_fig, goals_fig

    @app.callback(
        [
            Output("goalkeeper-buttons", "children"),
            Output("defender-buttons", "children"),
            Output("midfielder-buttons", "children"),
            Output("attacker-buttons", "children")
        ],
        Input("trigger-update", "children")
    )
    def update_player_buttons(_):
        # Read player data
        df = pd.read_csv("pages/data_serie_a_24-25/Juventus.csv")
        
        # Extract primary position for each player
        df['primary_pos'] = df['Posc'].str.split(',').str[0]
        
        # Create buttons for each position group
        goalkeepers = [create_player_button(player) for player in df[df['primary_pos'] == 'PO']['Jugador']]
        defenders = [create_player_button(player) for player in df[df['primary_pos'] == 'DF']['Jugador']]
        midfielders = [create_player_button(player) for player in df[df['primary_pos'] == 'CC']['Jugador']]
        attackers = [create_player_button(player) for player in df[df['primary_pos'] == 'DL']['Jugador']]
        
        return goalkeepers, defenders, midfielders, attackers

    @app.callback(
        Output("analysis-content", "children"),
        [Input("analysis-tabs", "active_tab")]
    )
    def render_tab_content(active_tab):
        if active_tab == "tab-offensive":
            # Load Serie A data for build-up analysis
            df_serie_a = pd.read_csv("pages/data_serie_a_24-25/Serie_A_24-25.csv")
            
            # Calculate average of top 4 teams
            top_4_teams = ['Napoli', 'Inter', 'Atalanta', 'Juventus']
            top_4_df = df_serie_a[df_serie_a['Equipo'].isin(top_4_teams)]
            
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
            
            # Add Juventus trace
            juve_data = df_serie_a[df_serie_a['Equipo'] == 'Juventus'].iloc[0]
            juve_values = [(juve_data[metric] / metrics[metric]['max']) for metric in metrics.keys()]
            juve_values.append(juve_values[0])  # Close the polygon
            
            fig1.add_trace(go.Scatterpolar(
                r=juve_values,
                theta=[metrics[m]['name'] for m in metrics.keys()] + [metrics[list(metrics.keys())[0]]['name']],
                fill='toself',
                name='Juventus',
                line=dict(color='#000000'),
                fillcolor='rgba(0,0,0,0.2)'
            ))

            # Add Top 4 average trace
            top_4_teams = ['Napoli', 'Inter', 'Atalanta', 'Juventus']
            top_4_df = df_serie_a[df_serie_a['Equipo'].isin(top_4_teams)]
            top_4_avg = top_4_df[list(metrics.keys())].mean()
            top_4_values = [(top_4_avg[metric] / metrics[metric]['max']) for metric in metrics.keys()]
            top_4_values.append(top_4_values[0])  # Close the polygon
            
            fig1.add_trace(go.Scatterpolar(
                r=top_4_values,
                theta=[metrics[m]['name'] for m in metrics.keys()] + [metrics[list(metrics.keys())[0]]['name']],
                fill='toself',
                name='Top 4 Average',
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
                title="Build-up Analysis vs Top 4",
                title_x=0.5
            )

            # Load Wyscout data for detailed attacking analysis
            df_wyscout = pd.read_csv("pages/data_serie_a_24-25/Juventus_wyscout.csv", sep=';')
            
            # Filter only Juventus data
            df_wyscout = df_wyscout[df_wyscout['Equipo'] == 'Juventus']
            
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
            juve_wyscout = df_wyscout[df_wyscout['Equipo'] == 'Juventus']
            pass_types = {
                'Lateral Passes': juve_wyscout['Pases laterales / logrados'].mean(),
                'Long Passes': juve_wyscout['Pases largos / logrados'].mean(),
                'Final Third Passes': juve_wyscout['Pases en el último tercio / logrados'].mean(),
                'Deep Passes': juve_wyscout['Pases en profundidad completados'].mean(),
                'Progressive Passes': juve_wyscout['Pases progresivos / precisos'].mean(),
                'Crosses': juve_wyscout['Centros / precisos'].mean()
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
                margin=dict(l=20, r=100, t=40, b=20),  # Increased right margin for labels
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.1)',
                    zeroline=False
                ),
                yaxis=dict(
                    showgrid=False,
                    autorange="reversed"  # To match the order of the dictionary
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
            
            # Text analysis
            build_up_analysis = html.Div([
                html.H5("Build-up Analysis", className="text-center mb-4"),
                html.P([
                    "Juventus shows strong build-up characteristics:",
                    html.Ul([
                        html.Li("Excellent ball control with 86.4% pass accuracy (vs 84.5% top 4 avg)"),
                        html.Li("Strong possession game at 58.1% (vs 56.3% top 4 avg)"),
                        html.Li("High number of progressive carries: 744 (vs 672 top 4 avg)"),
                        html.Li("Dominant in central third with 10,973 touches (highest among top 4)")
                    ])
                ])
            ], className="mt-4")

            attacking_analysis = html.Div([
                html.H5("Attacking Style Analysis", className="text-center mb-4"),
                html.P([
                    "Juventus attacking patterns show:",
                    html.Ul([
                        html.Li(f"Preference for positional attacks ({attack_types['Positional Attacks']:.1f} per game) over counter-attacks ({attack_types['Counter Attacks']:.1f} per game)"),
                        html.Li(f"Strong box presence with {df_wyscout['Toques en el área de penalti'].mean():.1f} touches in the box per game"),
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

            # Calculate Juventus values
            juve_data = df_serie_a[df_serie_a['Equipo'] == 'Juventus'].iloc[0]
            
            # Calculate derived metrics for Juventus
            juve_values = {
                'npxG/Sh': juve_data['npxG/90'] / juve_data['T/90'] if juve_data['T/90'] > 0 else 0,
                'G/T': juve_data['G/T'],
                'TalArc/90': juve_data['TalArc/90'],
                'Gls./90': juve_data['Gls./90']
            }

            # Normalize values between 0 and 1
            juve_normalized = []
            for metric in finishing_metrics.keys():
                value = juve_values[metric]
                max_val = finishing_metrics[metric]['max']
                value = value / max_val
                value = min(max(value, 0), 1)  # Clamp between 0 and 1
                juve_normalized.append(value)
            
            # Add first value to close the polygon
            juve_normalized.append(juve_normalized[0])

            # Add Juventus trace
            finishing_fig.add_trace(go.Scatterpolar(
                r=juve_normalized,
                theta=[metrics['name'] for metrics in finishing_metrics.values()] + [finishing_metrics[list(finishing_metrics.keys())[0]]['name']],
                fill='toself',
                name='Juventus',
                line=dict(color='#000000'),
                fillcolor='rgba(0,0,0,0.2)'
            ))

            # Calculate top 4 average
            top_4_data = df_serie_a[df_serie_a['Equipo'].isin(top_4_teams)]
            top_4_avg = {
                'npxG/Sh': (top_4_data['npxG/90'] / top_4_data['T/90']).mean(),
                'G/T': top_4_data['G/T'].mean(),
                'TalArc/90': top_4_data['TalArc/90'].mean(),
                'Gls./90': top_4_data['Gls./90'].mean()
            }

            # Normalize top 4 values
            top_4_normalized = []
            for metric in finishing_metrics.keys():
                value = top_4_avg[metric]
                max_val = finishing_metrics[metric]['max']
                value = value / max_val
                value = min(max(value, 0), 1)  # Clamp between 0 and 1
                top_4_normalized.append(value)
            
            # Add first value to close the polygon
            top_4_normalized.append(top_4_normalized[0])

            # Add Top 4 average trace
            finishing_fig.add_trace(go.Scatterpolar(
                r=top_4_normalized,
                theta=[metrics['name'] for metrics in finishing_metrics.values()] + [finishing_metrics[list(finishing_metrics.keys())[0]]['name']],
                fill='toself',
                name='Top 4 Average',
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
                title="Finishing Quality Analysis vs Top 4",
                title_x=0.5,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400
            )

            # Il testo si aggiornerà automaticamente con i nuovi valori
            finishing_analysis = html.Div([
                html.H5("Finishing Quality Analysis", className="text-center mb-4"),
                html.P([
                    "Analysis of Juventus finishing quality compared to top 4 teams:",
                    html.Ul([
                        html.Li(f"Shot Quality: {juve_values['npxG/Sh']:.3f} npxG per shot (Top 4 avg: {top_4_avg['npxG/Sh']:.3f})"),
                        html.Li(f"Conversion Rate: {juve_values['G/T']*100:.1f}% of shots scored (Top 4 avg: {top_4_avg['G/T']*100:.1f}%)"),
                        html.Li(f"Shots on Target per 90: {juve_values['TalArc/90']:.2f} (Top 4 avg: {top_4_avg['TalArc/90']:.2f})"),
                        html.Li(f"Goals per 90: {juve_values['Gls./90']:.2f} (Top 4 avg: {top_4_avg['Gls./90']:.2f})")
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
                    ], width=12)
                ])
            ])
            
        elif active_tab == "tab-defensive":
            # Load Wyscout data
            df_wyscout = pd.read_csv("pages/data_serie_a_24-25/Juventus_wyscout.csv", sep=';')
            
            # Load Serie A data for defensive quality analysis
            df_serie_a = pd.read_csv("pages/data_serie_a_24-25/Serie_A_24-25.csv")
            
            defensive_style_analysis = create_defensive_style_analysis(df_wyscout)
            defensive_quality_analysis = create_defensive_quality_analysis(df_serie_a)
            
            return html.Div([
                html.H4("Defensive Analysis", className="text-center mb-4"),
                defensive_style_analysis,
                html.Hr(className="my-4"),
                defensive_quality_analysis
            ])
            
        elif active_tab == "tab-set-pieces":
            # Load data
            df_serie_a = pd.read_csv("pages/data_serie_a_24-25/Serie_A_24-25.csv")
            df_wyscout = pd.read_csv("pages/data_serie_a_24-25/Juventus_wyscout.csv", sep=";")
            
            # Define top 4 teams
            top_4_teams = ['Napoli', 'Inter', 'Atalanta', 'Juventus']
            
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
            top_4_df = df_processed[df_processed['Equipo'].isin(top_4_teams)]
            
            # Calculate averages for insights (only numeric columns)
            numeric_columns = ['PassDead_GCA90', 'FK_per90', 'FK_Efficiency']
            top_4_avg = top_4_df[numeric_columns].mean()
            juve_data = top_4_df[top_4_df['Equipo'] == 'Juventus'].iloc[0]
            
            # Create radar chart
            metric_labels = {
                'PassDead_GCA90': 'Set Goals',
                'FK_per90': 'Free Kicks',
                'FK_Efficiency': 'Set Efficiency'
            }
            
            # Define fixed maximum values for each metric
            max_values = {
                'PassDead_GCA90': 0.3,    # Massimo valore per Goal-Creating Actions da palla inattiva per 90
                'FK_per90': 15.5,           # Massimo valore per calci di punizione per 90
                'FK_Efficiency': 3.0       # Massimo valore per efficienza dei calci piazzati
            }
            
            fig_radar = go.Figure()
            
            # Add traces for each team
            for team in top_4_teams:
                team_data = top_4_df[top_4_df['Equipo'] == team].iloc[0]
                # Normalize values to have a maximum radius of 2.5
                normalized_values = [team_data[col] * (2.5 / max_values[col]) for col in numeric_columns]
                fig_radar.add_trace(go.Scatterpolar(
                    r=normalized_values,
                    theta=[metric_labels[col] for col in numeric_columns],
                    name=team,
                    fill='toself'
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 2.5]  # Fixed range to 2.5
                    )),
                showlegend=True,
                title="Set Pieces Effectiveness - Top 4 Teams"
            )
            
            # Process Wyscout data for detailed Juventus analysis
            juve_wyscout = df_wyscout.copy()
            corners_total = juve_wyscout['Córneres / con remate'].mean()
            corners_shots = juve_wyscout['Unnamed: 39'].mean()
            freekicks_total = juve_wyscout['Tiros libres / con remate'].mean()
            freekicks_shots = juve_wyscout['Unnamed: 42'].mean()
            
            # Create bar chart for Juventus detailed analysis
            fig_detail = go.Figure(data=[
                go.Bar(name='Total', x=['Corner Kicks', 'Free Kicks'], 
                      y=[corners_total, freekicks_total]),
                go.Bar(name='With Shot', x=['Corner Kicks', 'Free Kicks'], 
                      y=[corners_shots, freekicks_shots])
            ])
            
            fig_detail.update_layout(
                barmode='group',
                title="Juventus Set Pieces Analysis - Average per Match",
                yaxis_title="Count"
            )
            
            # Generate insights
            def generate_insights(juve_data, top4_avg):
                insights = []
                metrics_info = {
                    'PassDead_GCA90': ('Goal-Creating Actions from Set Pieces per 90', 'higher'),
                    'FK_per90': ('Free Kicks per 90', 'neutral'),
                    'FK_Efficiency': ('Free Kick Efficiency (%)', 'higher')
                }
                
                for metric, (metric_name, preference) in metrics_info.items():
                    juve_value = juve_data[metric]
                    avg_value = top4_avg[metric]
                    diff_pct = ((juve_value - avg_value) / avg_value) * 100
                    
                    if abs(diff_pct) > 10:  # Only show significant differences
                        if diff_pct > 0:
                            color = "success" if preference == "higher" else "warning"
                            text = f"Juventus excels in {metric_name}, performing {abs(diff_pct):.1f}% better than the top 4 average"
                        else:
                            color = "warning" if preference == "higher" else "success"
                            text = f"Juventus shows room for improvement in {metric_name}, performing {abs(diff_pct):.1f}% below the top 4 average"
                        
                        insights.append(dbc.Alert(text, color=color, className="mb-2"))
                
                return insights
            
            insights = generate_insights(juve_data, top_4_avg)
            
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

    @app.callback(
        Output("formation-players", "children"),
        Input("trigger-update", "children")
    )
    def update_formation_players(_):
        """Update the formation display with player markers"""
        try:
            # Read player data
            df = pd.read_csv("pages/data_serie_a_24-25/Juventus.csv")
            
            # Convert minutes to numeric, removing any commas
            df['minutes'] = pd.to_numeric(df['Mín'].str.replace(',', ''), errors='coerce')
            
            # Find player with most minutes
            max_minutes_player = df.loc[df['minutes'].idxmax()]['Jugador']
            
            # Create player markers with minutes
            player_markers = []
            positions = {
                'GK': {'name': 'Di Gregorio', 'pos': (5, 95)},
                'LB': {'name': 'Cambiaso', 'pos': (20, 20)},
                'LCB': {'name': 'Kalulu', 'pos': (20, 40)},
                'RCB': {'name': 'Gatti', 'pos': (20, 60)},
                'RB': {'name': 'McKennie', 'pos': (20, 80)},
                'LCM': {'name': 'Locatelli', 'pos': (40, 40)},
                'RCM': {'name': 'Thuram', 'pos': (40, 60)},
                'LW': {'name': 'Yıldız', 'pos': (60, 20)},
                'CAM': {'name': 'Koopmeiners', 'pos': (60, 50)},
                'RW': {'name': 'González', 'pos': (60, 80)},
                'ST': {'name': 'Vlahović', 'pos': (80, 50)}
            }
            
            for role, info in positions.items():
                player_data = df[df['Jugador'] == info['name']]
                if not player_data.empty:
                    player = player_data.iloc[0]
                    minutes = int(player['minutes']) if not pd.isna(player['minutes']) else 0
                    is_most_played = player['Jugador'] == max_minutes_player
                    
                    marker = create_player_marker(
                        info['name'],
                        player['Número'] if 'Número' in df.columns else '',
                        minutes,
                        is_most_played
                    )
                    
                    # Add position-specific styling
                    x, y = info['pos']
                    marker.style.update({
                        'left': f'{x}%',
                        'bottom': f'{y}%',
                        'transform': 'translate(-50%, 50%)'
                    })
                    
                    player_markers.append(marker)
            
            return player_markers
            
        except Exception as e:
            print(f"Error updating formation players: {str(e)}")
            return []

def create_defensive_style_analysis(df_wyscout):
    # Filtra solo le partite di Serie A e gli avversari
    df_opponents = df_wyscout[
        (df_wyscout['Competición'] == 'Italy. Serie A') & 
        (df_wyscout['Equipo'] != 'Juventus')
    ].copy()

    # Calcola le percentuali per i vari tipi di recuperi palla
    df_opponents['% Recuperi Bassi'] = df_opponents['Unnamed: 20'].astype(float) / df_opponents['Balones recuperados /bajos / medios / altos'].astype(float) * 100
    df_opponents['% Recuperi Medi'] = df_opponents['Unnamed: 21'].astype(float) / df_opponents['Balones recuperados /bajos / medios / altos'].astype(float) * 100
    df_opponents['% Recuperi Alti'] = df_opponents['Unnamed: 22'].astype(float) / df_opponents['Balones recuperados /bajos / medios / altos'].astype(float) * 100
    
    # Calcola la percentuale di duelli difensivi vinti
    df_opponents['% Duelli Difensivi Vinti'] = df_opponents['Unnamed: 65'].astype(float) / df_opponents['Duelos defensivos / ganados'].astype(float) * 100
    
    # Calcola la percentuale di passaggi lunghi riusciti
    df_opponents['% Passaggi Lunghi Riusciti'] = df_opponents['Unnamed: 88'].astype(float) / df_opponents['Pases largos / logrados'].astype(float) * 100

    # Definisci gli stili di gioco basati su PPDA e intensità di passaggio
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

    # Metriche per il radar chart (usando i valori calcolati)
    metrics = {
        'PPDA': {'name': 'PPDA', 'max': 25},  # Ridotto da 20 per una migliore scala
        '% Duelli Difensivi Vinti': {'name': 'Defensive Duels Won %', 'max': 80},  # Ridotto da 100 per evidenziare meglio le differenze
        'Faltas': {'name': 'Fouls', 'max': 15},  # Ridotto da 20 per una migliore scala
        'Interceptaciones': {'name': 'Interceptions', 'max': 45},  # Ridotto da 15 per una migliore scala
        '% Recuperi Alti': {'name': 'High Recovery %', 'max': 30},  # Ridotto da 100 per evidenziare meglio le differenze
        '% Passaggi Lunghi Riusciti': {'name': 'Long Passes Success %', 'max': 80}  # Ridotto da 100 per evidenziare meglio le differenze
    }

    # Crea il radar chart
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
            # Calcola la media solo per la metrica specifica
            value = style_data[metric].astype(float).mean() / metrics[metric]['max']
            values.append(value)
        values.append(values[0])  # Chiudi il poligono
        
        radar_fig.add_trace(go.Scatterpolar(
            r=values,
            theta=[metrics[m]['name'] for m in metrics.keys()] + [metrics[list(metrics.keys())[0]]['name']],
            fill='toself',
            name=style,
            line=dict(color=colors[style]),
            fillcolor=colors[style].replace(')', ', 0.2)').replace('rgb', 'rgba'),
            hovertemplate=f"<b>{style}</b><br>" +
                         "<br>".join([f"{metrics[m]['name']}: {style_data[metric].astype(float).mean():.2f}" for m, metric in zip(metrics.keys(), metrics.keys())]) +
                         "<extra></extra>"
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
        legend=dict(
            yanchor="top",
            y=1.2,
            xanchor="left",
            x=0.1
        ),
        title=dict(
            text='Defensive Performance Against Different Playing Styles',
            y=0.95,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        height=600,
        margin=dict(t=100, b=50, l=50, r=50)
    )

    # Crea il grafico della distribuzione dei recuperi palla
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

    # Genera insights automatici
    insights = []
    for style in df_opponents['Style'].unique():
        style_data = df_opponents[df_opponents['Style'] == style]
        
        # Analisi PPDA
        ppda_avg = style_data['PPDA'].astype(float).mean()
        if ppda_avg < df_opponents['PPDA'].astype(float).mean():
            insights.append(f"✅ Strong pressing performance against {style} teams (PPDA: {ppda_avg:.2f})")
        
        # Analisi duelli difensivi
        duels_won = style_data['% Duelli Difensivi Vinti'].mean()
        if duels_won > 50:
            insights.append(f"💪 Good defensive duel success rate against {style} teams ({duels_won:.1f}%)")
        
        # Analisi recuperi palla alti
        high_recoveries = style_data['% Recuperi Alti'].mean()
        if high_recoveries > df_opponents['% Recuperi Alti'].mean():
            insights.append(f"🔄 Above average high ball recoveries against {style} teams ({high_recoveries:.1f}%)")
        
        # Analisi passaggi lunghi
        long_passes = style_data['% Passaggi Lunghi Riusciti'].mean()
        if long_passes > 70:
            insights.append(f"🎯 Excellent long pass success rate against {style} teams ({long_passes:.1f}%)")

    return html.Div([
        dcc.Graph(figure=radar_fig),
        html.H4("Ball Recovery Analysis", className="mt-4"),
        dcc.Graph(figure=recovery_fig),
        html.Div([
            html.H5("Key Defensive Insights", className="mt-4"),
            html.Ul([html.Li(insight) for insight in insights], className="mt-3")
        ], className="mt-4")
    ])

def create_defensive_quality_analysis(df_serie_a):
    # Carica i dati dalla classificazione
    clasificacion = pd.read_csv("pages/data_serie_a_24-25/clasificacion.csv")
    
    # Filtra solo le top 4 squadre
    top_4_teams = ['Napoli', 'Inter', 'Atalanta', 'Juventus']
    top_4_df = clasificacion[clasificacion['Equipo'].isin(top_4_teams)].copy()
    
    # Calcola GC90 e xGA90
    top_4_df['GC90'] = top_4_df['GC'] / top_4_df['PJ']
    top_4_df['xGA90'] = top_4_df['xGA'] / top_4_df['PJ']
    
    # Merge con i dati di Serie A per le altre statistiche
    top_4_df = top_4_df.merge(
        df_serie_a[['Equipo', 'Tkl_%', 'Exitosa%', 'Bloqueos_totales', 'Intercepciones', 'Errores', 'Tkl+Int']], 
        on='Equipo',
        how='left'
    )
    
    # Lista delle colonne numeriche che ci interessano
    numeric_columns = ['GC90', 'xGA90', 'Tkl_%', 'Exitosa%', 'Bloqueos_totales', 'Intercepciones', 'Errores', 'Tkl+Int']
    
    # Definisci le metriche e i loro valori massimi
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

    # Inverti gli errori (più è alto, meglio è)
    max_errores = top_4_df['Errores'].max()
    top_4_df['Errores'] = max_errores - top_4_df['Errores']

    # Crea il radar chart
    radar_fig = go.Figure()

    # Aggiungi una traccia per ogni squadra
    colors = {
        'Juventus': '#000000',
        'Inter': '#1D3557',
        'Napoli': '#457B9D',
        'Atalanta': '#A8DADC'
    }

    for team in top_4_teams:
        team_data = top_4_df[top_4_df['Equipo'] == team]
        values = []
        for metric in metrics.keys():
            value = team_data[metric].iloc[0] / metrics[metric]['max']
            value = min(max(value, 0), 1)  # Clamp tra 0 e 1
            values.append(value)
        values.append(values[0])  # Chiudi il poligono

        radar_fig.add_trace(go.Scatterpolar(
            r=values,
            theta=[metrics[m]['name'] for m in metrics.keys()] + [metrics[list(metrics.keys())[0]]['name']],
            fill='toself',
            name=team,
            line=dict(color=colors[team]),
            fillcolor=colors[team].replace(')', ', 0.2)').replace('rgb', 'rgba')
        ))

    # Aggiorna il layout
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
        title="Defensive Quality Analysis vs Top 4",
        height=500
    )

    # Genera insights automatici
    juve_data = top_4_df[top_4_df['Equipo'] == 'Juventus'].iloc[0]
    top_4_avg = top_4_df[top_4_df['Equipo'] != 'Juventus'][numeric_columns].mean()

    insights = []
    
    # Analisi dei punti di forza
    if juve_data['Tkl_%'] > top_4_avg['Tkl_%']:
        insights.append(f"✅ Strong tackling success rate ({juve_data['Tkl_%']:.1f}% vs {top_4_avg['Tkl_%']:.1f}% avg)")
    
    if juve_data['Bloqueos_totales'] > top_4_avg['Bloqueos_totales']:
        insights.append(f"💪 Excellent blocking ({juve_data['Bloqueos_totales']:.0f} vs {top_4_avg['Bloqueos_totales']:.0f} avg)")
    
    if juve_data['xGA90'] < top_4_avg['xGA90']:
        insights.append(f"🎯 Better than average xGA/90 ({juve_data['xGA90']:.2f} vs {top_4_avg['xGA90']:.2f} avg)")

    # Analisi delle aree di miglioramento
    if juve_data['Errores'] < top_4_avg['Errores']:
        insights.append(f"⚠️ Higher error rate than average ({max_errores - juve_data['Errores']:.0f} vs {max_errores - top_4_avg['Errores']:.0f} avg)")
    
    if juve_data['Exitosa%'] < top_4_avg['Exitosa%']:
        insights.append(f"📉 Lower duels won % ({juve_data['Exitosa%']:.1f}% vs {top_4_avg['Exitosa%']:.1f}% avg)")
    
    if juve_data['Intercepciones'] < top_4_avg['Intercepciones']:
        insights.append(f"⚠️ Fewer interceptions ({juve_data['Intercepciones']:.0f} vs {top_4_avg['Intercepciones']:.0f} avg)")

    return html.Div([
        dcc.Graph(figure=radar_fig),
        html.H5("Defensive Performance Insights", className="mt-4"),
        html.Ul([html.Li(insight) for insight in insights], className="mt-3")
    ])