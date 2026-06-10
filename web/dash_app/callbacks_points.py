"""
Колбэки для управления пользовательскими точками (ручное добавление, импорт/экспорт, удаление, редактирование).
"""
import json
import base64
import io
from datetime import datetime

import pandas as pd
from dash import dcc, html, dash_table, Input, Output, State, callback, no_update, ALL, callback_context

# Константа с колонками таблицы точек
POINTS_TABLE_COLUMNS = [
    {"name": "ID", "id": "ID", "editable": False},
    {"name": "Название", "id": "Название", "editable": True},
    {"name": "Срок (лет)", "id": "Срок (лет)", "editable": False},
    {"name": "Доходность (%)", "id": "Доходность (%)", "editable": True}
]


def register_callbacks(app):
    """Регистрирует колбэки для работы с точками."""

    @app.callback(
        [Output('custom-points-store', 'data'),
         Output('points-list-container', 'children'),
         Output('points-table', 'data'),
         Output('points-table', 'columns'),
         Output('point-name-input', 'value'),
         Output('point-term-input', 'value'),
         Output('point-yield-input', 'value'),
         Output('import-status', 'children')],
        [Input('add-point-btn', 'n_clicks'),
         Input('clear-points-btn', 'n_clicks'),
         Input('import-points-upload', 'contents')],
        [State('point-name-input', 'value'),
         State('point-term-input', 'value'),
         State('point-yield-input', 'value'),
         State('point-color-input', 'value'),
         State('point-size-input', 'value'),
         State('custom-points-store', 'data'),
         State('import-points-upload', 'filename')]
    )
    def manage_points(add_clicks, clear_clicks, upload_contents, name, term, yield_val,
                      color, size, current_points, filename):
        if current_points is None:
            current_points = []
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, '', '', '', ''

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'clear-points-btn':
            return [], html.Div("Все точки очищены"), [], POINTS_TABLE_COLUMNS, '', '', '', ''

        if button_id == 'import-points-upload' and upload_contents:
            try:
                content_type, content_string = upload_contents.split(',')
                decoded = base64.b64decode(content_string)
                if filename and filename.endswith('.json'):
                    points_data = json.loads(decoded.decode('utf-8'))
                    for i, p in enumerate(points_data):
                        p['id'] = i
                        if 'issuer' not in p:
                            p['issuer'] = None
                    table_data = [{'ID': p['id'], 'Название': p['name'], 'Срок (лет)': f"{p['term']:.2f}",
                                   'Доходность (%)': f"{p['yield']:.2f}"} for p in points_data]
                    points_list = _build_points_list(points_data)
                    return points_data, points_list, table_data, POINTS_TABLE_COLUMNS, '', '', '', \
                           html.Div(f"Импортировано {len(points_data)} точек", style={'color': 'green'})
                elif filename and filename.endswith('.csv'):
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                    points_data = []
                    for i, row in df.iterrows():
                        points_data.append({
                            'id': i,
                            'name': row.get('Название', row.get('name', '')),
                            'term': float(row.get('Срок', row.get('term', 0))),
                            'yield': float(row.get('Доходность', row.get('yield', 0))),
                            'color': row.get('Цвет', row.get('color', '#007bff')),
                            'size': int(row.get('Размер', row.get('size', 10))),
                            'issuer': None,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                    table_data = [{'ID': p['id'], 'Название': p['name'], 'Срок (лет)': f"{p['term']:.2f}",
                                   'Доходность (%)': f"{p['yield']:.2f}"} for p in points_data]
                    points_list = _build_points_list(points_data)
                    return points_data, points_list, table_data, POINTS_TABLE_COLUMNS, '', '', '', \
                           html.Div(f"Импортировано {len(points_data)} точек", style={'color': 'green'})
                else:
                    return no_update, no_update, no_update, no_update, '', '', '', \
                           html.Div("Поддерживаются только JSON и CSV", style={'color': 'red'})
            except Exception as e:
                return no_update, no_update, no_update, no_update, '', '', '', \
                       html.Div(f"Ошибка импорта: {str(e)}", style={'color': 'red'})

        if button_id == 'add-point-btn':
            if not name or not term or not yield_val:
                return no_update, html.Div("Заполните все поля!", style={'color': 'red'}), \
                       no_update, no_update, name, term, yield_val, ''
            try:
                term_val = float(term)
                yield_val_float = float(yield_val)
            except ValueError:
                return no_update, html.Div("Срок и доходность должны быть числами", style={'color': 'red'}), \
                       no_update, no_update, name, term, yield_val, ''

            new_id = len(current_points)
            new_point = {
                'id': new_id,
                'name': name.strip(),
                'issuer': None,
                'term': term_val,
                'yield': yield_val_float,
                'color': color,
                'size': int(size),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            updated_points = current_points + [new_point]

            points_list = _build_points_list(updated_points)
            table_data = [{'ID': p['id'], 'Название': p['name'], 'Срок (лет)': f"{p['term']:.2f}",
                           'Доходность (%)': f"{p['yield']:.2f}"} for p in updated_points]

            return updated_points, points_list, table_data, POINTS_TABLE_COLUMNS, '', '', '', ''

        return no_update, no_update, no_update, no_update, '', '', '', ''

    @app.callback(
        [Output('custom-points-store', 'data', allow_duplicate=True),
         Output('points-list-container', 'children', allow_duplicate=True),
         Output('points-table', 'data', allow_duplicate=True)],
        [Input({'type': 'delete-point-btn', 'index': ALL}, 'n_clicks')],
        [State('custom-points-store', 'data')],
        prevent_initial_call=True
    )
    def delete_point(delete_clicks, current_points):
        ctx = callback_context
        if not ctx.triggered or not current_points:
            return no_update, no_update, no_update

        if not any(delete_clicks):
            return no_update, no_update, no_update

        prop_id = ctx.triggered[0]['prop_id']
        json_part = prop_id.replace('.n_clicks', '') if '.n_clicks' in prop_id else prop_id

        try:
            button_id_dict = json.loads(json_part)
            point_id = button_id_dict['index']
        except Exception as e:
            print(f"Ошибка парсинга ID кнопки: {e}")
            return no_update, no_update, no_update

        updated_points = [p for p in current_points if p['id'] != point_id]
        for i, p in enumerate(updated_points):
            p['id'] = i

        points_list = _build_points_list(updated_points)
        table_data = [{'ID': p['id'], 'Название': p['name'], 'Срок (лет)': f"{p['term']:.2f}",
                       'Доходность (%)': f"{p['yield']:.2f}"} for p in updated_points]

        return updated_points, points_list, table_data

    @app.callback(
        [Output('custom-points-store', 'data', allow_duplicate=True),
         Output('points-list-container', 'children', allow_duplicate=True),
         Output('points-table', 'data', allow_duplicate=True),
         Output('points-table', 'selected_rows')],
        [Input('delete-selected-points-btn', 'n_clicks')],
        [State('points-table', 'selected_rows'),
         State('points-table', 'data'),
         State('custom-points-store', 'data')],
        prevent_initial_call=True
    )
    def delete_selected_points(n_clicks, selected_rows, table_data, current_points):
        if not n_clicks or n_clicks == 0:
            return no_update, no_update, no_update, no_update

        if not selected_rows or not table_data:
            return no_update, no_update, no_update, no_update

        selected_ids = [table_data[i]['ID'] for i in selected_rows]
        updated_points = [p for p in current_points if p['id'] not in selected_ids]

        for i, p in enumerate(updated_points):
            p['id'] = i

        points_list = _build_points_list(updated_points)
        table_data_new = [{'ID': p['id'], 'Название': p['name'], 'Срок (лет)': f"{p['term']:.2f}",
                           'Доходность (%)': f"{p['yield']:.2f}"} for p in updated_points]

        return updated_points, points_list, table_data_new, []

    @app.callback(
        [Output('custom-points-store', 'data', allow_duplicate=True),
         Output('points-list-container', 'children', allow_duplicate=True),
         Output('points-table', 'data', allow_duplicate=True)],
        [Input('points-table', 'data')],
        [State('points-table', 'data_previous'),
         State('custom-points-store', 'data')],
        prevent_initial_call=True
    )
    def edit_point_cell(new_table_data, old_table_data, current_points):
        ctx = callback_context
        if not ctx.triggered or not old_table_data or not current_points:
            return no_update, no_update, no_update

        changed = False
        new_points = [dict(p) for p in current_points]

        id_to_idx = {p['id']: i for i, p in enumerate(new_points)}

        for old_row, new_row in zip(old_table_data, new_table_data):
            if old_row['ID'] != new_row['ID']:
                continue
            point_id = old_row['ID']
            if point_id not in id_to_idx:
                continue
            idx = id_to_idx[point_id]

            # Изменение названия
            if old_row['Название'] != new_row['Название']:
                new_points[idx]['name'] = new_row['Название']
                changed = True

            # Изменение доходности
            if old_row['Доходность (%)'] != new_row['Доходность (%)']:
                try:
                    new_yield = float(new_row['Доходность (%)'])
                    new_points[idx]['yield'] = new_yield
                    changed = True
                except ValueError:
                    # Если введено не число – откатываем изменение
                    return no_update, no_update, no_update

        if not changed:
            return no_update, no_update, no_update

        points_list = _build_points_list(new_points)
        table_data = [{'ID': p['id'], 'Название': p['name'], 'Срок (лет)': f"{p['term']:.2f}",
                       'Доходность (%)': f"{p['yield']:.2f}"} for p in new_points]

        return new_points, points_list, table_data

    @app.callback(
        Output("download-points", "data"),
        [Input("download-points-btn", "n_clicks")],
        [State("custom-points-store", "data")]
    )
    def download_points(n_clicks, data):
        if n_clicks and data:
            try:
                points_list = []
                for p in data:
                    points_list.append({
                        'Название': p.get('name', ''),
                        'Эмитент': p.get('issuer', ''),
                        'Срок (лет)': p.get('term', 0),
                        'Доходность (%)': p.get('yield', 0),
                        'Цвет': p.get('color', '#007bff'),
                        'Размер': p.get('size', 10)
                    })
                df = pd.DataFrame(points_list)
                return dcc.send_data_frame(df.to_csv, "custom_points.csv", index=False)
            except Exception as e:
                print(f"Error downloading points: {e}")
        return None

    @app.callback(
        Output("export-points", "data"),
        [Input("export-points-btn", "n_clicks")],
        [State("custom-points-store", "data")]
    )
    def export_points(n_clicks, data):
        if n_clicks and data:
            try:
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                return dict(content=json_str, filename="custom_points.json")
            except Exception as e:
                print(f"Error exporting points: {e}")
        return None


def _build_points_list(points):
    """Вспомогательная функция для построения списка точек с кнопками удаления."""
    items = []
    for p in points:
        items.append(html.Div([
            html.Span("●", style={'color': p['color'], 'fontSize': '20px', 'marginRight': '5px'}),
            html.Span(f"{p['name']}: {p['term']:.2f} лет, {p['yield']:.2f}%", style={'font-weight': 'bold'}),
            html.Button("×", id={'type': 'delete-point-btn', 'index': p['id']},
                        style={'float': 'right', 'background': 'red', 'color': 'white', 'border': 'none',
                               'borderRadius': '50%', 'width': '20px', 'height': '20px', 'cursor': 'pointer'})
        ], style={'padding': '5px', 'margin': '3px 0', 'backgroundColor': '#f8f9fa',
                  'borderRadius': '5px', 'border': '1px solid #dee2e6'}))
    return items