"""
Dashboard principal consolidado do Surebets Hunter Pro.

Este arquivo unifica as implementações de app.py e app_refactored.py,
mantendo as melhores funcionalidades de ambos e removendo redundâncias.
"""

from dash import dcc, html, dash_table, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import requests
import sys
import os
import logging
import json
import dash
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from functools import wraps
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importar módulos unificados
from backend.core.i18n import get_text, get_language_dict, I18n, DEFAULT_LANGUAGE
from backend.apps.adapters import get_all_adapters, get_bookmaker_names
from config import settings

# Configuração de logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar sistema de internacionalização
i18n = I18n()

# Configurar lista de bookmakers centralizada
BOOKMAKER_ADAPTERS = get_all_adapters()
BOOKMAKERS = [
    {"label": name.title(), "value": name} 
    for name in get_bookmaker_names()
]

# Inicializar aplicação Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Surebets Hunter Pro"

def create_navbar() -> dbc.NavbarSimple:
    """Cria a barra de navegação unificada."""
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(i18n.t('dashboard_title'), href="#")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Português", id="lang-pt"),
                    dbc.DropdownMenuItem("English", id="lang-en"),
                ],
                nav=True,
                in_navbar=True,
                label="Language",
                id="language-dropdown"
            ),
        ],
        brand=i18n.t('dashboard_title'),
        brand_href="#",
        color="dark",
        dark=True,
        fluid=True,
    )

def create_filters_card() -> dbc.Card:
    """Cria o card de filtros consolidado."""
    return dbc.Card([
        dbc.CardHeader(html.H5(i18n.t('filters'), className="mb-0")),
        dbc.CardBody([
            # Filtro de esporte
            html.Label(i18n.t('sport'), className="mb-2"),
            dcc.Dropdown(
                id='sport-filter',
                options=[
                    {'label': '⚽ Futebol', 'value': 'soccer'},
                    {'label': '🎾 Tênis', 'value': 'tennis'},
                    {'label': '🏀 Basquete', 'value': 'basketball'}
                ],
                value=['soccer'],
                multi=True,
                placeholder=i18n.t('sport')
            ),
            
            html.Hr(),
            
            # Filtro de bookmakers
            html.Label(i18n.t('bookmakers'), className="mb-2"),
            dcc.Dropdown(
                id='bookmaker-filter',
                options=BOOKMAKERS,
                value=[],
                multi=True,
                placeholder=i18n.t('bookmakers')
            ),
            
            html.Hr(),
            
            # Filtro de lucro mínimo
            html.Label(i18n.t('min_profit'), className="mb-2"),
            dcc.Slider(
                id='profit-slider',
                min=0,
                max=20,
                step=0.5,
                value=2,
                marks={i: f'{i}%' for i in range(0, 21, 2)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
        ])
    ], className="mb-4")

def create_opportunities_card() -> dbc.Card:
    """Cria o card de oportunidades consolidado."""
    return dbc.Card([
        dbc.CardHeader([
            html.H5(i18n.t('real_time_opportunities'), className="mb-0 d-inline"),
            dbc.Button(
                i18n.t('update_now'),
                id="manual-refresh",
                color="info",
                size="sm",
                className="float-end"
            )
        ]),
        dbc.CardBody([
            # Campo de busca
            dbc.Input(
                id="search-input",
                placeholder=i18n.t('search_event_market'),
                type="text",
                className="mb-3"
            ),
            
            # Spinner para loading
            dbc.Spinner([
                dash_table.DataTable(
                    id='opportunities-table',
                    columns=[
                        {'name': i18n.t('event'), 'id': 'event', 'deletable': False},
                        {'name': i18n.t('market'), 'id': 'market', 'deletable': False},
                        {'name': i18n.t('profit'), 'id': 'profit', 'deletable': False, 'type': 'numeric'},
                        {'name': i18n.t('bookmakers'), 'id': 'bookmakers', 'deletable': False},
                        {'name': i18n.t('actions'), 'id': 'actions', 'presentation': 'markdown'}
                    ],
                    data=[],
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'color': 'white',
                        'fontWeight': 'bold'
                    },
                    style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    },
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{profit} > 5'},
                            'backgroundColor': 'rgba(0, 255, 0, 0.1)',
                            'color': 'lightgreen',
                        }
                    ],
                    sort_action="native",
                    filter_action="native",
                    row_selectable="single",
                    page_size=15,
                    export_format="csv"
                )
            ], color="primary"),
            
            # Mensagem de erro
            html.Div(id="error-message", className="mt-2"),
        ])
    ])

def create_stats_card() -> dbc.Card:
    """Cria o card de estatísticas."""
    return dbc.Card([
        dbc.CardHeader(html.H5("Estatísticas em Tempo Real", className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("0", id="total-opportunities", className="text-success"),
                    html.P("Oportunidades Ativas", className="text-muted"),
                ], md=3),
                dbc.Col([
                    html.H4("0%", id="avg-profit", className="text-info"),
                    html.P("Lucro Médio", className="text-muted"),
                ], md=3),
                dbc.Col([
                    html.H4("0", id="best-bookmaker", className="text-warning"),
                    html.P("Melhor Casa", className="text-muted"),
                ], md=3),
                dbc.Col([
                    html.H4("0", id="active-sports", className="text-primary"),
                    html.P("Esportes Ativos", className="text-muted"),
                ], md=3),
            ])
        ])
    ], className="mb-4")

def create_charts_card() -> dbc.Card:
    """Cria o card de gráficos."""
    return dbc.Card([
        dbc.CardHeader(html.H5("Análise Visual", className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="profit-distribution-chart")
                ], md=6),
                dbc.Col([
                    dcc.Graph(id="bookmaker-comparison-chart")
                ], md=6),
            ])
        ])
    ], className="mb-4")

def create_admin_panel() -> html.Div:
    """Cria o painel administrativo consolidado."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                # Card de autenticação
                dbc.Card([
                    dbc.CardHeader(html.H5("Autenticação Admin")),
                    dbc.CardBody([
                        html.Div(id="admin-auth-container", children=[
                            dbc.Input(
                                id='admin-password',
                                type='password',
                                placeholder='Senha admin',
                                className="mb-2"
                            ),
                            dbc.Button(
                                'Entrar como admin',
                                id='admin-login-btn',
                                color='primary',
                                className="me-2"
                            ),
                            dbc.Button(
                                'Logout',
                                id='admin-logout-btn',
                                color='danger',
                                style={'display': 'none'}
                            ),
                            html.Div(id='admin-login-status', className="mt-2")
                        ])
                    ])
                ], className="mb-4"),
                
                # Card de configurações
                dbc.Card([
                    dbc.CardHeader(html.H5(i18n.t('settings'))),
                    dbc.CardBody([
                        html.Div(id="admin-settings"),
                        dbc.Button(
                            i18n.t('save_settings'),
                            id="save-settings-btn",
                            color="primary",
                            className="mt-2"
                        ),
                        html.Div(id="settings-save-status", className="mt-2")
                    ])
                ], className="mb-4"),
                
                # Card de notificações
                dbc.Card([
                    dbc.CardHeader(html.H5(i18n.t('notifications'))),
                    dbc.CardBody([
                        dbc.Input(
                            id="test-notification-msg",
                            placeholder="Mensagem de teste",
                            type="text",
                            className="mb-2"
                        ),
                        dbc.Button(
                            i18n.t('send_test'),
                            id="test-notification-btn",
                            color="info"
                        ),
                        html.Div(id="notification-test-status", className="mt-2")
                    ])
                ], className="mb-4"),
                
                # Card de inserção de apostas
                dbc.Card([
                    dbc.CardHeader(html.H5(i18n.t('insert_bet'))),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label(i18n.t('event')),
                                    dcc.Dropdown(
                                        id="insert-event",
                                        placeholder="Nome do evento",
                                        options=[]
                                    ),
                                ], md=4),
                                dbc.Col([
                                    dbc.Label(i18n.t('market')),
                                    dcc.Input(
                                        id="insert-market",
                                        type="text",
                                        placeholder="Mercado (ex: 1X2)"
                                    ),
                                ], md=2),
                                dbc.Col([
                                    dbc.Label(i18n.t('selection')),
                                    dcc.Dropdown(
                                        id="insert-selection",
                                        placeholder="Seleção",
                                        options=[]
                                    ),
                                ], md=2),
                                dbc.Col([
                                    dbc.Label(i18n.t('odd')),
                                    dcc.Input(
                                        id="insert-odd",
                                        type="number",
                                        placeholder="Odd",
                                        min=1.01,
                                        step=0.01
                                    ),
                                ], md=2),
                                dbc.Col([
                                    dbc.Label(i18n.t('bookmaker')),
                                    dcc.Dropdown(
                                        id="insert-bookmaker",
                                        options=BOOKMAKERS,
                                        placeholder="Selecione a casa"
                                    ),
                                ], md=2),
                            ], className="mb-2"),
                            dbc.Button(
                                i18n.t('insert_bet'),
                                id="insert-bet-btn",
                                color="success",
                                className="mt-2"
                            ),
                            html.Div(id="insert-bet-status", className="mt-2"),
                        ])
                    ])
                ])
            ], width=12)
        ])
    ])

# Layout principal consolidado
app.layout = dbc.Container([
    # Store para dados da sessão
    dcc.Store(id='session', storage_type='session', data={}),
    
    # Barra de navegação
    create_navbar(),
    
    # Tabs principais
    dcc.Tabs(id='main-tabs', value='dashboard', children=[
        # Tab Dashboard
        dcc.Tab(
            label=i18n.t('dashboard_title'),
            value='dashboard',
            children=[
                html.Div([
                    dbc.Row([
                        dbc.Col(create_filters_card(), md=3),
                        dbc.Col(create_opportunities_card(), md=9),
                    ], className="mb-4"),
                    
                    create_stats_card(),
                    create_charts_card(),
                    
                    # Intervalo para atualização automática
                    dcc.Interval(
                        id='refresh-interval',
                        interval=5000,  # 5 segundos
                        n_intervals=0
                    ),
                ])
            ]
        ),
        
        # Tab Jogos
        dcc.Tab(
            label=i18n.t('games'),
            value='games',
            children=[
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(html.H5(i18n.t('live_games'))),
                                dbc.CardBody([
                                    dash_table.DataTable(
                                        id='live-games-table',
                                        columns=[
                                            {'name': i18n.t('event'), 'id': 'name'},
                                            {'name': i18n.t('status'), 'id': 'status'},
                                            {'name': i18n.t('start_time'), 'id': 'start_time'},
                                            {'name': i18n.t('bookmaker'), 'id': 'bookmaker'}
                                        ],
                                        data=[],
                                        style_table={'overflowX': 'auto'},
                                        style_cell={'textAlign': 'left'},
                                        style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},
                                        style_data={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'},
                                        page_size=10
                                    )
                                ])
                            ], className="mb-4")
                        ], width=12),
                        
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(html.H5(i18n.t('upcoming_games'))),
                                dbc.CardBody([
                                    dash_table.DataTable(
                                        id='upcoming-games-table',
                                        columns=[
                                            {'name': i18n.t('event'), 'id': 'name'},
                                            {'name': i18n.t('status'), 'id': 'status'},
                                            {'name': i18n.t('start_time'), 'id': 'start_time'},
                                            {'name': i18n.t('bookmaker'), 'id': 'bookmaker'}
                                        ],
                                        data=[],
                                        style_table={'overflowX': 'auto'},
                                        style_cell={'textAlign': 'left'},
                                        style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},
                                        style_data={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'},
                                        page_size=10
                                    )
                                ])
                            ])
                        ], width=12)
                    ]),
                    
                    # Intervalo para jogos
                    dcc.Interval(
                        id='refresh-games',
                        interval=10000,  # 10 segundos
                        n_intervals=0
                    ),
                ])
            ]
        ),
        
        # Tab Admin
        dcc.Tab(
            label=i18n.t('admin'),
            value='admin',
            children=[create_admin_panel()]
        ),
    ]),
    
    # Modal para detalhes
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(i18n.t('details'))),
        dbc.ModalBody(id="modal-body"),
        dbc.ModalFooter(
            dbc.Button(
                i18n.t('close'),
                id="close-modal",
                className="ms-auto",
                n_clicks=0
            )
        ),
    ], id="details-modal", is_open=False),
    
], fluid=True)

# Callbacks consolidados

@app.callback(
    [Output('opportunities-table', 'data'),
     Output('error-message', 'children'),
     Output('total-opportunities', 'children'),
     Output('avg-profit', 'children')],
    [Input('refresh-interval', 'n_intervals'),
     Input('manual-refresh', 'n_clicks'),
     Input('sport-filter', 'value'),
     Input('profit-slider', 'value'),
     Input('bookmaker-filter', 'value'),
     Input('search-input', 'value')],
    prevent_initial_call=False
)
def update_opportunities_table(n_intervals, n_clicks, sports, min_profit, bookmakers, search):
    """Atualiza a tabela de oportunidades com dados unificados."""
    try:
        # Coletar dados de todos os adaptadores
        all_opportunities = []
        
        for adapter_name, adapter in BOOKMAKER_ADAPTERS.items():
            if not bookmakers or adapter_name in bookmakers:
                for sport in (sports or ['soccer']):
                    live_odds = adapter.get_live_odds(sport, limit=20)
                    
                    for event in live_odds:
                        for market in event.get('markets', []):
                            # Calcular surebet mock (simplificado)
                            selections = market.get('selections', [])
                            if len(selections) >= 2:
                                profit = calculate_mock_profit(selections)
                                
                                if profit >= min_profit:
                                    opportunity = {
                                        'event': f"🏟️ {event['name']}",
                                        'market': market['name'],
                                        'profit': f"{profit:.2f}%",
                                        'bookmakers': adapter_name.title(),
                                        'actions': f"[📊 Detalhes](#{event['id']})"
                                    }
                                    
                                    # Filtro de busca
                                    if not search or search.lower() in opportunity['event'].lower() or search.lower() in opportunity['market'].lower():
                                        all_opportunities.append(opportunity)
        
        # Estatísticas
        total_ops = len(all_opportunities)
        avg_profit = sum(float(op['profit'].replace('%', '')) for op in all_opportunities) / max(total_ops, 1)
        
        return all_opportunities, "", str(total_ops), f"{avg_profit:.1f}%"
        
    except Exception as e:
        logger.error(f"Erro ao atualizar oportunidades: {e}")
        return [], dbc.Alert(f"Erro: {str(e)}", color="danger"), "0", "0%"

def calculate_mock_profit(selections: List[Dict[str, Any]]) -> float:
    """Calcula lucro mock para demonstração."""
    if len(selections) < 2:
        return 0
    
    # Fórmula simplificada de surebet
    inverse_sum = sum(1/selection['odds'] for selection in selections[:2])
    if inverse_sum < 1:
        return (1 - inverse_sum) * 100
    return 0

@app.callback(
    [Output('live-games-table', 'data'),
     Output('upcoming-games-table', 'data')],
    [Input('refresh-games', 'n_intervals')],
    prevent_initial_call=False
)
def update_games_tables(n_intervals):
    """Atualiza as tabelas de jogos."""
    try:
        live_games = []
        upcoming_games = []
        
        for adapter_name, adapter in BOOKMAKER_ADAPTERS.items():
            # Jogos ao vivo
            live_data = adapter.get_live_odds('soccer', limit=5)
            for game in live_data:
                live_games.append({
                    'name': game['name'],
                    'status': 'AO VIVO',
                    'start_time': datetime.fromisoformat(game['start_time'].replace('Z', '+00:00')).strftime('%H:%M'),
                    'bookmaker': adapter_name.title()
                })
            
            # Jogos futuros
            upcoming_data = adapter.get_upcoming_odds('soccer', limit=5)
            for game in upcoming_data:
                upcoming_games.append({
                    'name': game['name'],
                    'status': 'PROGRAMADO',
                    'start_time': datetime.fromisoformat(game['start_time'].replace('Z', '+00:00')).strftime('%d/%m %H:%M'),
                    'bookmaker': adapter_name.title()
                })
        
        return live_games[:10], upcoming_games[:10]
    
    except Exception as e:
        logger.error(f"Erro ao atualizar jogos: {e}")
        return [], []

@app.callback(
    [Output('profit-distribution-chart', 'figure'),
     Output('bookmaker-comparison-chart', 'figure')],
    [Input('opportunities-table', 'data')],
    prevent_initial_call=False
)
def update_charts(opportunities_data):
    """Atualiza os gráficos de análise."""
    try:
        if not opportunities_data:
            # Gráficos vazios
            empty_fig = go.Figure()
            empty_fig.update_layout(title="Aguardando dados...", template="plotly_dark")
            return empty_fig, empty_fig
        
        # Gráfico de distribuição de lucros
        profits = [float(op['profit'].replace('%', '')) for op in opportunities_data]
        profit_fig = go.Figure(data=[go.Histogram(x=profits, nbinsx=10)])
        profit_fig.update_layout(
            title="Distribuição de Lucros",
            xaxis_title="Lucro (%)",
            yaxis_title="Frequência",
            template="plotly_dark"
        )
        
        # Gráfico de comparação de bookmakers
        bookmaker_counts = {}
        for op in opportunities_data:
            bm = op['bookmakers']
            bookmaker_counts[bm] = bookmaker_counts.get(bm, 0) + 1
        
        bm_fig = go.Figure(data=[
            go.Bar(x=list(bookmaker_counts.keys()), y=list(bookmaker_counts.values()))
        ])
        bm_fig.update_layout(
            title="Oportunidades por Bookmaker",
            xaxis_title="Bookmaker",
            yaxis_title="Quantidade",
            template="plotly_dark"
        )
        
        return profit_fig, bm_fig
        
    except Exception as e:
        logger.error(f"Erro ao atualizar gráficos: {e}")
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Erro ao carregar gráficos", template="plotly_dark")
        return empty_fig, empty_fig

# Callback de autenticação admin (simplificado)
@app.callback(
    [Output('session', 'data'),
     Output('admin-login-status', 'children')],
    [Input('admin-login-btn', 'n_clicks')],
    [State('admin-password', 'value'),
     State('session', 'data')],
    prevent_initial_call=True
)
def admin_login(n_clicks, password, session_data):
    """Callback de login administrativo."""
    if n_clicks and password == 'admin123':  # Senha simplificada para demo
        session_data = session_data or {}
        session_data['admin_logged_in'] = True
        return session_data, dbc.Alert("Login realizado com sucesso!", color="success")
    
    return session_data or {}, dbc.Alert("Senha incorreta.", color="danger") if n_clicks else ""

if __name__ == '__main__':
    logger.info("Iniciando dashboard consolidado do Surebets Hunter Pro")
    app.run_server(
        debug=settings.DEBUG,
        host='0.0.0.0',
        port=settings.PORT
    )
