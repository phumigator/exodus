"""Разметка дашборда NEWS ANALYTICS."""
import datetime as dt

from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc

from dash_app.i18n import pip_colors, t


def _table_columns():
    return [
        {"name": t("analytics_col_date"), "id": "news_date"},
        {"name": t("analytics_col_company"), "id": "company_name"},
        {"name": t("analytics_col_title"), "id": "title"},
        {"name": t("analytics_col_sentiment"), "id": "sentiment_label"},
        {"name": t("analytics_col_source"), "id": "source", "presentation": "markdown"},
    ]


def _sentiment_options():
    return [
        {"label": t("analytics_sentiment_positive"), "value": "positive"},
        {"label": t("analytics_sentiment_negative"), "value": "negative"},
        {"label": t("analytics_sentiment_neutral"), "value": "neutral"},
    ]


def stat_tile(tile_id, label):
    colors = pip_colors()
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(label, className="stat-tile-label", style={"color": colors["text"], "fontSize": "13px"}),
                html.Div(id=tile_id, className="stat-tile-value", style={"fontSize": "32px", "fontWeight": "600"}),
            ]
        ),
        className="stat-tile",
    )


def create_layout():
    today = dt.date.today()
    default_start = today - dt.timedelta(days=30)
    colors = pip_colors()

    return dbc.Container(
        [
            html.H2(t("analytics_header_title"), style={"marginTop": "20px"}),
            html.Div(t("analytics_header_subtitle"), style={"color": colors["text"], "marginBottom": "20px"}),

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
                            placeholder=t("analytics_filter_companies_placeholder"),
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="filter-sentiment",
                            options=_sentiment_options(),
                            multi=True,
                            placeholder=t("analytics_filter_sentiment_placeholder"),
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
                    dbc.Col(stat_tile("kpi-total", t("analytics_kpi_total")), width=3),
                    dbc.Col(stat_tile("kpi-positive", t("analytics_kpi_positive")), width=3),
                    dbc.Col(stat_tile("kpi-negative", t("analytics_kpi_negative")), width=3),
                    dbc.Col(stat_tile("kpi-companies", t("analytics_kpi_companies")), width=3),
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
            html.H5(t("analytics_table_heading")),
            dash_table.DataTable(
                id="news-table",
                columns=_table_columns(),
                page_size=15,
                markdown_options={"link_target": "_blank"},
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left",
                    "fontFamily": "system-ui, sans-serif",
                    "padding": "8px",
                    "maxWidth": "400px",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "backgroundColor": colors["panel"],
                    "color": colors["text"],
                },
                style_header={
                    "fontWeight": "600",
                    "backgroundColor": colors["panel"],
                    "color": colors["green"],
                    "border": f"1px solid {colors['dim']}",
                },
                style_data={"border": f"1px solid {colors['dim']}"},
            ),
        ],
        fluid=True,
        style={"paddingBottom": "60px"},
    )
