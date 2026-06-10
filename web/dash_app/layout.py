"""
Модуль с макетом (layout) дашборда.
"""
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

# Стиль для левой панели (сайдбар)
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "25rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow-y": "auto",
}


def create_layout():
    """Возвращает корневой layout приложения."""
    return dbc.Container([
        # Заголовок
        dbc.Row([
            dbc.Col([
                html.H1("📊 ZCYC Dashboard + Облигации по ИНН",
                        className="text-center mb-4",
                        style={'color': '#2c3e50'})
            ], width=12)
        ]),

        dbc.Row([
            # Левая панель (управление ZCYC)
            dbc.Col([
                html.Div([
                    # Информация о данных
                    dbc.Card([
                        dbc.CardHeader("Информация о данных", className="bg-primary text-white"),
                        dbc.CardBody([
                            html.H5(id='date-display', className="card-title"),
                            html.H6(id='time-display', className="card-subtitle mb-2"),
                            html.P(
                                "Кривая бескупонной доходности (Zero-Coupon Yield Curve) - это зависимость доходности бескупонных облигаций от срока до погашения.",
                                className="card-text text-muted"),
                            dbc.Button("🔄 Обновить данные",
                                       id="refresh-btn",
                                       color="success",
                                       className="mt-2 w-100")
                        ])
                    ], className="mb-4"),

                    # Настройки графика
                    dbc.Card([
                        dbc.CardHeader("Настройки графика", className="bg-info text-white"),
                        dbc.CardBody([
                            html.H6("Диапазон срока (лет):", className="mt-2"),
                            dcc.RangeSlider(
                                id='x-range-slider',
                                min=0.01, max=50, step=0.5,
                                marks={i: str(i) for i in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]},
                                value=[0.01, 30],
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                            html.H6("Диапазон доходности (%):", className="mt-4"),
                            dcc.RangeSlider(
                                id='y-range-slider',
                                min=-10, max=50, step=0.5,
                                marks={i: str(i) for i in [-10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]},
                                value=[-2, 20],
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Цвет линии кривой:", className="mt-3"),
                                    dcc.Dropdown(
                                        id='line-color',
                                        options=[
                                            {'label': '🔴 Красный', 'value': '#dc3545'},
                                            {'label': '🔵 Синий', 'value': '#007bff'},
                                            {'label': '🟢 Зеленый', 'value': '#28a745'},
                                            {'label': '🟣 Фиолетовый', 'value': '#6f42c1'},
                                            {'label': '🟠 Оранжевый', 'value': '#fd7e14'},
                                            {'label': '⚫ Черный', 'value': '#343a40'}
                                        ],
                                        value='#dc3545', clearable=False
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Толщина линии:", className="mt-3"),
                                    dcc.Slider(
                                        id='line-width', min=1, max=6, step=0.5,
                                        marks={i: str(i) for i in range(1, 7)},
                                        value=3, tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6)
                            ]),
                            html.Label("Тип линии:", className="mt-3"),
                            dcc.Dropdown(
                                id='line-style',
                                options=[
                                    {'label': 'Сплошная', 'value': 'solid'},
                                    {'label': 'Пунктир', 'value': 'dash'},
                                    {'label': 'Точечная', 'value': 'dot'},
                                    {'label': 'Штрих-пунктир', 'value': 'dashdot'}
                                ],
                                value='solid', clearable=False
                            ),
                            # Чекбоксы для управления отображением
                            dbc.Row([
                                dbc.Col([
                                    dbc.Checklist(
                                        id='show-point-labels',
                                        options=[{"label": "Показывать названия точек", "value": True}],
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
                                        options=[{"label": "Показывать легенду", "value": True}],
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
                                        options=[{"label": "Показывать заголовок", "value": True}],
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
                                        options=[{"label": "Показать сетку", "value": True}],
                                        value=[True],
                                        switch=True,
                                        className="mt-2"
                                    )
                                ], width=12)
                            ]),
                            # Переключатель режима подписей
                            html.Label("Режим подписей точек:", className="mt-3"),
                            dcc.RadioItems(
                                id='label-mode',
                                options=[
                                    {'label': ' У точек', 'value': 'inline'},
                                    {'label': ' В выносках (с линиями)', 'value': 'callout'}
                                ],
                                value='inline',
                                labelStyle={'display': 'block', 'margin': '5px 0'}
                            ),
                            # Слайдер угла поворота подписей
                            html.Label("Угол поворота подписей (градусы):", className="mt-3"),
                            dcc.Slider(
                                id='label-angle',
                                min=-90, max=90, step=5,
                                marks={-90: '-90', -45: '-45', 0: '0', 45: '45', 90: '90'},
                                value=0,
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                            dbc.Button("🔄 Автонастройка оси Y",
                                       id="auto-y-btn",
                                       color="warning",
                                       className="mt-3 w-100")
                        ])
                    ], className="mb-4"),

                    # Форма для добавления пользовательских точек вручную
                    dbc.Card([
                        dbc.CardHeader("Добавить точки вручную", className="bg-success text-white"),
                        dbc.CardBody([
                            html.H6("Добавить новую точку:", className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Название инструмента:", className="mt-2"),
                                    dcc.Input(id='point-name-input', type='text', placeholder='Введите название...',
                                              className="w-100", style={'height': '38px'})
                                ], width=12)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Срок до погашения (лет):", className="mt-2"),
                                    dcc.Input(id='point-term-input', type='number', placeholder='0.5', step=0.1,
                                              className="w-100", style={'height': '38px'})
                                ], width=6),
                                dbc.Col([
                                    html.Label("Доходность (%):", className="mt-2"),
                                    dcc.Input(id='point-yield-input', type='number', placeholder='5.0', step=0.1,
                                              className="w-100", style={'height': '38px'})
                                ], width=6)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Цвет точки:", className="mt-2"),
                                    dcc.Dropdown(
                                        id='point-color-input',
                                        options=[
                                            {'label': '🔵 Синий', 'value': '#007bff'},
                                            {'label': '🟢 Зеленый', 'value': '#28a745'},
                                            {'label': '🟡 Желтый', 'value': '#ffc107'},
                                            {'label': '🔴 Красный', 'value': '#dc3545'},
                                            {'label': '🟣 Фиолетовый', 'value': '#6f42c1'},
                                            {'label': '🟠 Оранжевый', 'value': '#fd7e14'},
                                            {'label': '🩵 Голубой', 'value': '#17a2b8'},
                                            {'label': '💗 Розовый', 'value': '#e83e8c'},
                                            {'label': '⚫ Тёмно-серый', 'value': '#343a40'},
                                            {'label': '💚 Светло-зеленый', 'value': '#20c997'},
                                            {'label': '🔷 Индиго', 'value': '#6610f2'},
                                            {'label': '💜 Малиновый', 'value': '#d63384'},
                                            {'label': '⬜ Серый', 'value': '#6c757d'},
                                            {'label': '💙 Ярко-синий', 'value': '#0d6efd'},
                                            {'label': '🧡 Коралловый', 'value': '#ff7f50'},
                                            {'label': '🤎 Коричневый', 'value': '#8B4513'}
                                        ],
                                        value='#007bff', clearable=False
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Размер точки:", className="mt-2"),
                                    dcc.Slider(
                                        id='point-size-input', min=5, max=20, step=1,
                                        marks={i: str(i) for i in [5, 10, 15, 20]},
                                        value=10, tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=6)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("➕ Добавить точку",
                                               id="add-point-btn",
                                               color="primary",
                                               className="w-100 mt-3")
                                ], width=6),
                                dbc.Col([
                                    dbc.Button("🗑️ Очистить все точки",
                                               id="clear-points-btn",
                                               color="danger",
                                               className="w-100 mt-3")
                                ], width=6)
                            ]),
                            html.H6("Добавленные точки:", className="mt-4"),
                            html.Div(id='points-list-container', className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("📥 Экспорт точек (JSON)",
                                               id="export-points-btn",
                                               color="secondary",
                                               className="w-100 mt-2")
                                ], width=6),
                                dbc.Col([
                                    dcc.Upload(
                                        id='import-points-upload',
                                        children=html.Div(['📤 Импорт точек']),
                                        style={
                                            'width': '100%', 'height': '38px', 'lineHeight': '38px',
                                            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
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
                        dbc.CardHeader("📐 Модель кривой ZCYC", className="bg-light text-dark"),
                        dbc.CardBody([
                            html.P([
                                "Доходность для срока t (лет): ",
                                html.Strong("Y(t) = 100·(e^{G(t)} - 1)"),
                                html.Br(),
                                "где G(t) = β₀ + β₁·(τ/t)·(1 - e^{-t/τ}) + β₂·[(τ/t)·(1 - e^{-t/τ}) - e^{-t/τ}] + Σ_{i=1}^{9} gᵢ·exp(-(t - aᵢ)² / bᵢ²)",
                                html.Br(),
                                "β₀,β₁,β₂,τ,g₁…g₉ – параметры MOEX;  aᵢ,bᵢ – фиксированные константы (см. таблицу ниже)."
                            ], className="text-muted", style={"fontSize": "12px", "lineHeight": "1.4"})
                        ])
                    ], className="mb-4"),

                    # 2. Параметры модели ZCYC с MOEX (β₀, β₁, β₂, τ, g₁…g₉)
                    dbc.Card([
                        dbc.CardHeader("Параметры модели ZCYC (MOEX)", className="bg-warning text-dark"),
                        dbc.CardBody([
                            dash_table.DataTable(
                                id='params-table',
                                columns=[
                                    {"name": "Параметр", "id": "parameter"},
                                    {"name": "Значение", "id": "value"}
                                    # , {"name": "Описание", "id": "description"}
                                ],
                                data=[],  # будет заполнено колбэком update_data
                                style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': '12px'},
                                style_header={'backgroundColor': '#ffc107', 'fontWeight': 'bold'},
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
                                ]
                            )
                        ])
                    ], className="mb-4"),

                    # 3. Фиксированные константы aᵢ и bᵢ (i=1..9)
                    dbc.Card([
                        dbc.CardHeader("Фиксированные константы aᵢ, bᵢ", className="bg-secondary text-white"),
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
                                style_cell={'textAlign': 'center', 'padding': '6px', 'fontSize': '11px'},
                                style_header={'backgroundColor': '#6c757d', 'color': 'white', 'fontWeight': 'bold'},
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
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
                    dbc.CardHeader("Кривая бескупонной доходности с пользовательскими точками",
                                   className="bg-dark text-white"),
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
                                dbc.Button("📊 Скачать данные кривой (CSV)",
                                           id="download-data-btn",
                                           color="secondary",
                                           className="w-100")
                            ], width=4),
                            dbc.Col([
                                dbc.Button("📋 Скачать точки (CSV)",
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
                            dbc.CardHeader("Пользовательские точки", className="bg-info text-white"),
                            dbc.CardBody([
                                dash_table.DataTable(
                                    id='points-table',
                                    columns=[
                                        {"name": "ID", "id": "ID", "editable": False},
                                        {"name": "Название", "id": "Название", "editable": True},
                                        {"name": "Срок (лет)", "id": "Срок (лет)", "editable": False},
                                        {"name": "Доходность (%)", "id": "Доходность (%)", "editable": True}
                                    ],
                                    page_size=10,
                                    style_table={'overflowX': 'auto', 'height': '400px', 'overflowY': 'auto'},
                                    style_cell={'textAlign': 'center', 'padding': '8px'},
                                    style_header={'backgroundColor': 'rgb(200, 200, 200)', 'fontWeight': 'bold'},
                                    sort_action='native',
                                    sort_mode='single',
                                    row_selectable='multi'
                                ),
                                dbc.Button("🗑️ Удалить выбранные",
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
                            dbc.CardHeader("📈 Облигации по ИНН эмитента", className="bg-secondary text-white"),
                            dbc.CardBody([
                                # Первая строка: ИНН и кнопка загрузки
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Введите ИНН:"),
                                        dcc.Input(id='inn-input', type='text', placeholder='Например, 7707083893',
                                                  className="w-100", style={'height': '38px'}),
                                    ], width=6),
                                    dbc.Col([
                                        html.Label(" "),
                                        dbc.Button("🔍 Загрузить облигации", id='load-bonds-btn', color="primary",
                                                   className="w-100"),
                                    ], width=6)
                                ]),
                                # Вторая строка: выбор цвета и кнопки добавления
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Выберите цвет для добавляемых точек:", className="mt-2"),
                                        dcc.Dropdown(
                                            id='bond-point-color',
                                            options=[
                                                {'label': '🔵 Синий', 'value': '#007bff'},
                                                {'label': '🟢 Зеленый', 'value': '#28a745'},
                                                {'label': '🟡 Желтый', 'value': '#ffc107'},
                                                {'label': '🔴 Красный', 'value': '#dc3545'},
                                                {'label': '🟣 Фиолетовый', 'value': '#6f42c1'},
                                                {'label': '🟠 Оранжевый', 'value': '#fd7e14'},
                                                {'label': '🩵 Голубой', 'value': '#17a2b8'},
                                                {'label': '💗 Розовый', 'value': '#e83e8c'},
                                                {'label': '⚫ Тёмно-серый', 'value': '#343a40'},
                                                {'label': '💚 Светло-зеленый', 'value': '#20c997'},
                                                {'label': '🔷 Индиго', 'value': '#6610f2'},
                                                {'label': '💜 Малиновый', 'value': '#d63384'},
                                                {'label': '⬜ Серый', 'value': '#6c757d'},
                                                {'label': '💙 Ярко-синий', 'value': '#0d6efd'},
                                                {'label': '🧡 Коралловый', 'value': '#ff7f50'},
                                                {'label': '🤎 Коричневый', 'value': '#8B4513'}
                                            ],
                                            value='#007bff',
                                            clearable=False,
                                            className="mt-1"
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        html.Label(" "),
                                        dbc.Button("➕ Добавить выбранные", id='add-selected-points-btn',
                                                   color="success", className="w-100 mt-2"),
                                    ], width=4),
                                    dbc.Col([
                                        html.Label(" "),
                                        dbc.Button("➕ Добавить все", id='add-all-points-btn',
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
                                    style_cell={'textAlign': 'left', 'padding': '8px', 'fontSize': '12px'},
                                    style_header={'backgroundColor': '#6c757d', 'color': 'white', 'fontWeight': 'bold'},
                                    filter_action='native',
                                    sort_action='native'
                                ),
                                html.Hr(),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button("📥 Скачать таблицу CSV", id='download-bonds-csv-btn',
                                                   color="secondary", className="w-100")
                                    ], width=6),
                                    dbc.Col([
                                        dbc.Button("📥 Скачать таблицу JSON", id='download-bonds-json-btn',
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