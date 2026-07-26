"""NEWS ANALYTICS — раздел сводки новостей по компаниям, монтируется как отдельное Dash под-приложение.

Перенесено из отдельного проекта news-analytics (github.com/phumigator/... по завершении).
Оформление пока не приведено к общему pipboy-стилю ZCYC — раздел незавершённый.
"""
import dash
import dash_bootstrap_components as dbc

from .callbacks import register_callbacks
from .layout import create_layout


def create_analytics_app(server, url_base_pathname="/analytics/"):
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname=url_base_pathname,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title="News Analytics",
    )
    app.layout = create_layout
    register_callbacks(app)
    return app
