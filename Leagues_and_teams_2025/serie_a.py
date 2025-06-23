from dash import dcc, html, dash_table,  callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import dash

# --- Squadre per stagione ---
TEAMS_2425 = [
    {"name": "Atalanta", "image": "/assets/Serie_A/2024-2025/Atalanta.png", "url": "/team?name=atalanta"},
    {"name": "Bologna", "image": "/assets/Serie_A/2024-2025/Bologna.png", "url": "/team?name=bologna"},
    {"name": "Cagliari", "image": "/assets/Serie_A/2024-2025/Cagliari.png", "url": "/team?name=cagliari"},
    {"name": "Como", "image": "/assets/Serie_A/2024-2025/Como.png", "url": "/team?name=como"},
    {"name": "Empoli", "image": "/assets/Serie_A/2024-2025/Empoli.png", "url": "/team?name=empoli"},
    {"name": "Fiorentina", "image": "/assets/Serie_A/2024-2025/Fiorentina.png", "url": "/team?name=fiorentina"},
    {"name": "Genoa", "image": "/assets/Serie_A/2024-2025/Genoa.png", "url": "/team?name=genoa"},
    {"name": "Hellas Verona", "image": "/assets/Serie_A/2024-2025/Hellas_Verona.png", "url": "/team?name=hellas verona"},
    {"name": "Inter", "image": "/assets/Serie_A/2024-2025/Inter.png", "url": "/team?name=inter"},
    {"name": "Juventus", "image": "/assets/Serie_A/2024-2025/Juventus.png", "url": "/team?name=juventus"},
    {"name": "Lazio", "image": "/assets/Serie_A/2024-2025/Lazio.png", "url": "/team?name=lazio"},
    {"name": "Lecce", "image": "/assets/Serie_A/2024-2025/Lecce.png", "url": "/team?name=lecce"},
    {"name": "Milan", "image": "/assets/Serie_A/2024-2025/Milan.png", "url": "/team?name=milan"},
    {"name": "Monza", "image": "/assets/Serie_A/2024-2025/Monza.png", "url": "/team?name=monza"},
    {"name": "Napoli", "image": "/assets/Serie_A/2024-2025/Napoli.png", "url": "/team?name=napoli"},
    {"name": "Parma", "image": "/assets/Serie_A/2024-2025/Parma.png", "url": "/team?name=parma"},
    {"name": "Roma", "image": "/assets/Serie_A/2024-2025/Roma.png", "url": "/team?name=roma"},
    {"name": "Torino", "image": "/assets/Serie_A/2024-2025/Torino.png", "url": "/team?name=torino"},
    {"name": "Udinese", "image": "/assets/Serie_A/2024-2025/Udinese.png", "url": "/team?name=udinese"},
    {"name": "Venezia", "image": "/assets/Serie_A/2024-2025/Venezia.png", "url": "/team?name=venezia"}
]

TEAMS_2324 = [
    {"name": "Atalanta", "image": "/assets/Serie_A/2023-2024/Atalanta.png", "url": "/team?name=atalanta"},
    {"name": "Bologna", "image": "/assets/Serie_A/2023-2024/Bologna.png", "url": "/team?name=bologna"},
    {"name": "Cagliari", "image": "/assets/Serie_A/2023-2024/Cagliari.png", "url": "/team?name=cagliari"},
    {"name": "Empoli", "image": "/assets/Serie_A/2023-2024/Empoli.png", "url": "/team?name=empoli"},
    {"name": "Fiorentina", "image": "/assets/Serie_A/2023-2024/Fiorentina.png", "url": "/team?name=fiorentina"},
    {"name": "Frosinone", "image": "/assets/Serie_A/2023-2024/Frosinone.png", "url": "/team?name=frosinone"},
    {"name": "Genoa", "image": "/assets/Serie_A/2023-2024/Genoa.png", "url": "/team?name=genoa"},
    {"name": "Hellas Verona", "image": "/assets/Serie_A/2023-2024/Hellas_Verona.png", "url": "/team?name=hellas verona"},
    {"name": "Inter", "image": "/assets/Serie_A/2023-2024/Inter.png", "url": "/team?name=inter"},
    {"name": "Juventus", "image": "/assets/Serie_A/2023-2024/Juventus.png", "url": "/team?name=juventus"},
    {"name": "Lazio", "image": "/assets/Serie_A/2023-2024/Lazio.png", "url": "/team?name=lazio"},
    {"name": "Lecce", "image": "/assets/Serie_A/2023-2024/Lecce.png", "url": "/team?name=lecce"},
    {"name": "Milan", "image": "/assets/Serie_A/2023-2024/Milan.png", "url": "/team?name=milan"},
    {"name": "Monza", "image": "/assets/Serie_A/2023-2024/Monza.png", "url": "/team?name=monza"},
    {"name": "Napoli", "image": "/assets/Serie_A/2023-2024/Napoli.png", "url": "/team?name=napoli"},
    {"name": "Roma", "image": "/assets/Serie_A/2023-2024/Roma.png", "url": "/team?name=roma"},
    {"name": "Salernitana", "image": "/assets/Serie_A/2023-2024/Salernitana.png", "url": "/team?name=salernitana"},
    {"name": "Sassuolo", "image": "/assets/Serie_A/2023-2024/Sassuolo.png", "url": "/team?name=sassuolo"},
    {"name": "Torino", "image": "/assets/Serie_A/2023-2024/Torino.png", "url": "/team?name=torino"},
    {"name": "Udinese", "image": "/assets/Serie_A/2023-2024/Udinese.png", "url": "/team?name=udinese"}
]

TEAMS_2223 = [
    {"name": "Atalanta", "image": "/assets/Serie_A/2022-2023/Atalanta.png", "url": "/team?name=atalanta"},
    {"name": "Bologna", "image": "/assets/Serie_A/2022-2023/Bologna.png", "url": "/team?name=bologna"},
    {"name": "Cremonese", "image": "/assets/Serie_A/2022-2023/Cremonese.png", "url": "/team?name=cremonese"},
    {"name": "Empoli", "image": "/assets/Serie_A/2022-2023/Empoli.png", "url": "/team?name=empoli"},
    {"name": "Fiorentina", "image": "/assets/Serie_A/2022-2023/Fiorentina.png", "url": "/team?name=fiorentina"},
    {"name": "Hellas Verona", "image": "/assets/Serie_A/2022-2023/Hellas_Verona.png", "url": "/team?name=hellas verona"},
    {"name": "Inter", "image": "/assets/Serie_A/2022-2023/Inter.png", "url": "/team?name=inter"},
    {"name": "Juventus", "image": "/assets/Serie_A/2022-2023/Juventus.png", "url": "/team?name=juventus"},
    {"name": "Lazio", "image": "/assets/Serie_A/2022-2023/Lazio.png", "url": "/team?name=lazio"},
    {"name": "Lecce", "image": "/assets/Serie_A/2022-2023/Lecce.png", "url": "/team?name=lecce"},
    {"name": "Milan", "image": "/assets/Serie_A/2022-2023/Milan.png", "url": "/team?name=milan"},
    {"name": "Monza", "image": "/assets/Serie_A/2022-2023/Monza.png", "url": "/team?name=monza"},
    {"name": "Napoli", "image": "/assets/Serie_A/2022-2023/Napoli.png", "url": "/team?name=napoli"},
    {"name": "Roma", "image": "/assets/Serie_A/2022-2023/Roma.png", "url": "/team?name=roma"},
    {"name": "Salernitana", "image": "/assets/Serie_A/2022-2023/Salernitana.png", "url": "/team?name=salernitana"},
    {"name": "Sampdoria", "image": "/assets/Serie_A/2022-2023/Sampdoria.png", "url": "/team?name=sampdoria"},
    {"name": "Sassuolo", "image": "/assets/Serie_A/2022-2023/Sassuolo.png", "url": "/team?name=sassuolo"},
    {"name": "Spezia", "image": "/assets/Serie_A/2022-2023/Spezia.png", "url": "/team?name=spezia"},
    {"name": "Torino", "image": "/assets/Serie_A/2022-2023/Torino.png", "url": "/team?name=torino"},
    {"name": "Udinese", "image": "/assets/Serie_A/2022-2023/Udinese.png", "url": "/team?name=udinese"}
]

WYSCOUT_PATHS = {
    "2022-23": "/Users/federico/dash_project/data_serie_a_22-23",
    "2023-24": "/Users/federico/dash_project/data_serie_a_23-24",
    "2024-25": "/Users/federico/dash_project/data_serie_a_24-25"
}

# --- Navbar Serie A con dropdown stagione ---
navbar = dbc.Navbar(
    dbc.Container([
        html.H2("Serie A - Teams & Statistics", className="text-white", style={
            "fontWeight": "bold",
            "fontFamily": "'Poppins', sans-serif",
            "marginBottom": "0"
        }),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav([
                dcc.Dropdown(
                    id="season-selector",
                    options=[
                        {"label": "2024-2025", "value": "24-25"},
                        {"label": "2023-2024", "value": "23-24"},
                        {"label": "2022-2023", "value": "22-23"},
                    ],
                    value="24-25",
                    clearable=False,
                    style={"width": "140px"}
                )
            ], className="ms-auto", navbar=True),
            id="navbar-collapse",
            navbar=True,
        ),
    ], fluid=True),
    color="#1D3557",
    dark=True,
    className="mb-0",
)

layout = html.Div([
    navbar,
    dbc.Container([
        html.H3("Select a Team", className="text-center mb-4 mt-4", style={"color": "#1D3557"}),
        dbc.Row(id="team-cards-container", className="justify-content-center"),
        html.Hr(),
        html.Div(id="league-stats-container"),
        html.Hr(),
        

    
        dbc.ButtonGroup([
            dbc.Button("⚔️ Offensive Stats", id="btn-offensive", color="primary", outline=True, n_clicks=0, className="me-2"),
            dbc.Button("🛡️ Defensive Stats", id="btn-defensive", color="secondary", outline=True, n_clicks=0, className="me-2"),
            dbc.Button("🧠 Playing Style", id="btn-style", color="info", outline=True, n_clicks=0)
        ], className="d-flex justify-content-center my-4"),
        html.Div(id="offensive-stats-container", className="mt-4"),
        html.Div(id="defensive-stats-container", className="mt-4"),
        html.Div(id="style-stats-container", className="mt-4"),
        html.Div(id="advanced-stats-content", className="mt-4")
    ], className="pt-3"),
])

def load_league_stats(season):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder_map = {
        "24-25": "data_serie_a_24-25",
        "23-24": "data_serie_a_23-24",
        "22-23": "data_serie_a_22-23",
    }
    folder_name = folder_map.get(season)
    if not folder_name:
        return None
    data_path = os.path.join(current_dir, "..", folder_name)
    clasif = pd.read_csv(os.path.join(data_path, "clasificacion.csv"))
    return clasif

def add_team_logos(df, season):
    team_maps = {
        "24-25": TEAMS_2425,
        "23-24": TEAMS_2324,
        "22-23": TEAMS_2223,
    }
    team_dict = {team["name"]: team["image"] for team in team_maps[season]}
    df["Logo"] = df["Equipo"].map(team_dict)
    return df

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
        'Gls./90': 2.3,
        'xG/90': 2,
        'Ast/90': 1.7,
        'SCA90': 30,
        'T/90': 20,
        'Exitosa%': 50
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
    )
    return fig
    
def normalize_team_names(df):
    df['Equipo'] = df['Equipo'].astype(str).str.strip().str.lower()
    return df

def create_defensive_stats(df, season):
    clasif = load_league_stats(season)
    clasif = normalize_team_names(clasif)
    df = normalize_team_names(df)

    # Rinominare preventivamente GC per evitare duplicati
    if "GC" in df.columns:
        df.rename(columns={"GC": "GC_originale"}, inplace=True)

    # Esegui il merge con le colonne che ci interessano
    df = df.merge(clasif[['Equipo', 'GC', 'xGA']], on='Equipo', how='left')

    if 'GC' not in df.columns or 'xGA' not in df.columns:
        raise ValueError("❌ Merge fallito: colonne 'GC' o 'xGA' mancanti dopo il join.")
    df["Equipo"] = df["Equipo"].str.title()
    df = add_team_logos(df, season)

    # --- Radar ---
    defensive_radar_metrics = {
        'Tkl': 'Tackles',
        'Intercepciones': 'Interceptions',
        'Tkl+Int': 'Tkl+Int',
        'Bloqueos_totales': 'Blocks',
        '% de ganados': 'Duels Won %',
        'Errores': 'Errors (Inverse)'
    }

    max_reference = {
        'Tkl': 700, 'Intercepciones': 310, 'Tkl+Int': 1000,
        'Bloqueos_totales': 405, '% de ganados': 65, 'Errores': 25
    }

    radar_df = df[['Equipo'] + list(defensive_radar_metrics.keys())].copy()
    radar_df['Errores'] = radar_df['Errores'].max() - radar_df['Errores']
    for metrica in defensive_radar_metrics:
        radar_df[metrica] = radar_df[metrica] / max_reference[metrica]

    radar_fig = go.Figure()
    for i, row in radar_df.iterrows():
        valori_norm = row[list(defensive_radar_metrics.keys())].tolist()
        valori_norm.append(valori_norm[0])
        theta = list(defensive_radar_metrics.values()) + [list(defensive_radar_metrics.values())[0]]
        radar_fig.add_trace(go.Scatterpolar(
            r=valori_norm,
            theta=theta,
            fill='toself',
            name=row['Equipo'],
            hovertemplate=f"<b>{row['Equipo']}</b><extra></extra>"
        ))

    radar_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        height=600,
        title='🛡️ Defensive Radar',
        title_x=0.5,
        font=dict(color='#1D3557'),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )

    # --- Scatter xGA vs GC ---
    scatter_fig = go.Figure()
    scatter_fig.add_trace(go.Scatter(
        x=df['xGA'],
        y=df['GC'],
        mode='markers',
        marker=dict(size=0, opacity=0),
        hovertext=df['Equipo'],
        hoverinfo='text',
        customdata=df[['Equipo', 'xGA', 'GC']].values,
        hovertemplate='<b>%{customdata[0]}</b><br>xGA: %{customdata[1]:.2f}<br>GC: %{customdata[2]:.0f}<extra></extra>',
        showlegend=False
    ))

    # ✅ LOGHI: solo se il logo è una stringa valida
    for _, row in df.iterrows():
        logo_path = row['Logo']
        if isinstance(logo_path, str) and logo_path.strip():
            scatter_fig.add_layout_image(dict(
                source=logo_path,
                x=row['xGA'],
                y=row['GC'],
                xref="x",
                yref="y",
                sizex=4,
                sizey=4,
                xanchor="center",
                yanchor="middle",
                layer="above"
            ))
        else:
            print(f"⚠️ Logo mancante per {row['Equipo']}")

    scatter_fig.update_layout(
        height=600,
        title='🧱 xGA vs Goals Conceded',
        title_x=0.5,
        xaxis_title='Expected Goals Against (xGA)',
        yaxis_title='Goals Conceded',
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#1D3557')
    )

    # --- Zone chart ---
    zone_df = df[['Equipo', '3.º_def', '3.º_cent', '3.º_ataq']].copy()
    zone_df = zone_df.rename(columns={
        '3.º_def': 'Defensive Third',
        '3.º_cent': 'Middle Third',
        '3.º_ataq': 'Attacking Third'
    })
    zone_df['Total'] = zone_df[['Defensive Third', 'Middle Third', 'Attacking Third']].sum(axis=1)
    zone_df = zone_df.sort_values(by='Total', ascending=False)

    zone_fig = go.Figure()
    for zona in ['Defensive Third', 'Middle Third', 'Attacking Third']:
        zone_fig.add_trace(go.Bar(
            x=zone_df['Equipo'],
            y=zone_df[zona],
            name=zona
        ))
    zone_fig.update_layout(
        barmode='stack',
        height=600,
        title='🔍 Defensive Actions by Field Zone',
        title_x=0.5,
        xaxis_title='Team',
        yaxis_title='Actions',
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#1D3557'),
        legend_title='Zone'
    )

    return html.Div([
        dcc.Graph(figure=radar_fig, style={"height": "600px"}),
        html.H4("🧱 xGA vs Goals Conceded", className="mt-5", style={"color": "#1D3557"}),
        dcc.Graph(figure=scatter_fig, style={"height": "600px"}),
        html.H4("🔍 Defensive Actions by Field Zone", className="mt-5", style={"color": "#1D3557"}),
        dcc.Graph(figure=zone_fig, style={"height": "650px"})
    ])


# Componenti globali inizializzati
radar_chart_component_global = html.Div()
scatter_component_global = html.Div()
gca_stacked_component_global = html.Div()
defensive_stats_content_global = html.Div()

def get_color(row):
    pos = row["RL"]
    if pos == 1:
        return "#FFD700"  # Oro brillante
    elif pos in [2, 3, 4]:
        return "#00BFFF"  # Azzurro acceso (Champions League)
    elif pos in [5, 6]:
        return "#FFA500"  # Arancione (Europa/Conference)
    elif pos == 7:
        return "#32CD32"  # Verde acceso (extra europeo)
    elif pos in [18, 19, 20]:
        return "#FF4500"  # Rosso acceso (Retrocessione)
    else:
        return "#F0F0F0"  # Grigio per le altre

import plotly.graph_objects as go
import pandas as pd

import plotly.graph_objects as go
import os

def create_playing_styles_scatter(df, season):
    import plotly.graph_objects as go
    from dash import dcc, html
    import pandas as pd

    # Inversione PPDA per asse pressing
    df["Pressing"] = -df["PPDA"]
    df = df.rename(columns={"Intensidad de paso": "Pass Intensity"})

    # Aggiungi loghi
    df = add_team_logos(df, season)

    # Calcolo medie
    avg_pressing = df["Pressing"].mean()
    avg_intensity = df["Pass Intensity"].mean()

    fig = go.Figure()

    # Aggiungi loghi e hover invisibile
    for _, row in df.iterrows():
        team_name = row["Equipo"]
        logo_path = row["Logo"]
        if team_name == "Internazionale":
            logo_path = "/assets/Serie_A/2024-2025/Inter.png"
        if team_name == "Hellas Verona":
            logo_path = "/assets/Serie_A/2024-2025/Hellas_Verona.png"

        if pd.notna(logo_path):
            fig.add_layout_image(dict(
                source=logo_path,
                x=row["Pass Intensity"],
                y=row["Pressing"],
                xref="x",
                yref="y",
                sizex=0.5,
                sizey=0.5,
                xanchor="center",
                yanchor="middle",
                layer="above",
                name=team_name
            ))

            fig.add_trace(go.Scatter(
                x=[row["Pass Intensity"]],
                y=[row["Pressing"]],
                mode='markers',
                marker=dict(size=20, opacity=0),
                name=team_name,
                hovertemplate=(
                    f"<b>{team_name}</b><br>"
                    f"PPDA: {row['PPDA']}<br>"
                    f"Pass Intensity: {row['Pass Intensity']}<extra></extra>"
                ),
                showlegend=False
            ))

    # Linee guida centrali
    fig.add_shape(type="line", x0=avg_intensity, x1=avg_intensity,
                  y0=df["Pressing"].min()-1, y1=df["Pressing"].max()+1,
                  line=dict(dash="dot", width=1, color="gray"))
    fig.add_shape(type="line", x0=df["Pass Intensity"].min()-1, x1=df["Pass Intensity"].max()+1,
                  y0=avg_pressing, y1=avg_pressing,
                  line=dict(dash="dot", width=1, color="gray"))

    # Etichette quadranti: spostate agli angoli
    fig.add_annotation(
        x=df["Pass Intensity"].max() + 0.3,
        y=df["Pressing"].max() + 0.3,
        text="🔥 Pressure & Possession",
        showarrow=False,
        font=dict(size=14, color="#1D3557"))

    fig.add_annotation(
        x=df["Pass Intensity"].min() - 0.3,
        y=df["Pressing"].max() + 0.3,
        text="🧠 Deep Press",
        showarrow=False,
        font=dict(size=14, color="#1D3557"))

    fig.add_annotation(
        x=df["Pass Intensity"].min() - 0.3,
        y=df["Pressing"].min() - 0.3,
        text="🦎 Passive Build-up",
        showarrow=False,
        font=dict(size=14, color="#1D3557"))

    fig.add_annotation(
        x=df["Pass Intensity"].max() + 0.3,
        y=df["Pressing"].min() - 0.3,
        text="🌀 Fast Transitions",
        showarrow=False,
        font=dict(size=14, color="#1D3557"))

    # Layout
    fig.update_layout(
        title='🧠 Playing Styles Map',
        xaxis_title='Pass Intensity',
        yaxis_title='Pressing (−PPDA)',
        autosize=True,
        height=700,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#1D3557'),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="closest",
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True)
    )

    return dcc.Graph(figure=fig, style={"height": "700px"})

def generate_stats_layout(season):
    global radar_chart_component_global, scatter_component_global, gca_stacked_component_global, defensive_stats_content_global

    clasif = load_league_stats(season)
    if clasif is None:
        return html.Div("Dati non disponibili per questa stagione", className="text-danger")

    clasif = add_team_logos(clasif, season)
    clasif["TeamDisplay"] = clasif.apply(
        lambda row: f'![logo]({row["Logo"]})&nbsp;&nbsp;{row["Equipo"]}', axis=1
    )

    table_style = [
        {
            "if": {
                "column_id": "RL",
                "filter_query": f'{{RL}} = {row.RL}'
            },
            "backgroundColor": get_color(row),
            "color": "black"
        } for _, row in clasif.iterrows()
    ]

    classification_table = dash_table.DataTable(
        columns=[
            {"name": "#", "id": "RL"},
            {"name": "Team", "id": "TeamDisplay", "presentation": "markdown"},
            {"name": "Pts", "id": "Pts"},
            {"name": "⚽ GF", "id": "GF"},
            {"name": "🛡️ GC", "id": "GC"},
            {"name": "xG", "id": "xG"},
            {"name": "xGA", "id": "xGA"},
        ],
        data=clasif.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "center",
            "fontFamily": "Poppins",
            "padding": "6px",
            "whiteSpace": "nowrap",
        },
        style_header={"backgroundColor": "#1D3557", "color": "white", "fontWeight": "bold"},
        style_data_conditional=table_style,
        css=[{
            'selector': 'img',
            'rule': 'height: 18px; margin-right: 4px;'
        }]
    )

    folder_map = {
        "24-25": "data_serie_a_24-25",
        "23-24": "data_serie_a_23-24",
        "22-23": "data_serie_a_22-23",
    }
    current_dir = os.path.dirname(os.path.abspath(__file__))
    marcatori_path = os.path.join(current_dir, "..", folder_map[season], f"marcatori_serie_A_{season}.csv")
    marcatori_df = pd.read_csv(marcatori_path, sep=';')

    marcatori_table = dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in marcatori_df.columns],
        data=marcatori_df.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "fontFamily": "Poppins"},
        style_header={"backgroundColor": "#1D3557", "color": "white", "fontWeight": "bold"},
        style_data={"backgroundColor": "white", "color": "black"}
    )

    # Caricamento CSV con metriche
    filename_map = {
        "24-25": "Serie_A_24-25.csv",
        "23-24": "Serie_A_23-24.csv",
        "22-23": "Serie_A_22-23.csv"
    }
    csv_path = os.path.join(current_dir, "..", folder_map[season], filename_map[season])
    serie_a_df = pd.read_csv(csv_path)

    # COMPONENTI GRAFICI
    offensive_metrics = ['Equipo', 'Gls./90', 'xG/90', 'Ast/90', 'SCA90', 'T/90', 'Exitosa%']
    radar_fig = create_offensive_radar(serie_a_df[offensive_metrics])
    radar_chart_component_global = dcc.Graph(figure=radar_fig, style={"height": "600px"})

    df_loghi = add_team_logos(serie_a_df.copy(), season)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_loghi['xG'],
        y=df_loghi['Gls.'],
        mode='markers',
        marker=dict(size=0, opacity=0),
        hovertext=df_loghi['Equipo'],
        hoverinfo='text',
        customdata=df_loghi[['Equipo', 'xG', 'Gls.']].values,
        hovertemplate='<b>%{customdata[0]}</b><br>xG: %{customdata[1]:.2f}<br>Goals: %{customdata[2]:.0f}<extra></extra>',
        showlegend=False
    ))
    for _, row in df_loghi.iterrows():
        fig.add_layout_image(dict(
            source=row['Logo'],
            x=row['xG'],
            y=row['Gls.'],
            xref="x",
            yref="y",
            sizex=5,
            sizey=5,
            xanchor="center",
            yanchor="middle",
            layer="above"
        ))
    fig.update_layout(
        xaxis_title='Expected Goals (xG)',
        yaxis_title='Goals',
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#1D3557'),
        title='🎯 xG vs Goals',
        title_x=0.5,
        showlegend=False,
        height=600,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    scatter_component_global = dcc.Graph(figure=fig, style={"height": "600px"})

    gca_sources = serie_a_df[['Equipo', 'PassLive_GCA', 'PassDead_GCA', 'HASTA_GCA', 'Dis_GCA', 'FR_GCA', 'Def_GCA']].copy()
    gca_sources['Total_GCA'] = gca_sources.iloc[:, 1:].sum(axis=1)
    gca_sources_sorted = gca_sources.sort_values(by='Total_GCA', ascending=False)
    label_map = {
        'PassLive_GCA': 'Live-ball pass leading to goal',
        'PassDead_GCA': 'Set piece pass leading to goal',
        'HASTA_GCA': 'Transition action leading to goal',
        'Dis_GCA': 'Dribble leading to goal',
        'FR_GCA': 'Foul won leading to goal',
        'Def_GCA': 'Defensive action leading to goal'
    }
    gca_fig = go.Figure()
    for col in label_map:
        gca_fig.add_trace(go.Bar(
            x=gca_sources_sorted['Equipo'],
            y=gca_sources_sorted[col],
            name=label_map[col],
            hovertemplate=f"<b>%{{x}}</b><br>{label_map[col]}: %{{y}}<extra></extra>"
        ))
    gca_fig.update_layout(
        barmode='stack',
        title='Goal-Creating Actions Breakdown by Type',
        title_x=0.5,
        xaxis_title='Team',
        yaxis_title='Total GCA (Absolute)',
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#1D3557'),
        legend_title='GCA Type',
        height=600
    )
    gca_stacked_component_global = dcc.Graph(figure=gca_fig, style={"height": "650px", "width": "100%"})

    defensive_stats_content_global = create_defensive_stats(serie_a_df.copy(), season)

    # --- RENDER LAYOUT COMPLETO ---
    return html.Div([
        html.H4("🏆 Standings", className="mt-4 mb-2", style={"color": "#1D3557"}),
        classification_table,
        html.H4("🎯 Scores", className="mt-5 mb-2", style={"color": "#1D3557"}),
        marcatori_table,
        html.Hr(),
        html.H2("📊 Serie A Stats", className="text-center mt-4", style={"color": "#1D3557", "fontWeight": "bold"}),
      
        html.Div(id="offensive-stats-container", className="mt-4"),
        html.Div(id="defensive-stats-container", className="mt-4"),
        html.Div(id="style-stats-container", className="mt-4"),
        html.Div(id="advanced-stats-content", className="mt-4")
    ])

import glob
import os

import os
import pandas as pd

def load_wyscout_playing_style_data(wyscout_path, stagione):
    import pandas as pd
    import os

    data = []

    print(f"🔍 Scanning path: {wyscout_path}")

    for filename in os.listdir(wyscout_path):
        if not filename.endswith("_wyscout.csv"):
            continue

        file_path = os.path.join(wyscout_path, filename)
        print(f"🔄 Processing: {filename}")

        try:
            df = pd.read_csv(file_path, sep=';', encoding='utf-8')
            df.columns = df.columns.str.replace(r"\s+", " ", regex=True).str.strip()

            if stagione == "22-23":
                if not {"Squadra", "Media passaggi per possesso palla"}.issubset(df.columns):
                    print(f"❌ Colonne mancanti nel file {filename}")
                    continue

                squadra = filename.replace("_wyscout.csv", "")
                media_pp = df["Media passaggi per possesso palla"].astype(float).mean()

                data.append({
                    "Equipo": squadra,
                    "PPDA": None,
                    "Intensidad de paso": round(media_pp, 2)
                })
                print(f"✅ {squadra} - Intensidad: {round(media_pp, 2)}")

            else:
                required_cols = {"Equipo", "PPDA", "Intensidad de paso"}
                if not required_cols.issubset(df.columns):
                    print(f"❌ Colonne mancanti nel file {filename}")
                    continue

                df = df.dropna(subset=["PPDA", "Intensidad de paso"])
                if df.empty:
                    print(f"⚠️ Nessuna riga valida in {filename}")
                    continue

                equipo = filename.replace("_wyscout.csv", "").replace("_", " ").strip()
                df = df[df["Equipo"].str.strip().str.lower() == equipo.lower()]

                if df.empty:
                    print(f"⚠️ Nessuna riga per {equipo} in {filename}")
                    continue

                ppda = df["PPDA"].astype(float).mean()
                intensidad = df["Intensidad de paso"].astype(float).mean()


                data.append({
                    "Equipo": equipo,
                    "PPDA": round(ppda, 2),
                    "Intensidad de paso": round(intensidad, 2)
                })
                print(f"✅ {equipo} - PPDA: {round(ppda, 2)}, Intensidad: {round(intensidad, 2)}")

        except Exception as e:
            print(f"❌ Errore nel file {filename}: {e}")

    df_finale = pd.DataFrame(data)
    print(f"\n📊 DataFrame finale:\n{df_finale}")
    return df_finale
# Normalizza nome Inter
    df_finale["Equipo"] = df_finale["Equipo"].replace({"Internazionale": "Inter"})


def register_callbacks(app):
    @app.callback(
        Output("team-cards-container", "children"),
        Input("season-selector", "value")
    )
    def update_team_cards(season):
        teams = {
            "24-25": TEAMS_2425,
            "23-24": TEAMS_2324,
            "22-23": TEAMS_2223,
        }.get(season, [])
        return [
            dbc.Col(
                dbc.Card([
                    dbc.CardImg(src=team["image"], top=True, style={"height": "120px", "width": "120px", "objectFit": "contain", "margin": "auto", "padding": "10px"}),
                    dbc.CardBody([
                        html.H5(team["name"], className="text-center"),
                        dbc.Button("View Team", href=team["url"], color="primary", className="d-block mx-auto"),
                    ]),
                ], className="shadow-lg text-center"),
                width=3, className="mb-4") for team in teams
        ]

    @app.callback(
        Output("league-stats-container", "children"),
        Input("season-selector", "value")
    )
    def update_league_stats(season):
        return generate_stats_layout(season)

    @app.callback(
        Output("offensive-stats-container", "children"),
        Output("defensive-stats-container", "children"),
        Output("style-stats-container", "children"),
        Input("btn-offensive", "n_clicks"),
        Input("btn-defensive", "n_clicks"),
        Input("btn-style", "n_clicks"),
        Input("season-selector", "value")
    )
    def toggle_stat_sections(n_off, n_def, n_style, season):
        triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0] if dash.callback_context.triggered else None
        if triggered == "btn-offensive":
            return [
                html.Div([
                    html.H4("📈 Offensive Radar", className="mt-4", style={"color": "#1D3557"}),
                    radar_chart_component_global,
                    html.H4("🎯 xG vs Goals", className="mt-5", style={"color": "#1D3557"}),
                    scatter_component_global,
                    html.H4("🧩 Goal-Creation Breakdown", className="mt-5", style={"color": "#1D3557"}),
                    gca_stacked_component_global
                ])
            ], [], []
        elif triggered == "btn-defensive":
            return [], [defensive_stats_content_global], []

        elif triggered == "btn-style":
            season = dash.callback_context.inputs["season-selector.value"]
            folder_map = {
                "24-25": "data_serie_a_24-25",
                "23-24": "data_serie_a_23-24",
                "22-23": "data_serie_a_22-23",
            }
            current_dir = os.path.dirname(os.path.abspath(__file__))
            wyscout_path = os.path.join(current_dir, "data_serie_a_" + season)

             # season = "24-25", adatto come 'stagione'
            playing_df = load_wyscout_playing_style_data(wyscout_path, season)
            style_fig = create_playing_styles_scatter(playing_df, season)
            print("🧪 CONTENUTO playing_df:")
            print(playing_df.head())  # <<< AGGIUNGI QUESTA RIGA
            return [], [], [style_fig]

        # <- assicurati che questo sia fuori da tutti gli if
        return [], [], []
