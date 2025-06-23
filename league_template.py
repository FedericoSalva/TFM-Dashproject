# league_template.py aggiornato con toggle Offensive/Defensive Stats ma SENZA classifica e SENZA scatter con loghi

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import os
from urllib.parse import parse_qs
import dash

LEAGUE_NAMES = {
    "EPL": "Premier League",
    "Bundesliga": "Bundesliga",
    "Bundesliga_2": "Bundesliga 2",
    "Championship": "Championship",
    "Eredivisie": "Eredivisie",
    "Jupiler_Pro_League": "Jupiler Pro League",
    "La_Liga": "La Liga",
    "Liga_Argentina": "Liga Argentina",
    "Ligue_1": "Ligue 1",
    "Ligue_2": "Ligue 2",
    "MLS": "Major League Soccer",
    "Primeira_Liga": "Primeira Liga",
    "Serie_B": "Serie B",
    "Süper_Lig": "Süper Lig"
}

LEAGUE_SEASONS = {
    "MLS": ["24", "23"],
    "Liga_Argentina": ["24", "23"],
    "Brazilian_Série_A": ["24", "23"]
}
DEFAULT_SEASONS = ["24-25", "23-24", "22-23"]

layout = html.Div(id="dynamic-league-layout")

def register_callbacks(app):
    @app.callback(
        Output("dynamic-league-layout", "children"),
        Input("url", "search")
    )
    def render_league_layout(search):
        if not search:
            return html.Div("Nessuna lega selezionata", className="text-danger")

        query = parse_qs(search.lstrip("?"))
        league_code = query.get("league", [None])[0]
        if not league_code:
            return html.Div("Lega non trovata", className="text-danger")

        league_name = LEAGUE_NAMES.get(league_code, league_code)
        seasons = LEAGUE_SEASONS.get(league_code, DEFAULT_SEASONS)
        dropdown_options = [{"label": f"20{season}" if len(season)==2 else season, "value": season} for season in seasons]

        return html.Div([
            html.Div(
                dbc.Container([
                    dbc.Row([
                        dbc.Col(html.H2(
                            f"{league_name} - Teams & Statistics",
                            className="text-white",
                            style={"padding": "12px", "fontWeight": "bold"}
                        ), width=9),
                        dbc.Col(dcc.Dropdown(
                            id="season-selector-generic",
                            options=dropdown_options,
                            value=seasons[0],
                            clearable=False,
                            style={"marginTop": "10px"}
                        ), width=3)
                    ], align="center"),
                ], fluid=True, style={"backgroundColor": "#1D3557"}),
            ),
            dbc.Container([
                html.H3("Select a Team", className="text-center my-4", style={"color": "#1D3557"}),
                html.Div(id="team-cards-container-generic", className="my-4"),
                html.Hr(),
                html.Div([
                    html.Div([
                        dbc.ButtonGroup([
                            dbc.Button("⚔️ Offensive Stats", id="offensive-btn", color="primary", outline=True, active=True),
                            dbc.Button("🛡️ Defensive Stats", id="defensive-btn", color="secondary", outline=True)
                        ], className="mb-3")
                    ], className="text-center"),
                    html.Div(id="league-stats-container-generic")
                ])
            ], fluid=True)
        ])

    @app.callback(
        Output("team-cards-container-generic", "children"),
        Input("url", "search"),
        Input("season-selector-generic", "value")
    )
    def update_team_cards(search, season):
        if not search or not season:
            return []
        league_code = parse_qs(search.lstrip("?")).get("league", [None])[0]
        folder_path = os.path.join("assets", league_code)

        if not os.path.exists(folder_path):
            return []

        images = [f for f in os.listdir(folder_path) if f.endswith(".png")]
        return dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardImg(src=f"/assets/{league_code}/{img}", top=True, style={"height": "120px", "objectFit": "contain", "margin": "auto", "padding": "10px"}),
                    dbc.CardBody([
                        html.H5(img.replace(".png", "").replace("_", " "), className="text-center"),
                        dbc.Button(
                            "View Team", 
                            href=f"/team?team={img.replace('.png','')}&league={league_code}", 
                            color="primary", 
                            className="d-block mx-auto"
                        ),
                    ]),
                ], className="shadow-lg text-center mb-4"), width=3
            ) for img in sorted(images)
        ], className="g-4 justify-content-center")

    @app.callback(
        Output("league-stats-container-generic", "children"),
        Input("offensive-btn", "n_clicks"),
        Input("defensive-btn", "n_clicks"),
        State("url", "search"),
        State("season-selector-generic", "value")
    )
    def render_stats(off_n, def_n, search, season):
        if not search or not season:
            return ""
        ctx = dash.callback_context
        league_code = parse_qs(search.lstrip("?")).get("league", [None])[0]
        folder = f"data_{league_code}_{season}"
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, league_code, folder)

        try:
            stats = pd.read_csv(os.path.join(path, f"{league_code}_{season}.csv"))
        except:
            return html.Div("Dati non disponibili", className="text-danger")

        triggered = ctx.triggered_id
        if triggered == "defensive-btn":
            return html.Div([
                dcc.Graph(figure=create_defensive_radar(stats), style={"height": "600px"}),
                dcc.Graph(figure=create_defensive_zone_chart(stats), style={"height": "650px"})
            ])
        else:
            return html.Div([
                dcc.Graph(figure=create_offensive_radar(stats), style={"height": "600px"}),
                dcc.Graph(figure=create_goal_creation_chart(stats), style={"height": "650px"})
            ])

import plotly.graph_objects as go

def create_offensive_radar(df):
    # Colonne originali (in spagnolo) → Etichette in inglese
    radar_map = {
        'Gls./90': 'Goals/90',
        'xG/90': 'xG/90',
        'Ast/90': 'Assists/90',
        'SCA90': 'Shot Creating Actions/90',
        'T/90': 'Shots/90',
        'Exitosa%': 'Successful Dribbles %'
    }

    radar_metrics = list(radar_map.keys())
    radar_labels = list(radar_map.values())

    # Valori massimi realistici per normalizzazione
    max_reference = {
        'Gls./90': 3.0,
        'xG/90': 2.5,
        'Ast/90': 2,
        'SCA90': 40,
        'T/90': 20,
        'Exitosa%': 55
    }

    radar_df = df[['Equipo'] + radar_metrics].copy()

    for metrica in radar_metrics:
        radar_df[metrica] = radar_df[metrica] / max_reference[metrica]

    fig = go.Figure()
    for _, row in radar_df.iterrows():
        values = [row[m] for m in radar_metrics]
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=radar_labels + [radar_labels[0]],
            fill='toself',
            name=row['Equipo'],
            hovertemplate=(
                f"<b>{row['Equipo']}</b><br>" +
                f"Goals/90: {row['Gls./90'] * max_reference['Gls./90']:.2f}<br>" +
                f"xG/90: {row['xG/90'] * max_reference['xG/90']:.2f}<br>" +
                f"Assists/90: {row['Ast/90'] * max_reference['Ast/90']:.2f}<br>" +
                f"SCA90: {row['SCA90'] * max_reference['SCA90']:.2f}<br>" +
                f"Shots/90: {row['T/90'] * max_reference['T/90']:.2f}<br>" +
                f"Successful Dribbles %: {row['Exitosa%'] * max_reference['Exitosa%']:.2f}%<extra></extra>"
            )
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title="⚽ Offensive Radar"
    )
    return fig


def create_goal_creation_chart(df):
    cols = ['PassLive_GCA', 'PassDead_GCA', 'HASTA_GCA', 'Dis_GCA', 'FR_GCA', 'Def_GCA']
    label_map = {
        'PassLive_GCA': 'Live Pass', 'PassDead_GCA': 'Dead Pass',
        'HASTA_GCA': 'Transition', 'Dis_GCA': 'Dribble', 'FR_GCA': 'Foul', 'Def_GCA': 'Defensive'
    }
    df['Total'] = df[cols].sum(axis=1)
    df = df.sort_values(by='Total', ascending=False)
    fig = go.Figure()
    for col in cols:
        fig.add_trace(go.Bar(x=df['Equipo'], y=df[col], name=label_map[col]))
    fig.update_layout(barmode='stack', xaxis_title='Team', yaxis_title='GCA')
    return fig

def create_defensive_radar(df):
    radar_metrics = ['Tkl', 'Intercepciones', 'Tkl+Int', 'Bloqueos_totales', '% de ganados', 'Errores']
    df = df.copy()
    
    # Normalizza per 90 minuti dove ha senso (eccetto % e errori)
    for metrica in ['Tkl', 'Intercepciones', 'Tkl+Int', 'Bloqueos_totales']:
        df[metrica + '/90'] = df[metrica] / df['90 s']

    df['Errores_inverso'] = df['Errores'].max() - df['Errores']

    max_reference = {
        'Tkl/90': 25,
        'Intercepciones/90': 11,
        'Tkl+Int/90': 35,
        'Bloqueos_totales/90': 15,
        '% de ganados': 60,
        'Errores_inverso': df['Errores'].max()  # così l'inverso si scala correttamente
    }

    radar_df = df[['Equipo', 'Tkl/90', 'Intercepciones/90', 'Tkl+Int/90', 'Bloqueos_totales/90', '% de ganados', 'Errores_inverso']].copy()

    # Percentili su scala 100
    for metrica in radar_df.columns[1:]:
        radar_df[metrica] = radar_df[metrica] / max_reference[metrica] * 100

    fig = go.Figure()
    for _, row in radar_df.iterrows():
        values = [
            row['Tkl/90'],
            row['Intercepciones/90'],
            row['Tkl+Int/90'],
            row['Bloqueos_totales/90'],
            row['% de ganados'],
            row['Errores_inverso'],
            row['Tkl/90']
        ]
        original = df[df['Equipo'] == row['Equipo']].iloc[0]
        hovertext = (
            f"<b>{row['Equipo']}</b><br>" +
            f"Tkl/90: {original['Tkl']/original['90 s']:.2f}<br>" +
            f"Intercepciones/90: {original['Intercepciones']/original['90 s']:.2f}<br>" +
            f"Tkl+Int/90: {original['Tkl+Int']/original['90 s']:.2f}<br>" +
            f"Bloqueos totales/90: {original['Bloqueos_totales']/original['90 s']:.2f}<br>" +
            f"Duelli vinti %: {original['% de ganados']:.2f}<br>" +
            f"Errori (inversi): {original['Errores_inverso']:.2f}"
        )

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=['Tkl', 'Intercepciones', 'Tkl+Int', 'Bloqueos_totales', 'Duelli vinti %', 'Errori (inversi)', 'Tkl'],
            fill='toself',
            name=row['Equipo'],
            hoverinfo='text',
            text=hovertext
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True
    )
    return fig

def create_defensive_zone_chart(df):
    zone_df = df[['Equipo', '3.º_def', '3.º_cent', '3.º_ataq']].copy()
    zone_df = zone_df.rename(columns={
        '3.º_def': 'Defensive Third',
        '3.º_cent': 'Middle Third',
        '3.º_ataq': 'Attacking Third'
    })
    zone_df['Total'] = zone_df[['Defensive Third', 'Middle Third', 'Attacking Third']].sum(axis=1)
    zone_df = zone_df.sort_values(by='Total', ascending=False)
    fig = go.Figure()
    for zone in ['Defensive Third', 'Middle Third', 'Attacking Third']:
        fig.add_trace(go.Bar(x=zone_df['Equipo'], y=zone_df[zone], name=zone))
    fig.update_layout(barmode='stack', xaxis_title='Team', yaxis_title='Defensive Actions')
    return fig
