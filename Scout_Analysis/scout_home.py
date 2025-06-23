import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# List of positions with icons and colors
POSITIONS = [
    {
        "name": "Goalkeeper", 
        "icon": "fas fa-hand-paper",
        "color": "#e63946",
        "profiles": ["Playmaker_Keeper", "Shot_Stopper"],
        "url": "/scout-analysis?position=goalkeeper"
    },
    {
        "name": "Centre Back", 
        "icon": "fas fa-shield-alt",
        "color": "#457b9d",
        "profiles": ["Guardian", "Deep_Distributor", "Enforcer"],
        "url": "/scout-analysis?position=centreback"
    },
    {
        "name": "Full Back", 
        "icon": "fas fa-running",
        "color": "#1d3557",
        "profiles": ["Sentinel_Fullback", "Advanced_Wingback", "Overlapping_Runner"],
        "url": "/scout-analysis?position=fullback"
    },
    {
        "name": "Midfielder", 
        "icon": "fas fa-compass",
        "color": "#2a9d8f",
        "profiles": ["Pivot_Master", "Maestro", "Box_to_Box"],
        "url": "/scout-analysis?position=midfielder"
    },
    {
        "name": "Attacking Midfielder", 
        "icon": "fas fa-star",
        "color": "#f4a261",
        "profiles": ["Diez", "Space_Invader"],
        "url": "/scout-analysis?position=attacking_midfielder"
    },
    {
        "name": "Winger", 
        "icon": "fas fa-bolt",
        "color": "#e76f51",
        "profiles": ["Key_Passer", "Creative_Winger"],
        "url": "/scout-analysis?position=winger"
    },
    {
        "name": "Striker", 
        "icon": "fas fa-bullseye",
        "color": "#264653",
        "profiles": ["Falso_Nueve", "Aerial_Dominator", "Lethal_Striker"],
        "url": "/scout-analysis?position=striker"
    },
    {
        "name": "Valverde Profile", 
        "icon": "fas fa-dna",
        "color": "#6c757d",
        "profiles": ["Versatile players with high scores in 2+ different profiles"],
        "url": "/scout-analysis?position=valverde"
    }
]

def create_navbar():
    """Create navigation bar for Scout Analysis"""
    return dbc.Navbar(
        dbc.Container([
            # Logo/Brand con icona
            dbc.NavbarBrand([
                html.I(className="fas fa-search-location me-2", style={"fontSize": "1.3rem"}),
                "ScoutVision"
            ], 
                href="/",
                style={
                    "fontFamily": "'Poppins', sans-serif", 
                    "fontWeight": "700",
                    "fontSize": "1.5rem",
                    "color": "white",
                    "textDecoration": "none"
                }
            ),
            
            # Menu a tendina
            dbc.Nav([
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem([
                            html.I(className="fas fa-home me-2"),
                            "Home"
                        ], 
                        href="/", 
                        style={
                            "fontFamily": "'Poppins', sans-serif",
                            "padding": "10px 20px",
                            "transition": "all 0.3s ease"
                        },
                        className="dropdown-item-hover"
                        ),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem([
                            html.I(className="fas fa-chart-line me-2", style={"color": "#457b9d"}),
                            "Scout Analysis"
                        ], 
                        href="/scout-analysis", 
                        style={
                            "fontFamily": "'Poppins', sans-serif",
                            "padding": "10px 20px",
                            "transition": "all 0.3s ease"
                        },
                        className="dropdown-item-hover"
                        ),
                        dbc.DropdownMenuItem([
                            html.I(className="fas fa-users me-2", style={"color": "#e63946"}),
                            "Lineup Builder"
                        ], 
                        href="/lineup-builder", 
                        style={
                            "fontFamily": "'Poppins', sans-serif",
                            "padding": "10px 20px",
                            "transition": "all 0.3s ease"
                        },
                        className="dropdown-item-hover"
                        ),
                    ],
                    nav=True,
                    in_navbar=True,
                    label=[
                        html.I(className="fas fa-bars me-2"),
                        "Menu"
                    ],
                    toggle_style={
                        "color": "white",
                        "border": "2px solid rgba(255,255,255,0.3)",
                        "borderRadius": "25px",
                        "padding": "8px 20px",
                        "fontFamily": "'Poppins', sans-serif",
                        "fontWeight": "500",
                        "backgroundColor": "rgba(255,255,255,0.1)",
                        "transition": "all 0.3s ease"
                    }
                )
            ], className="ms-auto", navbar=True),
        ]),
        color="#1D3557",
        dark=True,
        className="mb-4",
        style={
            "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
            "borderBottom": "3px solid #457b9d"
        }
    )

def create_position_card(position):
    """Create a position card component"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(
                    className=position["icon"],
                    style={
                        "fontSize": "3rem",
                        "color": position["color"],
                        "marginBottom": "1rem"
                    }
                ),
                html.H4(
                    position["name"],
                    className="card-title text-center mb-3",
                    style={
                        "fontFamily": "'Poppins', sans-serif",
                        "fontWeight": "600",
                        "color": "#1D3557"
                    }
                ),
                html.Div([
                    html.Small(
                        f"Profiles: {len(position['profiles'])}",
                        className="text-muted d-block text-center mb-3"
                    ),
                    html.Div([
                        html.Span(
                            profile.replace('_', ' '),
                            className="badge bg-light text-dark me-1 mb-1",
                            style={"fontSize": "0.7rem"}
                        )
                        for profile in position["profiles"]
                    ], className="text-center")
                ]),
                dbc.Button(
                    "Analyze",
                    href=position["url"],
                    color="primary",
                    className="d-block mx-auto mt-3",
                    style={
                        "backgroundColor": position["color"],
                        "borderColor": position["color"],
                        "borderRadius": "25px",
                        "padding": "8px 25px"
                    }
                )
            ], className="text-center")
        ])
    ],
    className="h-100 shadow position-card",
    style={
        "border": "none",
        "borderRadius": "15px",
        "transition": "all 0.3s ease",
        "cursor": "pointer"
    })

# Layout della home page dello Scout Analysis
layout = html.Div([
    # Navbar
    create_navbar(),
    
    # Main content
    dbc.Container([
        # Header Section
        dbc.Row([
            dbc.Col([
                html.H1(
                    "🔍 Scout Analysis",
                    className="text-center mb-3",
                    style={
                        "color": "#1D3557", 
                        "fontFamily": "'Poppins', sans-serif", 
                        "fontWeight": "700",
                        "fontSize": "2.5rem"
                    }
                ),
                html.P(
                    "Select a position to start analyzing player profiles",
                    className="text-center text-muted lead mb-5",
                    style={"fontSize": "1.1rem"}
                )
            ], width=12)
        ], className="mb-5"),
        
        # Position Cards
        dbc.Row([
            dbc.Col(
                create_position_card(position),
                width=4,
                className="mb-4"
            )
            for position in POSITIONS
        ], className="justify-content-center"),
        
        # Sezione "Other Tools" con lo stile aggiornato
        html.Hr(className="my-5"),

        dbc.Row([
            dbc.Col([
                html.H2(
                    "Other Tools",
                    className="text-center mb-3",
                    style={
                        "color": "#1D3557",
                        "fontFamily": "'Poppins', sans-serif",
                        "fontWeight": "700"
                    }
                ),
                html.P(
                    "Additional utilities for player analysis and comparison",
                    className="text-center text-muted mb-5"
                )
            ])
        ], justify="center"),

        dbc.Row([
            # Card per Direct Comparison
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-balance-scale text-danger", style={"fontSize": "2.5rem"}),
                        html.H4("Direct Comparison", className="card-title text-center fw-bold mt-3"),
                        html.P(
                            "Compare stats and ratings between players",
                            className="card-text text-center text-muted"
                        ),
                        dcc.Link(
                            dbc.Button(
                                "Compare Players", 
                                color="danger", 
                                className="w-100 mt-3",
                                style={'borderRadius': '20px'}
                            ),
                            href="/player-comparison?mode=direct",
                            className="text-decoration-none"
                        )
                    ], className="text-center")
                ], className="h-100 shadow-sm border-0 p-3"),
                md=5
            ),
            # Card per Similar Players
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-users", style={"fontSize": "2.5rem", "color": "#20c997"}),
                        html.H4("Similar Players", className="card-title text-center fw-bold mt-3"),
                        html.P(
                            "Find players with similar characteristics",
                            className="card-text text-center text-muted"
                        ),
                        dcc.Link(
                            dbc.Button(
                                "Find Similar", 
                                className="w-100 mt-3",
                                style={'backgroundColor': '#20c997', 'borderColor': '#20c997', 'borderRadius': '20px'}
                            ),
                            href="/similar-players",
                            className="text-decoration-none"
                        )
                    ], className="text-center")
                ], className="h-100 shadow-sm border-0 p-3"),
                md=5
            )
        ], justify="center", className="g-4 mb-5")
    ])
])

# CSS aggiuntivo per le card delle posizioni
additional_css = """
<style>
.position-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.15) !important;
}

.position-card .card-body {
    padding: 2rem 1.5rem;
}

.position-card .badge {
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
}

.position-card i {
    transition: all 0.3s ease;
}

.position-card:hover i {
    transform: scale(1.1);
}
</style>
"""

# Callback per l'effetto hover sulle card
def register_scout_home_callbacks(app):
    app.clientside_callback(
        """
        function(n_clicks) {
            // Questo callback serve solo a triggerare l'effetto CSS
            return '';
        }
        """,
        Output("dummy-output", "children"),
        [Input({"type": "position-card", "index": ALL}, "n_clicks")]
    ) 
