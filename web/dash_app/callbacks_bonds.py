"""
Колбэки для загрузки облигаций по ИНН и добавления их как точек.
"""
import json
from datetime import datetime

import pandas as pd
from dash import dcc, html, dash_table, Input, Output, State, callback, no_update, callback_context

from .exchange import get_bonds_by_inn, get_cbr_rates, enrich_bonds
from .i18n import t


def register_callbacks(app):
    """Регистрирует колбэки для работы с облигациями."""

    @app.callback(
        [Output('bonds-data-store', 'data'),
         Output('bonds-status-message', 'children')],
        Input('load-bonds-btn', 'n_clicks'),
        State('inn-input', 'value'),
        prevent_initial_call=True
    )
    def load_bonds(n_clicks, inn):
        if not inn:
            return no_update, t('zcyc_enter_inn')
        try:
            bonds_df = get_bonds_by_inn(inn.strip())
            if bonds_df.empty:
                return None, t('zcyc_no_bonds_found').format(inn=inn)

            rates = get_cbr_rates()
            enriched_df = enrich_bonds(bonds_df, rates)

            if enriched_df.empty:
                return None, t('zcyc_bonds_found_no_details')

            return enriched_df.to_dict('records'), t('zcyc_bonds_loaded').format(count=len(enriched_df))

        except Exception as e:
            print(f"DEBUG [load_bonds]: exception: {e}")
            import traceback
            traceback.print_exc()
            return None, f"{t('zcyc_error_prefix')}{str(e)}"

    @app.callback(
        [Output('bonds-table', 'columns'),
         Output('bonds-table', 'data')],
        Input('bonds-data-store', 'data')
    )
    def update_bonds_table(data):
        if not data:
            return [], []
        df = pd.DataFrame(data)
        priority = ['Trade Code', 'Short Name', 'Issuer', 'Maturity Date',
                    'Days to Maturity', 'YTM', 'Effective Yield', 'Issue Volume (RUB)']
        existing = [c for c in priority if c in df.columns]
        other = [c for c in df.columns if c not in priority]
        ordered = existing + other
        columns = [{"name": col, "id": col} for col in ordered]
        return columns, df.to_dict('records')

    @app.callback(
        Output('download-bonds-csv', 'data'),
        Input('download-bonds-csv-btn', 'n_clicks'),
        State('bonds-data-store', 'data'),
        prevent_initial_call=True
    )
    def download_bonds_csv(n_clicks, data):
        if not data:
            return no_update
        df = pd.DataFrame(data)
        return dcc.send_data_frame(df.to_csv, "bonds.csv", index=False, encoding='utf-8')

    @app.callback(
        Output('download-bonds-json', 'data'),
        Input('download-bonds-json-btn', 'n_clicks'),
        State('bonds-data-store', 'data'),
        prevent_initial_call=True
    )
    def download_bonds_json(n_clicks, data):
        if not data:
            return no_update
        return dict(content=json.dumps(data, ensure_ascii=False, indent=2), filename="bonds.json")

    @app.callback(
        [Output('custom-points-store', 'data', allow_duplicate=True),
         Output('points-list-container', 'children', allow_duplicate=True),
         Output('points-table', 'data', allow_duplicate=True)],
        Input('add-selected-points-btn', 'n_clicks'),
        [State('bonds-table', 'selected_rows'),
         State('bonds-table', 'data'),
         State('custom-points-store', 'data'),
         State('bond-point-color', 'value')],
        prevent_initial_call=True
    )
    def add_selected_bonds_as_points(n_clicks, selected_rows, table_data, current_points, color):
        try:
            if not selected_rows or not table_data:
                if current_points is None:
                    current_points = []
                points_list = _build_points_list_from_store(current_points)
                table_data_points = _build_table_data_from_store(current_points)
                return current_points, points_list, table_data_points

            selected_bonds = [table_data[i] for i in selected_rows]
            issuer_name = selected_bonds[0].get('Issuer', 'Unknown') if selected_bonds else 'Unknown'
            return _add_bonds_to_points(selected_bonds, current_points, color, issuer_name)
        except Exception as e:
            print(f"ERROR in add_selected_bonds_as_points: {e}")
            import traceback
            traceback.print_exc()
            if current_points is None:
                current_points = []
            points_list = _build_points_list_from_store(current_points)
            table_data_points = _build_table_data_from_store(current_points)
            return current_points, points_list, table_data_points

    @app.callback(
        [Output('custom-points-store', 'data', allow_duplicate=True),
         Output('points-list-container', 'children', allow_duplicate=True),
         Output('points-table', 'data', allow_duplicate=True)],
        Input('add-all-points-btn', 'n_clicks'),
        [State('bonds-data-store', 'data'),
         State('custom-points-store', 'data'),
         State('bond-point-color', 'value')],
        prevent_initial_call=True
    )
    def add_all_bonds_as_points(n_clicks, bonds_data, current_points, color):
        try:
            if not bonds_data:
                if current_points is None:
                    current_points = []
                points_list = _build_points_list_from_store(current_points)
                table_data_points = _build_table_data_from_store(current_points)
                return current_points, points_list, table_data_points

            bonds_list = pd.DataFrame(bonds_data).to_dict('records')
            issuer_name = bonds_list[0].get('Issuer', 'Unknown') if bonds_list else 'Unknown'
            return _add_bonds_to_points(bonds_list, current_points, color, issuer_name)
        except Exception as e:
            print(f"ERROR in add_all_bonds_as_points: {e}")
            import traceback
            traceback.print_exc()
            if current_points is None:
                current_points = []
            points_list = _build_points_list_from_store(current_points)
            table_data_points = _build_table_data_from_store(current_points)
            return current_points, points_list, table_data_points


# Вспомогательные функции для работы с точками (используются только внутри этого модуля)
def _add_bonds_to_points(bonds_list, current_points, color, issuer_name=None):
    if current_points is None:
        current_points = []
    new_points = []
    max_id = max([p['id'] for p in current_points]) if current_points else -1

    for bond in bonds_list:
        max_id += 1
        name = bond.get('Short Name', bond.get('Trade Code', 'Unknown'))

        days_str = bond.get('Days to Maturity', '')
        term_years = None
        if days_str and days_str not in ('', 'None'):
            try:
                days = float(days_str)
                term_years = days / 365.0
            except:
                pass

        yield_val = None
        eff_str = bond.get('Effective Yield', '')
        if eff_str and eff_str not in ('', 'None'):
            try:
                yield_val = float(eff_str)
            except:
                pass
        if yield_val is None:
            ytm_str = bond.get('YTM', '')
            if ytm_str and ytm_str not in ('', 'None'):
                try:
                    yield_val = float(ytm_str)
                except:
                    pass

        if term_years is not None and yield_val is not None:
            new_points.append({
                'id': max_id,
                'name': name,
                'issuer': issuer_name,
                'term': term_years,
                'yield': yield_val,
                'color': color,
                'size': 10,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    if not new_points:
        points_list = _build_points_list_from_store(current_points)
        table_data_points = _build_table_data_from_store(current_points)
        return current_points, points_list, table_data_points

    updated_points = current_points + new_points
    points_list = _build_points_list_from_store(updated_points)
    table_data_points = _build_table_data_from_store(updated_points)
    return updated_points, points_list, table_data_points


def _build_points_list_from_store(points):
    """Строит список отображения точек для points-list-container."""
    items = []
    for p in points:
        items.append(html.Div([
            html.Span("●", style={'color': p['color'], 'fontSize': '20px', 'marginRight': '5px'}),
            html.Span(f"{p['name']}: {p['term']:.2f} {t('zcyc_years_word')}, {p['yield']:.2f}%",
                      style={'font-weight': 'bold'}),
            html.Button("×", id={'type': 'delete-point-btn', 'index': p['id']},
                        style={'float': 'right', 'background': 'red', 'color': 'white', 'border': 'none',
                               'borderRadius': '50%', 'width': '20px', 'height': '20px', 'cursor': 'pointer'})
        ], style={'padding': '5px', 'margin': '3px 0', 'backgroundColor': '#f8f9fa',
                  'borderRadius': '5px', 'border': '1px solid #dee2e6'}))
    return items


def _build_table_data_from_store(points):
    """Строит данные для таблицы points-table."""
    return [{'ID': p['id'], 'Название': p['name'], 'Срок (лет)': f"{p['term']:.2f}",
             'Доходность (%)': f"{p['yield']:.2f}"} for p in points]