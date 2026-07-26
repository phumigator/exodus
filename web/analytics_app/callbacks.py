"""Callbacks: фильтры -> KPI, графики, таблица."""
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output

from . import data
from .theme import (
    BASELINE,
    FONT_FAMILY,
    GRIDLINE,
    SENTIMENT_COLORS,
    SENTIMENT_LABELS_RU,
    SEQUENTIAL_BLUE,
    SURFACE,
    TEXT_MUTED,
    TEXT_PRIMARY,
)

BASE_LAYOUT = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY, size=13),
    margin=dict(l=10, r=10, t=40, b=10),
)


def _empty_figure(title):
    fig = go.Figure()
    fig.update_layout(title=title, **BASE_LAYOUT)
    fig.add_annotation(text="Нет данных за выбранный период", showarrow=False, font=dict(color=TEXT_MUTED))
    return fig


def _chart_by_company(df):
    if df.empty:
        return _empty_figure("Новости по компаниям")
    counts = df.groupby("company_name").size().sort_values(ascending=True).tail(15)
    fig = go.Figure(
        go.Bar(
            x=counts.values,
            y=counts.index,
            orientation="h",
            marker_color=SEQUENTIAL_BLUE,
        )
    )
    fig.update_layout(
        title="Новости по компаниям (топ-15)",
        xaxis=dict(gridcolor=GRIDLINE, zeroline=False),
        yaxis=dict(gridcolor=GRIDLINE),
        **BASE_LAYOUT,
    )
    return fig


def _chart_timeline(df):
    if df.empty:
        return _empty_figure("Динамика новостей")
    daily = df.groupby("news_date").size().reset_index(name="count").sort_values("news_date")
    fig = go.Figure(
        go.Scatter(
            x=daily["news_date"],
            y=daily["count"],
            mode="lines",
            line=dict(color=SEQUENTIAL_BLUE, width=2),
            fill="tozeroy",
            fillcolor="rgba(42,120,214,0.12)",
        )
    )
    fig.update_layout(
        title="Динамика количества новостей",
        xaxis=dict(gridcolor=GRIDLINE, zeroline=False),
        yaxis=dict(gridcolor=GRIDLINE, zeroline=False),
        **BASE_LAYOUT,
    )
    return fig


def _chart_sentiment_diverging(df):
    """Diverging stacked bar по компаниям, отцентрированный на нейтральной тональности."""
    if df.empty:
        return _empty_figure("Тональность по компаниям")

    pivot = df.pivot_table(index="company_name", columns="sentiment", values="id", aggfunc="count", fill_value=0)
    for s in ("negative", "neutral", "positive"):
        if s not in pivot.columns:
            pivot[s] = 0

    total = pivot["negative"] + pivot["neutral"] + pivot["positive"]
    pivot = pivot.loc[total.sort_values(ascending=True).index].tail(15)

    half_neutral = pivot["neutral"] / 2
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name=SENTIMENT_LABELS_RU["negative"],
            y=pivot.index,
            x=pivot["negative"],
            base=-(pivot["negative"] + half_neutral),
            orientation="h",
            marker_color=SENTIMENT_COLORS["negative"],
        )
    )
    fig.add_trace(
        go.Bar(
            name=SENTIMENT_LABELS_RU["neutral"],
            y=pivot.index,
            x=pivot["neutral"],
            base=-half_neutral,
            orientation="h",
            marker_color=SENTIMENT_COLORS["neutral"],
        )
    )
    fig.add_trace(
        go.Bar(
            name=SENTIMENT_LABELS_RU["positive"],
            y=pivot.index,
            x=pivot["positive"],
            base=half_neutral,
            orientation="h",
            marker_color=SENTIMENT_COLORS["positive"],
        )
    )
    fig.update_layout(
        title="Тональность по компаниям (топ-15 по объёму)",
        barmode="overlay",
        xaxis=dict(gridcolor=GRIDLINE, zeroline=True, zerolinecolor=BASELINE),
        yaxis=dict(gridcolor=GRIDLINE),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **BASE_LAYOUT,
    )
    return fig


def register_callbacks(app):
    @app.callback(
        Output("filter-companies", "options"),
        Input("filter-companies", "id"),
    )
    def load_company_options(_):
        return [{"label": name, "value": name} for name in data.load_company_names()]

    @app.callback(
        Output("kpi-total", "children"),
        Output("kpi-positive", "children"),
        Output("kpi-negative", "children"),
        Output("kpi-companies", "children"),
        Output("chart-by-company", "figure"),
        Output("chart-timeline", "figure"),
        Output("chart-sentiment-diverging", "figure"),
        Output("news-table", "data"),
        Input("filter-date-range", "start_date"),
        Input("filter-date-range", "end_date"),
        Input("filter-companies", "value"),
        Input("filter-sentiment", "value"),
    )
    def update_dashboard(start_date, end_date, companies, sentiments):
        df = data.load_news(date_from=start_date, date_to=end_date, companies=companies, sentiments=sentiments)

        total = len(df)
        positive = int((df["sentiment"] == "positive").sum()) if not df.empty else 0
        negative = int((df["sentiment"] == "negative").sum()) if not df.empty else 0
        companies_count = df["company_name"].nunique() if not df.empty else 0

        table_df = df.copy()
        if not table_df.empty:
            table_df["sentiment_label"] = table_df["sentiment"].map(SENTIMENT_LABELS_RU).fillna(table_df["sentiment"])
            table_df["news_date"] = pd.to_datetime(table_df["news_date"]).dt.strftime("%Y-%m-%d")

        return (
            f"{total:,}".replace(",", " "),
            positive,
            negative,
            companies_count,
            _chart_by_company(df),
            _chart_timeline(df),
            _chart_sentiment_diverging(df),
            table_df.to_dict("records"),
        )
