import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Lista delle leghe con immagini corrispondenti
LEAGUES = [
    {"name": "Premier League", "image": "/assets/Premier_League.png", "url": "/league?league=EPL"},
    {"name": "Serie A", "image": "/assets/Serie_A.png", "url": "/serie_a"},
    {"name": "La Liga", "image": "/assets/La_Liga.png", "url": "/league?league=La_Liga"},
    {"name": "Bundesliga", "image": "/assets/Bundesliga.png", "url": "/league?league=Bundesliga"},
    {"name": "Ligue 1", "image": "/assets/Ligue_1.png", "url": "/league?league=Ligue_1"},
    {"name": "Primeira Liga", "image": "/assets/Primeira_Liga.png", "url": "/league?league=Primeira_Liga"},
    {"name": "Serie B", "image": "/assets/serie_b_logo.png", "url": "/league?league=Serie_B"},
    {"name": "Bundesliga 2", "image": "/assets/Bundesliga_2_logo.png", "url": "/league?league=Bundesliga_2"},
    {"name": "Ligue 2", "image": "/assets/Ligue_2_logo.png", "url": "/league?league=Ligue_2"},
    {"name": "Championship", "image": "/assets/championship_logo.png", "url": "/league?league=Championship"},
    {"name": "Eredivisie", "image": "/assets/Eredivisie_logo.png", "url": "/league?league=Eredivisie"},
    {"name": "Jupiler Pro League", "image": "/assets/Jupiler_pro_league_logo.png", "url": "/league?league=Jupiler_Pro_League"},
    {"name": "Liga Argentina", "image": "/assets/Liga_profesional_de_futbol.png", "url": "/league?league=Liga_Argentina"},
    {"name": "MLS", "image": "/assets/MLS_logo.png", "url": "/league?league=MLS"},
    {"name": "Süper Lig", "image": "/assets/Süper_Lig_logo.png", "url": "/league?league=Süper_Lig"}
]

# Componente navbar con menu a tendina migliorato
def create_navbar():
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
            
            # Menu a tendina migliorato
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

# Layout della pagina delle leghe con navbar
layout = html.Div([
    # Navbar
    create_navbar(),
    
    # Contenuto principale
    dbc.Container(
        [
            html.H1(
                "Select a League",
                className="text-center mb-4",
                style={"color": "#1D3557", "fontFamily": "'Poppins', sans-serif", "fontWeight": "700"}
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardImg(src=league["image"], top=True, style={"height": "150px", "objectFit": "contain"}),
                                dbc.CardBody(
                                    [
                                        html.H5(
                                            league["name"],
                                            className="card-title text-center",
                                            style={"fontFamily": "'Poppins', sans-serif"}
                                        ),
                                        dbc.Button("View Teams", href=league["url"], color="primary", className="d-block mx-auto"),
                                    ]
                                ),
                            ],
                            className="shadow",
                        ),
                        width=4,
                        className="mb-4",
                    )
                    for league in LEAGUES
                ],
                className="justify-content-center",
            ),
        ],
        className="py-5",
    ),
    html.Footer(
        dbc.Container(
            [
                html.P(
                    "© 2025 ScoutVision - All Rights Reserved",
                    className="text-center",
                    style={"fontFamily": "'Poppins', sans-serif"}
                ),
            ],
            className="py-3",
        ),
        style={"backgroundColor": "#1D3557", "color": "white", "marginTop": "50px"},
    ),
])