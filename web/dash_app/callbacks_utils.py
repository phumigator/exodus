"""
Общие колбэки (статус скачивания, отладка).
"""
from dash import html, Input, Output, callback, callback_context

from .i18n import t


def register_callbacks(app):
    """Регистрирует общие колбэки."""

    @app.callback(
        Output('download-status', 'children'),
        [Input('download-data-btn', 'n_clicks'),
         Input('download-points-btn', 'n_clicks'),
         Input('export-points-btn', 'n_clicks')]
    )
    def update_download_status(data_clicks, points_clicks, export_clicks):
        ctx = callback_context
        if not ctx.triggered:
            return ""
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'download-data-btn':
            return html.Span(t('zcyc_status_curve_downloaded'), className="text-success")
        elif button_id == 'download-points-btn':
            return html.Span(t('zcyc_status_points_csv_downloaded'), className="text-success")
        elif button_id == 'export-points-btn':
            return html.Span(t('zcyc_status_points_json_exported'), className="text-success")
        return ""

    @app.callback(
        Output('debug-store-output', 'children'),
        Input('custom-points-store', 'data')
    )
    def debug_store(data):
        print(f"DEBUG [store] data = {data}")
        return ""