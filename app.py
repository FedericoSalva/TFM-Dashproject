import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'pages', 'Scout Analysis'))

# app.py aggiornato e corretto per /league?league=XYZ routing

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Import pages
import pages.league as league_page
import pages.serie_a as serie_a_page
import pages.league_template as league_template_page
import pages.team_page as team_page
# import pages.serie_a_routes as serie_a_routes  # Commentato temporaneamente per errore indentazione
import pages.league_routes as league_routes
import pages.serie_a_teams as serie_a_teams
from pages.team_analysis import LEAGUE_FOLDER_MAPPING

# Import Scout Analysis pages
import pages.Scout_Analysis.scout_analysis as scout_analysis_page
import pages.Scout_Analysis.scout_home as scout_home_page
import pages.Scout_Analysis.player_comparison as player_comparison
import pages.Scout_Analysis.similar_players as similar_players

# Initialize Dash
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ]
)
app.title = "ScoutVision"

# CSS personalizzato per effetti hover
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .dropdown-item-hover:hover {
                background: linear-gradient(135deg, #457b9d, #1D3557) !important;
                color: white !important;
                transform: translateX(5px);
            }
            
            .navbar-nav .dropdown-toggle:hover {
                background-color: rgba(255,255,255,0.2) !important;
                transform: scale(1.05);
            }
            
            .navbar-brand:hover {
                transform: scale(1.05);
                transition: all 0.3s ease;
            }
            
            .dropdown-menu {
                animation: slideDown 0.3s ease-out;
                border-radius: 15px !important;
                border: none !important;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
                margin-top: 10px !important;
                min-width: 200px !important;
            }
            
            /* Scout Analysis Card Styles */
            .hover-card {
                transition: all 0.3s ease;
                border: 1px solid #e9ecef;
                border-radius: 15px;
                overflow: hidden;
            }
            
            .hover-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15) !important;
                border-color: #1D3557;
            }
            
            .hover-card .card-header {
                background: linear-gradient(135deg, #1D3557, #457b9d);
                color: white;
                border-bottom: none;
                padding: 1rem;
            }
            
            .hover-card .card-body {
                padding: 1.5rem;
            }
            
            .hover-card .badge {
                font-size: 0.8rem;
                padding: 0.5rem 0.8rem;
                border-radius: 20px;
            }
            
            .hover-card ul {
                margin-bottom: 0;
            }
            
            .hover-card li {
                padding: 0.25rem 0;
                border-bottom: 1px solid #f8f9fa;
            }
            
            .hover-card li:last-child {
                border-bottom: none;
            }
            
            /* Tab Styles */
            .nav-tabs .nav-link {
                border: none;
                border-radius: 10px 10px 0 0;
                margin-right: 5px;
                padding: 12px 20px;
                font-weight: 500;
                color: #6c757d;
                transition: all 0.3s ease;
            }
            
            .nav-tabs .nav-link:hover {
                background-color: #f8f9fa;
                color: #1D3557;
            }
            
            .nav-tabs .nav-link.active {
                background: linear-gradient(135deg, #1D3557, #457b9d);
                color: white;
                border: none;
            }
            
            /* Filter Card Styles */
            .filter-card {
                border-radius: 15px;
                border: 1px solid #e9ecef;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            }
            
            .filter-card .card-header {
                background: linear-gradient(135deg, #457b9d, #1D3557);
                color: white;
                border-radius: 15px 15px 0 0;
                border-bottom: none;
                padding: 1rem 1.5rem;
            }
            
            /* DataTable Styles */
            .dash-table-container {
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# 🔁 REGISTRA I CALLBACK
serie_a_page.register_callbacks(app)
league_template_page.register_callbacks(app)
team_page.register_team_callbacks(app)
scout_analysis_page.register_callbacks(app)  # Register scout analysis callbacks
player_comparison.register_callbacks(app) # Register player comparison callbacks
similar_players.register_callbacks(app) # <-- NUOVA REGISTRAZIONE CALLBACK

# Register Serie A team callbacks for all teams
for team in serie_a_teams.teams:
    serie_a_teams.register_team_callbacks(app, team)

# Layout principale
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id="selected-season", storage_type="session"),
    dbc.Container(id='page-content', className="p-4")
])

# Routing
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('url', 'search')
)
def display_page(pathname, search):
    if pathname == '/':
        return league_page.layout
    elif pathname == '/scout-analysis':
        # Check if there are query parameters for specific position
        if search:
            from urllib.parse import parse_qs
            params = parse_qs(search[1:])
            position = params.get('position', [None])[0]
            if position:
                # Return the full scout analysis page with position filter
                return scout_analysis_page.layout
        # Return the Scout Analysis home page
        return scout_home_page.layout
    elif pathname == '/player-comparison':
        return player_comparison.create_layout()
    elif pathname == '/similar-players': # <-- NUOVA ROTTA
        return similar_players.create_layout()
    elif pathname == '/lineup-builder':
        # Temporaneamente mostriamo una pagina placeholder per Lineup Builder
        return html.Div([
            html.H1("Lineup Builder", style={"textAlign": "center", "color": "#1D3557", "fontFamily": "'Poppins', sans-serif"}),
            html.P("Strumento per creare la tua squadra ideale - In costruzione", 
                   style={"textAlign": "center", "fontSize": "18px", "marginTop": "50px"}),
            dbc.Button("Torna alla Home", href="/", color="primary", className="d-block mx-auto mt-4")
        ], style={"padding": "50px"})
    elif pathname == '/serie_a':
        return serie_a_page.layout
    elif pathname.startswith('/league'):
        from urllib.parse import parse_qs
        if search:
            params = parse_qs(search[1:])
            league_name = params.get('league', [None])[0]
            if league_name:
                return league_template_page.layout
        return html.Div("League not specified")
    elif pathname.startswith('/team'):
        from urllib.parse import parse_qs
        if search:
            params = parse_qs(search[1:])
            
            # Handle new format (?team=X&league=Y)
            team_name = params.get('team', [None])[0]
            league_name = params.get('league', [None])[0]
            
            # Handle legacy Serie A format (?name=team_name)
            if not team_name and params.get('name'):
                team_name = params.get('name', [None])[0]
                # Check if it's Juventus before routing to serie_a_teams
                if team_name and team_name.lower() == 'juventus':
                    return team_page.layout
                # For other legacy format teams, route to Serie A teams directly
                return serie_a_teams.get_team_layout(team_name)
            
            # Handle new format with team and league parameters
            if team_name and league_name:
                if team_name.lower() == 'juventus':
                    return team_page.layout
                elif league_name == 'Serie A':
                    return serie_a_teams.get_team_layout(team_name)
                else:
                    return league_routes.get_league_team_layout(team_name, league_name)
        
        return html.Div("Team or league not specified")
    else:
        return html.Div("404 - Page not found")
 

if __name__ == '__main__':
    app.run_server(debug=True)
