"""
Модуль с макетом (layout) дашборда.
"""
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

from .i18n import t, pip_colors

# Стиль для левой панели (сайдбар); фон/цвета берёт из Pip-Boy CSS (body.pipboy-page)
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "25rem",
    "padding": "2rem 1rem",
    "overflow-y": "auto",
}


def _line_color_options():
    return [
        {'label': f"🔴 {t('zcyc_color_red')}", 'value': '#dc3545'},
        {'label': f"🔵 {t('zcyc_color_blue')}", 'value': '#007bff'},
        {'label': f"🟢 {t('zcyc_color_green')}", 'value': '#28a745'},
        {'label': f"🟣 {t('zcyc_color_purple')}", 'value': '#6f42c1'},
        {'label': f"🟠 {t('zcyc_color_orange')}", 'value': '#fd7e14'},
        {'label': f"⚫ {t('zcyc_color_black')}", 'value': '#343a40'},
    ]


def _point_color_options():
    return [
        {'label': f"🔵 {t('zcyc_color_blue')}", 'value': '#007bff'},
        {'label': f"🟢 {t('zcyc_color_green')}", 'value': '#28a745'},
        {'label': f"🟡 {t('zcyc_color_yellow')}", 'value': '#ffc107'},
        {'label': f"🔴 {t('zcyc_color_red')}", 'value': '#dc3545'},
        {'label': f"🟣 {t('zcyc_color_purple')}", 'value': '#6f42c1'},
        {'label': f"🟠 {t('zcyc_color_orange')}", 'value': '#fd7e14'},
        {'label': f"🩵 {t('zcyc_color_cyan')}", 'value': '#17a2b8'},
        {'label': f"💗 {t('zcyc_color_pink')}", 'value': '#e83e8c'},
        {'label': f"⚫ {t('zcyc_color_darkgray')}", 'value': '#343a40'},
        {'label': f"💚 {t('zcyc_color_lightgreen')}", 'value': '#20c997'},
        {'label': f"🔷 {t('zcyc_color_indigo')}", 'value': '#6610f2'},
        {'label': f"💜 {t('zcyc_color_magenta')}", 'value': '#d63384'},
        {'label': f"⬜ {t('zcyc_color_gray')}", 'value': '#6c757d'},
        {'label': f"💙 {t('zcyc_color_brightblue')}", 'value': '#0d6efd'},
        {'label': f"🧡 {t('zcyc_color_coral')}", 'value': '#ff7f50'},
        {'label': f"🤎 {t('zcyc_color_brown')}", 'value': '#8B4513'},
    ]


def _bg_color_options():
    """Базовые цвета фона графика: тёмные приглушённые оттенки (чтобы зелёный/
    янтарный текст поверх оставался читаемым) плюс белый — для белого шрифт/
    сетка графика переключаются на тёмные (см. _text_color_for_bg в
    callbacks_curve.py). 'auto' возвращает фон к цвету текущей языковой темы."""
    return [
        {'label': t('zcyc_bg_default'), 'value': 'auto'},
        {'label': f"🔴 {t('zcyc_color_red')}", 'value': '#2a0e0e'},
        {'label': f"🔵 {t('zcyc_color_blue')}", 'value': '#0e1a2a'},
        {'label': f"🟢 {t('zcyc_color_green')}", 'value': '#0e2a16'},
        {'label': f"🟣 {t('zcyc_color_purple')}", 'value': '#1e0e2a'},
        {'label': f"🟠 {t('zcyc_color_orange')}", 'value': '#2a1c0e'},
        {'label': f"⚫ {t('zcyc_color_black')}", 'value': '#050505'},
        {'label': f"🟡 {t('zcyc_color_yellow')}", 'value': '#2a260e'},
        {'label': f"⬜ {t('zcyc_color_gray')}", 'value': '#16181a'},
        {'label': f"⚪ {t('zcyc_color_white')}", 'value': '#ffffff'},
    ]


def _line_style_options():
    return [
        {'label': t('zcyc_line_style_solid'), 'value': 'solid'},
        {'label': t('zcyc_line_style_dash'), 'value': 'dash'},
        {'label': t('zcyc_line_style_dot'), 'value': 'dot'},
        {'label': t('zcyc_line_style_dashdot'), 'value': 'dashdot'},
    ]


def create_layout():
    """Возвращает корневой layout приложения (перестраивается на каждый запрос, см. serve_layout в __init__.py)."""
    colors = pip_colors()
    return dbc.Container([
        # Заголовок
        dbc.Row([
            dbc.Col([
                html.H1(t('zcyc_page_title'), className="text-center mb-4")
            ], width=12)
        ]),

        dbc.Row([
            # Левая панель (управление ZCYC)
            dbc.Col([
                html.Div([
                    # Информация о данных
                    dbc.Card([
                        dbc.CardHeader(t('zcyc_info_card_header'), className="bg-primary text-white"),
                        dbc.CardBody([
                            html.H5(id='date-display', className="card-title"),
                            html.H6(id='time-display', className="card-subtitle mb-2"),
                            html.P(t('zcyc_info_card_text'), className="card-text text-muted"),
                            dbc.Button(t('zcyc_refresh_btn'),
                                       id="refresh-btn",
                                       color="success",
                                       className="mt-2 w-100")
                        ])
                    ], className="mb-4"),

                    # Настройки графика
                    dbc.Card([
                        dbc.CardHeader(t('zcyc_settings_card_header'), className="bg-info text-white"),
                        dbc.CardBody([
                            html.H6(t('zcyc_term_range_label'), className="mt-2"),
                            dcc.RangeSlider(
                                id='x-range-slider',
                                min=0.01, max=50, step=0.5,
                                marks={i: str(i) for i in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]},
                                value=[0.01, 30],
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                            html.H6(t('zcyc_yield_range_label'), className="mt-4"),
                            dcc.RangeSlider(
                                id='y-range-slider',
                                min=-10, max=50, step=0.5,
                                marks={i: str(i) for i in [-10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]},
                                value=[-2, 20],
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(t('zcyc_line_color_label'), className="mt-3"),
                                    dcc.Dropdown(
                                        id='line-color',
                                        options=_line_color_options(),
                                        value='#dc3545', clearable=False
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label(t('zcyc_line_width_label'), className="mt-3"),
                                    dcc.Slider(
                                        id='line-width', min=1, max=6, step=0.5,
                                        marks={i: str(i) for i in range(1, 7)},
                                        value=3, tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6)
                            ]),
                            html.Label(t('zcyc_line_style_label'), className="mt-3"),
                            dcc.Dropdown(
                                id='line-style',
                                options=_line_style_options(),
                                value='solid', clearable=False
                            ),
                            html.Label(t('zcyc_bg_color_label'), className="mt-3"),
                            dcc.Dropdown(
                                id='chart-bg-color',
                                options=_bg_color_options(),
                                value='auto', clearable=False
                            ),
                            # Чекбоксы для управления отображением
                            dbc.Row([
                                dbc.Col([
                                    dbc.Checklist(
                                        id='show-point-labels',
                                        options=[{"label": t('zcyc_show_point_labels'), "value": True}],
                                        value=[True],
                                        switch=True,
                                        className="mt-3"
                                    )
                                ], width=12)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Checklist(
                                        id='show-legend',
                                        options=[{"label": t('zcyc_show_legend'), "value": True}],
                                        value=[True],
                                        switch=True,
                                        className="mt-2"
                                    )
                                ], width=12)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Checklist(
                                        id='show-title',
                                        options=[{"label": t('zcyc_show_title'), "value": True}],
                                        value=[True],
                                        switch=True,
                                        className="mt-2"
                                    )
                                ], width=12)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Checklist(
                                        id='show-grid',
                                        options=[{"label": t('zcyc_show_grid'), "value": True}],
                                        value=[True],
                                        switch=True,
                                        className="mt-2"
                                    )
                                ], width=12)
                            ]),
                            # Переключатель режима подписей
                            html.Label(t('zcyc_label_mode_label'), className="mt-3"),
                            dcc.RadioItems(
                                id='label-mode',
                                options=[
                                    {'label': t('zcyc_label_mode_inline'), 'value': 'inline'},
                                    {'label': t('zcyc_label_mode_callout'), 'value': 'callout'}
                                ],
                                value='inline',
                                labelStyle={'display': 'block', 'margin': '5px 0'}
                            ),
                            dbc.Button(t('zcyc_auto_y_btn'),
                                       id="auto-y-btn",
                                       color="warning",
                                       className="mt-3 w-100")
                        ])
                    ], className="mb-4"),

                    # Форма для добавления пользовательских точек вручную
                    dbc.Card([
                        dbc.CardHeader(t('zcyc_add_points_card_header'), className="bg-success text-white"),
                        dbc.CardBody([
                            html.H6(t('zcyc_add_point_subheading'), className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(t('zcyc_point_name_label'), className="mt-2"),
                                    dcc.Input(id='point-name-input', type='text',
                                              placeholder=t('zcyc_point_name_placeholder'),
                                              className="w-100", style={'height': '38px'})
                                ], width=12)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(t('zcyc_point_term_label'), className="mt-2"),
                                    dcc.Input(id='point-term-input', type='number', placeholder='0.5', step=0.1,
                                              className="w-100", style={'height': '38px'})
                                ], width=6),
                                dbc.Col([
                                    html.Label(t('zcyc_point_yield_label'), className="mt-2"),
                                    dcc.Input(id='point-yield-input', type='number', placeholder='5.0', step=0.1,
                                              className="w-100", style={'height': '38px'})
                                ], width=6)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label(t('zcyc_point_color_label'), className="mt-2"),
                                    dcc.Dropdown(
                                        id='point-color-input',
                                        options=_point_color_options(),
                                        value='#007bff', clearable=False
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label(t('zcyc_point_size_label'), className="mt-2"),
                                    dcc.Slider(
                                        id='point-size-input', min=5, max=20, step=1,
                                        marks={i: str(i) for i in [5, 10, 15, 20]},
                                        value=10, tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(t('zcyc_add_point_btn'),
                                               id="add-point-btn",
                                               color="primary",
                                               className="w-100 mt-3")
                                ], width=6),
                                dbc.Col([
                                    dbc.Button(t('zcyc_clear_points_btn'),
                                               id="clear-points-btn",
                                               color="danger",
                                               className="w-100 mt-3")
                                ], width=6)
                            ]),
                            html.H6(t('zcyc_added_points_heading'), className="mt-4"),
                            html.Div(id='points-list-container', className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(t('zcyc_export_points_btn'),
                                               id="export-points-btn",
                                               color="secondary",
                                               className="w-100 mt-2")
                                ], width=6),
                                dbc.Col([
                                    dcc.Upload(
                                        id='import-points-upload',
                                        children=html.Div([t('zcyc_import_points_label')]),
                                        style={
                                            'width': '100%', 'height': '38px', 'lineHeight': '38px',
                                            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                                            'borderColor': colors['dim'], 'color': colors['text'],
                                            'textAlign': 'center', 'marginTop': '8px', 'cursor': 'pointer'
                                        },
                                        multiple=False
                                    )
                                ], width=6)
                            ]),
                            html.Div(id='import-status', className="text-muted mt-2")
                        ])
                    ], className="mb-4"),

                    # 1. Справочная информация о формуле ZCYC (текстовый вариант)
                    dbc.Card([
                        dbc.CardHeader(t('zcyc_formula_card_header'), className="bg-light text-dark"),
                        dbc.CardBody([
                            html.P([
                                t('zcyc_formula_intro'),
                                html.Strong("Y(t) = 100·(e^{G(t)} - 1)"),
                                html.Br(),
                                t('zcyc_formula_where'),
                                html.Br(),
                                t('zcyc_formula_note'),
                            ], className="text-muted", style={"fontSize": "12px", "lineHeight": "1.4"})
                        ])
                    ], className="mb-4"),

                    # 2. Параметры модели ZCYC с MOEX (β₀, β₁, β₂, τ, g₁…g₉)
                    dbc.Card([
                        dbc.CardHeader(t('zcyc_params_card_header'), className="bg-warning text-dark"),
                        dbc.CardBody([
                            dash_table.DataTable(
                                id='params-table',
                                columns=[
                                    {"name": t('zcyc_param_col'), "id": "parameter"},
                                    {"name": t('zcyc_value_col'), "id": "value"}
                                ],
                                data=[],  # будет заполнено колбэком update_data
                                style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': '12px',
                                            'backgroundColor': colors['panel'], 'color': colors['text'],
                                            'border': f"1px solid {colors['dim']}"},
                                style_header={'backgroundColor': colors['dim'], 'color': colors['green'],
                                              'fontWeight': 'bold', 'border': f"1px solid {colors['dim']}"},
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': colors['panel']}
                                ]
                            )
                        ])
                    ], className="mb-4"),

                    # 3. Фиксированные константы aᵢ и bᵢ (i=1..9)
                    dbc.Card([
                        dbc.CardHeader(t('zcyc_constants_card_header'), className="bg-secondary text-white"),
                        dbc.CardBody([
                            dash_table.DataTable(
                                id='constants-table',
                                columns=[
                                    {"name": "i", "id": "i"},
                                    {"name": "aᵢ", "id": "a"},
                                    {"name": "bᵢ", "id": "b"}
                                ],
                                data=[
                                    {"i": 1, "a": 0.0, "b": 0.6},
                                    {"i": 2, "a": 0.6, "b": 0.96},
                                    {"i": 3, "a": 2.2, "b": 1.536},
                                    {"i": 4, "a": 5.4, "b": 2.4576},
                                    {"i": 5, "a": 12.0, "b": 3.93216},
                                    {"i": 6, "a": 25.0, "b": 6.291456},
                                    {"i": 7, "a": 50.6, "b": 10.0663296},
                                    {"i": 8, "a": 101.4, "b": 16.10612736},
                                    {"i": 9, "a": 202.8, "b": 25.76980378}
                                ],
                                style_cell={'textAlign': 'center', 'padding': '6px', 'fontSize': '11px',
                                            'backgroundColor': colors['panel'], 'color': colors['text'],
                                            'border': f"1px solid {colors['dim']}"},
                                style_header={'backgroundColor': colors['dim'], 'color': colors['green'],
                                              'fontWeight': 'bold', 'border': f"1px solid {colors['dim']}"},
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': colors['panel']}
                                ]
                            )
                        ])
                    ], className="mb-4")
                ], style=SIDEBAR_STYLE)
            ], width=3),

            # Правая часть (основной контент)
            dbc.Col([
                # Основной график
                dbc.Card([
                    dbc.CardHeader(t('zcyc_main_chart_card_header'), className="bg-dark text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='zcyc-plot',
                            style={'height': '500px'},
                            config={
                                'toImageButtonOptions': {
                                    'format': 'png',
                                    'filename': 'zcyc_plot',
                                    'height': 600,
                                    'width': 1200,
                                    'scale': 2
                                },
                                'displaylogo': False,
                                'modeBarButtonsToAdd': ['toImage']
                            }
                        ),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(t('zcyc_download_curve_btn'),
                                           id="download-data-btn",
                                           color="secondary",
                                           className="w-100")
                            ], width=4),
                            dbc.Col([
                                dbc.Button(t('zcyc_download_points_csv_btn'),
                                           id="download-points-btn",
                                           color="secondary",
                                           className="w-100")
                            ], width=4),
                            dbc.Col([
                                html.Div(id='download-status', className="text-muted")
                            ], width=4)
                        ])
                    ])
                ], className="mb-4"),

                # Блок: Пользовательские точки (таблица)
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(t('zcyc_custom_points_card_header'), className="bg-info text-white"),
                            dbc.CardBody([
                                dash_table.DataTable(
                                    id='points-table',
                                    columns=[
                                        {"name": t('zcyc_col_id'), "id": "ID", "editable": False},
                                        {"name": t('zcyc_col_name'), "id": "Название", "editable": True},
                                        {"name": t('zcyc_col_term'), "id": "Срок (лет)", "editable": False},
                                        {"name": t('zcyc_col_yield'), "id": "Доходность (%)", "editable": True}
                                    ],
                                    page_size=10,
                                    style_table={'overflowX': 'auto', 'height': '400px', 'overflowY': 'auto'},
                                    style_cell={'textAlign': 'center', 'padding': '8px',
                                                'backgroundColor': colors['panel'], 'color': colors['text'],
                                                'border': f"1px solid {colors['dim']}"},
                                    style_header={'backgroundColor': colors['dim'], 'color': colors['green'],
                                                  'fontWeight': 'bold', 'border': f"1px solid {colors['dim']}"},
                                    sort_action='native',
                                    sort_mode='single',
                                    row_selectable='multi'
                                ),
                                dbc.Button(t('zcyc_delete_selected_btn'),
                                           id="delete-selected-points-btn",
                                           color="danger",
                                           className="mt-2")
                            ])
                        ])
                    ], width=12)
                ], className="mt-4"),

                # Блок: Облигации по ИНН эмитента
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(t('zcyc_bonds_card_header'), className="bg-secondary text-white"),
                            dbc.CardBody([
                                # Первая строка: ИНН и кнопка загрузки
                                dbc.Row([
                                    dbc.Col([
                                        html.Label(t('zcyc_inn_label')),
                                        dcc.Input(id='inn-input', type='text',
                                                  placeholder=t('zcyc_inn_placeholder'),
                                                  className="w-100", style={'height': '38px'}),
                                    ], width=6),
                                    dbc.Col([
                                        html.Label(" "),
                                        dbc.Button(t('zcyc_load_bonds_btn'), id='load-bonds-btn', color="primary",
                                                   className="w-100"),
                                    ], width=6)
                                ]),
                                # Вторая строка: выбор цвета и кнопки добавления
                                dbc.Row([
                                    dbc.Col([
                                        html.Label(t('zcyc_bond_color_label'), className="mt-2"),
                                        dcc.Dropdown(
                                            id='bond-point-color',
                                            options=_point_color_options(),
                                            value='#007bff',
                                            clearable=False,
                                            className="mt-1"
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        html.Label(" "),
                                        dbc.Button(t('zcyc_add_selected_btn'), id='add-selected-points-btn',
                                                   color="success", className="w-100 mt-2"),
                                    ], width=4),
                                    dbc.Col([
                                        html.Label(" "),
                                        dbc.Button(t('zcyc_add_all_btn'), id='add-all-points-btn',
                                                   color="info", className="w-100 mt-2"),
                                    ], width=4)
                                ]),
                                html.Hr(),
                                html.Div(id='bonds-status-message', className="text-muted mb-2"),
                                dash_table.DataTable(
                                    id='bonds-table',
                                    columns=[],
                                    data=[],
                                    row_selectable='multi',
                                    page_size=8,
                                    style_table={'overflowX': 'auto'},
                                    style_cell={'textAlign': 'left', 'padding': '8px', 'fontSize': '12px',
                                                'backgroundColor': colors['panel'], 'color': colors['text'],
                                                'border': f"1px solid {colors['dim']}"},
                                    style_header={'backgroundColor': colors['dim'], 'color': colors['green'],
                                                  'fontWeight': 'bold', 'border': f"1px solid {colors['dim']}"},
                                    filter_action='native',
                                    sort_action='native'
                                ),
                                html.Hr(),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(t('zcyc_download_bonds_csv_btn'), id='download-bonds-csv-btn',
                                                   color="secondary", className="w-100")
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Button(t('zcyc_download_bonds_json_btn'), id='download-bonds-json-btn',
                                                   color="secondary", className="w-100")
                                    ], width=6)
                                ])
                            ])
                        ])
                    ], width=12)
                ], className="mt-4")
            ], width=9, style={'margin-left': '25rem'})
        ]),

        # Скрытые элементы для скачивания
        dcc.Download(id="download-data"),
        dcc.Download(id="download-points"),
        dcc.Download(id="export-points"),
        dcc.Download(id="download-bonds-csv"),
        dcc.Download(id="download-bonds-json"),

        # Хранилища данных
        dcc.Store(id='zcyc-data-store'),
        dcc.Store(id='calculated-curve-store'),
        dcc.Store(id='custom-points-store', data=[]),
        dcc.Store(id='bonds-data-store'),
        dcc.Store(id='cbr-rates-store'),

        # Интервал для автообновления
        dcc.Interval(
            id='interval-component',
            interval=5 * 60 * 1000,
            n_intervals=0
        ),

        # Для отладки (скрытый элемент)
        html.Div(id='debug-store-output', style={'display': 'none'})

    ], fluid=True)
