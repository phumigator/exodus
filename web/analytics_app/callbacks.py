"""Callbacks: фильтры -> KPI, графики, таблица."""
from urllib.parse import urlparse

import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output

from . import data
from .theme import SENTIMENT_COLORS, SEQUENTIAL_BLUE
from dash_app.i18n import pip_colors, t


def _sentiment_labels():
    return {
        "positive": t("analytics_sentiment_positive"),
        "negative": t("analytics_sentiment_negative"),
        "neutral": t("analytics_sentiment_neutral"),
    }


def _base_layout(colors):
    return dict(
        paper_bgcolor=colors["panel"],
        plot_bgcolor=colors["panel"],
        font=dict(color=colors["text"], size=13),
        margin=dict(l=10, r=10, t=40, b=10),
    )


def _empty_figure(title, colors):
    fig = go.Figure()
    fig.update_layout(title=title, **_base_layout(colors))
    fig.add_annotation(text=t("analytics_chart_no_data"), showarrow=False, font=dict(color=colors["text"]))
    return fig


def _chart_by_company(df, colors):
    if df.empty:
        return _empty_figure(t("analytics_chart_by_company_title"), colors)
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
        title=t("analytics_chart_by_company_title"),
        xaxis=dict(gridcolor=colors["dim"], zeroline=False),
        yaxis=dict(gridcolor=colors["dim"]),
        **_base_layout(colors),
    )
    return fig


def _chart_timeline(df, colors):
    if df.empty:
        return _empty_figure(t("analytics_chart_timeline_title"), colors)
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
        title=t("analytics_chart_timeline_title"),
        xaxis=dict(gridcolor=colors["dim"], zeroline=False),
        yaxis=dict(gridcolor=colors["dim"], zeroline=False),
        **_base_layout(colors),
    )
    return fig


def _chart_sentiment_diverging(df, colors):
    """Diverging stacked bar по компаниям, отцентрированный на нейтральной тональности."""
    if df.empty:
        return _empty_figure(t("analytics_chart_sentiment_title"), colors)

    labels = _sentiment_labels()
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
            name=labels["negative"],
            y=pivot.index,
            x=pivot["negative"],
            base=-(pivot["negative"] + half_neutral),
            orientation="h",
            marker_color=SENTIMENT_COLORS["negative"],
        )
    )
    fig.add_trace(
        go.Bar(
            name=labels["neutral"],
            y=pivot.index,
            x=pivot["neutral"],
            base=-half_neutral,
            orientation="h",
            marker_color=SENTIMENT_COLORS["neutral"],
        )
    )
    fig.add_trace(
        go.Bar(
            name=labels["positive"],
            y=pivot.index,
            x=pivot["positive"],
            base=half_neutral,
            orientation="h",
            marker_color=SENTIMENT_COLORS["positive"],
        )
    )
    fig.update_layout(
        title=t("analytics_chart_sentiment_title"),
        barmode="overlay",
        xaxis=dict(gridcolor=colors["dim"], zeroline=True, zerolinecolor=colors["dim"]),
        yaxis=dict(gridcolor=colors["dim"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=colors["text"])),
        **_base_layout(colors),
    )
    return fig


def _source_link(source):
    """`source` в БД бывает полным URL статьи ('https://www.rbc.ru/...') или просто
    голым доменом ('vedomosti.ru', без схемы) — во втором случае ссылка на конкретную
    статью недоступна, ведём на главную страницу издания."""
    if not source:
        return ""
    url = source if source.startswith(("http://", "https://")) else f"https://{source}"
    domain = urlparse(url).netloc.removeprefix("www.") or source
    return f"[{domain}]({url})"


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
        colors = pip_colors()
        labels = _sentiment_labels()

        total = len(df)
        positive = int((df["sentiment"] == "positive").sum()) if not df.empty else 0
        negative = int((df["sentiment"] == "negative").sum()) if not df.empty else 0
        companies_count = df["company_name"].nunique() if not df.empty else 0

        table_df = df.copy()
        if not table_df.empty:
            table_df["sentiment_label"] = table_df["sentiment"].map(labels).fillna(table_df["sentiment"])
            table_df["news_date"] = pd.to_datetime(table_df["news_date"]).dt.strftime("%Y-%m-%d")
            table_df["source"] = table_df["source"].apply(_source_link)

        return (
            f"{total:,}".replace(",", " "),
            positive,
            negative,
            companies_count,
            _chart_by_company(df, colors),
            _chart_timeline(df, colors),
            _chart_sentiment_diverging(df, colors),
            table_df.to_dict("records"),
        )
