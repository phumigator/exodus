"""
Колбэки для загрузки данных ZCYC, расчёта кривой и настройки графика.
"""
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, callback, no_update, callback_context
import dash_bootstrap_components as dbc

from .exchange import fetch_zcyc_data, calculate_zcyc_curve, default_zcyc_data
from .i18n import t, pip_colors

CURVE_POINTS = 1500


def _text_color_for_bg(bg_hex, text_fallback, grid_fallback):
    """Тёмный текст/сетка для светлых фонов (сейчас актуально только для белого
    в _bg_color_options), иначе — обычные цвета темы (зелёный/янтарный)."""
    try:
        r, g, b = int(bg_hex[1:3], 16), int(bg_hex[3:5], 16), int(bg_hex[5:7], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    except (TypeError, ValueError):
        return text_fallback, grid_fallback
    if luminance > 0.6:
        return '#1a1a1a', '#999999'
    return text_fallback, grid_fallback


def register_callbacks(app):
    """Регистрирует колбэки, связанные с кривой и графиком."""

    @app.callback(
        [Output('zcyc-data-store', 'data'),
         Output('params-table', 'data'),
         Output('date-display', 'children'),
         Output('time-display', 'children')],
        [Input('refresh-btn', 'n_clicks'),
         Input('interval-component', 'n_intervals')]
    )
    def update_data(n_clicks, n_intervals):
        ctx = callback_context
        if not ctx.triggered:
            # Используем default_zcyc_data, если нет триггера
            date_display = f"{t('zcyc_date_prefix')}{default_zcyc_data['tradedate'].iloc[0]}"
            time_display = f"{t('zcyc_time_prefix')}{default_zcyc_data['tradetime'].iloc[0]}"
            params_data = [
                {"parameter": "B1 (beta0)", "value": f"{float(default_zcyc_data['B1'].iloc[0]):.6f}"},
                {"parameter": "B2 (beta1)", "value": f"{float(default_zcyc_data['B2'].iloc[0]):.6f}"},
                {"parameter": "B3 (beta2)", "value": f"{float(default_zcyc_data['B3'].iloc[0]):.6f}"},
                {"parameter": "T1 (tau)", "value": f"{float(default_zcyc_data['T1'].iloc[0]):.6f}"},
                {"parameter": t('zcyc_param_date'), "value": default_zcyc_data['tradedate'].iloc[0]}
            ]
            return default_zcyc_data.to_dict('records'), params_data, date_display, time_display

        df_data_new, error = fetch_zcyc_data()
        if df_data_new is None:
            # Если ошибка, возвращаем no_update для всех выходов
            return no_update, no_update, no_update, no_update

        date_display = f"{t('zcyc_date_prefix')}{df_data_new['tradedate'].iloc[0]}"
        time_display = f"{t('zcyc_time_prefix')}{df_data_new['tradetime'].iloc[0]}"

        params_data = [
            {"parameter": "B1 (beta0)", "value": f"{float(df_data_new['B1'].iloc[0]):.6f}"},
            {"parameter": "B2 (beta1)", "value": f"{float(df_data_new['B2'].iloc[0]):.6f}"},
            {"parameter": "B3 (beta2)", "value": f"{float(df_data_new['B3'].iloc[0]):.6f}"},
            {"parameter": "T1 (tau)", "value": f"{float(df_data_new['T1'].iloc[0]):.6f}"},
            {"parameter": t('zcyc_param_date'), "value": df_data_new['tradedate'].iloc[0]}
        ]

        return df_data_new.to_dict('records'), params_data, date_display, time_display

    @app.callback(
        Output('calculated-curve-store', 'data'),
        [Input('zcyc-data-store', 'data'),
         Input('x-range-slider', 'value')]
    )
    def calculate_curve(data, x_range):
        if not data:
            return {}
        try:
            df_data = pd.DataFrame(data)
            if df_data.empty:
                return {}
            params = df_data.iloc[0].to_dict()
            t_min, t_max = x_range
            results_df, error = calculate_zcyc_curve(params, t_min, t_max, CURVE_POINTS)
            if error:
                return {}
            return results_df.to_dict('records')
        except Exception as e:
            print(f"Exception in calculate_curve: {e}")
            return {}

    @app.callback(
        Output('zcyc-plot', 'figure'),
        [Input('calculated-curve-store', 'data'),
         Input('y-range-slider', 'value'),
         Input('line-color', 'value'),
         Input('line-width', 'value'),
         Input('line-style', 'value'),
         Input('zcyc-data-store', 'data'),
         Input('custom-points-store', 'data'),
         Input('show-point-labels', 'value'),
         Input('show-legend', 'value'),
         Input('show-title', 'value'),
         Input('show-grid', 'value'),
         Input('label-mode', 'value'),
         Input('x-range-slider', 'value'),
         Input('chart-bg-color', 'value')]
    )
    def update_plots(curve_data, y_range, line_color, line_width, line_style,
                     raw_data, custom_points, show_labels, show_legend, show_title,
                     show_grid, label_mode, x_range, chart_bg_color):
        # Преобразование чекбоксов
        show_labels = bool(show_labels and show_labels[0]) if isinstance(show_labels, list) else bool(show_labels)
        show_legend = bool(show_legend and show_legend[0]) if isinstance(show_legend, list) else bool(show_legend)
        show_title = bool(show_title and show_title[0]) if isinstance(show_title, list) else bool(show_title)
        show_grid = bool(show_grid and show_grid[0]) if isinstance(show_grid, list) else bool(show_grid)

        colors = pip_colors()
        # Ручной выбор фона (dropdown 'chart-bg-color') переопределяет фон темы,
        # пока не выбран пункт "По умолчанию" (value='auto').
        bg_color = chart_bg_color if chart_bg_color and chart_bg_color != 'auto' else colors['panel']
        text_color, grid_color = _text_color_for_bg(bg_color, colors['text'], colors['dim'])

        if not curve_data:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title=t('zcyc_no_curve_data') if show_title else "",
                xaxis_title=t('zcyc_x_axis_title'),
                yaxis_title=t('zcyc_y_axis_title'),
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color,
                font=dict(color=text_color),
                height=500
            )
            return empty_fig

        try:
            results_df = pd.DataFrame(curve_data)
            if results_df.empty:
                empty_fig = go.Figure()
                empty_fig.update_layout(
                    title=t('zcyc_curve_data_empty') if show_title else "",
                    plot_bgcolor=bg_color,
                    paper_bgcolor=bg_color,
                    font=dict(color=text_color),
                    height=500,
                )
                return empty_fig

            fig_main = go.Figure()
            fig_main.add_trace(go.Scatter(
                x=results_df['Срок (лет)'],
                y=results_df['Доходность (%)'],
                mode='lines',
                name=t('zcyc_curve_trace_name'),
                line=dict(color=line_color, width=line_width, dash=line_style),
                hovertemplate=(f"{t('zcyc_term_word')}: %{{x:.2f}} {t('zcyc_years_word')}<br>"
                                f"{t('zcyc_yield_word')}: %{{y:.4f}}%<extra></extra>")
            ))

            if custom_points:
                groups = {}
                for point in custom_points:
                    key = point.get('issuer') if point.get('issuer') else point['name']
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(point)

                for group_name, points in groups.items():
                    color = points[0]['color']
                    x_vals = [p['term'] for p in points]
                    y_vals = [p['yield'] for p in points]
                    names = [p['name'] for p in points]
                    sizes = [p.get('size', 10) for p in points]

                    # Добавляем маркеры (всегда)
                    fig_main.add_trace(go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode='markers',
                        name=group_name,
                        marker=dict(size=sizes, color=color, symbol='circle', line=dict(width=1, color='white')),
                        hovertemplate=(
                            "<b>%{text}</b><br>"
                            f"{t('zcyc_term_word')}: %{{x:.2f}} {t('zcyc_years_word')}<br>"
                            f"{t('zcyc_yield_word')}: %{{y:.2f}}%<br>"
                            "<extra></extra>"
                        ),
                        text=names  # для ховера
                    ))

                    # Добавляем подписи в зависимости от режима
                    if show_labels:
                        if label_mode == 'inline':
                            # Текст рядом с точками
                            fig_main.add_trace(go.Scatter(
                                x=x_vals,
                                y=y_vals,
                                mode='text',
                                text=names,
                                textposition="top center",
                                textfont=dict(size=10),
                                showlegend=False,
                                hoverinfo='none'
                            ))
                        else:  # callout
                            # Вычисляем смещение на основе диапазонов осей
                            if x_range is not None and len(x_range) == 2:
                                x_min, x_max = x_range
                                x_offset = (x_max - x_min) * 0.02  # 2% от ширины диапазона
                            else:
                                x_offset = 0.2
                            if y_range is not None and len(y_range) == 2:
                                y_min, y_max = y_range
                                y_offset = (y_max - y_min) * 0.02
                            else:
                                y_offset = 0.1

                            for i, point in enumerate(points):
                                fig_main.add_annotation(
                                    x=point['term'],
                                    y=point['yield'],
                                    ax=point['term'] + x_offset,
                                    ay=point['yield'] + y_offset,
                                    xref='x',
                                    yref='y',
                                    axref='x',
                                    ayref='y',
                                    text=point['name'],
                                    showarrow=True,
                                    arrowhead=2,
                                    arrowsize=1,
                                    arrowwidth=1,
                                    arrowcolor='gray',
                                    font=dict(size=10),
                                    align='center',
                                    bordercolor='lightgray',
                                    borderwidth=1,
                                    borderpad=2,
                                    bgcolor='rgba(255,255,255,0.8)'
                                )

            title_text = ''
            if show_title:
                title_text = t('zcyc_chart_title')
                if raw_data:
                    try:
                        df_raw = pd.DataFrame(raw_data)
                        if not df_raw.empty:
                            date_str = df_raw['tradedate'].iloc[0]
                            time_str = df_raw['tradetime'].iloc[0]
                            title_text += f' - {date_str} {time_str}'
                    except:
                        pass
                if custom_points:
                    title_text += t('zcyc_points_count_suffix').format(count=len(custom_points))

            # Формируем настройки осей с учётом сетки
            xaxis_layout = dict(
                title=t('zcyc_x_axis_title'),
                showgrid=show_grid,
                gridwidth=1,
                gridcolor=grid_color,
                griddash='solid'
            )
            yaxis_layout = dict(
                title=t('zcyc_y_axis_title'),
                range=y_range,
                showgrid=show_grid,
                gridwidth=1,
                gridcolor=grid_color,
                griddash='solid'
            )

            fig_main.update_layout(
                title=title_text,
                xaxis=xaxis_layout,
                yaxis=yaxis_layout,
                hovermode='closest',
                showlegend=show_legend,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                            font=dict(color=text_color)),
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color,
                font=dict(color=text_color),
                height=500
            )

            return fig_main

        except Exception as e:
            print(f"Exception in update_plots: {e}")
            import traceback
            traceback.print_exc()
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title=f"{t('zcyc_error_prefix')}{str(e)}" if show_title else "",
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color,
                font=dict(color=text_color),
            )
            return empty_fig

    @app.callback(
        Output('y-range-slider', 'value'),
        [Input('auto-y-btn', 'n_clicks'),
         Input('calculated-curve-store', 'data'),
         Input('custom-points-store', 'data')],
        [State('y-range-slider', 'value')]
    )
    def auto_adjust_y_range(n_clicks, curve_data, custom_points, current_range):
        ctx = callback_context
        if not ctx.triggered:
            return current_range
        min_val = float('inf')
        max_val = float('-inf')
        if curve_data:
            try:
                df = pd.DataFrame(curve_data)
                if not df.empty and 'Доходность (%)' in df.columns:
                    min_val = min(min_val, df['Доходность (%)'].min())
                    max_val = max(max_val, df['Доходность (%)'].max())
            except:
                pass
        if custom_points:
            try:
                for p in custom_points:
                    y = p.get('yield')
                    if y is not None:
                        min_val = min(min_val, y)
                        max_val = max(max_val, y)
            except:
                pass
        if min_val == float('inf') or max_val == float('-inf'):
            return current_range
        padding = (max_val - min_val) * 0.1
        new_min = max(min_val - padding, -10)
        new_max = min(max_val + padding, 20)
        return [new_min, new_max]

    @app.callback(
        Output("download-data", "data"),
        [Input("download-data-btn", "n_clicks")],
        [State("calculated-curve-store", "data")]
    )
    def download_data(n_clicks, data):
        if n_clicks and data:
            try:
                df = pd.DataFrame(data)
                return dcc.send_data_frame(df.to_csv, "zcyc_data.csv", index=False)
            except Exception as e:
                print(f"Error downloading data: {e}")
        return None