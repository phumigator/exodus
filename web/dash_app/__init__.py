"""
ZCYC Dash-приложение, монтируемое как под-приложение Flask.
"""
import dash
import dash_bootstrap_components as dbc

from .layout import create_layout
from .callbacks_curve import register_callbacks as register_curve
from .callbacks_points import register_callbacks as register_points
from .callbacks_bonds import register_callbacks as register_bonds
from .callbacks_utils import register_callbacks as register_utils


def create_dash_app(server, url_base_pathname="/zcyc/"):
    """Создаёт Dash-приложение, использующее переданный Flask-сервер."""
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname=url_base_pathname,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title="ZCYC",
        suppress_callback_exceptions=True,
    )

    app.layout = create_layout()

    register_curve(app)
    register_points(app)
    register_bonds(app)
    register_utils(app)

    return app
