"""Разметка дашборда NEWS ANALYTICS."""
import datetime as dt

from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc

from .theme import TEXT_MUTED

TABLE_COLUMNS = [
    {"name": "Дата", "id": "news_date"},
    {"name": "Компания", "id": "company_name"},
    {"name": "Заголовок", "id": "title"},
    {"name": "Тональность", "id": "sentiment_label"},
    {"name": "Источник", "id": "source"},
]


def stat_tile(tile_id, label):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(label, className="stat-tile-label", style={"color": TEXT_MUTED, "fontSize": "13px"}),
                html.Div(id=tile_id, className="stat-tile-value", style={"fontSize": "32px", "fontWeight": "600"}),
            ]
        ),
        className="stat-tile",
    )


def create_layout():
    today = dt.date.today()
    default_start = today - dt.timedelta(days=30)

    return dbc.Container(
        [
            html.H2("NEWS ANALYTICS", style={"marginTop": "20px"}),
            html.Div("Сводка новостей по компаниям (источник: vedomosti.ru, классификация LLM)", style={"color": TEXT_MUTED, "marginBottom": "20px"}),

            # Filters — одна строка над графиками
            dbc.Row(
                [
                    dbc.Col(
                        dcc.DatePickerRange(
                            id="filter-date-range",
                            start_date=default_start,
                            end_date=today,
                            display_format="YYYY-MM-DD",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="filter-companies",
                            multi=True,
                            placeholder="Все компании",
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="filter-sentiment",
                            options=[
                                {"label": "Позитив", "value": "positive"},
                                {"label": "Негатив", "value": "negative"},
                                {"label": "Нейтрально", "value": "neutral"},
                            ],
                            multi=True,
                            placeholder="Все тональности",
                        ),
                        width=3,
                    ),
                ],
                className="mb-4",
                align="center",
            ),

            # KPI row
            dbc.Row(
                [
                    dbc.Col(stat_tile("kpi-total", "Всего новостей"), width=3),
                    dbc.Col(stat_tile("kpi-positive", "Позитивных"), width=3),
                    dbc.Col(stat_tile("kpi-negative", "Негативных"), width=3),
                    dbc.Col(stat_tile("kpi-companies", "Компаний в выборке"), width=3),
                ],
                className="mb-4 g-3",
            ),

            # Charts
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="chart-by-company"), width=6),
                    dbc.Col(dcc.Graph(id="chart-timeline"), width=6),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="chart-sentiment-diverging"), width=12),
                ],
                className="mb-4",
            ),

            # Table
            html.H5("Новости"),
            dash_table.DataTable(
                id="news-table",
                columns=TABLE_COLUMNS,
                page_size=15,
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "fontFamily": "system-ui, sans-serif", "padding": "8px", "maxWidth": "400px", "overflow": "hidden", "textOverflow": "ellipsis"},
                style_header={"fontWeight": "600", "backgroundColor": "#f9f9f7"},
            ),
        ],
        fluid=True,
        style={"paddingBottom": "60px"},
    )
