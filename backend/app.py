# Certifique-se de instalar as dependências:
# pip install dash dash-bootstrap-components flask-cors
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import requests
from backend.bookmakers import BOOKMAKERS_LIST
import dash
from dash.exceptions import PreventUpdate
import json

# BOOKMAKERS centralizado do módulo backend.bookmakers
BOOKMAKERS = [
    {"label": b["name"], "value": b["name"]} for b in BOOKMAKERS_LIST
]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
    dcc.Tabs(id="main-tabs", value="tab-main", children=[
        dcc.Tab(label="Dashboard", value="tab-main", children=[
            dbc.Row([
                dbc.Col(html.H1("🤑 Surebets Hunter Pro", className="text-center mb-4"), width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Filtros Ativos", className="h5"),
                        dbc.CardBody([
                            html.Label("Esporte", className="mb-2"),
                            dcc.Dropdown(
                                id='sport-filter',
                                options=[
                                    {'label': '⚽ Futebol', 'value': 'soccer'},
                                    {'label': '🎾 Tênis', 'value': 'tennis'},
                                    {'label': '🏀 Basquete', 'value': 'basketball'}
                                ],
                                value=['soccer'],
                                multi=True,
                                placeholder="Selecione o(s) esporte(s)",
                                tooltip={'placement': 'top', 'always_visible': False, 'text': 'Filtre por esporte'}
                            ),
                            html.Hr(),
                            html.Label("Casas de Apostas", className="mb-2"),
                            dcc.Dropdown(
                                id='bookmaker-filter',
                                options=BOOKMAKERS,
                                value=[],
                                multi=True,
                                placeholder="Selecione as casas",
                                tooltip={'placement': 'top', 'always_visible': False, 'text': 'Filtre por casa de aposta'}
                            ),
                            html.Hr(),
                            html.Label("Lucro Mínimo (%)", className="mb-2"),
                            dcc.Slider(
                                id='profit-slider',
                                min=0,
                                max=20,
                                step=0.5,
                                value=2,
                                marks={i: f'{i}%' for i in range(0, 21, 2)},
                                tooltip={"placement": "bottom", "always_visible": False}
                            ),
                        ])
                    ], className="mb-4")
                ], xs=12, sm=12, md=4, lg=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Oportunidades em Tempo Real", className="h5"),
                        dbc.CardBody([
                            dbc.Input(id="search-input", placeholder="Buscar evento ou mercado...", type="text", className="mb-2"),
                            dbc.Spinner(children=[
                                dash_table.DataTable(
                                    id='live-table',
                                    columns=[
                                        {'name': 'Evento', 'id': 'event', 'deletable': False, 'selectable': True},
                                        {'name': 'Mercado', 'id': 'market', 'deletable': False, 'selectable': True},
                                        {'name': 'Lucro %', 'id': 'profit', 'deletable': False, 'selectable': True, 'type': 'numeric'},
                                        {'name': 'Casas', 'id': 'bookmakers', 'deletable': False, 'selectable': True},
                                        {'name': 'Ações', 'id': 'actions', 'presentation': 'markdown'}
                                    ],
                                    style_table={'overflowX': 'auto'},
                                    style_cell={'textAlign': 'left'},
                                    style_header={
                                        'backgroundColor': 'rgb(30, 30, 30)',
                                        'color': 'white'
                                    },
                                    style_data={
                                        'backgroundColor': 'rgb(50, 50, 50)',
                                        'color': 'white'
                                    },
                                    sort_action="native",
                                    filter_action="native",
                                    row_selectable="single",
                                    page_size=10,
                                    tooltip_header={
                                        'event': 'Nome do evento',
                                        'market': 'Tipo de mercado',
                                        'profit': 'Lucro estimado',
                                        'bookmakers': 'Casas envolvidas',
                                        'actions': 'Clique para detalhes'
                                    }
                                )
                            ], color="primary", fullscreen=False, id="loading-spinner"),
                            dbc.Button("Atualizar Agora", id="manual-refresh", color="info", className="mb-2"),
                            html.Div(id="error-message"),
                        ])
                    ]),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Detalhes da Oportunidade")),
                            dbc.ModalBody(id="modal-body"),
                            dbc.ModalFooter(
                                dbc.Button("Fechar", id="close-modal", className="ms-auto", n_clicks=0)
                            ),
                        ],
                        id="details-modal",
                        is_open=False,
                    ),
                ], xs=12, sm=12, md=8, lg=9)
            ], className="mb-4"),
            dcc.Interval(id='refresh', interval=5000),
            dcc.Store(id='session', storage_type='session')
        ]),
        dcc.Tab(label="Administração", value="tab-admin", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Configurações Gerais"),
                        dbc.CardBody([
                            html.Div(id="admin-settings"),
                            dbc.Button("Salvar Configurações", id="save-settings-btn", color="primary", className="mt-2"),
                            html.Div(id="settings-save-status", className="mt-2")
                        ])
                    ], className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader("Notificações"),
                        dbc.CardBody([
                            dbc.Input(id="test-notification-msg", placeholder="Mensagem de teste", type="text"),
                            dbc.Button("Enviar Teste", id="test-notification-btn", color="info", className="mt-2"),
                            html.Div(id="notification-test-status", className="mt-2")
                        ])
                    ], className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader("Banco de Dados"),
                        dbc.CardBody([
                            html.Div(id="db-overview")
                        ])
                    ]),
                    dbc.Card([
                        dbc.CardHeader("Inserir Nova Aposta"),
                        dbc.CardBody([
                            dbc.Form([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Evento"),
                                        dcc.Dropdown(id="insert-event", placeholder="Nome do evento", options=[], autoComplete="on"),
                                    ], md=4),
                                    dbc.Col([
                                        dbc.Label("Mercado"),
                                        dcc.Input(id="insert-market", type="text", placeholder="Mercado (ex: 1X2)", debounce=True, autoComplete="on"),
                                    ], md=2),
                                    dbc.Col([
                                        dbc.Label("Seleção"),
                                        dcc.Dropdown(id="insert-selection", placeholder="Seleção (ex: Casa)", options=[], autoComplete="on"),
                                    ], md=2),
                                    dbc.Col([
                                        dbc.Label("Odd"),
                                        dcc.Input(id="insert-odd", type="number", placeholder="Odd", debounce=True, min=1.01, step=0.01),
                                    ], md=2),
                                    dbc.Col([
                                        dbc.Label("Bookmaker"),
                                        dcc.Dropdown(id="insert-bookmaker", options=BOOKMAKERS, placeholder="Selecione a casa", autoComplete="on"),
                                    ], md=2),
                                ], className="mb-2"),
                                dbc.Button("Inserir Aposta", id="insert-bet-btn", color="success", className="mt-2"),
                                html.Div(id="insert-bet-status", className="mt-2"),
                            ])
                        ])
                    ], className="mb-4"),
                ], width=12)
            ])
        ])
    ]),
], fluid=True)

@app.callback(
    Output('live-table', 'data'),
    Output('error-message', 'children'),
    Input('refresh', 'n_intervals'),
    Input('sport-filter', 'value'),
    Input('profit-slider', 'value'),
    Input('manual-refresh', 'n_clicks'),
    Input('bookmaker-filter', 'value'),
    Input('search-input', 'value'),
    prevent_initial_call=True
)
def update_table(n, sports, min_profit, n_clicks, bookmakers, search):
    """Busca dados do backend com filtros aplicados"""
    try:
        response = requests.post(
            'http://localhost:5000/api/opportunities',
            json={'sports': sports, 'min_profit': min_profit, 'bookmakers': bookmakers},
            timeout=3
        )
        filtered_data = response.json()
        error_msg = ""
    except Exception as e:
        error_msg = dbc.Alert(f"Erro ao buscar dados: {e}", color="danger", dismissable=True)
        filtered_data = []
    # Filtro de busca local
    if search:
        filtered_data = [
            item for item in filtered_data
            if search.lower() in item['event'].lower() or search.lower() in item['market'].lower()
        ]
    return [{
        'event': f"🏟️ {item['event']}",
        'market': item['market'],
        'profit': f"{item['profit']:.2f}% 🔥" if item['profit'] > 5 else f"{item['profit']:.2f}%",
        'bookmakers': " vs ".join(item['bookmakers']),
        'actions': f"[📈 Detalhes](#)"
    } for item in filtered_data], error_msg

@app.callback(
    Output("details-modal", "is_open"),
    Output("modal-body", "children"),
    Input("live-table", "active_cell"),
    State("live-table", "data"),
    Input("close-modal", "n_clicks"),
    prevent_initial_call=True
)
def show_details(active_cell, table_data, close_clicks):
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].startswith("close-modal"):
        return False, ""
    if active_cell and active_cell['column_id'] == 'actions':
        row = table_data[active_cell['row']]
        # Exemplo de detalhes, pode ser expandido conforme necessário
        details = [
            html.P(f"Evento: {row['event']}"),
            html.P(f"Mercado: {row['market']}"),
            html.P(f"Lucro: {row['profit']}"),
            html.P(f"Casas: {row['bookmakers']}"),
            html.Hr(),
            html.P("Mais detalhes podem ser exibidos aqui...")
        ]
        return True, details
    return False, ""

@app.callback(
    Output("admin-settings", "children"),
    Input("main-tabs", "value"),
    prevent_initial_call=True
)
def load_admin_settings(tab):
    if tab != "tab-admin":
        return ""
    try:
        response = requests.get("http://localhost:5000/api/admin/settings")
        data = response.json()
        return html.Pre(str(data))
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar configurações: {e}", color="danger")

@app.callback(
    Output("settings-save-status", "children"),
    Input("save-settings-btn", "n_clicks"),
    State("admin-settings", "children"),
    prevent_initial_call=True
)
def save_admin_settings(n_clicks, settings_data):
    if not n_clicks:
        return ""
    try:
        # Aqui você pode adaptar para enviar dados editáveis
        response = requests.post("http://localhost:5000/api/admin/settings", json={})
        if response.status_code == 200:
            return dbc.Alert("Configurações salvas com sucesso!", color="success")
        return dbc.Alert("Erro ao salvar configurações.", color="danger")
    except Exception as e:
        return dbc.Alert(f"Erro: {e}", color="danger")

@app.callback(
    Output("notification-test-status", "children"),
    Input("test-notification-btn", "n_clicks"),
    State("test-notification-msg", "value"),
    prevent_initial_call=True
)
def test_notification(n_clicks, msg):
    if not n_clicks or not msg:
        return ""
    try:
        response = requests.post("http://localhost:5000/api/admin/test-notification", json={"message": msg})
        if response.status_code == 200:
            return dbc.Alert("Notificação enviada!", color="success")
        return dbc.Alert("Falha ao enviar notificação.", color="danger")
    except Exception as e:
        return dbc.Alert(f"Erro: {e}", color="danger")

@app.callback(
    Output("db-overview", "children"),
    Input("main-tabs", "value"),
    prevent_initial_call=True
)
def load_db_overview(tab):
    if tab != "tab-admin":
        return ""
    try:
        response = requests.get("http://localhost:5000/api/admin/db-overview")
        data = response.json()
        return html.Pre(str(data))
    except Exception as e:
        return dbc.Alert(f"Erro ao carregar dados do banco: {e}", color="danger")

# Adiciona um formulário para inserção de apostas no painel admin
# (Removido: redefinição duplicada do app.layout)

# Callback para automação de sugestões inteligentes (exemplo: autocomplete de evento)
@app.callback(
    Output("insert-event", "value"),
    Input("insert-market", "value"),
    prevent_initial_call=True
)
def auto_suggest_event(market):
    # Exemplo: sugestão automática baseada no mercado
    if market and market.lower() == "1x2":
        return "Futebol - Campeonato Brasileiro"
    raise PreventUpdate

# Sugestão automática de seleção baseada no mercado
@app.callback(
    Output("insert-selection", "value"),
    Input("insert-market", "value"),
    prevent_initial_call=True
)
def auto_suggest_selection(market):
    if market and market.lower() == "1x2":
        return "Casa"
    raise PreventUpdate

# Sugestão automática de odd baseada na seleção
@app.callback(
    Output("insert-odd", "value"),
    Input("insert-selection", "value"),
    prevent_initial_call=True
)
def auto_suggest_odd(selection):
    if selection and selection.lower() == "casa":
        return 1.80
    raise PreventUpdate

# Sugestão automática de bookmaker baseada na seleção
@app.callback(
    Output("insert-bookmaker", "value"),
    Input("insert-selection", "value"),
    prevent_initial_call=True
)
def auto_suggest_bookmaker(selection):
    if selection and selection.lower() == "casa":
        return BOOKMAKERS[0]["value"] if BOOKMAKERS else None
    raise PreventUpdate

# Sugestão baseada em histórico (autocomplete)
@app.callback(
    Output("insert-event", "options"),
    Output("insert-selection", "options"),
    Output("insert-odd", "value"),
    Input("main-tabs", "value"),
    Input("insert-selection", "value"),
    prevent_initial_call=True
)
def load_suggestions(tab, selection):
    if tab != "tab-admin":
        raise PreventUpdate
    try:
        response = requests.get("http://localhost:5000/api/admin/suggestions")
        data = response.json()
        event_opts = [{"label": e["name"], "value": e["name"]} for e in data.get("events", [])]
        selection_opts = [{"label": s["name"], "value": s["name"]} for s in data.get("selections", [])]
        # Sugere odd média se seleção for informada
        odd_val = None
        if selection:
            for o in data.get("odds", []):
                if o["name"] == selection:
                    odd_val = o["avg_odd"]
        return event_opts, selection_opts, odd_val
    except Exception:
        raise PreventUpdate

# Validação avançada no frontend
@app.callback(
    Output("insert-bet-status", "children"),
    Input("insert-bet-btn", "n_clicks"),
    State("insert-event", "value"),
    State("insert-market", "value"),
    State("insert-selection", "value"),
    State("insert-odd", "value"),
    State("insert-bookmaker", "value"),
    prevent_initial_call=True
)
def validate_bet(n_clicks, event, market, selection, odd, bookmaker):
    if not n_clicks:
        raise PreventUpdate
    if not all([event, market, selection, odd, bookmaker]):
        return dbc.Alert("Preencha todos os campos!", color="warning")
    try:
        odd = float(odd)
        if odd < 1.01:
            return dbc.Alert("Odd deve ser maior que 1.00!", color="danger")
    except Exception:
        return dbc.Alert("Odd inválida!", color="danger")
    return ""

# Callback para inserir aposta, atualizar tabela e limpar formulário
@app.callback(
    Output("insert-bet-status", "children"),
    Output("live-table", "data", allow_duplicate=True),
    Output("insert-event", "value"),
    Output("insert-market", "value"),
    Output("insert-selection", "value"),
    Output("insert-odd", "value"),
    Output("insert-bookmaker", "value"),
    Input("insert-bet-btn", "n_clicks"),
    State("insert-event", "value"),
    State("insert-market", "value"),
    State("insert-selection", "value"),
    State("insert-odd", "value"),
    State("insert-bookmaker", "value"),
    State("live-table", "data"),
    prevent_initial_call=True
)
def insert_bet(n_clicks, event, market, selection, odd, bookmaker, table_data):
    if not n_clicks:
        raise PreventUpdate
    if not all([event, market, selection, odd, bookmaker]):
        return dbc.Alert("Preencha todos os campos!", color="warning"), table_data, event, market, selection, odd, bookmaker
    # Envia para o backend (POST real)
    try:
        response = requests.post(
            "http://localhost:5000/api/admin/insert-bet",
            json={
                "event": event,
                "market": market,
                "selection": selection,
                "odd": odd,
                "bookmaker": bookmaker
            }, timeout=3
        )
        if response.status_code == 200:
            msg = dbc.Alert("Aposta inserida com sucesso!", color="success")
            # Atualiza tabela local
            new_row = {
                'event': event,
                'market': market,
                'profit': f"{odd:.2f}%",
                'bookmakers': bookmaker,
                'actions': "[📈 Detalhes](#)"
            }
            updated_table = table_data or []
            updated_table.insert(0, new_row)
            # Limpa o formulário
            return msg, updated_table, "", "", "", None, None
        else:
            return dbc.Alert("Erro ao inserir aposta no backend.", color="danger"), table_data, event, market, selection, odd, bookmaker
    except Exception as e:
        return dbc.Alert(f"Erro: {e}", color="danger"), table_data, event, market, selection, odd, bookmaker

if __name__ == '__main__':
    app.run_server(debug=False, port=8050)